"""Health and readiness check endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.dependencies import DbSessionDep

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe -- always returns 200 if the process is running."""
    return {"status": "ok"}


@router.get("/health/ready")
async def ready(db: DbSessionDep) -> dict[str, str]:
    """Readiness probe -- verifies database connectivity.

    Returns 200 only when the application can successfully execute a
    trivial query against the database.  Load balancers and orchestrators
    should use this endpoint to decide whether to route traffic.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        logger.exception("Readiness check failed: database unreachable")
        raise
