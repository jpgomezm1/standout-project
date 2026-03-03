"""Request/response Pydantic models for incident endpoints."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class IncidentStatusEnum(str, Enum):
    """Allowed status values for incident status transitions."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class IncidentPriorityEnum(str, Enum):
    """Allowed priority values for incident filtering."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentResponse(BaseModel):
    """Full incident representation returned by the API."""

    id: UUID
    property_id: UUID
    incident_type: str
    title: str
    description: str
    status: str
    priority: str
    reported_by: UUID | None = None
    assigned_to: UUID | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None

    model_config = {"from_attributes": True}


class IncidentStatusUpdate(BaseModel):
    """Payload for updating an incident's status."""

    status: IncidentStatusEnum = Field(
        ..., description="Target status: open, acknowledged, in_progress, or resolved"
    )
