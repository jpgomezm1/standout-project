"""Central event dispatcher for domain events.

The ``EventEngine`` maintains a registry of ``AbstractEventHandler``
instances keyed by ``EventType``.  When an ``OperationalEvent`` is
dispatched, the engine invokes every registered handler for that event
type sequentially.  A failure in one handler is logged but never blocks
subsequent handlers from executing.
"""

from __future__ import annotations

import logging
from collections import defaultdict

from app.domain.entities.event import EventType, OperationalEvent
from app.services.handlers.base import AbstractEventHandler

logger = logging.getLogger(__name__)


class EventEngine:
    """In-process pub-sub engine for ``OperationalEvent`` instances."""

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[AbstractEventHandler]] = defaultdict(list)

    # -- Registration -------------------------------------------------------- #

    def register(self, event_type: EventType, handler: AbstractEventHandler) -> None:
        """Register *handler* to be invoked when *event_type* is dispatched."""
        self._handlers[event_type].append(handler)
        logger.debug(
            "Registered handler %s for event type '%s'",
            handler.__class__.__name__,
            event_type.value,
        )

    # -- Dispatch ------------------------------------------------------------ #

    async def dispatch(self, event: OperationalEvent) -> None:
        """Dispatch *event* to all handlers registered for its type.

        Handlers execute sequentially.  Each handler is wrapped in its own
        try/except so that a single failure does not prevent the remaining
        handlers from running.
        """
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            logger.warning(
                "No handlers registered for event type '%s' (event id=%s)",
                event.event_type.value,
                event.id,
            )
            return

        logger.info(
            "Dispatching event '%s' (id=%s) to %d handler(s)",
            event.event_type.value,
            event.id,
            len(handlers),
        )

        for handler in handlers:
            try:
                await handler.handle(event)
            except Exception:
                logger.exception(
                    "Handler %s failed for event %s (type=%s)",
                    handler.__class__.__name__,
                    event.id,
                    event.event_type.value,
                )
                # Never block other handlers
