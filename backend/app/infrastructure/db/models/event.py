"""ORM model for the ``events`` table (append-only event store)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, UUIDPrimaryKeyMixin


class EventModel(UUIDPrimaryKeyMixin, Base):
    """Immutable operational event -- the core of the event-sourced state."""

    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ("
            "'ITEM_BROKEN', 'ITEM_MISSING', "
            "'ITEM_SENT_TO_LAUNDRY', 'ITEM_RETURNED_FROM_LAUNDRY', "
            "'MAINTENANCE_ISSUE', 'LOW_STOCK_ALERT', "
            "'INCIDENT_ACKNOWLEDGED', 'INCIDENT_IN_PROGRESS', 'INCIDENT_RESOLVED', "
            "'LAUNDRY_RETURNED', 'LAUNDRY_PARTIALLY_RETURNED', 'LAUNDRY_LOST'"
            ")",
            name="ck_events_event_type",
        ),
        # Composite indexes for the most frequent query patterns.
        Index("ix_events_property_created", "property_id", "created_at"),
        Index(
            "ix_events_property_type_created",
            "property_id",
            "event_type",
            "created_at",
        ),
        Index("ix_events_sequence_num", "sequence_num"),
        # GIN index for arbitrary JSONB queries on payload.
        Index("ix_events_payload_gin", "payload", postgresql_using="gin"),
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Dict] = mapped_column(JSONB, nullable=False)
    source_message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("raw_messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 3), nullable=True
    )
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("telegram_users.id", ondelete="SET NULL"),
        nullable=True,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    sequence_num: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), unique=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # -- Relationships -------------------------------------------------------
    property: Mapped["PropertyModel"] = relationship(
        "PropertyModel", back_populates="events"
    )
    source_message: Mapped[Optional["RawMessageModel"]] = relationship(
        "RawMessageModel", lazy="joined"
    )
    actor: Mapped[Optional["TelegramUserModel"]] = relationship(
        "TelegramUserModel", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<EventModel id={self.id!r} type={self.event_type!r} "
            f"seq={self.sequence_num!r}>"
        )
