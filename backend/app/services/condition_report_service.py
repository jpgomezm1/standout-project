"""Condition report service — orchestrates the multi-message Telegram inspection flow.

A housekeeper starts a session via /reporte, sends audio and photos, and
finalises with /listo.  The service collects all media, generates a
structured report via the LLM, and dispatches operational events.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.domain.entities.event import EventType, OperationalEvent
from app.infrastructure.channels.telegram_adapter import TelegramAdapter
from app.infrastructure.db.models.condition_report import (
    ConditionReportModel,
    ConditionReportSessionModel,
)
from app.infrastructure.db.models.inventory_item import InventoryItemModel
from app.infrastructure.db.models.property import PropertyModel
from app.infrastructure.llm.openai_client import OpenAIClient
from app.services.event_engine import EventEngine

logger = logging.getLogger(__name__)

# Event types that can be generated from condition reports
_VALID_CR_EVENT_TYPES = {"ITEM_MISSING", "ITEM_BROKEN", "MAINTENANCE_ISSUE"}


class ConditionReportService:
    """Orchestrator for the condition report flow."""

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        event_engine: EventEngine,
        openai_client: OpenAIClient,
        telegram_adapter: TelegramAdapter,
    ) -> None:
        self._session = session
        self._settings = settings
        self._event_engine = event_engine
        self._openai = openai_client
        self._telegram = telegram_adapter

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    async def start_session(
        self,
        chat_id: int,
        property_id: UUID,
        staff_id: UUID | None = None,
    ) -> UUID:
        """Create a new collecting session and notify the user."""
        # Fetch property name for the confirmation message
        prop = await self._session.get(PropertyModel, property_id)
        prop_name = prop.name if prop else "propiedad"

        session_model = ConditionReportSessionModel(
            id=uuid4(),
            property_id=property_id,
            staff_id=staff_id,
            telegram_chat_id=chat_id,
            status="collecting",
            voice_transcriptions=[],
            photo_analyses=[],
            photo_file_ids=[],
        )
        self._session.add(session_model)
        await self._session.flush()

        await self._telegram.send_message(
            chat_id,
            f"Sesión de reporte iniciada para *{prop_name}*.\n\n"
            "Envía audios describiendo el estado del inmueble y fotos de daños.\n"
            "Cuando termines, envía /listo",
        )

        logger.info(
            "Condition report session %s started for property %s (chat_id=%d)",
            session_model.id,
            property_id,
            chat_id,
        )
        return session_model.id

    async def get_active_session(
        self, chat_id: int
    ) -> ConditionReportSessionModel | None:
        """Return the active (collecting) session for a chat, if any."""
        stmt = (
            select(ConditionReportSessionModel)
            .where(ConditionReportSessionModel.telegram_chat_id == chat_id)
            .where(ConditionReportSessionModel.status == "collecting")
            .order_by(ConditionReportSessionModel.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Media collection
    # ------------------------------------------------------------------

    async def add_voice(self, session_id: UUID, audio_bytes: bytes) -> None:
        """Transcribe audio and append to the session."""
        session_model = await self._session.get(
            ConditionReportSessionModel, session_id
        )
        if session_model is None:
            logger.error("Session %s not found for add_voice", session_id)
            return

        transcription = await self._openai.transcribe_audio(audio_bytes)

        # Append to the JSONB list
        transcriptions = list(session_model.voice_transcriptions or [])
        transcriptions.append(transcription)
        session_model.voice_transcriptions = transcriptions
        await self._session.flush()

        await self._telegram.send_message(
            session_model.telegram_chat_id,
            "Audio recibido y transcrito.",
        )
        logger.info(
            "Voice added to session %s (%d transcriptions total)",
            session_id,
            len(transcriptions),
        )

    async def add_photo(
        self,
        session_id: UUID,
        photo_bytes: bytes,
        file_id: str | None = None,
    ) -> None:
        """Analyze a photo and append to the session."""
        session_model = await self._session.get(
            ConditionReportSessionModel, session_id
        )
        if session_model is None:
            logger.error("Session %s not found for add_photo", session_id)
            return

        analysis = await self._openai.analyze_image(
            photo_bytes,
            "Describe detalladamente el estado de esta área u objeto de la propiedad. "
            "Identifica cualquier daño, suciedad, elemento faltante o problema de mantenimiento.",
        )

        analyses = list(session_model.photo_analyses or [])
        analyses.append(analysis)
        session_model.photo_analyses = analyses

        if file_id:
            file_ids = list(session_model.photo_file_ids or [])
            file_ids.append(file_id)
            session_model.photo_file_ids = file_ids

        await self._session.flush()

        await self._telegram.send_message(
            session_model.telegram_chat_id,
            "Foto recibida y analizada.",
        )
        logger.info(
            "Photo added to session %s (%d photos total)",
            session_id,
            len(analyses),
        )

    # ------------------------------------------------------------------
    # Finalisation
    # ------------------------------------------------------------------

    async def finalize(self, session_id: UUID) -> UUID | None:
        """Generate the condition report and dispatch events."""
        session_model = await self._session.get(
            ConditionReportSessionModel, session_id
        )
        if session_model is None:
            logger.error("Session %s not found for finalize", session_id)
            return None

        session_model.status = "processing"
        await self._session.flush()

        try:
            # Build context with property info and inventory
            context = await self._build_context(session_model.property_id)

            # Generate structured report via LLM
            report_data = await self._openai.generate_condition_report(
                transcriptions=list(session_model.voice_transcriptions or []),
                photo_analyses=list(session_model.photo_analyses or []),
                context=context,
            )

            # Create operational events
            events_created = await self._create_events(
                report_data.get("operational_events", []),
                session_model.property_id,
            )

            # Persist the report
            report_model = ConditionReportModel(
                id=uuid4(),
                session_id=session_id,
                property_id=session_model.property_id,
                staff_id=session_model.staff_id,
                report_data={
                    "inventory": report_data.get("inventory", []),
                    "damages": report_data.get("damages", []),
                    "general_condition": report_data.get("general_condition", "fair"),
                },
                summary=report_data.get("summary", ""),
                events_created=events_created,
            )
            self._session.add(report_model)

            session_model.status = "completed"
            await self._session.flush()

            await self._telegram.send_message(
                session_model.telegram_chat_id,
                f"Reporte generado exitosamente. "
                f"Se crearon {events_created} evento(s) operacional(es).\n"
                "Puedes verlo en el panel web.",
            )

            logger.info(
                "Condition report %s finalized for session %s (%d events created)",
                report_model.id,
                session_id,
                events_created,
            )
            return report_model.id

        except Exception:
            logger.exception("Failed to finalize session %s", session_id)
            session_model.status = "failed"
            await self._session.flush()

            await self._telegram.send_message(
                session_model.telegram_chat_id,
                "Error al generar el reporte. Por favor intenta de nuevo con /reporte.",
            )
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _build_context(self, property_id: UUID) -> dict:
        """Build LLM context with property name and inventory."""
        prop = await self._session.get(PropertyModel, property_id)
        property_name = prop.name if prop else "Propiedad desconocida"

        stmt = select(InventoryItemModel).where(
            InventoryItemModel.property_id == property_id
        )
        result = await self._session.execute(stmt)
        items = result.scalars().all()

        inventory_items = [
            {
                "item_name": item.item_name,
                "expected_quantity": item.expected_quantity,
            }
            for item in items
        ]

        return {
            "property_name": property_name,
            "inventory_items": inventory_items,
        }

    async def _create_events(
        self,
        operational_events: list[dict],
        property_id: UUID,
    ) -> int:
        """Dispatch operational events from the report findings."""
        count = 0
        now = datetime.now(timezone.utc)

        for evt_data in operational_events:
            event_type_str = evt_data.get("event_type", "")
            if event_type_str not in _VALID_CR_EVENT_TYPES:
                logger.warning(
                    "Skipping invalid event type from condition report: %s",
                    event_type_str,
                )
                continue

            try:
                event_type = EventType(event_type_str)
            except ValueError:
                continue

            event = OperationalEvent(
                id=uuid4(),
                property_id=property_id,
                event_type=event_type,
                payload={
                    "item_name": evt_data.get("item_name"),
                    "quantity": evt_data.get("quantity", 1),
                    "description": evt_data.get("description", ""),
                    "priority": evt_data.get("priority", "medium"),
                    "source": "condition_report",
                },
                source_message_id=None,
                confidence_score=0.9,
                actor_id=None,
                idempotency_key=f"cr-{uuid4()}",
                created_at=now,
            )

            await self._event_engine.dispatch(event)
            count += 1

        logger.info("Created %d operational events from condition report", count)
        return count
