"""Laundry flow tracking endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from datetime import datetime, timezone

from app.api.v1.schemas.laundry_schemas import LaundryFlowResponse, LaundryStatusEnum, LaundryStatusUpdate
from app.dependencies import DbSessionDep
from app.domain.entities.laundry import LaundryStatus
from app.infrastructure.db.repositories.laundry_repository import LaundryRepository
from app.infrastructure.db.repositories.property_repository import PropertyRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/properties/{property_id}/laundry", tags=["laundry"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flow_to_response(flow) -> LaundryFlowResponse:
    """Map a domain LaundryFlow entity to an API response model."""
    return LaundryFlowResponse(
        id=flow.id,
        property_id=flow.property_id,
        status=flow.status.value.lower(),
        items=flow.items,
        total_pieces=flow.total_pieces,
        sent_at=flow.sent_at,
        expected_return_at=flow.expected_return_at,
        returned_at=flow.returned_at,
        created_at=flow.created_at,
        updated_at=flow.updated_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[LaundryFlowResponse])
async def get_laundry_flows(
    property_id: UUID,
    db: DbSessionDep,
    status: LaundryStatusEnum | None = Query(
        default=None, description="Filter by laundry status"
    ),
) -> list[LaundryFlowResponse]:
    """Return laundry flows for a property, optionally filtered by status.

    Results are ordered by sent date descending (most recent first).
    """
    # Verify property exists
    prop_repo = PropertyRepository(db)
    prop = await prop_repo.get_by_id(property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    domain_status: LaundryStatus | None = None
    if status is not None:
        domain_status = LaundryStatus(status.value.upper())

    repo = LaundryRepository(db)
    flows = await repo.get_by_property(
        property_id=property_id,
        status=domain_status,
    )

    return [_flow_to_response(f) for f in flows]


@router.get("/{flow_id}", response_model=LaundryFlowResponse)
async def get_laundry_flow(
    property_id: UUID,
    flow_id: UUID,
    db: DbSessionDep,
) -> LaundryFlowResponse:
    """Return a single laundry flow by its ID.

    Validates that the flow belongs to the specified property.
    """
    repo = LaundryRepository(db)
    flow = await repo.get_by_id(flow_id)
    if flow is None:
        raise HTTPException(status_code=404, detail="Laundry flow not found")

    if flow.property_id != property_id:
        raise HTTPException(
            status_code=404,
            detail="Laundry flow not found for this property",
        )

    return _flow_to_response(flow)


@router.patch("/{flow_id}", response_model=LaundryFlowResponse)
async def update_laundry_status(
    property_id: UUID,
    flow_id: UUID,
    body: LaundryStatusUpdate,
    db: DbSessionDep,
) -> LaundryFlowResponse:
    """Manually update a laundry flow status (e.g. mark as returned)."""
    repo = LaundryRepository(db)
    flow = await repo.get_by_id(flow_id)
    if flow is None:
        raise HTTPException(status_code=404, detail="Laundry flow not found")
    if flow.property_id != property_id:
        raise HTTPException(status_code=404, detail="Laundry flow not found for this property")

    new_status = LaundryStatus(body.status.value.upper())
    now = datetime.now(timezone.utc)

    update_fields: dict = {"status": new_status, "updated_at": now}
    if new_status == LaundryStatus.RETURNED:
        update_fields["returned_at"] = now
    elif new_status == LaundryStatus.SENT:
        update_fields["returned_at"] = None

    updated_flow = flow.model_copy(update=update_fields)
    stored = await repo.update(updated_flow)
    await db.commit()

    return _flow_to_response(stored)
