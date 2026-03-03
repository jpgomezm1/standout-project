"""Interpretation service — classifies and enriches raw inbound text.

Combines LLM-based text interpretation with entity resolution to produce
structured event data from free-form user messages.  Supports audio
transcription as a first-class capability.
"""

from __future__ import annotations

import logging
from typing import Any

from app.domain.entities.message import InboundMessage
from app.domain.interfaces.llm_client import ILLMClient
from app.services.entity_resolver import EntityResolver

logger = logging.getLogger(__name__)


class InterpretationService:
    """Uses an LLM and fuzzy-matching entity resolver to classify unstructured input."""

    def __init__(
        self,
        llm_client: ILLMClient,
        entity_resolver: EntityResolver,
    ) -> None:
        self._llm_client = llm_client
        self._entity_resolver = entity_resolver

    # -- Audio transcription ------------------------------------------------- #

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe raw audio bytes into text via the LLM client.

        The audio content is written to a temporary file and the path is
        forwarded to the LLM client's ``transcribe_audio`` method.

        Returns the transcribed text, or an empty string on failure.
        """
        import tempfile
        import os

        tmp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".ogg", delete=False
            ) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            transcription = await self._llm_client.transcribe_audio(tmp_path)
            logger.info(
                "Transcribed %d bytes of audio -> %d characters",
                len(audio_data),
                len(transcription),
            )
            return transcription
        except Exception:
            logger.exception("Audio transcription failed")
            return ""
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    logger.warning("Could not delete temp audio file: %s", tmp_path)

    # -- Text interpretation ------------------------------------------------- #

    async def interpret(
        self,
        text: str,
        message: InboundMessage,
    ) -> list[dict[str, Any]]:
        """Interpret free-form *text* into a list of structured event dicts.

        Steps:
        1. Build an entity context so the LLM knows existing properties/items.
        2. Send the text + context to the LLM for classification.
        3. Run each raw event through the entity resolver for ID matching.

        Each dict in the returned list contains at minimum ``event_type``,
        ``confidence``, and any extracted parameters.
        """
        context = await self._entity_resolver.build_context()

        logger.debug(
            "Interpreting message %s (len=%d) with %d known properties",
            message.id,
            len(text),
            len(context.get("properties", [])),
        )

        raw_events = await self._llm_client.interpret_text(text, context)

        if not raw_events:
            logger.info("LLM returned no events for message %s", message.id)
            return []

        resolved: list[dict[str, Any]] = []
        for evt in raw_events:
            evt = await self._entity_resolver.resolve(evt)
            resolved.append(evt)

        logger.info(
            "Interpreted message %s -> %d event(s): %s",
            message.id,
            len(resolved),
            [e.get("event_type", "?") for e in resolved],
        )
        return resolved
