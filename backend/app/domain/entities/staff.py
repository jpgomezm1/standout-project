from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class StaffRole(str, Enum):
    """Role classification for staff members."""

    HOUSEKEEPER = "HOUSEKEEPER"
    PROPERTY_MANAGER = "PROPERTY_MANAGER"


class StaffMember(BaseModel):
    """A member of the operational team (housekeeper or property manager)."""

    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    role: StaffRole
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
