from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class LaundryStatus(str, Enum):
    """Lifecycle status of a laundry flow."""

    SENT = "SENT"
    IN_PROGRESS = "IN_PROGRESS"
    RETURNED = "RETURNED"
    PARTIALLY_RETURNED = "PARTIALLY_RETURNED"
    LOST = "LOST"


class LaundryFlow(BaseModel):
    """Tracks a batch of items sent to and returned from a laundry service.

    ``items`` is a list of dicts describing individual item types and
    quantities (e.g. ``[{"name": "bath_towel", "quantity": 12}]``).
    ``total_pieces`` is the aggregate count across all item entries.
    """

    id: UUID
    property_id: UUID
    status: LaundryStatus
    items: list[dict] = Field(default_factory=list)
    total_pieces: int
    sent_at: datetime
    expected_return_at: datetime | None = None
    returned_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
