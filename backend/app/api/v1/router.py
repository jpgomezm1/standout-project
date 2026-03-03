"""V1 API router -- aggregates all endpoint sub-routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    condition_reports,
    dashboard,
    events,
    health,
    housekeeping,
    incidents,
    inventory,
    laundry,
    properties,
    reservations,
    staff,
    telegram,
)

router = APIRouter()

# Health & readiness probes (no prefix)
router.include_router(health.router)

# Telegram webhook
router.include_router(telegram.router)

# Core resource endpoints
router.include_router(properties.router)
router.include_router(events.router)
router.include_router(incidents.router)

# Inventory endpoints (mixed: property-scoped + top-level item routes)
router.include_router(inventory.router)

# Laundry flows (property-scoped)
router.include_router(laundry.router)

# Reservations (property-scoped + individual)
router.include_router(reservations.router)

# Staff members (property-scoped + individual)
router.include_router(staff.router)

# Housekeeping assignments (reservation-scoped)
router.include_router(housekeeping.router)

# Condition reports
router.include_router(condition_reports.router)

# Dashboard aggregation
router.include_router(dashboard.router)
