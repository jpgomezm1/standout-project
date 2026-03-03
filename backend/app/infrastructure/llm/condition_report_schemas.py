"""Pydantic models for structured condition report output (OpenAI Structured Outputs)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractedConditionEvent(BaseModel):
    """An operational event extracted from a condition report."""

    event_type: str = Field(
        description="One of: ITEM_MISSING, ITEM_BROKEN, MAINTENANCE_ISSUE",
    )
    item_name: str | None = Field(
        None,
        description="Name of the inventory item involved, if applicable",
    )
    quantity: int = Field(
        1,
        description="Number of items affected",
    )
    description: str = Field(
        description="Human-readable description of the issue",
    )
    priority: str = Field(
        "medium",
        description="Urgency level: low, medium, high, or critical",
    )


class InventoryItem(BaseModel):
    """A single inventory item observed during the condition report."""

    item_name: str = Field(description="Name of the item")
    expected_count: int | None = Field(
        None, description="Expected quantity from inventory records"
    )
    actual_count: int | None = Field(
        None, description="Actual quantity observed"
    )
    condition: str = Field(
        description="Observed condition: good, damaged, or missing"
    )
    notes: str | None = Field(
        None, description="Additional observations about this item"
    )


class DamageReport(BaseModel):
    """A damage or issue found during the property inspection."""

    location: str = Field(
        description="Area of the property: bedroom, bathroom, kitchen, living_room, etc."
    )
    description: str = Field(description="Description of the damage or issue")
    severity: str = Field(
        description="Severity level: low, medium, high, or critical"
    )
    photo_index: int | None = Field(
        None, description="Index of the related photo, if any"
    )


class ConditionReportResponse(BaseModel):
    """Top-level structured response for a property condition report."""

    inventory: list[InventoryItem] = Field(
        description="List of inventory items observed during the inspection"
    )
    damages: list[DamageReport] = Field(
        description="List of damages or issues found"
    )
    general_condition: str = Field(
        description="Overall property condition: excellent, good, fair, or poor"
    )
    summary: str = Field(
        description="Brief summary of the property condition in Spanish"
    )
    operational_events: list[ExtractedConditionEvent] = Field(
        description="Operational events to create based on findings"
    )
