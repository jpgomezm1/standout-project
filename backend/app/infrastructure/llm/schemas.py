"""Pydantic models for structured LLM output (OpenAI Structured Outputs)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractedEvent(BaseModel):
    """A single operational event extracted from an unstructured message."""

    event_type: str = Field(
        description=(
            "One of the valid event types: ITEM_BROKEN, ITEM_MISSING, "
            "ITEM_REPLACED, ITEM_SENT_TO_LAUNDRY, ITEM_RETURNED_FROM_LAUNDRY, "
            "MAINTENANCE_ISSUE, LOW_STOCK_ALERT, INCIDENT_ACKNOWLEDGED, "
            "INCIDENT_IN_PROGRESS, INCIDENT_RESOLVED, LAUNDRY_RETURNED, "
            "LAUNDRY_PARTIALLY_RETURNED, LAUNDRY_LOST"
        ),
    )
    property_name: str | None = Field(
        None,
        description="Name or alias of the property this event relates to",
    )
    item_name: str | None = Field(
        None,
        description="Name of the inventory item involved, if applicable",
    )
    quantity: int = Field(
        1,
        description="Number of items affected (defaults to 1)",
    )
    description: str = Field(
        description="Human-readable description of the event in the original language",
    )
    confidence: float = Field(
        description="Confidence score between 0 and 1 indicating extraction certainty",
    )
    priority: str = Field(
        "medium",
        description="Urgency level: low, medium, high, or critical",
    )


class LLMEventExtractionResponse(BaseModel):
    """Top-level structured response returned by the LLM extraction call."""

    events: list[ExtractedEvent] = Field(
        description="List of operational events extracted from the message",
    )
    summary: str = Field(
        description="Brief summary of the original message content",
    )
