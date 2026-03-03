from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class IncidentStatus(str, Enum):
    """Lifecycle status of an incident."""

    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class IncidentPriority(str, Enum):
    """Severity / urgency classification for incidents."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Incident(BaseModel):
    """An operational incident reported against a property.

    Incidents progress through a simple state machine:
    OPEN -> ACKNOWLEDGED -> IN_PROGRESS -> RESOLVED.
    """

    id: UUID
    property_id: UUID
    incident_type: str
    title: str
    description: str
    status: IncidentStatus
    priority: IncidentPriority
    reported_by: UUID | None = None
    assigned_to: UUID | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
