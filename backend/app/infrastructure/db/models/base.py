"""SQLAlchemy declarative base with reusable column mixins."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    """Application-wide declarative base.

    All ORM models inherit from this class so that Alembic can discover
    the full metadata via ``Base.metadata``.
    """

    pass


class UUIDPrimaryKeyMixin:
    """Mixin that adds a UUID primary key with a PostgreSQL server-side default."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )


class TimestampMixin:
    """Mixin that adds ``created_at`` and ``updated_at`` columns.

    * ``created_at`` is set once on INSERT via a server-side ``now()`` default.
    * ``updated_at`` is refreshed on every UPDATE via ``onupdate``.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class CreatedAtMixin:
    """Lighter mixin when only ``created_at`` is needed (append-only tables)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
