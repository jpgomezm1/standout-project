"""ORM model for the ``raw_messages`` table."""

from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class RawMessageModel(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Raw inbound message received from a messaging channel."""

    __tablename__ = "raw_messages"
    __table_args__ = (
        UniqueConstraint(
            "telegram_chat_id",
            "telegram_message_id",
            name="uq_raw_messages_chat_msg",
        ),
        CheckConstraint(
            "message_type IN ('text', 'photo', 'voice', 'video', 'document')",
            name="ck_raw_messages_message_type",
        ),
        CheckConstraint(
            "processing_status IN ('received', 'processing', 'processed', "
            "'needs_clarification', 'pending_retry', 'failed')",
            name="ck_raw_messages_processing_status",
        ),
        # Partial index to speed up queries for messages that still need work.
        Index(
            "ix_raw_messages_pending_processing",
            "processing_status",
            postgresql_where="processing_status IN ('received', 'processing', 'pending_retry')",
        ),
    )

    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    telegram_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    telegram_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    message_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_references: Mapped[List] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    raw_payload: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    processing_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="'received'"
    )
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<RawMessageModel id={self.id!r} "
            f"status={self.processing_status!r}>"
        )
