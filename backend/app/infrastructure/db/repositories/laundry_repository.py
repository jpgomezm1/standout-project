"""PostgreSQL-backed implementation of :class:`ILaundryRepository`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.laundry import LaundryFlow, LaundryStatus
from app.domain.interfaces.repositories import ILaundryRepository
from app.infrastructure.db.models.laundry_flow import LaundryFlowModel


class LaundryRepository(ILaundryRepository):
    """Async SQLAlchemy adapter for laundry-flow persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Mapping helpers -----------------------------------------------------

    @staticmethod
    def _to_domain(model: LaundryFlowModel) -> LaundryFlow:
        return LaundryFlow(
            id=model.id,
            property_id=model.property_id,
            status=LaundryStatus(model.status.upper()),
            items=model.items or [],
            total_pieces=model.total_pieces,
            sent_at=model.sent_at,
            expected_return_at=model.expected_return_at,
            returned_at=model.returned_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: LaundryFlow) -> LaundryFlowModel:
        return LaundryFlowModel(
            id=entity.id,
            property_id=entity.property_id,
            status=entity.status.value.lower(),
            items=entity.items,
            total_pieces=entity.total_pieces,
            sent_at=entity.sent_at,
            expected_return_at=entity.expected_return_at,
            returned_at=entity.returned_at,
        )

    # -- Interface implementation --------------------------------------------

    async def get_by_property(
        self,
        property_id: UUID,
        status: LaundryStatus | None = None,
    ) -> list[LaundryFlow]:
        stmt = (
            select(LaundryFlowModel)
            .where(LaundryFlowModel.property_id == property_id)
            .order_by(LaundryFlowModel.sent_at.desc())
        )
        if status is not None:
            stmt = stmt.where(LaundryFlowModel.status == status.value.lower())

        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_latest_open_by_property(self, property_id: UUID) -> LaundryFlow | None:
        """Return the most recent non-terminal flow for a property."""
        stmt = (
            select(LaundryFlowModel)
            .where(LaundryFlowModel.property_id == property_id)
            .where(LaundryFlowModel.status.in_(["sent", "in_progress", "partially_returned"]))
            .order_by(LaundryFlowModel.sent_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_by_id(self, id: UUID) -> LaundryFlow | None:
        model = await self._session.get(LaundryFlowModel, id)
        return self._to_domain(model) if model else None

    async def create(self, flow: LaundryFlow) -> LaundryFlow:
        model = self._to_model(flow)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def update(self, flow: LaundryFlow) -> LaundryFlow:
        model = await self._session.get(LaundryFlowModel, flow.id)
        if model is None:
            raise ValueError(f"LaundryFlow {flow.id} not found")

        model.status = flow.status.value.lower()
        model.items = flow.items
        model.total_pieces = flow.total_pieces
        model.expected_return_at = flow.expected_return_at
        model.returned_at = flow.returned_at

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)
