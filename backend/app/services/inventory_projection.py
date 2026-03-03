"""Inventory projection — derives current stock state from the event log.

This service provides read-model queries over inventory data.  Because
item quantities are event-sourced (not stored as mutable counters), this
projection replays the relevant events to compute the current state on
demand.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from app.domain.interfaces.repositories import IInventoryRepository

logger = logging.getLogger(__name__)


class InventoryProjection:
    """Derives current inventory state from the event-sourced store."""

    def __init__(self, inventory_repo: IInventoryRepository) -> None:
        self._inventory_repo = inventory_repo

    async def get_current_stock(self, property_id: UUID) -> list[dict[str, Any]]:
        """Return current quantities for every item at *property_id*.

        Each dict in the returned list contains at least:
        - ``item``: the ``InventoryItem`` entity
        - ``current_quantity``: the derived count
        - ``low_stock_threshold``: from the item definition
        """
        return await self._inventory_repo.get_current_quantities(property_id)

    async def check_low_stock(self, property_id: UUID) -> list[dict[str, Any]]:
        """Return items at *property_id* whose stock is at or below their threshold.

        Useful for generating ``LOW_STOCK_ALERT`` events or dashboard warnings.
        """
        items = await self.get_current_stock(property_id)
        low_stock = [
            item
            for item in items
            if item.get("current_quantity", 0) <= item.get("low_stock_threshold", 0)
        ]

        if low_stock:
            logger.info(
                "Property %s has %d item(s) at or below low-stock threshold",
                property_id,
                len(low_stock),
            )

        return low_stock
