"""Entity resolver — fuzzy-matches free-text names to canonical domain entities.

Uses ``thefuzz`` for string similarity scoring against known property names,
aliases, and inventory item names.  A match is accepted when the similarity
score meets or exceeds the configured threshold (default 80).
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from thefuzz import fuzz, process  # type: ignore[import-untyped]

from app.domain.interfaces.repositories import IInventoryRepository, IPropertyRepository

logger = logging.getLogger(__name__)

# Minimum similarity score (0-100) for a fuzzy match to be accepted.
_DEFAULT_MATCH_THRESHOLD: int = 80


class EntityResolver:
    """Resolves free-text entity names to their canonical IDs.

    Both ``build_context`` and ``resolve`` may hit the database via the
    injected repositories.  Callers should consider caching the context
    dict if it is reused across multiple interpretations within a short
    time window.
    """

    def __init__(
        self,
        property_repo: IPropertyRepository,
        inventory_repo: IInventoryRepository,
        *,
        match_threshold: int = _DEFAULT_MATCH_THRESHOLD,
    ) -> None:
        self._property_repo = property_repo
        self._inventory_repo = inventory_repo
        self._match_threshold = match_threshold

    # -- Context building ---------------------------------------------------- #

    async def build_context(self) -> dict[str, Any]:
        """Return a context dict of known entities for LLM prompt augmentation.

        The returned structure is designed to be injected verbatim into the
        LLM interpretation prompt so the model knows which properties and
        items exist.
        """
        properties = await self._property_repo.get_all()
        return {
            "properties": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "aliases": p.aliases,
                }
                for p in properties
            ],
        }

    # -- Resolution ---------------------------------------------------------- #

    async def resolve(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Attempt to resolve free-text names in *event_data* to entity IDs.

        Currently resolves:
        - ``property_name`` -> ``property_id``
        - ``item_name`` -> ``item_id`` (requires ``property_id`` to be set)

        Returns the (potentially enriched) *event_data* dict.
        """
        event_data = await self._resolve_property(event_data)
        event_data = await self._resolve_item(event_data)
        return event_data

    # -- Property resolution ------------------------------------------------- #

    async def _resolve_property(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Fuzzy-match ``property_name`` to a ``property_id``."""
        if "property_id" in event_data and event_data["property_id"]:
            return event_data

        property_name = event_data.get("property_name")
        if not property_name:
            return event_data

        properties = await self._property_repo.get_all()
        if not properties:
            logger.warning("No properties in database; cannot resolve '%s'", property_name)
            return event_data

        # Build a lookup: display_name -> Property, including aliases.
        name_lookup: dict[str, Any] = {}
        for prop in properties:
            name_lookup[prop.name] = prop
            for alias in prop.aliases:
                name_lookup[alias] = prop

        if not name_lookup:
            return event_data

        match = process.extractOne(
            property_name,
            list(name_lookup.keys()),
            scorer=fuzz.token_sort_ratio,
        )

        if match and match[1] >= self._match_threshold:
            matched_name, score = match[0], match[1]
            resolved_property = name_lookup[matched_name]
            event_data["property_id"] = str(resolved_property.id)
            logger.info(
                "Resolved property_name '%s' -> '%s' (id=%s, score=%d)",
                property_name,
                resolved_property.name,
                resolved_property.id,
                score,
            )
        else:
            best = f" (best: '{match[0]}' score={match[1]})" if match else ""
            logger.info(
                "Could not resolve property_name '%s' above threshold %d%s",
                property_name,
                self._match_threshold,
                best,
            )

        return event_data

    # -- Item resolution ----------------------------------------------------- #

    async def _resolve_item(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Fuzzy-match ``item_name`` to an ``item_id`` within the resolved property."""
        if "item_id" in event_data and event_data["item_id"]:
            return event_data

        item_name = event_data.get("item_name")
        if not item_name:
            return event_data

        property_id_raw = event_data.get("property_id")
        if not property_id_raw:
            logger.debug(
                "Cannot resolve item_name '%s' without a property_id", item_name
            )
            return event_data

        try:
            property_id = UUID(str(property_id_raw))
        except ValueError:
            logger.error("Invalid property_id '%s'; cannot resolve item", property_id_raw)
            return event_data

        items = await self._inventory_repo.get_by_property(property_id)
        if not items:
            logger.warning(
                "No inventory items for property %s; cannot resolve '%s'",
                property_id,
                item_name,
            )
            return event_data

        name_lookup = {item.item_name: item for item in items}

        match = process.extractOne(
            item_name,
            list(name_lookup.keys()),
            scorer=fuzz.token_sort_ratio,
        )

        if match and match[1] >= self._match_threshold:
            matched_name, score = match[0], match[1]
            resolved_item = name_lookup[matched_name]
            event_data["item_id"] = str(resolved_item.id)
            logger.info(
                "Resolved item_name '%s' -> '%s' (id=%s, score=%d)",
                item_name,
                resolved_item.item_name,
                resolved_item.id,
                score,
            )
        else:
            best = f" (best: '{match[0]}' score={match[1]})" if match else ""
            logger.info(
                "Could not resolve item_name '%s' above threshold %d%s",
                item_name,
                self._match_threshold,
                best,
            )

        return event_data
