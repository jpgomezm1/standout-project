from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Property(BaseModel):
    """A managed hospitality property (apartment, house, hotel, etc.).

    Each property has a canonical name, a physical address, and an
    IANA timezone used to localise timestamps for the operations team.
    Aliases allow the NLP layer to match informal property references
    (e.g. "el apto de la 93") to the canonical record.
    """

    id: UUID
    name: str
    address: str
    timezone: str = Field(default="America/Bogota")
    aliases: list[str] = Field(default_factory=list)
    housekeepers_needed: int = 1
    is_active: bool = True
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
