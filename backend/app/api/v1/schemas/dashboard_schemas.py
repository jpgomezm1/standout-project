"""Request/response Pydantic models for dashboard endpoints."""

from __future__ import annotations

from pydantic import BaseModel

from app.api.v1.schemas.event_schemas import EventResponse


class DashboardSummary(BaseModel):
    """Aggregated operational summary across all (or a single) properties."""

    total_properties: int
    active_incidents: int
    critical_incidents: int
    items_in_laundry: int
    low_stock_items: int
    recent_events: list[EventResponse]
