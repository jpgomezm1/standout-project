from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.event import EventType, OperationalEvent


class IEventStore(ABC):
    """Port for the append-only event store.

    Implementations (e.g. a PostgreSQL-backed adapter) must guarantee
    idempotency based on ``OperationalEvent.idempotency_key``.
    """

    @abstractmethod
    async def append(self, event: OperationalEvent) -> OperationalEvent:
        """Persist a new event and return the stored record."""
        ...

    @abstractmethod
    async def get_by_property(
        self,
        property_id: UUID,
        event_type: EventType | None = None,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[OperationalEvent]:
        """Retrieve events for a property, optionally filtered by type and date."""
        ...

    @abstractmethod
    async def get_by_item(
        self,
        item_id: UUID,
        since: datetime | None = None,
    ) -> list[OperationalEvent]:
        """Retrieve events related to a specific inventory item."""
        ...
