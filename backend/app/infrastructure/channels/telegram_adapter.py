"""Telegram channel adapter — implements :class:`IChannelAdapter`.

Handles webhook parsing, media downloads, and outbound message delivery
for the Telegram Bot API.
"""

from __future__ import annotations

import hmac
import logging
from datetime import datetime, timezone
from uuid import uuid4

import httpx

from app.domain.entities.message import InboundMessage, MessageType, ProcessingStatus
from app.domain.interfaces.channel_adapter import IChannelAdapter

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}"
TELEGRAM_FILE_API = "https://api.telegram.org/file/bot{token}"

# Timeout configuration for outbound HTTP calls to the Telegram API.
_HTTP_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)


class TelegramAdapter(IChannelAdapter):
    """Concrete channel adapter for Telegram.

    Parameters
    ----------
    bot_token:
        The Telegram Bot API token (from BotFather).
    webhook_secret:
        The secret token configured for webhook verification via the
        ``X-Telegram-Bot-Api-Secret-Token`` header.
    """

    def __init__(self, bot_token: str, webhook_secret: str) -> None:
        self.bot_token = bot_token
        self.webhook_secret = webhook_secret
        self.api_base = TELEGRAM_API.format(token=bot_token)
        self.file_base = TELEGRAM_FILE_API.format(token=bot_token)

    # ------------------------------------------------------------------
    # Webhook verification
    # ------------------------------------------------------------------

    def verify_secret(self, secret_token: str) -> bool:
        """Return *True* if the given token matches the configured secret.

        Uses :func:`hmac.compare_digest` to prevent timing-based attacks.
        """
        return hmac.compare_digest(secret_token, self.webhook_secret)

    # ------------------------------------------------------------------
    # Webhook parsing
    # ------------------------------------------------------------------

    async def parse_webhook(self, payload: dict) -> InboundMessage:
        """Parse a raw Telegram webhook payload into an :class:`InboundMessage`.

        Supports TEXT, PHOTO, VOICE, VIDEO, and DOCUMENT message types.
        For media messages, the file reference(s) are stored in
        ``file_references`` for later download.
        """
        message = payload.get("message", {})
        chat = message.get("chat", {})
        sender = message.get("from", {})

        chat_id: int = chat.get("id", 0)
        message_id: int = message.get("message_id", 0)
        user_id: int = sender.get("id", 0)

        # -- Determine message type and extract content --------------------
        msg_type = MessageType.TEXT
        content_text: str | None = message.get("text")
        file_refs: list[dict] = []

        if "photo" in message:
            msg_type = MessageType.PHOTO
            # Telegram sends multiple sizes; use the largest (last element).
            photo = message["photo"][-1]
            file_refs.append({"file_id": photo["file_id"], "type": "photo"})
            content_text = message.get("caption")

        elif "voice" in message:
            msg_type = MessageType.VOICE
            file_refs.append(
                {"file_id": message["voice"]["file_id"], "type": "voice"},
            )

        elif "video" in message:
            msg_type = MessageType.VIDEO
            file_refs.append(
                {"file_id": message["video"]["file_id"], "type": "video"},
            )
            content_text = message.get("caption")

        elif "document" in message:
            msg_type = MessageType.DOCUMENT
            file_refs.append(
                {"file_id": message["document"]["file_id"], "type": "document"},
            )
            content_text = message.get("caption")

        logger.info(
            "Parsed Telegram message %d from chat %d (type=%s)",
            message_id,
            chat_id,
            msg_type.value,
        )

        return InboundMessage(
            id=uuid4(),
            telegram_chat_id=chat_id,
            telegram_message_id=message_id,
            telegram_user_id=user_id,
            message_type=msg_type,
            content_text=content_text,
            file_references=file_refs,
            raw_payload=payload,
            processing_status=ProcessingStatus.RECEIVED,
            created_at=datetime.now(timezone.utc),
        )

    # ------------------------------------------------------------------
    # Media download
    # ------------------------------------------------------------------

    async def download_media(self, file_id: str) -> bytes:
        """Download a media file from Telegram by its ``file_id``.

        Makes two HTTP calls:
        1. ``getFile`` to resolve the ``file_path`` on Telegram's servers.
        2. A direct GET to download the raw bytes.
        """
        logger.debug("Downloading media file_id=%s", file_id)
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            # Step 1: resolve file path
            resp = await client.get(
                f"{self.api_base}/getFile",
                params={"file_id": file_id},
            )
            resp.raise_for_status()
            file_path = resp.json()["result"]["file_path"]

            # Step 2: download raw bytes
            file_resp = await client.get(f"{self.file_base}/{file_path}")
            file_resp.raise_for_status()

        logger.info(
            "Downloaded %d bytes for file_id=%s",
            len(file_resp.content),
            file_id,
        )
        return file_resp.content

    # ------------------------------------------------------------------
    # Outbound messaging
    # ------------------------------------------------------------------

    async def send_message(self, chat_id: int, text: str) -> None:
        """Send a Markdown-formatted text message to the given *chat_id*."""
        logger.debug("Sending message to chat_id=%d (%d chars)", chat_id, len(text))
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.post(
                f"{self.api_base}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
            )
            resp.raise_for_status()
        logger.info("Message sent to chat_id=%d", chat_id)

    # ------------------------------------------------------------------
    # Inline keyboards and callback queries
    # ------------------------------------------------------------------

    async def send_inline_keyboard(
        self,
        chat_id: int,
        text: str,
        buttons: list[list[dict]],
    ) -> None:
        """Send a message with an inline keyboard.

        Parameters
        ----------
        chat_id:
            Target chat identifier.
        text:
            Message text (Markdown).
        buttons:
            Rows of buttons. Each button is a dict with ``text`` and
            ``callback_data`` keys.
        """
        logger.debug("Sending inline keyboard to chat_id=%d", chat_id)
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.post(
                f"{self.api_base}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "reply_markup": {"inline_keyboard": buttons},
                },
            )
            if not resp.is_success:
                logger.error(
                    "Telegram sendMessage (inline keyboard) failed: %s",
                    resp.text,
                )
            resp.raise_for_status()
        logger.info("Inline keyboard sent to chat_id=%d", chat_id)

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: str | None = None,
    ) -> None:
        """Respond to a callback query to dismiss the spinner in Telegram."""
        logger.debug("Answering callback_query_id=%s", callback_query_id)
        payload: dict = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.post(
                f"{self.api_base}/answerCallbackQuery",
                json=payload,
            )
            resp.raise_for_status()

    @staticmethod
    def parse_callback_query(payload: dict) -> dict:
        """Extract useful fields from a ``callback_query`` update.

        Returns a dict with: ``chat_id``, ``user_id``, ``callback_data``,
        ``callback_query_id``, ``message_id``.
        """
        cq = payload["callback_query"]
        message = cq.get("message", {})
        chat = message.get("chat", {})
        return {
            "chat_id": chat.get("id", 0),
            "user_id": cq.get("from", {}).get("id", 0),
            "callback_data": cq.get("data", ""),
            "callback_query_id": cq.get("id", ""),
            "message_id": message.get("message_id", 0),
        }
