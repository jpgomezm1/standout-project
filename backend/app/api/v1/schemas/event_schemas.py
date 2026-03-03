"""Request/response Pydantic models for event endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EventResponse(BaseModel):
    """Immutable operational event returned by the API."""

    id: UUID
    property_id: UUID
    event_type: str
    payload: dict
    source_message_id: UUID | None = None
    confidence_score: float
    actor_id: UUID | None = None
    idempotency_key: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EventListParams(BaseModel):
    """Query parameters for filtering events (used as documentation reference)."""

    property_id: UUID | None = None
    event_type: str | None = None
    since: datetime | None = None
    limit: int = Field(default=50, ge=1, le=200)
