from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """The media type of an inbound message."""

    TEXT = "TEXT"
    PHOTO = "PHOTO"
    VOICE = "VOICE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"


class ProcessingStatus(str, Enum):
    """Processing pipeline status for an inbound message."""

    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    PENDING_RETRY = "PENDING_RETRY"
    FAILED = "FAILED"


class InboundMessage(BaseModel):
    """Raw inbound message received from a messaging channel (e.g. Telegram).

    This is the first object created when a webhook payload arrives.
    It preserves the original platform identifiers and raw payload so that
    downstream processors can re-interpret the message if needed.
    """

    id: UUID
    telegram_chat_id: int
    telegram_message_id: int
    telegram_user_id: int
    message_type: MessageType
    content_text: str | None = None
    file_references: list[dict] = Field(default_factory=list)
    raw_payload: dict = Field(default_factory=dict)
    processing_status: ProcessingStatus
    created_at: datetime
