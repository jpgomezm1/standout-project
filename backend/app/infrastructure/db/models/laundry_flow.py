"""ORM model for the ``laundry_flows`` table."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class LaundryFlowModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tracks a batch of items sent to and returned from a laundry service."""

    __tablename__ = "laundry_flows"
    __table_args__ = (
        CheckConstraint(
            "status IN ('sent', 'in_progress', 'returned', "
            "'partially_returned', 'lost')",
            name="ck_laundry_flows_status",
        ),
        CheckConstraint(
            "returned_at IS NULL OR returned_at >= sent_at",
            name="ck_laundry_flows_return_after_sent",
        ),
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="'sent'"
    )
    items: Mapped[List] = mapped_column(JSONB, nullable=False, server_default="[]")
    total_pieces: Mapped[int] = mapped_column(Integer, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expected_return_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    returned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # -- Relationships -------------------------------------------------------
    property: Mapped["PropertyModel"] = relationship(
        "PropertyModel", back_populates="laundry_flows"
    )

    def __repr__(self) -> str:
        return (
            f"<LaundryFlowModel id={self.id!r} "
            f"status={self.status!r} total_pieces={self.total_pieces!r}>"
        )
