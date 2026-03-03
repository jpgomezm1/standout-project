"""PostgreSQL-backed implementation of :class:`IIncidentRepository`."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.incident import (
    Incident,
    IncidentPriority,
    IncidentStatus,
)
from app.domain.interfaces.repositories import IIncidentRepository
from app.infrastructure.db.models.incident import IncidentModel


class IncidentRepository(IIncidentRepository):
    """Async SQLAlchemy adapter for incident persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Mapping helpers -----------------------------------------------------

    @staticmethod
    def _to_domain(model: IncidentModel) -> Incident:
        return Incident(
            id=model.id,
            property_id=model.property_id,
            incident_type=model.incident_type or "",
            title=model.title,
            description=model.description or "",
            status=IncidentStatus(model.status.upper()),
            priority=IncidentPriority(model.priority.upper()),
            reported_by=model.reported_by,
            assigned_to=model.assigned_to,
            created_at=model.created_at,
            updated_at=model.updated_at,
            resolved_at=model.resolved_at,
        )

    @staticmethod
    def _to_model(entity: Incident) -> IncidentModel:
        return IncidentModel(
            id=entity.id,
            property_id=entity.property_id,
            incident_type=entity.incident_type,
            title=entity.title,
            description=entity.description,
            status=entity.status.value.lower(),
            priority=entity.priority.value.lower(),
            reported_by=entity.reported_by,
            assigned_to=entity.assigned_to,
            resolved_at=entity.resolved_at,
        )

    # -- Interface implementation --------------------------------------------

    async def get_all(
        self,
        property_id: UUID | None = None,
        status: IncidentStatus | None = None,
        priority: IncidentPriority | None = None,
    ) -> list[Incident]:
        stmt = select(IncidentModel).order_by(IncidentModel.created_at.desc())

        if property_id is not None:
            stmt = stmt.where(IncidentModel.property_id == property_id)
        if status is not None:
            stmt = stmt.where(IncidentModel.status == status.value.lower())
        if priority is not None:
            stmt = stmt.where(IncidentModel.priority == priority.value.lower())

        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_id(self, id: UUID) -> Incident | None:
        model = await self._session.get(IncidentModel, id)
        return self._to_domain(model) if model else None

    async def create(self, incident: Incident) -> Incident:
        model = self._to_model(incident)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def update_status(
        self,
        id: UUID,
        status: IncidentStatus,
        resolved_at: datetime | None = None,
    ) -> Incident | None:
        model = await self._session.get(IncidentModel, id)
        if model is None:
            return None

        model.status = status.value.lower()
        if resolved_at is not None:
            model.resolved_at = resolved_at

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)
