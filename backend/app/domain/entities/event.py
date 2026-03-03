from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Enumeration of all operational event types tracked by the system."""

    ITEM_BROKEN = "ITEM_BROKEN"
    ITEM_MISSING = "ITEM_MISSING"
    ITEM_SENT_TO_LAUNDRY = "ITEM_SENT_TO_LAUNDRY"
    ITEM_RETURNED_FROM_LAUNDRY = "ITEM_RETURNED_FROM_LAUNDRY"
    MAINTENANCE_ISSUE = "MAINTENANCE_ISSUE"
    LOW_STOCK_ALERT = "LOW_STOCK_ALERT"
    INCIDENT_ACKNOWLEDGED = "INCIDENT_ACKNOWLEDGED"
    INCIDENT_IN_PROGRESS = "INCIDENT_IN_PROGRESS"
    INCIDENT_RESOLVED = "INCIDENT_RESOLVED"
    LAUNDRY_RETURNED = "LAUNDRY_RETURNED"
    LAUNDRY_PARTIALLY_RETURNED = "LAUNDRY_PARTIALLY_RETURNED"
    LAUNDRY_LOST = "LAUNDRY_LOST"


class OperationalEvent(BaseModel, frozen=True):
    """Immutable record of a single operational event within a property.

    Events are the core building block of the system's event-sourced state.
    Each event carries a typed payload and is linked back to the inbound
    message that originated it (when applicable).
    """

    id: UUID
    property_id: UUID
    event_type: EventType
    payload: dict
    source_message_id: UUID | None = None
    confidence_score: float = Field(ge=0, le=1)
    actor_id: UUID | None = None
    idempotency_key: str
    created_at: datetime
