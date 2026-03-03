from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.message import InboundMessage


class IChannelAdapter(ABC):
    """Port for messaging-channel integration (e.g. Telegram, WhatsApp).

    Each channel provides its own concrete adapter that knows how to
    parse the raw webhook, fetch media files, and send outbound replies.
    """

    @abstractmethod
    async def parse_webhook(self, payload: dict) -> InboundMessage:
        """Convert a raw webhook *payload* into an ``InboundMessage``."""
        ...

    @abstractmethod
    async def download_media(self, file_id: str) -> bytes:
        """Download and return the raw bytes for the given *file_id*."""
        ...

    @abstractmethod
    async def send_message(self, chat_id: int, text: str) -> None:
        """Send a text message to the specified *chat_id*."""
        ...
