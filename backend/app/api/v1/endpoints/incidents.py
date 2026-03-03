"""Incident management endpoints."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.api.v1.schemas.incident_schemas import (
    IncidentPriorityEnum,
    IncidentResponse,
    IncidentStatusEnum,
    IncidentStatusUpdate,
)
from app.dependencies import DbSessionDep
from app.domain.entities.incident import IncidentPriority, IncidentStatus
from app.infrastructure.db.repositories.incident_repository import IncidentRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/incidents", tags=["incidents"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _incident_to_response(incident) -> IncidentResponse:
    """Map a domain Incident entity to an API response model."""
    return IncidentResponse(
        id=incident.id,
        property_id=incident.property_id,
        incident_type=incident.incident_type,
        title=incident.title,
        description=incident.description,
        status=incident.status.value.lower(),
        priority=incident.priority.value.lower(),
        reported_by=incident.reported_by,
        assigned_to=incident.assigned_to,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        resolved_at=incident.resolved_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[IncidentResponse])
async def list_incidents(
    db: DbSessionDep,
    property_id: UUID | None = Query(default=None, description="Filter by property"),
    status: IncidentStatusEnum | None = Query(default=None, description="Filter by status"),
    priority: IncidentPriorityEnum | None = Query(default=None, description="Filter by priority"),
) -> list[IncidentResponse]:
    """Return incidents, optionally filtered by property, status, or priority.

    Results are ordered by creation date descending (newest first).
    """
    repo = IncidentRepository(db)

    # Map API enum values to domain enum values
    domain_status: IncidentStatus | None = None
    if status is not None:
        domain_status = IncidentStatus(status.value.upper())

    domain_priority: IncidentPriority | None = None
    if priority is not None:
        domain_priority = IncidentPriority(priority.value.upper())

    incidents = await repo.get_all(
        property_id=property_id,
        status=domain_status,
        priority=domain_priority,
    )

    return [_incident_to_response(i) for i in incidents]


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    db: DbSessionDep,
) -> IncidentResponse:
    """Return a single incident by its ID."""
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return _incident_to_response(incident)


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: UUID,
    data: IncidentStatusUpdate,
    db: DbSessionDep,
) -> IncidentResponse:
    """Transition an incident to a new status.

    The valid status progression is:
    ``open`` -> ``acknowledged`` -> ``in_progress`` -> ``resolved``.

    When transitioning to ``resolved``, the ``resolved_at`` timestamp is
    set automatically.
    """
    repo = IncidentRepository(db)

    # Check the incident exists
    existing = await repo.get_by_id(incident_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    domain_status = IncidentStatus(data.status.value.upper())

    # Auto-set resolved_at when transitioning to resolved
    resolved_at: datetime | None = None
    if domain_status == IncidentStatus.RESOLVED:
        resolved_at = datetime.now(timezone.utc)

    updated = await repo.update_status(
        id=incident_id,
        status=domain_status,
        resolved_at=resolved_at,
    )

    if updated is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return _incident_to_response(updated)
