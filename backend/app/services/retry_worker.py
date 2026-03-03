"""Background retry worker for messages stuck in ``PENDING_RETRY`` status.

Runs as a long-lived ``asyncio.Task`` started during the application
lifespan.  On each cycle it queries for retryable messages and re-submits
them through the ``IngestService`` pipeline.  A failure in one message
does not prevent others from being retried.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from app.domain.interfaces.repositories import IRawMessageRepository

if TYPE_CHECKING:
    from app.services.ingest_service import IngestService

logger = logging.getLogger(__name__)

_DEFAULT_POLL_INTERVAL_SECONDS: int = 60


class RetryWorker:
    """Periodically retries messages that previously failed processing."""

    def __init__(
        self,
        raw_message_repo: IRawMessageRepository,
        ingest_service: IngestService,
        *,
        interval: int = _DEFAULT_POLL_INTERVAL_SECONDS,
    ) -> None:
        self._raw_message_repo = raw_message_repo
        self._ingest_service = ingest_service
        self._interval = interval
        self._running: bool = False

    @property
    def is_running(self) -> bool:
        """Return ``True`` if the worker loop is currently active."""
        return self._running

    async def start(self) -> None:
        """Begin the retry loop.

        This coroutine runs indefinitely until ``stop`` is called or the
        task is cancelled.  It is designed to be wrapped in an
        ``asyncio.Task`` and cancelled on application shutdown.
        """
        self._running = True
        logger.info(
            "RetryWorker started (poll_interval=%ds)", self._interval
        )

        while self._running:
            try:
                await self._retry_cycle()
            except asyncio.CancelledError:
                logger.info("RetryWorker cancelled — shutting down")
                self._running = False
                raise
            except Exception:
                logger.exception("RetryWorker cycle failed; will retry next cycle")

            await asyncio.sleep(self._interval)

    def stop(self) -> None:
        """Signal the retry loop to stop after the current cycle."""
        self._running = False
        logger.info("RetryWorker stop requested")

    # -- Internal ------------------------------------------------------------ #

    async def _retry_cycle(self) -> None:
        """Run a single retry cycle: fetch and re-process pending messages."""
        messages = await self._raw_message_repo.get_pending_retry()
        if not messages:
            return

        logger.info(
            "RetryWorker found %d message(s) to retry", len(messages)
        )

        for msg in messages:
            try:
                await self._ingest_service.process_message(msg.id)
                logger.info("Retry succeeded for message %s", msg.id)
            except Exception:
                logger.exception("Retry failed for message %s", msg.id)
