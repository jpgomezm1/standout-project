"""ORM models for ``staff_members``, ``property_staff_assignments``, and ``housekeeping_assignments`` tables."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PropertyStaffAssignmentModel(Base):
    """Many-to-many join table between properties and staff members."""

    __tablename__ = "property_staff_assignments"

    property_id: Mapped["uuid.UUID"] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        primary_key=True,
    )
    staff_id: Mapped["uuid.UUID"] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff_members.id", ondelete="CASCADE"),
        primary_key=True,
    )


class StaffMemberModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A member of the operational team."""

    __tablename__ = "staff_members"
    __table_args__ = (
        CheckConstraint(
            "role IN ('housekeeper', 'property_manager')",
            name="ck_staff_members_role",
        ),
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )

    # Relationships
    assignments: Mapped[List["PropertyStaffAssignmentModel"]] = relationship(
        "PropertyStaffAssignmentModel",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<StaffMemberModel id={self.id!r} name={self.first_name!r} {self.last_name!r} role={self.role!r}>"


class HousekeepingAssignmentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Assignment of a housekeeper to a reservation on a specific date."""

    __tablename__ = "housekeeping_assignments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled')",
            name="ck_housekeeping_assignments_status",
        ),
        UniqueConstraint(
            "reservation_id", "staff_id", "scheduled_date",
            name="uq_housekeeping_assignment",
        ),
    )

    reservation_id: Mapped["uuid.UUID"] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    staff_id: Mapped["uuid.UUID"] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff_members.id", ondelete="CASCADE"),
        nullable=False,
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="scheduled"
    )

    # Relationships
    staff_member: Mapped["StaffMemberModel"] = relationship(
        "StaffMemberModel", lazy="selectin",
    )
