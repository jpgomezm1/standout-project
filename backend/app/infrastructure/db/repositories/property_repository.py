"""PostgreSQL-backed implementation of :class:`IPropertyRepository`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Text, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.property import Property
from app.domain.interfaces.repositories import IPropertyRepository
from app.infrastructure.db.models.property import PropertyModel


class PropertyRepository(IPropertyRepository):
    """Async SQLAlchemy adapter for property persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Mapping helpers -----------------------------------------------------

    @staticmethod
    def _to_domain(model: PropertyModel) -> Property:
        return Property(
            id=model.id,
            name=model.name,
            address=model.address or "",
            timezone=model.timezone,
            aliases=model.aliases or [],
            housekeepers_needed=model.housekeepers_needed,
            is_active=model.is_active,
            metadata=model.metadata_ or {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: Property) -> PropertyModel:
        return PropertyModel(
            id=entity.id,
            name=entity.name,
            address=entity.address,
            timezone=entity.timezone,
            aliases=entity.aliases,
            housekeepers_needed=entity.housekeepers_needed,
            is_active=entity.is_active,
            metadata_=entity.metadata,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    # -- Interface implementation --------------------------------------------

    async def get_all(self) -> list[Property]:
        stmt = select(PropertyModel).where(PropertyModel.is_active.is_(True))
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_id(self, id: UUID) -> Property | None:
        model = await self._session.get(PropertyModel, id)
        return self._to_domain(model) if model else None

    async def create(self, property: Property) -> Property:
        model = self._to_model(property)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def search_by_name(self, query: str) -> list[Property]:
        """ILIKE search on ``name`` and a JSONB text-containment check on ``aliases``.

        The aliases column is a JSONB array of strings.  We cast it to text
        and use ILIKE so that a query like ``"apto 93"`` matches an alias
        such as ``"el apto de la 93"``.
        """
        pattern = f"%{query}%"
        stmt = select(PropertyModel).where(
            or_(
                PropertyModel.name.ilike(pattern),
                # Cast the JSONB array to text and do a case-insensitive search.
                PropertyModel.aliases.cast(Text).ilike(pattern),
            )
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]
