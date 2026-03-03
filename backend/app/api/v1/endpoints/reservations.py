"""Reservation management endpoints."""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query

from app.api.v1.schemas.reservation_schemas import (
    BookingChannelEnum,
    ReservationCreate,
    ReservationResponse,
    ReservationStatusEnum,
)
from app.dependencies import DbSessionDep
from app.domain.entities.reservation import (
    BookingChannel,
    Reservation,
    ReservationStatus,
)
from app.infrastructure.db.repositories.reservation_repository import (
    ReservationRepository,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["reservations"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reservation_to_response(r: Reservation) -> ReservationResponse:
    """Map a domain Reservation entity to an API response model."""
    return ReservationResponse(
        id=r.id,
        property_id=r.property_id,
        guest_name=r.guest_name,
        check_in=r.check_in,
        check_out=r.check_out,
        status=r.status.value.lower(),
        num_guests=r.num_guests,
        channel=r.channel.value.lower(),
        internal_notes=r.internal_notes,
        amount=r.amount,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/properties/{property_id}/reservations",
    response_model=list[ReservationResponse],
)
async def list_reservations(
    property_id: UUID,
    db: DbSessionDep,
    status: ReservationStatusEnum | None = Query(default=None, description="Filter by status"),
    from_date: date | None = Query(default=None, description="Start of date range"),
    to_date: date | None = Query(default=None, description="End of date range"),
) -> list[ReservationResponse]:
    """Return reservations for a property, optionally filtered by status and date range."""
    repo = ReservationRepository(db)

    domain_status: ReservationStatus | None = None
    if status is not None:
        domain_status = ReservationStatus(status.value.upper())

    reservations = await repo.get_by_property(
        property_id=property_id,
        status=domain_status,
        from_date=from_date,
        to_date=to_date,
    )

    return [_reservation_to_response(r) for r in reservations]


@router.get(
    "/reservations/{reservation_id}",
    response_model=ReservationResponse,
)
async def get_reservation(
    reservation_id: UUID,
    db: DbSessionDep,
) -> ReservationResponse:
    """Return a single reservation by its ID."""
    repo = ReservationRepository(db)
    reservation = await repo.get_by_id(reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return _reservation_to_response(reservation)


@router.post(
    "/properties/{property_id}/reservations",
    response_model=ReservationResponse,
    status_code=201,
)
async def create_reservation(
    property_id: UUID,
    data: ReservationCreate,
    db: DbSessionDep,
) -> ReservationResponse:
    """Create a new reservation for a property."""
    repo = ReservationRepository(db)

    now = datetime.now(timezone.utc)
    new_reservation = Reservation(
        id=uuid4(),
        property_id=property_id,
        guest_name=data.guest_name,
        check_in=data.check_in,
        check_out=data.check_out,
        status=ReservationStatus(data.status.value.upper()),
        num_guests=data.num_guests,
        channel=BookingChannel(data.channel.value.upper()),
        internal_notes=data.internal_notes,
        amount=data.amount,
        created_at=now,
        updated_at=now,
    )

    created = await repo.create(new_reservation)
    return _reservation_to_response(created)
