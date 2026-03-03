from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ReservationStatus(str, Enum):
    """Lifecycle status of a reservation."""

    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class BookingChannel(str, Enum):
    """Source channel for the booking."""

    AIRBNB = "AIRBNB"
    BOOKING = "BOOKING"
    DIRECT = "DIRECT"
    OTHER = "OTHER"


class Reservation(BaseModel):
    """A guest reservation at a property."""

    id: UUID
    property_id: UUID
    guest_name: str
    check_in: date
    check_out: date
    status: ReservationStatus
    num_guests: int
    channel: BookingChannel
    internal_notes: str = ""
    amount: Decimal | None = None
    created_at: datetime
    updated_at: datetime
