"""Request/response Pydantic models for staff endpoints."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class StaffRoleEnum(str, Enum):
    HOUSEKEEPER = "housekeeper"
    PROPERTY_MANAGER = "property_manager"


class StaffResponse(BaseModel):
    """Full staff member representation returned by the API."""

    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None
    role: str
    is_active: bool
    property_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StaffCreate(BaseModel):
    """Payload for creating a new staff member."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    role: StaffRoleEnum
    property_id: UUID | None = None


class HousekeepingAssignmentResponse(BaseModel):
    """Housekeeping assignment representation."""

    id: UUID
    reservation_id: UUID
    staff_id: UUID
    staff_name: str
    property_name: str | None = None
    guest_name: str | None = None
    scheduled_date: date
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HousekeepingAssignmentCreate(BaseModel):
    """Payload for manual housekeeping assignment."""

    reservation_id: UUID
    staff_id: UUID
    scheduled_date: date
    notes: str | None = None
