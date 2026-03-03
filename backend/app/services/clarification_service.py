"""Clarification service — requests missing information from the end user.

When the interpretation pipeline cannot confidently map an inbound message
to a fully-resolved event, this service sends a follow-up message through
the channel adapter asking the user to supply the missing details.
"""

from __future__ import annotations

import logging
from typing import Any

from app.domain.entities.message import InboundMessage
from app.domain.interfaces.channel_adapter import IChannelAdapter

logger = logging.getLogger(__name__)


class ClarificationService:
    """Sends targeted clarification requests to users via the channel adapter."""

    def __init__(
        self,
        channel_adapter: IChannelAdapter,
        *,
        pending_repo: Any | None = None,
    ) -> None:
        self._channel_adapter = channel_adapter
        # Optional repository for persisting pending clarification state.
        # Not yet implemented; will be used for tracking outstanding requests.
        self._pending_repo = pending_repo

    async def request_clarification(
        self,
        message: InboundMessage,
        partial_data: dict[str, Any],
    ) -> None:
        """Analyse *partial_data* for missing fields and ask the user to fill them.

        Sends a single message enumerating which pieces of information are
        still required before the event can be processed.
        """
        missing: list[str] = self._detect_missing_fields(partial_data)

        if not missing:
            logger.debug(
                "No missing fields detected for message %s; skipping clarification",
                message.id,
            )
            return

        text = self._build_clarification_text(missing)

        logger.info(
            "Requesting clarification for message %s (chat_id=%d): missing=%s",
            message.id,
            message.telegram_chat_id,
            missing,
        )

        try:
            await self._channel_adapter.send_message(message.telegram_chat_id, text)
        except Exception:
            logger.exception(
                "Failed to send clarification request for message %s",
                message.id,
            )

        # Persist pending clarification state if a repo is available.
        if self._pending_repo is not None:
            try:
                await self._pending_repo.save_pending(
                    message_id=message.id,
                    missing_fields=missing,
                    partial_data=partial_data,
                )
            except Exception:
                logger.exception(
                    "Failed to persist pending clarification for message %s",
                    message.id,
                )

    # -- Internal helpers ---------------------------------------------------- #

    @staticmethod
    def _detect_missing_fields(partial_data: dict[str, Any]) -> list[str]:
        """Return a list of human-readable descriptions for each missing field."""
        missing: list[str] = []

        if not partial_data.get("property_id"):
            missing.append("property (which property is this about?)")

        if not partial_data.get("event_type"):
            missing.append("event type (what happened?)")

        if not partial_data.get("item_name") and not partial_data.get("item_id"):
            # Only flag as missing when the event type implies an item reference.
            event_type = partial_data.get("event_type", "")
            item_related = {"ITEM_BROKEN", "ITEM_MISSING", "ITEM_SENT_TO_LAUNDRY"}
            if event_type in item_related:
                missing.append("item name (which item is affected?)")

        return missing

    @staticmethod
    def _build_clarification_text(missing: list[str]) -> str:
        """Format a user-facing clarification message."""
        lines = [f"- {m}" for m in missing]
        return "I need more information to process your message:\n" + "\n".join(lines)
