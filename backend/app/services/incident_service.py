"""Incident service — query and lifecycle operations for incidents.

Provides a thin application-layer facade over the incident repository,
adding business-rule enforcement (e.g. setting ``resolved_at`` on
resolution) and structured logging.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from app.domain.entities.incident import Incident, IncidentPriority, IncidentStatus
from app.domain.interfaces.repositories import IIncidentRepository

logger = logging.getLogger(__name__)


class IncidentService:
    """Application service for querying and updating incidents."""

    def __init__(self, incident_repo: IIncidentRepository) -> None:
        self._incident_repo = incident_repo

    # -- Queries ------------------------------------------------------------- #

    async def get_incidents(
        self,
        property_id: UUID | None = None,
        status: IncidentStatus | None = None,
        priority: IncidentPriority | None = None,
    ) -> list[Incident]:
        """Return incidents filtered by the given criteria.

        All parameters are optional; when omitted, no filter is applied for
        that dimension.
        """
        incidents = await self._incident_repo.get_all(
            property_id=property_id,
            status=status,
            priority=priority,
        )
        logger.debug(
            "Queried incidents (property_id=%s, status=%s, priority=%s) -> %d result(s)",
            property_id,
            status,
            priority,
            len(incidents),
        )
        return incidents

    async def get_incident_by_id(self, incident_id: UUID) -> Incident | None:
        """Return a single incident by its primary key, or ``None``."""
        return await self._incident_repo.get_by_id(incident_id)

    # -- Commands ------------------------------------------------------------ #

    async def update_status(
        self,
        incident_id: UUID,
        new_status: IncidentStatus,
    ) -> Incident | None:
        """Transition an incident to *new_status*.

        Automatically sets ``resolved_at`` when transitioning to RESOLVED.
        Returns the updated ``Incident``, or ``None`` if the incident was
        not found.
        """
        resolved_at: datetime | None = None
        if new_status == IncidentStatus.RESOLVED:
            resolved_at = datetime.now(timezone.utc)

        updated = await self._incident_repo.update_status(
            incident_id,
            new_status,
            resolved_at=resolved_at,
        )

        if updated is None:
            logger.warning(
                "Attempted to update incident %s to '%s' but it was not found",
                incident_id,
                new_status.value,
            )
            return None

        logger.info(
            "Incident %s transitioned to '%s'%s",
            incident_id,
            new_status.value,
            f" (resolved_at={resolved_at.isoformat()})" if resolved_at else "",
        )
        return updated
