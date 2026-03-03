"""Condition report REST API endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.api.v1.schemas.condition_report_schemas import (
    ConditionReportDetailResponse,
    ConditionReportListResponse,
    ReportDataResponse,
)
from app.dependencies import DbSessionDep
from app.infrastructure.db.models.condition_report import (
    ConditionReportModel,
    ConditionReportSessionModel,
)
from app.infrastructure.db.models.property import PropertyModel
from app.infrastructure.db.models.staff import StaffMemberModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["condition-reports"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _enrich_report(db, report: ConditionReportModel) -> dict:
    """Add property_name, staff_name, and session data to a report dict."""
    prop = await db.get(PropertyModel, report.property_id)
    property_name = prop.name if prop else "Desconocida"

    staff_name = None
    if report.staff_id:
        staff = await db.get(StaffMemberModel, report.staff_id)
        if staff:
            staff_name = f"{staff.first_name} {staff.last_name}"

    report_data = report.report_data or {}
    general_condition = report_data.get("general_condition", "fair")

    return {
        "id": report.id,
        "session_id": report.session_id,
        "property_id": report.property_id,
        "property_name": property_name,
        "staff_name": staff_name,
        "general_condition": general_condition,
        "summary": report.summary,
        "events_created": report.events_created,
        "report_data": report_data,
        "created_at": report.created_at,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/condition-reports",
    response_model=list[ConditionReportListResponse],
)
async def list_condition_reports(
    db: DbSessionDep,
    property_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    """List condition reports, optionally filtered by property."""
    stmt = (
        select(ConditionReportModel)
        .order_by(ConditionReportModel.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if property_id:
        stmt = stmt.where(ConditionReportModel.property_id == property_id)

    result = await db.execute(stmt)
    reports = result.scalars().all()

    enriched = []
    for report in reports:
        data = await _enrich_report(db, report)
        enriched.append(data)

    return enriched


@router.get(
    "/condition-reports/{report_id}",
    response_model=ConditionReportDetailResponse,
)
async def get_condition_report(
    report_id: UUID,
    db: DbSessionDep,
) -> dict:
    """Get a single condition report with full detail."""
    report = await db.get(ConditionReportModel, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Condition report not found")

    data = await _enrich_report(db, report)

    # Add photo_file_ids from the session
    session = await db.get(ConditionReportSessionModel, report.session_id)
    data["photo_file_ids"] = list(session.photo_file_ids) if session else []

    return data


@router.get(
    "/properties/{property_id}/condition-reports",
    response_model=list[ConditionReportListResponse],
)
async def list_property_condition_reports(
    property_id: UUID,
    db: DbSessionDep,
    limit: int = Query(default=50, le=100),
) -> list[dict]:
    """List condition reports for a specific property."""
    stmt = (
        select(ConditionReportModel)
        .where(ConditionReportModel.property_id == property_id)
        .order_by(ConditionReportModel.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    reports = result.scalars().all()

    enriched = []
    for report in reports:
        data = await _enrich_report(db, report)
        enriched.append(data)

    return enriched
