"""Messaging channel adapters (Telegram, WhatsApp, etc.)."""

from app.infrastructure.channels.telegram_adapter import TelegramAdapter

__all__ = [
    "TelegramAdapter",
]
