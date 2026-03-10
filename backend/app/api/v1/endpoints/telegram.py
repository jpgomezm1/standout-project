"""Telegram webhook endpoint and background message processing."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header, Request
from sqlalchemy import select

from app.config import Settings
from app.dependencies import DbSessionDep, EventEngineDep, IngestServiceDep, SettingsDep, get_condition_report_service
from app.infrastructure.channels.telegram_adapter import TelegramAdapter
from app.infrastructure.db.models.property import PropertyModel
from app.infrastructure.db.models.raw_message import RawMessageModel
from app.infrastructure.db.models.telegram_user import TelegramUserModel
from app.infrastructure.db.session import get_session_factory, get_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


# ---------------------------------------------------------------------------
# Background task: process a persisted inbound message
# ---------------------------------------------------------------------------

async def process_message_background(
    message_id: UUID,
    chat_id: int,
    settings: Settings,
) -> None:
    """Process a persisted inbound message outside the request lifecycle.

    Creates its own database session so the original request can return
    immediately.  Errors are logged but never propagated -- Telegram
    must always receive a 200 to avoid retries.
    """
    from app.infrastructure.channels.telegram_adapter import TelegramAdapter as _TA
    from app.infrastructure.db.repositories.event_repository import EventRepository
    from app.infrastructure.db.repositories.inventory_repository import InventoryRepository
    from app.infrastructure.db.repositories.property_repository import PropertyRepository
    from app.infrastructure.db.repositories.raw_message_repository import RawMessageRepository
    from app.infrastructure.llm.openai_client import OpenAIClient
    from app.services.clarification_service import ClarificationService
    from app.services.entity_resolver import EntityResolver
    from app.services.event_engine import EventEngine
    from app.services.ingest_service import IngestService
    from app.services.interpretation_service import InterpretationService

    engine = get_engine(settings.DATABASE_URL)
    session_factory = get_session_factory(engine)

    telegram_adapter = _TA(
        bot_token=settings.TELEGRAM_BOT_TOKEN,
        webhook_secret=settings.TELEGRAM_WEBHOOK_SECRET,
    )

    async with session_factory() as session:
        try:
            # Fetch the raw message
            model = await session.get(RawMessageModel, message_id)
            if model is None:
                logger.error(
                    "Background processing: message %s not found", message_id
                )
                return

            # Update status to processing
            model.processing_status = "processing"
            await session.flush()

            # Build all dependencies for the IngestService
            from app.infrastructure.db.repositories.incident_repository import IncidentRepository as _IR

            openai_client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
            property_repo = PropertyRepository(session)
            inventory_repo = InventoryRepository(session)
            incident_repo = _IR(session)
            entity_resolver = EntityResolver(property_repo, inventory_repo, incident_repo)
            interpretation_service = InterpretationService(openai_client, entity_resolver)
            event_store = EventRepository(session)
            event_engine = EventEngine()

            # Register all domain handlers so events actually get processed
            from app.services.handlers import register_all_handlers
            register_all_handlers(event_engine, session_factory=session_factory)

            clarification_service = ClarificationService(telegram_adapter)
            raw_message_repo = RawMessageRepository(session)

            ingest_service = IngestService(
                raw_message_repo=raw_message_repo,
                interpretation_service=interpretation_service,
                event_store=event_store,
                event_engine=event_engine,
                channel_adapter=telegram_adapter,
                clarification_service=clarification_service,
                settings=settings,
            )

            await ingest_service.process_message(message_id)

            await session.commit()

            # Notify the user that the message was processed
            await telegram_adapter.send_message(
                chat_id,
                "Mensaje recibido y procesado correctamente.",
            )

            logger.info(
                "Background processing complete for message %s", message_id
            )
        except Exception:
            logger.exception(
                "Background processing failed for message %s", message_id
            )
            try:
                model = await session.get(RawMessageModel, message_id)
                if model is not None:
                    model.processing_status = "pending_retry"
                    await session.commit()
            except Exception:
                logger.exception(
                    "Failed to mark message %s as pending_retry", message_id
                )
                await session.rollback()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_telegram_adapter(settings: Settings) -> TelegramAdapter:
    return TelegramAdapter(
        bot_token=settings.TELEGRAM_BOT_TOKEN,
        webhook_secret=settings.TELEGRAM_WEBHOOK_SECRET,
    )


async def _resolve_staff_id(db, telegram_user_id: int):
    """Try to resolve a staff_id from a telegram_user_id.

    Matches telegram_user first_name + last_name against staff_members.
    Returns None if no match is found.
    """
    from app.infrastructure.db.models.staff import StaffMemberModel

    stmt = select(TelegramUserModel).where(
        TelegramUserModel.telegram_id == telegram_user_id
    )
    result = await db.execute(stmt)
    tg_user = result.scalar_one_or_none()
    if not tg_user:
        return None

    # Try to match by name
    if tg_user.first_name:
        staff_stmt = select(StaffMemberModel).where(
            StaffMemberModel.first_name == tg_user.first_name,
        )
        if tg_user.last_name:
            staff_stmt = staff_stmt.where(
                StaffMemberModel.last_name == tg_user.last_name,
            )
        staff_result = await db.execute(staff_stmt)
        staff = staff_result.scalar_one_or_none()
        if staff:
            return staff.id

    return None


# ---------------------------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------------------------

@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: DbSessionDep,
    settings: SettingsDep,
    event_engine: EventEngineDep,
    cr_service=Depends(get_condition_report_service),
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, str]:
    """Receive and process an incoming Telegram webhook update.

    Workflow:
    1. Verify the webhook secret token (if configured).
    2. Handle callback queries (inline keyboard selections).
    3. Handle condition report commands and media.
    4. Fall through to normal message processing pipeline.

    Always returns HTTP 200 to prevent Telegram from retrying.
    """
    # -- 1. Secret verification ------------------------------------------------
    if settings.TELEGRAM_WEBHOOK_SECRET:
        if (
            not x_telegram_bot_api_secret_token
            or x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET
        ):
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

    payload = await request.json()

    # Basic payload validation
    update_id = payload.get("update_id")
    if update_id is None:
        logger.warning("Received Telegram payload without update_id")
        return {"status": "ignored"}

    telegram_adapter = _build_telegram_adapter(settings)

    # -- 2. Handle callback queries (property selection for /reporte) ----------
    if "callback_query" in payload:
        try:
            cq = telegram_adapter.parse_callback_query(payload)
            callback_data: str = cq["callback_data"]
            chat_id: int = cq["chat_id"]
            user_id: int = cq["user_id"]

            await telegram_adapter.answer_callback_query(cq["callback_query_id"])

            if callback_data.startswith("cr_property:"):
                property_id_str = callback_data.split(":", 1)[1]
                property_id = UUID(property_id_str)
                staff_id = await _resolve_staff_id(db, user_id)
                await cr_service.start_session(chat_id, property_id, staff_id)
                return {"status": "accepted"}

        except Exception:
            logger.exception("Error handling callback query")
        return {"status": "accepted"}

    # -- 3. Handle message updates ---------------------------------------------
    if "message" not in payload:
        logger.debug("Ignoring non-message update %s", update_id)
        return {"status": "ignored"}

    message = payload["message"]
    chat = message.get("chat", {})
    sender = message.get("from", {})
    chat_id = chat.get("id", 0)
    user_id = sender.get("id", 0)
    text = message.get("text", "")

    # -- 3a. /reporte command → show property selection keyboard ---------------
    if text.startswith("/reporte"):
        try:
            # Check for existing active session
            active = await cr_service.get_active_session(chat_id)
            if active:
                await telegram_adapter.send_message(
                    chat_id,
                    "Ya tienes una sesión activa. Envía /listo para finalizarla o continúa enviando audios y fotos.",
                )
                return {"status": "accepted"}

            # Fetch available properties
            stmt = select(PropertyModel).where(PropertyModel.is_active.is_(True)).order_by(PropertyModel.name)
            result = await db.execute(stmt)
            properties = result.scalars().all()

            if not properties:
                await telegram_adapter.send_message(chat_id, "No hay propiedades disponibles.")
                return {"status": "accepted"}

            # Build inline keyboard: one button per property
            buttons = [
                [{"text": prop.name, "callback_data": f"cr_property:{prop.id}"}]
                for prop in properties
            ]
            await telegram_adapter.send_inline_keyboard(
                chat_id,
                "Selecciona la propiedad para el reporte de condición:",
                buttons,
            )
        except Exception:
            logger.exception("Error handling /reporte command")
        return {"status": "accepted"}

    # -- 3b. /listo command → finalize active session --------------------------
    if text.startswith("/listo"):
        try:
            active = await cr_service.get_active_session(chat_id)
            if active:
                await cr_service.finalize(active.id)
            else:
                await telegram_adapter.send_message(
                    chat_id,
                    "No hay sesión activa. Usa /reporte para iniciar una.",
                )
        except Exception:
            logger.exception("Error handling /listo command")
        return {"status": "accepted"}

    # -- 3c. Media during active session → collect into session ----------------
    active_session = await cr_service.get_active_session(chat_id)
    if active_session:
        try:
            if "voice" in message:
                file_id = message["voice"]["file_id"]
                audio_bytes = await telegram_adapter.download_media(file_id)
                await cr_service.add_voice(active_session.id, audio_bytes)
                return {"status": "accepted"}

            if "photo" in message:
                # Telegram sends multiple sizes; use the largest
                photo = message["photo"][-1]
                file_id = photo["file_id"]
                photo_bytes = await telegram_adapter.download_media(file_id)
                await cr_service.add_photo(active_session.id, photo_bytes, file_id)
                return {"status": "accepted"}

            # Text during active session: ignore or pass through
            if text and not text.startswith("/"):
                await telegram_adapter.send_message(
                    chat_id,
                    "Sesión activa: envía audios o fotos. Cuando termines, envía /listo.",
                )
                return {"status": "accepted"}
        except Exception:
            logger.exception("Error processing media for active session")
            return {"status": "accepted"}

    # -- 4. Normal message processing (existing pipeline) ----------------------
    parsed = await telegram_adapter.parse_webhook(payload)

    from sqlalchemy.exc import IntegrityError

    raw_model = RawMessageModel(
        id=parsed.id,
        telegram_chat_id=parsed.telegram_chat_id,
        telegram_message_id=parsed.telegram_message_id,
        telegram_user_id=parsed.telegram_user_id,
        message_type=parsed.message_type.value.lower(),
        content_text=parsed.content_text,
        file_references=parsed.file_references,
        raw_payload=parsed.raw_payload,
        processing_status=parsed.processing_status.value.lower(),
    )

    try:
        db.add(raw_model)
        await db.flush()
    except IntegrityError:
        await db.rollback()
        logger.info(
            "Duplicate message: chat_id=%d message_id=%d",
            parsed.telegram_chat_id,
            parsed.telegram_message_id,
        )
        return {"status": "duplicate"}

    # -- 5. Process message inline (not in background) -------------------------
    try:
        from app.infrastructure.db.repositories.event_repository import EventRepository
        from app.infrastructure.db.repositories.inventory_repository import InventoryRepository
        from app.infrastructure.db.repositories.property_repository import PropertyRepository
        from app.infrastructure.db.repositories.raw_message_repository import RawMessageRepository
        from app.infrastructure.llm.openai_client import OpenAIClient
        from app.services.clarification_service import ClarificationService
        from app.services.entity_resolver import EntityResolver
        from app.services.ingest_service import IngestService
        from app.services.interpretation_service import InterpretationService

        from app.infrastructure.db.repositories.incident_repository import IncidentRepository

        openai_client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
        property_repo = PropertyRepository(db)
        inventory_repo = InventoryRepository(db)
        incident_repo = IncidentRepository(db)
        entity_resolver = EntityResolver(property_repo, inventory_repo, incident_repo)
        interpretation_service = InterpretationService(openai_client, entity_resolver)
        event_store = EventRepository(db)
        clarification_service = ClarificationService(telegram_adapter)
        raw_message_repo = RawMessageRepository(db)

        ingest_service = IngestService(
            raw_message_repo=raw_message_repo,
            interpretation_service=interpretation_service,
            event_store=event_store,
            event_engine=event_engine,
            channel_adapter=telegram_adapter,
            clarification_service=clarification_service,
            settings=settings,
        )

        await ingest_service.process_message(parsed.id)

        await telegram_adapter.send_message(
            chat_id,
            "Mensaje recibido y procesado correctamente.",
        )

        logger.info(
            "Processed Telegram update %s (message_id=%s)",
            update_id,
            parsed.id,
        )
    except Exception:
        logger.exception("Failed to process message %s inline", parsed.id)
        await telegram_adapter.send_message(
            chat_id,
            "Mensaje recibido. Hubo un error al procesarlo, se reintentará.",
        )

    return {"status": "accepted"}
