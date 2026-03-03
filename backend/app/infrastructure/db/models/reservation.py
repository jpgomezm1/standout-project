"""ORM model for the ``reservations`` table."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ReservationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A guest reservation at a property."""

    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint(
            "check_out > check_in",
            name="ck_reservations_checkout_after_checkin",
        ),
        CheckConstraint(
            "status IN ('confirmed', 'in_progress', 'completed', 'cancelled')",
            name="ck_reservations_status",
        ),
        CheckConstraint(
            "channel IN ('airbnb', 'booking', 'direct', 'other')",
            name="ck_reservations_channel",
        ),
        Index(
            "ix_reservations_property_dates",
            "property_id",
            "check_in",
            "check_out",
        ),
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    guest_name: Mapped[str] = mapped_column(String(255), nullable=False)
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="'confirmed'"
    )
    num_guests: Mapped[int] = mapped_column(Integer, nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    # -- Relationships -------------------------------------------------------
    property: Mapped["PropertyModel"] = relationship(
        "PropertyModel", back_populates="reservations"
    )

    def __repr__(self) -> str:
        return (
            f"<ReservationModel id={self.id!r} guest={self.guest_name!r} "
            f"status={self.status!r}>"
        )
