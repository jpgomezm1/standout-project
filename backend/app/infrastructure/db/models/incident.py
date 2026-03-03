"""ORM model for the ``incidents`` table."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class IncidentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An operational incident reported against a property."""

    __tablename__ = "incidents"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'acknowledged', 'in_progress', 'resolved')",
            name="ck_incidents_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')",
            name="ck_incidents_priority",
        ),
        # Partial index: fast lookup for unresolved incidents.
        Index(
            "ix_incidents_unresolved",
            "property_id",
            "status",
            postgresql_where="status != 'resolved'",
        ),
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    incident_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="'open'"
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="'medium'"
    )
    reported_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telegram_users.id", ondelete="SET NULL"),
        nullable=True,
    )
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telegram_users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # -- Relationships -------------------------------------------------------
    property: Mapped["PropertyModel"] = relationship(
        "PropertyModel", back_populates="incidents"
    )
    reporter: Mapped[Optional["TelegramUserModel"]] = relationship(
        "TelegramUserModel", foreign_keys=[reported_by], lazy="joined"
    )
    assignee: Mapped[Optional["TelegramUserModel"]] = relationship(
        "TelegramUserModel", foreign_keys=[assigned_to], lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<IncidentModel id={self.id!r} title={self.title!r} "
            f"status={self.status!r}>"
        )
