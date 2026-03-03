"""PostgreSQL-backed implementation of :class:`IEventStore`."""

from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import cast, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.event import EventType, OperationalEvent
from app.domain.interfaces.event_store import IEventStore
from app.infrastructure.db.models.event import EventModel


class EventRepository(IEventStore):
    """Append-only event store backed by the ``events`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Mapping helpers -----------------------------------------------------

    @staticmethod
    def _to_domain(model: EventModel) -> OperationalEvent:
        return OperationalEvent(
            id=model.id,
            property_id=model.property_id,
            event_type=EventType(model.event_type),
            payload=model.payload,
            source_message_id=model.source_message_id,
            confidence_score=float(model.confidence_score) if model.confidence_score is not None else 0.0,
            actor_id=model.actor_id,
            idempotency_key=model.idempotency_key,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(event: OperationalEvent) -> EventModel:
        return EventModel(
            id=event.id,
            property_id=event.property_id,
            event_type=event.event_type.value,
            payload=event.payload,
            source_message_id=event.source_message_id,
            confidence_score=event.confidence_score,
            actor_id=event.actor_id,
            idempotency_key=event.idempotency_key,
        )

    # -- Interface implementation --------------------------------------------

    async def append(self, event: OperationalEvent) -> OperationalEvent:
        """Persist a new event and return the stored record (including ``sequence_num``)."""
        model = self._to_model(event)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_property(
        self,
        property_id: UUID,
        event_type: EventType | None = None,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[OperationalEvent]:
        stmt = (
            select(EventModel)
            .where(EventModel.property_id == property_id)
            .order_by(EventModel.created_at.desc())
            .limit(limit)
        )
        if event_type is not None:
            stmt = stmt.where(EventModel.event_type == event_type.value)
        if since is not None:
            stmt = stmt.where(EventModel.created_at >= since)

        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_item(
        self,
        item_id: UUID,
        since: datetime | None = None,
    ) -> list[OperationalEvent]:
        """Retrieve events whose ``payload`` references *item_id*.

        Uses the PostgreSQL ``@>`` JSONB containment operator to match events
        where ``payload->>'item_id'`` equals the given UUID string.
        """
        containment_value = cast(
            json.dumps({"item_id": str(item_id)}), JSONB
        )
        stmt = (
            select(EventModel)
            .where(EventModel.payload.op("@>")(containment_value))
            .order_by(EventModel.created_at.desc())
        )
        if since is not None:
            stmt = stmt.where(EventModel.created_at >= since)

        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]
