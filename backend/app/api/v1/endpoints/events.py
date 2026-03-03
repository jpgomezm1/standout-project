"""Event store query endpoints."""

from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.api.v1.schemas.event_schemas import EventResponse
from app.dependencies import DbSessionDep
from app.domain.entities.event import EventType
from app.infrastructure.db.repositories.event_repository import EventRepository
from app.infrastructure.db.repositories.property_repository import PropertyRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    db: DbSessionDep,
    property_id: UUID | None = Query(default=None, description="Filter by property"),
    event_type: str | None = Query(default=None, description="Filter by event type"),
    since: datetime | None = Query(default=None, description="Events created after this timestamp"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum events to return"),
) -> list[EventResponse]:
    """Return operational events, optionally filtered by property, type, and date.

    Events are returned in reverse chronological order.  A ``property_id``
    is required to scope the query; omitting it returns an empty list to
    prevent unbounded table scans.
    """
    if property_id is None:
        return []

    # Validate event_type if provided
    parsed_event_type: EventType | None = None
    if event_type is not None:
        try:
            parsed_event_type = EventType(event_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event_type '{event_type}'. "
                f"Valid types: {[e.value for e in EventType]}",
            )

    repo = EventRepository(db)
    events = await repo.get_by_property(
        property_id=property_id,
        event_type=parsed_event_type,
        since=since,
        limit=limit,
    )

    return [
        EventResponse(
            id=e.id,
            property_id=e.property_id,
            event_type=e.event_type.value,
            payload=e.payload,
            source_message_id=e.source_message_id,
            confidence_score=e.confidence_score,
            actor_id=e.actor_id,
            idempotency_key=e.idempotency_key,
            created_at=e.created_at,
        )
        for e in events
    ]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: DbSessionDep,
) -> EventResponse:
    """Return a single event by its ID.

    Queries the events table directly by primary key.
    """
    from app.infrastructure.db.models.event import EventModel

    model = await db.get(EventModel, event_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Event not found")

    repo = EventRepository(db)
    event = repo._to_domain(model)

    return EventResponse(
        id=event.id,
        property_id=event.property_id,
        event_type=event.event_type.value,
        payload=event.payload,
        source_message_id=event.source_message_id,
        confidence_score=event.confidence_score,
        actor_id=event.actor_id,
        idempotency_key=event.idempotency_key,
        created_at=event.created_at,
    )
