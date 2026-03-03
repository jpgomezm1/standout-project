"""Property management endpoints."""

from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.property_schemas import (
    PropertyCreate,
    PropertyListResponse,
    PropertyResponse,
    PropertySummaryResponse,
    PropertyUpdate,
)
from app.dependencies import DbSessionDep
from app.domain.entities.incident import IncidentStatus
from app.domain.entities.laundry import LaundryStatus
from app.domain.entities.property import Property
from app.domain.entities.reservation import ReservationStatus
from app.domain.entities.staff import StaffRole
from app.infrastructure.db.repositories.incident_repository import IncidentRepository
from app.infrastructure.db.repositories.inventory_repository import InventoryRepository
from app.infrastructure.db.repositories.laundry_repository import LaundryRepository
from app.infrastructure.db.repositories.property_repository import PropertyRepository
from app.infrastructure.db.repositories.reservation_repository import ReservationRepository
from app.infrastructure.db.repositories.staff_repository import StaffRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/properties", tags=["properties"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _build_summary(
    prop: Property,
    db: DbSessionDep,
) -> PropertySummaryResponse:
    """Enrich a property domain entity with aggregated operational counts.

    Uses asyncio.gather to parallelise independent queries.
    """
    incident_repo = IncidentRepository(db)
    laundry_repo = LaundryRepository(db)
    inventory_repo = InventoryRepository(db)
    reservation_repo = ReservationRepository(db)
    staff_repo = StaffRepository(db)

    today = date.today()
    week_ahead = today + timedelta(days=7)

    # Run all independent queries in parallel
    (
        open_incidents,
        acknowledged_incidents,
        in_progress_incidents,
        sent_flows,
        in_progress_flows,
        quantity_rows,
        upcoming,
        current,
        pms,
    ) = await asyncio.gather(
        incident_repo.get_all(property_id=prop.id, status=IncidentStatus.OPEN),
        incident_repo.get_all(property_id=prop.id, status=IncidentStatus.ACKNOWLEDGED),
        incident_repo.get_all(property_id=prop.id, status=IncidentStatus.IN_PROGRESS),
        laundry_repo.get_by_property(property_id=prop.id, status=LaundryStatus.SENT),
        laundry_repo.get_by_property(property_id=prop.id, status=LaundryStatus.IN_PROGRESS),
        inventory_repo.get_current_quantities(property_id=prop.id),
        reservation_repo.get_by_property(
            property_id=prop.id,
            status=ReservationStatus.CONFIRMED,
            from_date=today,
            to_date=week_ahead,
        ),
        reservation_repo.get_by_property(
            property_id=prop.id,
            status=ReservationStatus.IN_PROGRESS,
        ),
        staff_repo.get_by_property(prop.id, role=StaffRole.PROPERTY_MANAGER),
    )

    active_count = len(open_incidents) + len(acknowledged_incidents) + len(in_progress_incidents)
    items_in_laundry = sum(f.total_pieces for f in sent_flows) + sum(
        f.total_pieces for f in in_progress_flows
    )
    low_stock_count = sum(
        1
        for row in quantity_rows
        if row["current_quantity"] < row["item"].low_stock_threshold
    )
    current_guest = current[0].guest_name if current else None
    pm_name = f"{pms[0].first_name} {pms[0].last_name}" if pms else None

    return PropertySummaryResponse(
        id=prop.id,
        name=prop.name,
        address=prop.address,
        timezone=prop.timezone,
        aliases=prop.aliases,
        housekeepers_needed=prop.housekeepers_needed,
        is_active=prop.is_active,
        metadata=prop.metadata,
        created_at=prop.created_at,
        updated_at=prop.updated_at,
        active_incidents=active_count,
        items_in_laundry=items_in_laundry,
        low_stock_alerts=low_stock_count,
        upcoming_reservations=len(upcoming),
        current_guest=current_guest,
        property_manager=pm_name,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[PropertyListResponse])
async def list_properties(
    db: DbSessionDep,
    search: str | None = Query(default=None, description="Search by name or alias"),
) -> list[PropertyListResponse]:
    """Return all active properties with lightweight data (1 query with LEFT JOIN for PM).

    This endpoint is optimised for listing views — no heavy aggregations.
    """
    # Build a single query that LEFT JOINs to get PM name
    stmt = text("""
        SELECT
            p.id,
            p.name,
            COALESCE(p.address, '') AS address,
            p.timezone,
            p.is_active,
            p.housekeepers_needed,
            CASE
                WHEN sm.id IS NOT NULL
                THEN sm.first_name || ' ' || sm.last_name
                ELSE NULL
            END AS property_manager
        FROM properties p
        LEFT JOIN property_staff_assignments psa ON psa.property_id = p.id
        LEFT JOIN staff_members sm ON sm.id = psa.staff_id AND sm.role = 'property_manager'
        WHERE p.is_active = true
        ORDER BY p.name
    """)

    result = await db.execute(stmt)
    rows = result.mappings().all()

    results = [
        PropertyListResponse(
            id=row["id"],
            name=row["name"],
            address=row["address"],
            timezone=row["timezone"],
            is_active=row["is_active"],
            housekeepers_needed=row["housekeepers_needed"],
            property_manager=row["property_manager"],
        )
        for row in rows
    ]

    if search:
        pattern = search.lower()
        results = [r for r in results if pattern in r.name.lower() or pattern in r.address.lower()]

    return results


@router.get("/{property_id}", response_model=PropertySummaryResponse)
async def get_property(
    property_id: UUID,
    db: DbSessionDep,
) -> PropertySummaryResponse:
    """Return a single property with full enrichment (KPIs, staff, etc.)."""
    repo = PropertyRepository(db)
    prop = await repo.get_by_id(property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    return await _build_summary(prop, db)


@router.post("", response_model=PropertyResponse, status_code=201)
async def create_property(
    data: PropertyCreate,
    db: DbSessionDep,
) -> PropertyResponse:
    """Create a new property and return the persisted record."""
    repo = PropertyRepository(db)

    now = datetime.now(timezone.utc)
    new_property = Property(
        id=uuid4(),
        name=data.name,
        address=data.address,
        timezone=data.timezone,
        aliases=data.aliases,
        housekeepers_needed=data.housekeepers_needed,
        is_active=True,
        metadata=data.metadata,
        created_at=now,
        updated_at=now,
    )

    created = await repo.create(new_property)

    return PropertyResponse(
        id=created.id,
        name=created.name,
        address=created.address,
        timezone=created.timezone,
        aliases=created.aliases,
        housekeepers_needed=created.housekeepers_needed,
        is_active=created.is_active,
        metadata=created.metadata,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: UUID,
    data: PropertyUpdate,
    db: DbSessionDep,
) -> PropertyResponse:
    """Partially update an existing property.

    Only fields present in the request body are modified.
    """
    from app.infrastructure.db.models.property import PropertyModel

    model = await db.get(PropertyModel, property_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Property not found")

    update_data = data.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        # Map the schema field name to the ORM column name
        update_data["metadata_"] = update_data.pop("metadata")

    for field, value in update_data.items():
        setattr(model, field, value)

    await db.flush()
    await db.refresh(model)

    repo = PropertyRepository(db)
    return PropertyResponse.model_validate(repo._to_domain(model))
