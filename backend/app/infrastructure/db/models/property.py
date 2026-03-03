"""ORM model for the ``properties`` table."""

from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PropertyModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A managed hospitality property."""

    __tablename__ = "properties"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="America/Bogota"
    )
    aliases: Mapped[List] = mapped_column(JSONB, nullable=False, server_default="[]")
    housekeepers_needed: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    metadata_: Mapped[Dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )

    # -- Relationships (back-populated by children) -------------------------
    inventory_items: Mapped[List["InventoryItemModel"]] = relationship(
        "InventoryItemModel", back_populates="property", lazy="selectin"
    )
    incidents: Mapped[List["IncidentModel"]] = relationship(
        "IncidentModel", back_populates="property", lazy="selectin"
    )
    laundry_flows: Mapped[List["LaundryFlowModel"]] = relationship(
        "LaundryFlowModel", back_populates="property", lazy="selectin"
    )
    events: Mapped[List["EventModel"]] = relationship(
        "EventModel", back_populates="property", lazy="noload"
    )
    reservations: Mapped[List["ReservationModel"]] = relationship(
        "ReservationModel", back_populates="property", lazy="noload"
    )
    staff_assignments: Mapped[List["PropertyStaffAssignmentModel"]] = relationship(
        "PropertyStaffAssignmentModel", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<PropertyModel id={self.id!r} name={self.name!r}>"
