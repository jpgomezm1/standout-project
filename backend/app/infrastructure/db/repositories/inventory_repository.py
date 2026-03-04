"""PostgreSQL-backed implementation of :class:`IInventoryRepository`.

The ``get_current_quantities`` method derives the real-time stock level for
each inventory item by replaying the event log -- the canonical source of
truth in the event-sourced architecture.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Integer, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.item import InventoryItem, ItemCategory
from app.domain.interfaces.repositories import IInventoryRepository
from app.infrastructure.db.models.event import EventModel
from app.infrastructure.db.models.inventory_item import InventoryItemModel


class InventoryRepository(IInventoryRepository):
    """Async SQLAlchemy adapter for inventory persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Mapping helpers -----------------------------------------------------

    @staticmethod
    def _to_domain(model: InventoryItemModel) -> InventoryItem:
        return InventoryItem(
            id=model.id,
            property_id=model.property_id,
            item_name=model.item_name,
            category=ItemCategory(model.category),
            expected_quantity=model.expected_quantity,
            low_stock_threshold=model.low_stock_threshold,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: InventoryItem) -> InventoryItemModel:
        return InventoryItemModel(
            id=entity.id,
            property_id=entity.property_id,
            item_name=entity.item_name,
            category=entity.category.value,
            expected_quantity=entity.expected_quantity,
            low_stock_threshold=entity.low_stock_threshold,
        )

    # -- Interface implementation --------------------------------------------

    async def get_by_property(self, property_id: UUID) -> list[InventoryItem]:
        stmt = select(InventoryItemModel).where(
            InventoryItemModel.property_id == property_id
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_id(self, id: UUID) -> InventoryItem | None:
        model = await self._session.get(InventoryItemModel, id)
        return self._to_domain(model) if model else None

    async def create(self, item: InventoryItem) -> InventoryItem:
        model = self._to_model(item)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_current_quantities(
        self,
        property_id: UUID,
    ) -> list[dict]:
        """Derive current quantities for each item by replaying relevant events.

        The query joins ``inventory_items`` with ``events`` on the same
        property and computes:

        .. code-block:: sql

            current_quantity = expected_quantity + SUM(
                CASE event_type
                    WHEN 'ITEM_BROKEN'                THEN -(payload->>'quantity')::INT
                    WHEN 'ITEM_MISSING'               THEN -(payload->>'quantity')::INT
                    WHEN 'ITEM_SENT_TO_LAUNDRY'       THEN -(payload->>'quantity')::INT
                    WHEN 'ITEM_RETURNED_FROM_LAUNDRY'  THEN  (payload->>'quantity')::INT
                END
            )

        Events are correlated to inventory items via
        ``payload->>'item_name' = inventory_items.item_name``.
        """
        # Build the CASE expression for quantity delta per event type.
        qty_expr = func.coalesce(
            func.sum(
                case(
                    (
                        EventModel.event_type == "ITEM_BROKEN",
                        -func.cast(
                            EventModel.payload["quantity"].astext,
                            Integer,
                        ),
                    ),
                    (
                        EventModel.event_type == "ITEM_MISSING",
                        -func.cast(
                            EventModel.payload["quantity"].astext,
                            Integer,
                        ),
                    ),
                    (
                        EventModel.event_type == "ITEM_SENT_TO_LAUNDRY",
                        -func.cast(
                            EventModel.payload["quantity"].astext,
                            Integer,
                        ),
                    ),
                    (
                        EventModel.event_type == "ITEM_RETURNED_FROM_LAUNDRY",
                        func.cast(
                            EventModel.payload["quantity"].astext,
                            Integer,
                        ),
                    ),
                    (
                        EventModel.event_type == "ITEM_REPLACED",
                        func.cast(
                            EventModel.payload["quantity"].astext,
                            Integer,
                        ),
                    ),
                )
            ),
            0,
        )

        stmt = (
            select(
                InventoryItemModel,
                (InventoryItemModel.expected_quantity + qty_expr).label(
                    "current_quantity"
                ),
            )
            .outerjoin(
                EventModel,
                (EventModel.property_id == InventoryItemModel.property_id)
                & (
                    EventModel.payload["item_name"].astext
                    == InventoryItemModel.item_name
                )
                & (
                    EventModel.event_type.in_(
                        [
                            "ITEM_BROKEN",
                            "ITEM_MISSING",
                            "ITEM_SENT_TO_LAUNDRY",
                            "ITEM_RETURNED_FROM_LAUNDRY",
                            "ITEM_REPLACED",
                        ]
                    )
                ),
            )
            .where(InventoryItemModel.property_id == property_id)
            .group_by(InventoryItemModel.id)
        )

        result = await self._session.execute(stmt)
        rows: list[dict] = []
        for item_model, current_qty in result.all():
            rows.append(
                {
                    "item": self._to_domain(item_model),
                    "current_quantity": current_qty or item_model.expected_quantity,
                }
            )
        return rows
