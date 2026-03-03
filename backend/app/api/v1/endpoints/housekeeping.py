"""Housekeeping assignment endpoints."""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query

from app.api.v1.schemas.staff_schemas import (
    HousekeepingAssignmentCreate,
    HousekeepingAssignmentResponse,
)
from app.dependencies import DbSessionDep
from app.domain.entities.housekeeping import AssignmentStatus, HousekeepingAssignment
from app.domain.entities.staff import StaffMember
from app.infrastructure.db.repositories.housekeeping_repository import HousekeepingRepository

router = APIRouter(tags=["housekeeping"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assignment_to_response(
    assignment: HousekeepingAssignment,
    staff_name: str,
    *,
    property_name: str | None = None,
    guest_name: str | None = None,
) -> HousekeepingAssignmentResponse:
    return HousekeepingAssignmentResponse(
        id=assignment.id,
        reservation_id=assignment.reservation_id,
        staff_id=assignment.staff_id,
        staff_name=staff_name,
        property_name=property_name,
        guest_name=guest_name,
        scheduled_date=assignment.scheduled_date,
        notes=assignment.notes,
        status=assignment.status.value,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


def _staff_to_dict(s: StaffMember) -> dict:
    return {
        "id": str(s.id),
        "first_name": s.first_name,
        "last_name": s.last_name,
        "email": s.email,
        "phone": s.phone,
        "role": s.role.value if hasattr(s.role, 'value') else s.role,
        "is_active": s.is_active,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/reservations/{reservation_id}/housekeeping",
    response_model=list[HousekeepingAssignmentResponse],
)
async def list_reservation_housekeeping(
    reservation_id: UUID,
    db: DbSessionDep,
) -> list[HousekeepingAssignmentResponse]:
    """Return all housekeeping assignments for a reservation."""
    from app.infrastructure.db.repositories.staff_repository import StaffRepository

    hk_repo = HousekeepingRepository(db)
    staff_repo = StaffRepository(db)

    assignments = await hk_repo.get_by_reservation(reservation_id)
    results = []
    for a in assignments:
        staff = await staff_repo.get_by_id(a.staff_id)
        name = f"{staff.first_name} {staff.last_name}" if staff else "Unknown"
        results.append(_assignment_to_response(a, name))
    return results


@router.post(
    "/housekeeping-assignments",
    response_model=HousekeepingAssignmentResponse,
    status_code=201,
)
async def create_housekeeping_assignment(
    body: HousekeepingAssignmentCreate,
    db: DbSessionDep,
) -> HousekeepingAssignmentResponse:
    """Create a manual housekeeping assignment."""
    from app.infrastructure.db.repositories.staff_repository import StaffRepository

    staff_repo = StaffRepository(db)
    staff = await staff_repo.get_by_id(body.staff_id)
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff member not found")

    now = datetime.now(timezone.utc)
    assignment = HousekeepingAssignment(
        id=uuid4(),
        reservation_id=body.reservation_id,
        staff_id=body.staff_id,
        scheduled_date=body.scheduled_date,
        notes=body.notes,
        status=AssignmentStatus.SCHEDULED,
        created_at=now,
        updated_at=now,
    )

    hk_repo = HousekeepingRepository(db)
    created = await hk_repo.create(assignment)
    name = f"{staff.first_name} {staff.last_name}"
    return _assignment_to_response(created, name)


@router.get(
    "/properties/{property_id}/housekeeping-assignments",
    response_model=list[HousekeepingAssignmentResponse],
)
async def list_property_housekeeping(
    property_id: UUID,
    db: DbSessionDep,
    start: date = Query(...),
    end: date = Query(...),
) -> list[HousekeepingAssignmentResponse]:
    """Return housekeeping assignments for a property in a date range."""
    hk_repo = HousekeepingRepository(db)
    rows = await hk_repo.get_by_property(property_id, start, end)
    return [
        _assignment_to_response(a, staff_name, guest_name=guest_name)
        for a, staff_name, guest_name in rows
    ]


@router.get(
    "/staff/{staff_id}/housekeeping-assignments",
    response_model=list[HousekeepingAssignmentResponse],
)
async def list_staff_housekeeping(
    staff_id: UUID,
    db: DbSessionDep,
    start: date = Query(...),
    end: date = Query(...),
) -> list[HousekeepingAssignmentResponse]:
    """Return housekeeping assignments for a staff member in a date range."""
    hk_repo = HousekeepingRepository(db)
    rows = await hk_repo.get_by_staff(staff_id, start, end)
    return [
        _assignment_to_response(a, "", property_name=prop_name)
        for a, prop_name in rows
    ]


@router.get(
    "/housekeeping-assignments",
    response_model=list[HousekeepingAssignmentResponse],
)
async def list_all_housekeeping(
    db: DbSessionDep,
    start: date = Query(...),
    end: date = Query(...),
) -> list[HousekeepingAssignmentResponse]:
    """Return all housekeeping assignments in a date range."""
    hk_repo = HousekeepingRepository(db)
    rows = await hk_repo.get_all_in_range(start, end)
    return [
        _assignment_to_response(a, staff_name, property_name=prop_name)
        for a, staff_name, prop_name in rows
    ]


@router.get("/housekeeping-assignments/available")
async def list_available_housekeepers(
    db: DbSessionDep,
    target_date: date = Query(..., alias="date"),
) -> list[dict]:
    """Return housekeepers available on a given date."""
    hk_repo = HousekeepingRepository(db)
    available = await hk_repo.get_available_on_date(target_date)
    return [_staff_to_dict(s) for s in available]


@router.delete(
    "/housekeeping-assignments/{assignment_id}",
    status_code=204,
)
async def delete_housekeeping_assignment(
    assignment_id: UUID,
    db: DbSessionDep,
) -> None:
    """Delete a housekeeping assignment."""
    hk_repo = HousekeepingRepository(db)
    deleted = await hk_repo.delete(assignment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Housekeeping assignment not found")
