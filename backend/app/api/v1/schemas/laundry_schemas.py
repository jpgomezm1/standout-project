"""Request/response Pydantic models for laundry endpoints."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class LaundryStatusEnum(str, Enum):
    """Allowed status values for laundry flow filtering."""

    SENT = "sent"
    IN_PROGRESS = "in_progress"
    RETURNED = "returned"
    PARTIALLY_RETURNED = "partially_returned"
    LOST = "lost"


class LaundryStatusUpdate(BaseModel):
    """Request body for updating a laundry flow status."""

    status: LaundryStatusEnum


class LaundryFlowResponse(BaseModel):
    """Laundry flow batch representation returned by the API."""

    id: UUID
    property_id: UUID
    status: str
    items: list[dict]
    total_pieces: int
    sent_at: datetime
    expected_return_at: datetime | None = None
    returned_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
