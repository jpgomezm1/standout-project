"""FastAPI application entry-point."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Async lifespan: runs on startup / shutdown."""
    settings = get_settings()

    # -- Startup --------------------------------------------------------- #
    logger.info("Starting StandOut backend (env=%s)", settings.APP_ENV)

    # 1. Initialise the async database engine & session factory
    from app.infrastructure.db.session import init_engine, dispose_engine

    engine, session_factory = init_engine(settings.DATABASE_URL)
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    # 2. Initialise the domain event engine (singleton)
    from app.services.event_engine import EventEngine

    event_engine = EventEngine()
    app.state.event_engine = event_engine

    # 3. Register event handlers (lightweight — no DB needed yet)
    from app.services.handlers import register_all_handlers

    register_all_handlers(event_engine, session_factory=session_factory)

    # 4. Start the retry-worker background task (placeholder — no-op for now)
    async def _retry_loop() -> None:
        while True:
            await asyncio.sleep(60)

    retry_task = asyncio.create_task(_retry_loop(), name="retry-worker")
    app.state.retry_task = retry_task

    logger.info("Startup complete")

    yield

    # -- Shutdown -------------------------------------------------------- #
    logger.info("Shutting down StandOut backend")

    retry_task.cancel()
    try:
        await retry_task
    except asyncio.CancelledError:
        pass

    await dispose_engine(engine)
    logger.info("Shutdown complete")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title="StandOut API",
        description="Operational Event Orchestrator for short-term rental operations",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    # -- Middleware ------------------------------------------------------- #
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_BASE_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -- Routers --------------------------------------------------------- #
    from app.api.v1.router import router as v1_router

    application.include_router(v1_router, prefix="/api/v1")

    # -- Health ---------------------------------------------------------- #
    @application.get("/", tags=["health"])
    async def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "standout-backend",
            "env": settings.APP_ENV,
        }

    return application


app = create_app()
