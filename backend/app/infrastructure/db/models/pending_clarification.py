"""ORM model for the ``pending_clarifications`` table."""

from __future__ import annotations

import uuid
from typing import Dict, Optional

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PendingClarificationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A clarification request linked to an ambiguous inbound message."""

    __tablename__ = "pending_clarifications"

    original_message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("raw_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    missing_fields: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    partial_event_data: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    resolved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )

    # -- Relationships -------------------------------------------------------
    original_message: Mapped["RawMessageModel"] = relationship(
        "RawMessageModel", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<PendingClarificationModel id={self.id!r} "
            f"resolved={self.resolved!r}>"
        )
