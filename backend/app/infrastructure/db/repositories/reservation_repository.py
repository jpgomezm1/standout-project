"""PostgreSQL-backed implementation of :class:`IReservationRepository`."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.reservation import (
    BookingChannel,
    Reservation,
    ReservationStatus,
)
from app.domain.interfaces.repositories import IReservationRepository
from app.infrastructure.db.models.reservation import ReservationModel


class ReservationRepository(IReservationRepository):
    """Async SQLAlchemy adapter for reservation persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Mapping helpers -----------------------------------------------------

    @staticmethod
    def _to_domain(model: ReservationModel) -> Reservation:
        return Reservation(
            id=model.id,
            property_id=model.property_id,
            guest_name=model.guest_name,
            check_in=model.check_in,
            check_out=model.check_out,
            status=ReservationStatus(model.status.upper()),
            num_guests=model.num_guests,
            channel=BookingChannel(model.channel.upper()),
            internal_notes=model.internal_notes or "",
            amount=model.amount,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: Reservation) -> ReservationModel:
        return ReservationModel(
            id=entity.id,
            property_id=entity.property_id,
            guest_name=entity.guest_name,
            check_in=entity.check_in,
            check_out=entity.check_out,
            status=entity.status.value.lower(),
            num_guests=entity.num_guests,
            channel=entity.channel.value.lower(),
            internal_notes=entity.internal_notes or None,
            amount=entity.amount,
        )

    # -- Interface implementation --------------------------------------------

    async def get_by_property(
        self,
        property_id: UUID,
        status: ReservationStatus | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Reservation]:
        stmt = (
            select(ReservationModel)
            .where(ReservationModel.property_id == property_id)
            .order_by(ReservationModel.check_in.asc())
        )

        if status is not None:
            stmt = stmt.where(ReservationModel.status == status.value.lower())

        # Overlap query for calendar: check_in <= to_date AND check_out >= from_date
        if from_date is not None:
            stmt = stmt.where(ReservationModel.check_out >= from_date)
        if to_date is not None:
            stmt = stmt.where(ReservationModel.check_in <= to_date)

        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_id(self, id: UUID) -> Reservation | None:
        model = await self._session.get(ReservationModel, id)
        return self._to_domain(model) if model else None

    async def create(self, reservation: Reservation) -> Reservation:
        model = self._to_model(reservation)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)
