from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class AssignmentStatus(str, Enum):
    """Status of a housekeeping assignment."""

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HousekeepingAssignment(BaseModel):
    """Assignment of a housekeeper to a reservation on a specific date."""

    id: UUID
    reservation_id: UUID
    staff_id: UUID
    scheduled_date: date
    notes: str | None = None
    status: AssignmentStatus = AssignmentStatus.SCHEDULED
    created_at: datetime
    updated_at: datetime
