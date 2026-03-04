from __future__ import annotations

from abc import ABC, abstractmethod


class ILLMClient(ABC):
    """Port for large-language-model operations.

    Implementations wrap a specific provider (e.g. OpenAI, Anthropic) and
    expose the two capabilities the domain layer requires: audio
    transcription and free-text interpretation.
    """

    @abstractmethod
    async def transcribe_audio(self, file_path: str) -> str:
        """Transcribe an audio file at *file_path* and return the text."""
        ...

    @abstractmethod
    async def interpret_text(
        self,
        text: str,
        context: dict,
    ) -> list[dict]:
        """Interpret free-form *text* using the given *context*.

        Returns a list of structured interpretation dicts, each representing
        a detected intent / event with its associated confidence score and
        extracted parameters.
        """
        ...

    @abstractmethod
    async def analyze_image(self, image_data: bytes, prompt: str) -> str:
        """Analyze an image and return a free-form text description."""
        ...
