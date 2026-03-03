from __future__ import annotations

from pydantic import BaseModel, Field


class ConfidenceScore(BaseModel, frozen=True):
    """Immutable value object representing an LLM interpretation confidence.

    Thresholds:
    - ``is_high``  (>= 0.8): safe to auto-process without human review.
    - ``is_acceptable`` (>= 0.4): may proceed but flag for review.
    - ``needs_clarification`` (< 0.4): ask the user to rephrase / confirm.
    """

    value: float = Field(ge=0, le=1)

    @property
    def is_high(self) -> bool:
        """Return ``True`` when confidence is 0.8 or above."""
        return self.value >= 0.8

    @property
    def is_acceptable(self) -> bool:
        """Return ``True`` when confidence is 0.4 or above."""
        return self.value >= 0.4

    @property
    def needs_clarification(self) -> bool:
        """Return ``True`` when confidence is below 0.4."""
        return self.value < 0.4
