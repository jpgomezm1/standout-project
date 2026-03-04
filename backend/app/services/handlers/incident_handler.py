"""Event handler that manages the incident lifecycle.

Reacts to creation events (``ITEM_BROKEN``, ``ITEM_MISSING``,
``MAINTENANCE_ISSUE``) by opening new incidents, and to status-transition
events (``INCIDENT_ACKNOWLEDGED``, ``INCIDENT_IN_PROGRESS``,
``INCIDENT_RESOLVED``) by updating existing incident records.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable
from uuid import UUID, uuid4

from app.domain.entities.event import EventType, OperationalEvent
from app.domain.entities.incident import Incident, IncidentPriority, IncidentStatus
from app.services.handlers.base import AbstractEventHandler

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from app.domain.interfaces.repositories import IIncidentRepository

logger = logging.getLogger(__name__)

# Maps creation event types to their default incident priority.
_EVENT_PRIORITY_MAP: dict[EventType, IncidentPriority] = {
    EventType.ITEM_BROKEN: IncidentPriority.HIGH,
    EventType.ITEM_MISSING: IncidentPriority.MEDIUM,
    EventType.MAINTENANCE_ISSUE: IncidentPriority.MEDIUM,
}

# Maps creation event types to a human-readable incident type label.
_EVENT_INCIDENT_TYPE_MAP: dict[EventType, str] = {
    EventType.ITEM_BROKEN: "broken_item",
    EventType.ITEM_MISSING: "missing_item",
    EventType.MAINTENANCE_ISSUE: "maintenance",
}

# Human-readable title prefixes per event type.
_EVENT_TITLE_MAP: dict[EventType, str] = {
    EventType.ITEM_BROKEN: "Ítem roto",
    EventType.ITEM_MISSING: "Ítem faltante",
    EventType.MAINTENANCE_ISSUE: "Problema de mantenimiento",
}

# Maps status-transition event types to the target ``IncidentStatus``.
_STATUS_TRANSITION_MAP: dict[EventType, IncidentStatus] = {
    EventType.INCIDENT_ACKNOWLEDGED: IncidentStatus.ACKNOWLEDGED,
    EventType.INCIDENT_IN_PROGRESS: IncidentStatus.IN_PROGRESS,
    EventType.INCIDENT_RESOLVED: IncidentStatus.RESOLVED,
}

# Union of all event types this handler cares about.
HANDLED_EVENT_TYPES: frozenset[EventType] = frozenset(
    list(_EVENT_PRIORITY_MAP.keys()) + list(_STATUS_TRANSITION_MAP.keys())
)


class IncidentHandler(AbstractEventHandler):
    """Creates and updates incidents in response to operational events."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repo_factory: Callable[[AsyncSession], IIncidentRepository],
    ) -> None:
        self._session_factory = session_factory
        self._repo_factory = repo_factory

    async def handle(self, event: OperationalEvent) -> None:
        if event.event_type in _EVENT_PRIORITY_MAP:
            await self._create_incident(event)
        elif event.event_type in _STATUS_TRANSITION_MAP:
            await self._update_incident_status(event)
        else:
            logger.debug(
                "IncidentHandler ignoring unrelated event type '%s'",
                event.event_type.value,
            )

    # -- Internal helpers ---------------------------------------------------- #

    async def _create_incident(self, event: OperationalEvent) -> None:
        """Open a new incident from a creation event."""
        payload = event.payload
        now = datetime.now(timezone.utc)

        priority_override = payload.get("priority")
        if priority_override:
            try:
                priority = IncidentPriority(priority_override)
            except ValueError:
                priority = _EVENT_PRIORITY_MAP[event.event_type]
        else:
            priority = _EVENT_PRIORITY_MAP[event.event_type]

        # Build a human-readable title from the payload
        default_prefix = _EVENT_TITLE_MAP.get(event.event_type, event.event_type.value)
        item_name = payload.get("item_name", "")
        property_name = payload.get("property_name", "")
        quantity = payload.get("quantity", "")

        if item_name and property_name:
            qty_int = int(quantity) if quantity else 1
            if qty_int > 1:
                # Simple Spanish pluralization
                if item_name.endswith(("a", "e", "i", "o", "u")):
                    plural_name = item_name + "s"
                else:
                    plural_name = item_name + "es"
                default_title = f"{default_prefix}: {qty_int} {plural_name} en {property_name}"
            else:
                default_title = f"{default_prefix}: {item_name} en {property_name}"
        elif property_name:
            default_title = f"{default_prefix} en {property_name}"
        else:
            default_title = default_prefix

        incident = Incident(
            id=uuid4(),
            property_id=event.property_id,
            incident_type=_EVENT_INCIDENT_TYPE_MAP[event.event_type],
            title=payload.get("title", default_title),
            description=payload.get("description", ""),
            status=IncidentStatus.OPEN,
            priority=priority,
            reported_by=event.actor_id,
            created_at=now,
            updated_at=now,
        )

        async with self._session_factory() as session:
            repo = self._repo_factory(session)
            stored = await repo.create(incident)
            await session.commit()

        logger.info(
            "Created incident %s (type=%s, priority=%s) from event %s",
            stored.id,
            stored.incident_type,
            stored.priority.value,
            event.id,
        )

    async def _update_incident_status(self, event: OperationalEvent) -> None:
        """Transition an existing incident to a new status.

        If ``incident_id`` is present in the payload it is used directly.
        Otherwise the handler looks up the most recent open incident for the
        property, optionally matching by item name — this covers the common
        Telegram-driven scenario where the user says "ya repusieron el plato
        del Penthouse".
        """
        incident_id_raw = event.payload.get("incident_id")

        new_status = _STATUS_TRANSITION_MAP[event.event_type]
        resolved_at = (
            datetime.now(timezone.utc)
            if new_status == IncidentStatus.RESOLVED
            else None
        )

        async with self._session_factory() as session:
            repo = self._repo_factory(session)

            if incident_id_raw:
                try:
                    incident_id = UUID(str(incident_id_raw))
                except ValueError:
                    logger.error(
                        "Invalid incident_id '%s' in event %s payload",
                        incident_id_raw,
                        event.id,
                    )
                    return

                updated = await repo.update_status(
                    incident_id, new_status, resolved_at=resolved_at
                )
            else:
                # Fallback: find the most recent open incident for this property
                item_name = event.payload.get("item_name")
                incident = await repo.get_latest_open_by_property(
                    event.property_id, item_name=item_name
                )
                if incident is None:
                    logger.warning(
                        "No matching open incident for property %s (item=%s) "
                        "from event %s",
                        event.property_id,
                        item_name,
                        event.id,
                    )
                    return

                logger.info(
                    "No incident_id in event %s; matched open incident %s ('%s')",
                    event.id,
                    incident.id,
                    incident.title,
                )
                updated = await repo.update_status(
                    incident.id, new_status, resolved_at=resolved_at
                )

            await session.commit()

        if updated is None:
            logger.warning(
                "Incident not found when processing event %s",
                event.id,
            )
            return

        logger.info(
            "Updated incident %s to status '%s' from event %s",
            updated.id,
            new_status.value,
            event.id,
        )
