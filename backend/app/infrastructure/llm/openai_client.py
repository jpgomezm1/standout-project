"""OpenAI-backed implementation of :class:`ILLMClient`.

Provides audio transcription via Whisper and structured event extraction
via GPT-4o with OpenAI Structured Outputs.
"""

from __future__ import annotations

import base64
import io
import logging

from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.domain.interfaces.llm_client import ILLMClient
from app.infrastructure.llm.condition_report_schemas import ConditionReportResponse
from app.infrastructure.llm.prompts import get_condition_report_system_prompt, get_extraction_system_prompt
from app.infrastructure.llm.schemas import LLMEventExtractionResponse

logger = logging.getLogger(__name__)

_RETRYABLE_ERRORS = (APITimeoutError, APIConnectionError, RateLimitError)


class OpenAIClient(ILLMClient):
    """Concrete LLM client backed by the OpenAI API.

    Parameters
    ----------
    api_key:
        OpenAI API secret key.
    transcription_model:
        Model identifier used for audio transcription (default ``whisper-1``).
    chat_model:
        Model identifier used for structured chat completions (default ``gpt-4o``).
    """

    def __init__(
        self,
        api_key: str,
        *,
        transcription_model: str = "whisper-1",
        chat_model: str = "gpt-4o",
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self._transcription_model = transcription_model
        self._chat_model = chat_model

    # ------------------------------------------------------------------
    # Audio transcription
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        reraise=True,
    )
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe raw audio bytes using OpenAI Whisper.

        Parameters
        ----------
        audio_data:
            Raw audio bytes (typically Opus-encoded OGG from Telegram).
        """
        logger.debug("Transcribing %d bytes of audio", len(audio_data))
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.ogg"
        transcript = await self.client.audio.transcriptions.create(
            model=self._transcription_model,
            file=audio_file,
            language="es",
        )
        logger.info("Transcription complete (%d chars)", len(transcript.text))
        return transcript.text

    # ------------------------------------------------------------------
    # Text interpretation (structured extraction)
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        reraise=True,
    )
    async def interpret_text(self, text: str, context: dict) -> list[dict]:
        """Extract operational events from free-form *text*.

        Uses OpenAI Structured Outputs (``response_format``) to guarantee
        that the response conforms to :class:`LLMEventExtractionResponse`.

        Parameters
        ----------
        text:
            The user message to interpret.
        context:
            Contextual information (known properties, etc.) injected into the
            system prompt.
        """
        system_prompt = get_extraction_system_prompt(context)
        logger.debug("Interpreting text (%d chars) with %s", len(text), self._chat_model)

        completion = await self.client.beta.chat.completions.parse(
            model=self._chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            response_format=LLMEventExtractionResponse,
        )
        result = completion.choices[0].message.parsed
        if result is None:
            logger.warning("LLM returned null parsed result for text interpretation")
            return []

        events = [evt.model_dump() for evt in result.events]
        logger.info("Extracted %d event(s) from text", len(events))
        return events

    # ------------------------------------------------------------------
    # Image interpretation (structured extraction)
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        reraise=True,
    )
    async def interpret_image(
        self,
        image_url: str,
        text: str,
        context: dict,
    ) -> list[dict]:
        """Extract operational events from an image (with optional caption).

        Parameters
        ----------
        image_url:
            A publicly-accessible URL for the image to analyse.
        text:
            Optional caption or accompanying text.  If empty, a default
            instruction is used.
        context:
            Contextual information injected into the system prompt.
        """
        system_prompt = get_extraction_system_prompt(context)
        user_text = text or "Describe what you see and extract any operational events."

        logger.debug("Interpreting image with %s", self._chat_model)

        completion = await self.client.beta.chat.completions.parse(
            model=self._chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
            response_format=LLMEventExtractionResponse,
        )
        result = completion.choices[0].message.parsed
        if result is None:
            logger.warning("LLM returned null parsed result for image interpretation")
            return []

        events = [evt.model_dump() for evt in result.events]
        logger.info("Extracted %d event(s) from image", len(events))
        return events

    # ------------------------------------------------------------------
    # Image analysis (free-form description for condition reports)
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        reraise=True,
    )
    async def analyze_image(self, image_data: bytes, prompt: str) -> str:
        """Analyze an image and return a free-form text description.

        Converts raw bytes to a base64 data URL and uses GPT-4o vision.

        Parameters
        ----------
        image_data:
            Raw image bytes (JPEG/PNG).
        prompt:
            Instruction for what to describe in the image.
        """
        b64 = base64.b64encode(image_data).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"

        logger.debug("Analyzing image (%d bytes) with %s", len(image_data), self._chat_model)

        completion = await self.client.chat.completions.create(
            model=self._chat_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            max_tokens=500,
        )
        description = completion.choices[0].message.content or ""
        logger.info("Image analysis complete (%d chars)", len(description))
        return description

    # ------------------------------------------------------------------
    # Condition report generation (structured output)
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        reraise=True,
    )
    async def generate_condition_report(
        self,
        transcriptions: list[str],
        photo_analyses: list[str],
        context: dict,
    ) -> dict:
        """Generate a structured condition report from collected data.

        Parameters
        ----------
        transcriptions:
            List of audio transcription texts.
        photo_analyses:
            List of image analysis descriptions.
        context:
            Property context (name, inventory items).
        """
        system_prompt = get_condition_report_system_prompt(context)

        # Build user message combining all transcriptions and photo analyses
        parts: list[str] = []
        if transcriptions:
            parts.append("TRANSCRIPCIONES DE AUDIO:")
            for i, t in enumerate(transcriptions, 1):
                parts.append(f"  Audio {i}: {t}")

        if photo_analyses:
            parts.append("\nANÁLISIS DE FOTOS:")
            for i, a in enumerate(photo_analyses, 1):
                parts.append(f"  Foto {i}: {a}")

        user_message = "\n".join(parts) or "Sin contenido proporcionado."

        logger.debug("Generating condition report with %s", self._chat_model)

        completion = await self.client.beta.chat.completions.parse(
            model=self._chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format=ConditionReportResponse,
        )
        result = completion.choices[0].message.parsed
        if result is None:
            logger.warning("LLM returned null parsed result for condition report")
            return {
                "inventory": [],
                "damages": [],
                "general_condition": "fair",
                "summary": "No se pudo generar el reporte.",
                "operational_events": [],
            }

        logger.info(
            "Condition report generated: %d inventory items, %d damages, %d events",
            len(result.inventory),
            len(result.damages),
            len(result.operational_events),
        )
        return result.model_dump()
