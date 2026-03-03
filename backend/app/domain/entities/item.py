from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ItemCategory(str, Enum):
    """High-level category for inventory items."""

    LINEN = "LINEN"
    TOWEL = "TOWEL"
    KITCHEN = "KITCHEN"
    BATHROOM = "BATHROOM"
    FURNITURE = "FURNITURE"
    ELECTRONIC = "ELECTRONIC"
    OTHER = "OTHER"


class InventoryItem(BaseModel):
    """A tracked inventory item within a property.

    ``expected_quantity`` is the baseline count that the property should
    maintain.  ``low_stock_threshold`` triggers a LOW_STOCK_ALERT event
    when the derived current quantity drops below this level.
    """

    id: UUID
    property_id: UUID
    item_name: str
    category: ItemCategory
    expected_quantity: int
    low_stock_threshold: int
    created_at: datetime
    updated_at: datetime
