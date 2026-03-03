"""Dashboard aggregation endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.v1.schemas.dashboard_schemas import DashboardSummary
from app.api.v1.schemas.event_schemas import EventResponse
from app.dependencies import DbSessionDep
from app.domain.entities.event import EventType
from app.domain.entities.incident import IncidentPriority, IncidentStatus
from app.domain.entities.laundry import LaundryStatus
from app.infrastructure.db.repositories.event_repository import EventRepository
from app.infrastructure.db.repositories.incident_repository import IncidentRepository
from app.infrastructure.db.repositories.inventory_repository import InventoryRepository
from app.infrastructure.db.repositories.laundry_repository import LaundryRepository
from app.infrastructure.db.repositories.property_repository import PropertyRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(
    db: DbSessionDep,
    property_id: UUID | None = Query(
        default=None,
        description="Scope summary to a single property (omit for all properties)",
    ),
) -> DashboardSummary:
    """Return an aggregated operational summary.

    When ``property_id`` is provided, the summary is scoped to that
    single property.  Otherwise it aggregates across all active
    properties.
    """
    prop_repo = PropertyRepository(db)
    incident_repo = IncidentRepository(db)
    laundry_repo = LaundryRepository(db)
    inventory_repo = InventoryRepository(db)

    # -- Total properties -------------------------------------------------- #
    if property_id is not None:
        prop = await prop_repo.get_by_id(property_id)
        properties = [prop] if prop else []
    else:
        properties = await prop_repo.get_all()

    total_properties = len(properties)

    # -- Incidents --------------------------------------------------------- #
    # Fetch active incidents (all non-resolved statuses)
    active_incidents_count = 0
    critical_incidents_count = 0

    for status in (IncidentStatus.OPEN, IncidentStatus.ACKNOWLEDGED, IncidentStatus.IN_PROGRESS):
        incidents = await incident_repo.get_all(
            property_id=property_id,
            status=status,
        )
        active_incidents_count += len(incidents)

        # Count critical among these
        critical_incidents_count += sum(
            1 for i in incidents if i.priority == IncidentPriority.CRITICAL
        )

    # -- Items in laundry -------------------------------------------------- #
    items_in_laundry = 0
    for prop in properties:
        for laundry_status in (LaundryStatus.SENT, LaundryStatus.IN_PROGRESS):
            flows = await laundry_repo.get_by_property(
                property_id=prop.id,
                status=laundry_status,
            )
            items_in_laundry += sum(f.total_pieces for f in flows)

    # -- Low-stock items --------------------------------------------------- #
    low_stock_items = 0
    for prop in properties:
        quantity_rows = await inventory_repo.get_current_quantities(
            property_id=prop.id
        )
        low_stock_items += sum(
            1
            for row in quantity_rows
            if row["current_quantity"] < row["item"].low_stock_threshold
        )

    # -- Recent events ----------------------------------------------------- #
    recent_events: list[EventResponse] = []
    for prop in properties:
        events = await EventRepository(db).get_by_property(
            property_id=prop.id,
            limit=10,
        )
        for e in events:
            recent_events.append(
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
            )

    # Sort by created_at descending and limit to 20 most recent
    recent_events.sort(key=lambda e: e.created_at, reverse=True)
    recent_events = recent_events[:20]

    return DashboardSummary(
        total_properties=total_properties,
        active_incidents=active_incidents_count,
        critical_incidents=critical_incidents_count,
        items_in_laundry=items_in_laundry,
        low_stock_items=low_stock_items,
        recent_events=recent_events,
    )
