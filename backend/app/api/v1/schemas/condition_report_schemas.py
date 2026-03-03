"""Request/response Pydantic models for condition report endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConditionReportListResponse(BaseModel):
    """Lightweight condition report representation for listing views."""

    id: UUID
    property_id: UUID
    property_name: str
    staff_name: str | None = None
    general_condition: str
    summary: str
    events_created: int
    created_at: datetime

    model_config = {"from_attributes": True}


class InventoryItemResponse(BaseModel):
    item_name: str
    expected_count: int | None = None
    actual_count: int | None = None
    condition: str
    notes: str | None = None


class DamageReportResponse(BaseModel):
    location: str
    description: str
    severity: str
    photo_index: int | None = None


class ReportDataResponse(BaseModel):
    inventory: list[InventoryItemResponse] = []
    damages: list[DamageReportResponse] = []
    general_condition: str = "fair"


class ConditionReportDetailResponse(BaseModel):
    """Full condition report representation with structured data."""

    id: UUID
    session_id: UUID
    property_id: UUID
    property_name: str
    staff_name: str | None = None
    general_condition: str
    summary: str
    events_created: int
    report_data: ReportDataResponse
    photo_file_ids: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}
