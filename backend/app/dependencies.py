"""FastAPI dependency injection providers."""

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def get_settings_dep() -> Settings:
    """Return the cached application settings singleton."""
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_settings_dep)]


# ---------------------------------------------------------------------------
# Database session
# ---------------------------------------------------------------------------

async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield an async database session per request, with automatic cleanup.

    The session factory is stored on ``app.state`` during the lifespan
    startup phase (see ``app.main``).
    """
    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


# ---------------------------------------------------------------------------
# Event engine
# ---------------------------------------------------------------------------

def get_event_engine(request: Request) -> Any:
    """Return the singleton EventEngine stored on application state."""
    return request.app.state.event_engine


EventEngineDep = Annotated[Any, Depends(get_event_engine)]


# ---------------------------------------------------------------------------
# Application services
# ---------------------------------------------------------------------------

def get_ingest_service(
    session: DbSessionDep,
    settings: SettingsDep,
    event_engine: EventEngineDep,
) -> Any:
    """Build an IngestService with its required collaborators."""
    from app.services.ingest_service import IngestService

    return IngestService(
        session=session,
        settings=settings,
        event_engine=event_engine,
    )


IngestServiceDep = Annotated[Any, Depends(get_ingest_service)]


def get_interpretation_service(
    session: DbSessionDep,
    settings: SettingsDep,
) -> Any:
    """Build an InterpretationService with its required collaborators."""
    from app.services.interpretation_service import InterpretationService

    return InterpretationService(
        session=session,
        settings=settings,
    )


InterpretationServiceDep = Annotated[Any, Depends(get_interpretation_service)]


# ---------------------------------------------------------------------------
# Condition report service
# ---------------------------------------------------------------------------

def get_condition_report_service(
    session: DbSessionDep,
    settings: SettingsDep,
    event_engine: EventEngineDep,
) -> Any:
    """Build a ConditionReportService with its required collaborators."""
    from app.infrastructure.channels.telegram_adapter import TelegramAdapter
    from app.infrastructure.llm.openai_client import OpenAIClient
    from app.services.condition_report_service import ConditionReportService

    openai_client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
    telegram_adapter = TelegramAdapter(
        bot_token=settings.TELEGRAM_BOT_TOKEN,
        webhook_secret=settings.TELEGRAM_WEBHOOK_SECRET,
    )
    return ConditionReportService(
        session=session,
        settings=settings,
        event_engine=event_engine,
        openai_client=openai_client,
        telegram_adapter=telegram_adapter,
    )


ConditionReportServiceDep = Annotated[Any, Depends(get_condition_report_service)]
