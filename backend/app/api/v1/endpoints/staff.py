"""Staff management endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from app.api.v1.schemas.staff_schemas import StaffCreate, StaffResponse
from app.dependencies import DbSessionDep
from app.domain.entities.staff import StaffMember, StaffRole
from app.infrastructure.db.repositories.staff_repository import StaffRepository

router = APIRouter(tags=["staff"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _staff_to_response(
    staff: StaffMember,
    repo: StaffRepository,
) -> StaffResponse:
    """Convert a domain StaffMember to an API response with property_id."""
    property_ids = await repo.get_property_ids_for_staff(staff.id)
    return StaffResponse(
        id=staff.id,
        first_name=staff.first_name,
        last_name=staff.last_name,
        email=staff.email,
        phone=staff.phone,
        role=staff.role.value.lower(),
        is_active=staff.is_active,
        property_id=property_ids[0] if property_ids else None,
        created_at=staff.created_at,
        updated_at=staff.updated_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/staff", response_model=list[StaffResponse])
async def list_all_staff(
    db: DbSessionDep,
) -> list[StaffResponse]:
    """Return all active staff members."""
    repo = StaffRepository(db)
    staff_list = await repo.get_all()
    return [await _staff_to_response(s, repo) for s in staff_list]


@router.get("/staff/housekeepers", response_model=list[StaffResponse])
async def list_housekeepers(
    db: DbSessionDep,
) -> list[StaffResponse]:
    """Return all active housekeepers (pool)."""
    repo = StaffRepository(db)
    housekeepers = await repo.get_all_housekeepers()
    return [await _staff_to_response(s, repo) for s in housekeepers]


@router.get(
    "/properties/{property_id}/staff",
    response_model=list[StaffResponse],
)
async def list_property_staff(
    property_id: UUID,
    db: DbSessionDep,
) -> list[StaffResponse]:
    """Return all staff members assigned to a property."""
    repo = StaffRepository(db)
    staff_list = await repo.get_by_property(property_id)
    return [await _staff_to_response(s, repo) for s in staff_list]


@router.get("/staff/{staff_id}", response_model=StaffResponse)
async def get_staff_member(
    staff_id: UUID,
    db: DbSessionDep,
) -> StaffResponse:
    """Return a single staff member by ID."""
    repo = StaffRepository(db)
    staff = await repo.get_by_id(staff_id)
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return await _staff_to_response(staff, repo)


@router.post("/staff", response_model=StaffResponse, status_code=201)
async def create_staff_member(
    data: StaffCreate,
    db: DbSessionDep,
) -> StaffResponse:
    """Create a new staff member with optional property assignment."""
    repo = StaffRepository(db)

    now = datetime.now(timezone.utc)
    new_staff = StaffMember(
        id=uuid4(),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        role=StaffRole(data.role.value.upper()),
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    created = await repo.create(new_staff, data.property_id)
    return await _staff_to_response(created, repo)
