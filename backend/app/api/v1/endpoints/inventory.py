"""Inventory management endpoints."""

from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.api.v1.schemas.event_schemas import EventResponse
from app.api.v1.schemas.inventory_schemas import InventoryItemResponse
from app.dependencies import DbSessionDep
from app.infrastructure.db.repositories.event_repository import EventRepository
from app.infrastructure.db.repositories.inventory_repository import InventoryRepository
from app.infrastructure.db.repositories.property_repository import PropertyRepository

logger = logging.getLogger(__name__)

router = APIRouter(tags=["inventory"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_inventory_response(item, current_quantity: int) -> InventoryItemResponse:
    """Map an inventory item domain entity + derived quantity to a response."""
    return InventoryItemResponse(
        id=item.id,
        property_id=item.property_id,
        item_name=item.item_name,
        category=item.category.value,
        expected_quantity=item.expected_quantity,
        current_quantity=current_quantity,
        low_stock_threshold=item.low_stock_threshold,
        is_low_stock=current_quantity < item.low_stock_threshold,
    )


# ---------------------------------------------------------------------------
# Property-scoped inventory endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/properties/{property_id}/inventory",
    response_model=list[InventoryItemResponse],
)
async def get_property_inventory(
    property_id: UUID,
    db: DbSessionDep,
) -> list[InventoryItemResponse]:
    """Return all inventory items for a property with derived current quantities.

    Current quantities are computed by replaying the event log against
    each item's expected (baseline) quantity.
    """
    # Verify property exists
    prop_repo = PropertyRepository(db)
    prop = await prop_repo.get_by_id(property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    repo = InventoryRepository(db)
    quantity_rows = await repo.get_current_quantities(property_id)

    return [
        _build_inventory_response(row["item"], row["current_quantity"])
        for row in quantity_rows
    ]


# ---------------------------------------------------------------------------
# Item-level endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/inventory/{item_id}",
    response_model=InventoryItemResponse,
)
async def get_inventory_item(
    item_id: UUID,
    db: DbSessionDep,
) -> InventoryItemResponse:
    """Return a single inventory item by its ID with derived current quantity.

    The current quantity is computed by replaying events for the item's
    property and filtering to the specific item.
    """
    repo = InventoryRepository(db)
    item = await repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Derive current quantity for this specific item
    quantity_rows = await repo.get_current_quantities(item.property_id)
    current_qty = item.expected_quantity  # default
    for row in quantity_rows:
        if row["item"].id == item_id:
            current_qty = row["current_quantity"]
            break

    return _build_inventory_response(item, current_qty)


@router.get(
    "/inventory/{item_id}/history",
    response_model=list[EventResponse],
)
async def get_inventory_item_history(
    item_id: UUID,
    db: DbSessionDep,
    since: datetime | None = Query(
        default=None, description="Only return events after this timestamp"
    ),
) -> list[EventResponse]:
    """Return the event history for a specific inventory item.

    Events are retrieved by matching ``payload.item_id`` using a JSONB
    containment query.  Results are in reverse chronological order.
    """
    # Verify the item exists
    inv_repo = InventoryRepository(db)
    item = await inv_repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    event_repo = EventRepository(db)
    events = await event_repo.get_by_item(item_id=item_id, since=since)

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
