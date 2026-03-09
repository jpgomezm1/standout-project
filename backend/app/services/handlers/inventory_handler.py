"""Event handler for inventory tracking.

Inventory state is derived from the event log (event-sourced), so this
handler primarily validates that referenced items exist and logs the
operation.  Future iterations may trigger real-time notifications on
``LOW_STOCK_ALERT`` events.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable
from uuid import UUID

from app.domain.entities.event import EventType, OperationalEvent
from app.domain.entities.incident import IncidentStatus
from app.services.handlers.base import AbstractEventHandler

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from app.domain.interfaces.repositories import IInventoryRepository

logger = logging.getLogger(__name__)

# Event types this handler is responsible for.
HANDLED_EVENT_TYPES: frozenset[EventType] = frozenset(
    {
        EventType.ITEM_BROKEN,
        EventType.ITEM_MISSING,
        EventType.ITEM_REPLACED,
        EventType.LOW_STOCK_ALERT,
    }
)


class InventoryHandler(AbstractEventHandler):
    """Validates inventory-related events and logs them for auditability.

    Because inventory quantities are derived by replaying the event log,
    this handler does not mutate counts directly.  Its role is to validate
    that the referenced item exists and to record operational logs that
    downstream projections and notifications can rely on.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repo_factory: Callable[[AsyncSession], IInventoryRepository],
    ) -> None:
        self._session_factory = session_factory
        self._repo_factory = repo_factory

    async def handle(self, event: OperationalEvent) -> None:
        if event.event_type in (EventType.ITEM_BROKEN, EventType.ITEM_MISSING, EventType.ITEM_REPLACED):
            await self._validate_item(event)
            if event.event_type == EventType.ITEM_REPLACED:
                await self._update_incident_on_replacement(event)
        elif event.event_type == EventType.LOW_STOCK_ALERT:
            await self._handle_low_stock_alert(event)
        else:
            logger.debug(
                "InventoryHandler ignoring unrelated event type '%s'",
                event.event_type.value,
            )

    # -- Internal helpers ---------------------------------------------------- #

    async def _validate_item(self, event: OperationalEvent) -> None:
        """Validate that the item referenced in the event payload exists."""
        item_id_raw = event.payload.get("item_id")
        if not item_id_raw:
            logger.warning(
                "Inventory event %s (type=%s) has no 'item_id' in payload; "
                "skipping validation",
                event.id,
                event.event_type.value,
            )
            return

        try:
            item_id = UUID(str(item_id_raw))
        except ValueError:
            logger.error(
                "Invalid item_id '%s' in event %s payload",
                item_id_raw,
                event.id,
            )
            return

        async with self._session_factory() as session:
            repo = self._repo_factory(session)
            item = await repo.get_by_id(item_id)

        if item is None:
            logger.warning(
                "Item %s referenced in event %s not found in inventory",
                item_id,
                event.id,
            )
            return

        logger.info(
            "Inventory event recorded: item '%s' (%s) — event type '%s', event id %s",
            item.item_name,
            item.id,
            event.event_type.value,
            event.id,
        )

    async def _update_incident_on_replacement(self, event: OperationalEvent) -> None:
        """When an item is replaced, update the related incident status.

        Finds the most recent open/acknowledged incident for the same property
        and item, then transitions it to IN_PROGRESS (partial replacement).
        """
        from app.infrastructure.db.repositories.incident_repository import IncidentRepository

        item_name = event.payload.get("item_name")
        if not item_name:
            return

        async with self._session_factory() as session:
            repo = IncidentRepository(session)
            incident = await repo.get_latest_open_by_property(
                event.property_id, item_name=item_name
            )
            if incident is None:
                return

            # Only update if it's still OPEN or ACKNOWLEDGED
            if incident.status in (IncidentStatus.OPEN, IncidentStatus.ACKNOWLEDGED):
                await repo.update_status(incident.id, IncidentStatus.IN_PROGRESS)
                await session.commit()
                logger.info(
                    "Incident %s moved to IN_PROGRESS after partial replacement "
                    "of '%s' (event %s)",
                    incident.id,
                    item_name,
                    event.id,
                )

    async def _handle_low_stock_alert(self, event: OperationalEvent) -> None:
        """Log a low-stock alert for future notification integration."""
        item_id_raw = event.payload.get("item_id")
        current_qty = event.payload.get("current_quantity", "unknown")

        logger.warning(
            "LOW_STOCK_ALERT for property %s — item_id=%s, current_quantity=%s "
            "(event id=%s).  TODO: send notification.",
            event.property_id,
            item_id_raw,
            current_qty,
            event.id,
        )
