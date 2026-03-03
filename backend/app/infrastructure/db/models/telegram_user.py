"""ORM model for the ``telegram_users`` table."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class TelegramUserModel(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """A Telegram user known to the system."""

    __tablename__ = "telegram_users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('operator', 'manager', 'admin')",
            name="ck_telegram_users_role",
        ),
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<TelegramUserModel id={self.id!r} "
            f"telegram_id={self.telegram_id!r} role={self.role!r}>"
        )
