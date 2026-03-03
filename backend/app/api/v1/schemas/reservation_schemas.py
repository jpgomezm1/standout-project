"""Request/response Pydantic models for reservation endpoints."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ReservationStatusEnum(str, Enum):
    confirmed = "confirmed"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class BookingChannelEnum(str, Enum):
    airbnb = "airbnb"
    booking = "booking"
    direct = "direct"
    other = "other"


class ReservationResponse(BaseModel):
    """Full reservation representation returned by the API."""

    id: UUID
    property_id: UUID
    guest_name: str
    check_in: date
    check_out: date
    status: str
    num_guests: int
    channel: str
    internal_notes: str
    amount: Decimal | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReservationCreate(BaseModel):
    """Payload for creating a new reservation."""

    guest_name: str = Field(..., min_length=1, max_length=255)
    check_in: date
    check_out: date
    status: ReservationStatusEnum = Field(default=ReservationStatusEnum.confirmed)
    num_guests: int = Field(..., ge=1)
    channel: BookingChannelEnum
    internal_notes: str = Field(default="")
    amount: Decimal | None = Field(default=None)
