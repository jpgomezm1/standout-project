"""Request/response Pydantic models for inventory endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InventoryItemResponse(BaseModel):
    """Inventory item with its derived current quantity."""

    id: UUID
    property_id: UUID
    item_name: str
    category: str
    expected_quantity: int
    current_quantity: int
    low_stock_threshold: int
    is_low_stock: bool

    model_config = {"from_attributes": True}
