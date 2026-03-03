"""Event handler registration and public exports.

All concrete handlers and the abstract base class are re-exported here
for convenient import.  ``register_all_handlers`` wires every handler
into the provided ``EventEngine``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.domain.entities.event import EventType
from app.infrastructure.db.repositories.incident_repository import IncidentRepository
from app.infrastructure.db.repositories.inventory_repository import InventoryRepository
from app.infrastructure.db.repositories.laundry_repository import LaundryRepository
from app.services.handlers.base import AbstractEventHandler
from app.services.handlers.incident_handler import (
    HANDLED_EVENT_TYPES as INCIDENT_EVENTS,
    IncidentHandler,
)
from app.services.handlers.inventory_handler import (
    HANDLED_EVENT_TYPES as INVENTORY_EVENTS,
    InventoryHandler,
)
from app.services.handlers.laundry_handler import (
    HANDLED_EVENT_TYPES as LAUNDRY_EVENTS,
    LaundryHandler,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from app.services.event_engine import EventEngine

logger = logging.getLogger(__name__)

__all__ = [
    "AbstractEventHandler",
    "IncidentHandler",
    "InventoryHandler",
    "LaundryHandler",
    "register_all_handlers",
]


def register_all_handlers(
    engine: EventEngine,
    *,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Instantiate all domain handlers and register them with *engine*.

    This function is the single wiring point invoked during application
    startup.  Each handler receives the ``session_factory`` so it can
    create fresh database sessions per event dispatch (avoiding stale
    sessions from startup).
    """
    # -- Incident handler ---------------------------------------------------- #
    incident_handler = IncidentHandler(
        session_factory=session_factory,
        repo_factory=lambda s: IncidentRepository(s),
    )
    for event_type in INCIDENT_EVENTS:
        engine.register(event_type, incident_handler)

    # -- Inventory handler --------------------------------------------------- #
    inventory_handler = InventoryHandler(
        session_factory=session_factory,
        repo_factory=lambda s: InventoryRepository(s),
    )
    for event_type in INVENTORY_EVENTS:
        engine.register(event_type, inventory_handler)

    # -- Laundry handler ----------------------------------------------------- #
    laundry_handler = LaundryHandler(
        session_factory=session_factory,
        repo_factory=lambda s: LaundryRepository(s),
    )
    for event_type in LAUNDRY_EVENTS:
        engine.register(event_type, laundry_handler)

    logger.info(
        "Registered %d handler(s) across %d event type(s)",
        3,
        len(INCIDENT_EVENTS | INVENTORY_EVENTS | LAUNDRY_EVENTS),
    )
