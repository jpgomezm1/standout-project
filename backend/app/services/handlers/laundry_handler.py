"""Event handler for the laundry flow lifecycle.

Creates ``LaundryFlow`` records when items are sent to laundry, and
transitions them through the ``LaundryStatus`` state machine as return /
loss events arrive.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable, Optional
from uuid import UUID, uuid4

from app.domain.entities.event import EventType, OperationalEvent
from app.domain.entities.laundry import LaundryFlow, LaundryStatus
from app.services.handlers.base import AbstractEventHandler

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from app.domain.interfaces.repositories import ILaundryRepository

logger = logging.getLogger(__name__)

# Maps event types to the ``LaundryStatus`` they transition a flow into.
_STATUS_TRANSITION_MAP: dict[EventType, LaundryStatus] = {
    EventType.ITEM_RETURNED_FROM_LAUNDRY: LaundryStatus.RETURNED,
    EventType.LAUNDRY_RETURNED: LaundryStatus.RETURNED,
    EventType.LAUNDRY_PARTIALLY_RETURNED: LaundryStatus.PARTIALLY_RETURNED,
    EventType.LAUNDRY_LOST: LaundryStatus.LOST,
}

# All event types this handler is registered for.
HANDLED_EVENT_TYPES: frozenset[EventType] = frozenset(
    {EventType.ITEM_SENT_TO_LAUNDRY} | set(_STATUS_TRANSITION_MAP.keys())
)


class LaundryHandler(AbstractEventHandler):
    """Manages ``LaundryFlow`` records in response to laundry events."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repo_factory: Callable[[AsyncSession], ILaundryRepository],
    ) -> None:
        self._session_factory = session_factory
        self._repo_factory = repo_factory

    async def handle(self, event: OperationalEvent) -> None:
        if event.event_type == EventType.ITEM_SENT_TO_LAUNDRY:
            await self._create_flow(event)
        elif event.event_type in _STATUS_TRANSITION_MAP:
            await self._update_flow_status(event)
        else:
            logger.debug(
                "LaundryHandler ignoring unrelated event type '%s'",
                event.event_type.value,
            )

    # -- Internal helpers ---------------------------------------------------- #

    async def _create_flow(self, event: OperationalEvent) -> None:
        """Create a new ``LaundryFlow`` when items are sent to laundry."""
        payload = event.payload
        now = datetime.now(timezone.utc)

        items = payload.get("items", [])
        # If LLM returned item_name/quantity instead of items list, build it
        if not items and payload.get("item_name"):
            qty = int(payload.get("quantity", 1))
            items = [{"name": payload["item_name"], "quantity": qty}]

        total_pieces = payload.get(
            "total_pieces",
            sum(i.get("quantity", 0) for i in items),
        )

        expected_return_raw = payload.get("expected_return_at")
        expected_return_at: Optional[datetime] = None
        if expected_return_raw:
            try:
                expected_return_at = datetime.fromisoformat(str(expected_return_raw))
            except (ValueError, TypeError):
                logger.warning(
                    "Invalid expected_return_at '%s' in event %s; ignoring",
                    expected_return_raw,
                    event.id,
                )

        flow = LaundryFlow(
            id=uuid4(),
            property_id=event.property_id,
            status=LaundryStatus.SENT,
            items=items,
            total_pieces=total_pieces,
            sent_at=now,
            expected_return_at=expected_return_at,
            created_at=now,
            updated_at=now,
        )

        async with self._session_factory() as session:
            repo = self._repo_factory(session)
            stored = await repo.create(flow)
            await session.commit()

        logger.info(
            "Created LaundryFlow %s (pieces=%d) for property %s from event %s",
            stored.id,
            stored.total_pieces,
            stored.property_id,
            event.id,
        )

    async def _update_flow_status(self, event: OperationalEvent) -> None:
        """Transition an existing ``LaundryFlow`` to a new status.

        If ``laundry_flow_id`` is present in the payload, it is used directly.
        Otherwise the handler looks up the most recent open flow for the
        property, which covers the common Telegram-driven scenario where the
        user simply says "devolvieron las toallas del Penthouse".
        """
        flow_id_raw = event.payload.get("laundry_flow_id")

        async with self._session_factory() as session:
            repo = self._repo_factory(session)

            flow = None
            if flow_id_raw:
                try:
                    flow_id = UUID(str(flow_id_raw))
                except ValueError:
                    logger.error(
                        "Invalid laundry_flow_id '%s' in event %s payload",
                        flow_id_raw,
                        event.id,
                    )
                    return
                flow = await repo.get_by_id(flow_id)
            else:
                # Fallback: find the most recent open flow for the property
                flow = await repo.get_latest_open_by_property(event.property_id)
                if flow:
                    logger.info(
                        "No laundry_flow_id in event %s; matched latest open flow %s",
                        event.id,
                        flow.id,
                    )

            if flow is None:
                logger.warning(
                    "No matching LaundryFlow found for event %s (property %s)",
                    event.id,
                    event.property_id,
                )
                return

            new_status = _STATUS_TRANSITION_MAP[event.event_type]
            now = datetime.now(timezone.utc)

            # For return events, accumulate quantities across all returns
            # to decide if the full batch is back or just a partial return.
            if new_status == LaundryStatus.RETURNED:
                returned_qty = int(event.payload.get("quantity", 0))

                # Sum ALL previous return-type events for this property
                # since the flow was sent (covers both ITEM_RETURNED_FROM_LAUNDRY
                # and LAUNDRY_RETURNED events).
                from app.infrastructure.db.repositories.event_repository import EventRepository
                event_repo = EventRepository(session)
                all_events = await event_repo.get_by_property(
                    property_id=event.property_id, limit=200
                )

                return_event_types = {
                    "ITEM_RETURNED_FROM_LAUNDRY",
                    "LAUNDRY_RETURNED",
                    "LAUNDRY_PARTIALLY_RETURNED",
                }
                previously_returned = 0
                for e in all_events:
                    if e.id == event.id:
                        continue
                    if e.event_type.value not in return_event_types:
                        continue
                    # Only count events after this flow was sent
                    if e.created_at.replace(tzinfo=None) < flow.sent_at.replace(tzinfo=None):
                        continue
                    previously_returned += int(e.payload.get("quantity", 0))

                total_returned = previously_returned + returned_qty
                logger.info(
                    "Return calculation for flow %s: current=%d + previous=%d = %d of %d total_pieces",
                    flow.id, returned_qty, previously_returned, total_returned, flow.total_pieces,
                )

                if total_returned >= flow.total_pieces:
                    new_status = LaundryStatus.RETURNED
                elif total_returned > 0:
                    new_status = LaundryStatus.PARTIALLY_RETURNED
                # If total_returned == 0 and no quantity info, keep RETURNED
                # (the LLM explicitly said it's returned)

            update_fields: dict = {"status": new_status, "updated_at": now}
            if new_status == LaundryStatus.RETURNED:
                update_fields["returned_at"] = now

            updated_flow = flow.model_copy(update=update_fields)
            stored = await repo.update(updated_flow)
            await session.commit()

        logger.info(
            "Updated LaundryFlow %s to status '%s' from event %s",
            stored.id,
            new_status.value,
            event.id,
        )
