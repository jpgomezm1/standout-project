"""Request/response Pydantic models for property endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PropertyCreate(BaseModel):
    """Payload for creating a new property."""

    name: str = Field(..., min_length=1, max_length=255, description="Canonical property name")
    address: str = Field(default="", max_length=1000, description="Physical address")
    timezone: str = Field(default="America/Bogota", max_length=50, description="IANA timezone")
    aliases: list[str] = Field(default_factory=list, description="Informal name aliases for NLP matching")
    housekeepers_needed: int = Field(default=1, ge=0, description="Number of housekeepers needed per turn")
    metadata: dict = Field(default_factory=dict, description="Arbitrary key-value metadata")


class PropertyUpdate(BaseModel):
    """Payload for partially updating a property."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, max_length=1000)
    timezone: str | None = Field(default=None, max_length=50)
    aliases: list[str] | None = None
    housekeepers_needed: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    metadata: dict | None = None


class PropertyResponse(BaseModel):
    """Full property representation returned by the API."""

    id: UUID
    name: str
    address: str
    timezone: str
    aliases: list[str]
    housekeepers_needed: int = 1
    is_active: bool
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PropertyListResponse(BaseModel):
    """Lightweight property representation for listing views."""

    id: UUID
    name: str
    address: str
    timezone: str
    is_active: bool
    housekeepers_needed: int = 1
    property_manager: str | None = None

    model_config = {"from_attributes": True}


class PropertySummaryResponse(PropertyResponse):
    """Property with aggregated operational counts for detail view."""

    active_incidents: int = 0
    items_in_laundry: int = 0
    low_stock_alerts: int = 0
    upcoming_reservations: int = 0
    current_guest: str | None = None
    property_manager: str | None = None
