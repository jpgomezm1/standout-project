"""Request/response Pydantic models for Telegram webhook validation."""

from __future__ import annotations

from pydantic import BaseModel


class TelegramWebhookResponse(BaseModel):
    """Standard response returned to Telegram after processing a webhook."""

    status: str


class TelegramMessageInfo(BaseModel):
    """Extracted metadata from a Telegram webhook payload (for logging/debugging)."""

    update_id: int
    chat_id: int | None = None
    message_id: int | None = None
    from_user_id: int | None = None
    message_type: str | None = None
