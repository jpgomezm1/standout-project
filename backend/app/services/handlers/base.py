"""Abstract base class for all domain event handlers.

Every concrete handler inherits from ``AbstractEventHandler`` and implements
the ``handle`` method.  The event engine invokes handlers through this
uniform interface, ensuring that handler discovery and dispatch remain
decoupled from specific business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.event import OperationalEvent


class AbstractEventHandler(ABC):
    """Base class for event handlers dispatched by the ``EventEngine``."""

    @abstractmethod
    async def handle(self, event: OperationalEvent) -> None:
        """Process a single operational event.

        Implementations **must not** propagate exceptions that should be
        silently swallowed; the engine will log and continue for unhandled
        errors, but handlers should manage their own error semantics when
        possible.
        """
        ...
