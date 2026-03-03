"""ORM model for the ``inventory_items`` table."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class InventoryItemModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A tracked inventory item within a property."""

    __tablename__ = "inventory_items"
    __table_args__ = (
        UniqueConstraint("property_id", "item_name", name="uq_inventory_property_item"),
        CheckConstraint(
            "category IN ('LINEN', 'TOWEL', 'KITCHEN', 'BATHROOM', "
            "'FURNITURE', 'ELECTRONIC', 'OTHER')",
            name="ck_inventory_items_category",
        ),
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    expected_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    low_stock_threshold: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )

    # -- Relationships -------------------------------------------------------
    property: Mapped["PropertyModel"] = relationship(
        "PropertyModel", back_populates="inventory_items"
    )

    def __repr__(self) -> str:
        return (
            f"<InventoryItemModel id={self.id!r} "
            f"item_name={self.item_name!r} category={self.category!r}>"
        )
