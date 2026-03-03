from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class EntityRef(BaseModel, frozen=True):
    """Lightweight, immutable reference to a domain entity.

    Used when a full entity load is unnecessary but the caller still
    needs to know *which* entity and of *what kind* is being referenced
    (e.g. inside event payloads or notification messages).
    """

    entity_type: str
    entity_id: UUID
    display_name: str
