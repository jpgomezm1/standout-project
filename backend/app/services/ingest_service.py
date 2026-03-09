"""Ingest service — the main pipeline orchestrator.

Provides two entry-points:

1. ``process_webhook`` — the fast path.  Parses the raw payload, persists
   the inbound message, and returns immediately so the Telegram webhook
   can receive a 200 response within the timeout window.

2. ``process_message`` — the background processing path.  Downloads any
   media, runs interpretation, resolves entities, checks confidence, and
   dispatches the resulting ``OperationalEvent``(s) through the event
   engine.  If confidence is too low or a required field is missing, the
   clarification service is invoked instead.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.config import Settings
from app.domain.entities.event import EventType, OperationalEvent
from app.domain.entities.message import MessageType, ProcessingStatus
from app.domain.interfaces.channel_adapter import IChannelAdapter
from app.domain.interfaces.event_store import IEventStore
from app.domain.interfaces.repositories import IRawMessageRepository
from app.domain.value_objects.confidence import ConfidenceScore
from app.services.clarification_service import ClarificationService
from app.services.event_engine import EventEngine
from app.services.interpretation_service import InterpretationService

logger = logging.getLogger(__name__)


class IngestService:
    """Orchestrates the full message-to-event pipeline."""

    def __init__(
        self,
        raw_message_repo: IRawMessageRepository,
        interpretation_service: InterpretationService,
        event_store: IEventStore,
        event_engine: EventEngine,
        channel_adapter: IChannelAdapter,
        clarification_service: ClarificationService,
        settings: Settings,
    ) -> None:
        self._raw_message_repo = raw_message_repo
        self._interpretation_service = interpretation_service
        self._event_store = event_store
        self._event_engine = event_engine
        self._channel_adapter = channel_adapter
        self._clarification_service = clarification_service
        self._settings = settings

    # -- Fast path ----------------------------------------------------------- #

    async def process_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Parse and persist the raw webhook payload.

        Returns a minimal response dict immediately.  Actual processing
        happens later via ``process_message``.
        """
        message = await self._channel_adapter.parse_webhook(payload)
        stored = await self._raw_message_repo.create(message)
        logger.info(
            "Webhook accepted — message %s (chat=%d, type=%s)",
            stored.id,
            stored.telegram_chat_id,
            stored.message_type.value,
        )
        return {"status": "accepted", "message_id": str(stored.id)}

    # -- Background processing ----------------------------------------------- #

    async def process_message(self, message_id: UUID) -> None:
        """Run the full interpretation and dispatch pipeline for *message_id*.

        State transitions:
          RECEIVED -> PROCESSING -> PROCESSED          (happy path)
          RECEIVED -> PROCESSING -> NEEDS_CLARIFICATION (low confidence / missing fields)
          RECEIVED -> PROCESSING -> PENDING_RETRY       (transient failure)
        """
        message = await self._raw_message_repo.get_by_id(message_id)
        if message is None:
            logger.error("Message %s not found; cannot process", message_id)
            return

        await self._raw_message_repo.update_status(
            message_id, ProcessingStatus.PROCESSING
        )

        try:
            content = await self._extract_content(message)
            interpreted_events = await self._interpretation_service.interpret(
                content, message
            )

            if not interpreted_events:
                logger.warning(
                    "No events interpreted from message %s; marking as processed",
                    message_id,
                )
                await self._raw_message_repo.update_status(
                    message_id, ProcessingStatus.PROCESSED
                )
                return

            for evt_data in interpreted_events:
                needs_clarification = await self._check_and_clarify(
                    message, evt_data
                )
                if needs_clarification:
                    await self._raw_message_repo.update_status(
                        message_id, ProcessingStatus.NEEDS_CLARIFICATION
                    )
                    return

                event = self._build_event(evt_data, message_id)
                stored_event = await self._event_store.append(event)
                await self._event_engine.dispatch(stored_event)

            await self._raw_message_repo.update_status(
                message_id, ProcessingStatus.PROCESSED
            )
            logger.info(
                "Message %s processed successfully — %d event(s) dispatched",
                message_id,
                len(interpreted_events),
            )

        except Exception:
            logger.exception("Failed to process message %s", message_id)
            await self._raw_message_repo.update_status(
                message_id, ProcessingStatus.PENDING_RETRY
            )

    # -- Internal helpers ---------------------------------------------------- #

    async def _extract_content(self, message: Any) -> str:
        """Combine text content with any transcribed media."""
        content = message.content_text or ""

        if message.file_references:
            for ref in message.file_references:
                file_id = ref.get("file_id") if isinstance(ref, dict) else getattr(ref, "file_id", None)
                if not file_id:
                    continue

                try:
                    media_bytes = await self._channel_adapter.download_media(file_id)
                except Exception:
                    logger.exception(
                        "Failed to download media file_id=%s for message %s",
                        file_id,
                        message.id,
                    )
                    continue

                if message.message_type == MessageType.VOICE:
                    transcription = await self._interpretation_service.transcribe(
                        media_bytes
                    )
                    if transcription:
                        content = f"{content} {transcription}".strip()

                elif message.message_type == MessageType.PHOTO:
                    description = await self._interpretation_service.analyze_image(
                        media_bytes, content
                    )
                    if description:
                        content = f"{content} [Imagen: {description}]".strip()

        return content

    async def _check_and_clarify(
        self,
        message: Any,
        evt_data: dict[str, Any],
    ) -> bool:
        """Return ``True`` if clarification is needed (and request it).

        Clarification is required when:
        - The confidence score is below the ``needs_clarification`` threshold.
        - A required field (``property_id``) is missing after resolution.
        """
        confidence = ConfidenceScore(value=evt_data.get("confidence", 0.0))

        if confidence.needs_clarification or not evt_data.get("property_id"):
            await self._clarification_service.request_clarification(
                message, evt_data
            )
            logger.info(
                "Clarification requested for message %s (confidence=%.2f, "
                "has_property_id=%s)",
                message.id,
                confidence.value,
                bool(evt_data.get("property_id")),
            )
            return True

        return False

    @staticmethod
    def _build_event(
        evt_data: dict[str, Any],
        source_message_id: UUID,
    ) -> OperationalEvent:
        """Construct an ``OperationalEvent`` from the interpreted data."""
        now = datetime.now(timezone.utc)

        # Extract known top-level fields; everything else goes into payload.
        event_type_raw = evt_data.get("event_type", "")
        try:
            event_type = EventType(event_type_raw)
        except ValueError:
            # Fallback: attempt case-insensitive match
            event_type = EventType(event_type_raw.upper())

        property_id = UUID(str(evt_data["property_id"]))
        confidence = float(evt_data.get("confidence", 0.0))
        actor_id_raw = evt_data.get("actor_id")
        actor_id = UUID(str(actor_id_raw)) if actor_id_raw else None

        # Build the payload from all remaining fields.
        reserved_keys = {
            "event_type",
            "property_id",
            "confidence",
            "actor_id",
            "source_message_id",
        }
        payload = {k: v for k, v in evt_data.items() if k not in reserved_keys}

        idempotency_key = evt_data.get(
            "idempotency_key",
            f"{source_message_id}:{event_type.value}:{now.isoformat()}",
        )

        return OperationalEvent(
            id=uuid4(),
            property_id=property_id,
            event_type=event_type,
            payload=payload,
            source_message_id=source_message_id,
            confidence_score=confidence,
            actor_id=actor_id,
            idempotency_key=idempotency_key,
            created_at=now,
        )
