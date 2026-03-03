"""ORM models for ``condition_report_sessions`` and ``condition_reports`` tables."""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ConditionReportSessionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Multi-message Telegram session for collecting a property condition report."""

    __tablename__ = "condition_report_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('collecting', 'processing', 'completed', 'failed')",
            name="ck_condition_report_sessions_status",
        ),
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
    )
    staff_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff_members.id", ondelete="SET NULL"),
        nullable=True,
    )
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="collecting"
    )
    voice_transcriptions: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    photo_analyses: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    photo_file_ids: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )

    # Relationships
    report: Mapped[Optional["ConditionReportModel"]] = relationship(
        "ConditionReportModel", back_populates="session", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<ConditionReportSessionModel id={self.id!r} "
            f"property_id={self.property_id!r} status={self.status!r}>"
        )


class ConditionReportModel(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Final structured condition report generated from a session."""

    __tablename__ = "condition_reports"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("condition_report_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
    )
    staff_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staff_members.id", ondelete="SET NULL"),
        nullable=True,
    )
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    events_created: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )

    # Relationships
    session: Mapped["ConditionReportSessionModel"] = relationship(
        "ConditionReportSessionModel", back_populates="report"
    )

    def __repr__(self) -> str:
        return (
            f"<ConditionReportModel id={self.id!r} "
            f"property_id={self.property_id!r} events_created={self.events_created!r}>"
        )
