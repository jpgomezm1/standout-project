"""PostgreSQL-backed implementation of :class:`IHousekeepingRepository`."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.housekeeping import AssignmentStatus, HousekeepingAssignment
from app.domain.entities.staff import StaffMember, StaffRole
from app.domain.interfaces.repositories import IHousekeepingRepository
from app.infrastructure.db.models.staff import (
    HousekeepingAssignmentModel,
    StaffMemberModel,
)


class HousekeepingRepository(IHousekeepingRepository):
    """Async SQLAlchemy adapter for housekeeping assignment persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Mapping helpers -----------------------------------------------------

    @staticmethod
    def _to_domain(model: HousekeepingAssignmentModel) -> HousekeepingAssignment:
        return HousekeepingAssignment(
            id=model.id,
            reservation_id=model.reservation_id,
            staff_id=model.staff_id,
            scheduled_date=model.scheduled_date,
            notes=model.notes,
            status=AssignmentStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _staff_to_domain(model: StaffMemberModel) -> StaffMember:
        return StaffMember(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone=model.phone,
            role=StaffRole(model.role.upper()),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # -- Interface implementation --------------------------------------------

    async def get_by_reservation(self, reservation_id: UUID) -> list[HousekeepingAssignment]:
        stmt = (
            select(HousekeepingAssignmentModel)
            .where(HousekeepingAssignmentModel.reservation_id == reservation_id)
            .order_by(HousekeepingAssignmentModel.scheduled_date)
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_property(
        self,
        property_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[tuple[HousekeepingAssignment, str, str]]:
        """Assignments for a property in a date range.

        Returns tuples of (assignment, staff_name, guest_name).
        """
        from app.infrastructure.db.models.reservation import ReservationModel

        stmt = (
            select(HousekeepingAssignmentModel, StaffMemberModel, ReservationModel)
            .join(StaffMemberModel, HousekeepingAssignmentModel.staff_id == StaffMemberModel.id)
            .join(ReservationModel, HousekeepingAssignmentModel.reservation_id == ReservationModel.id)
            .where(
                and_(
                    ReservationModel.property_id == property_id,
                    HousekeepingAssignmentModel.scheduled_date >= start_date,
                    HousekeepingAssignmentModel.scheduled_date <= end_date,
                )
            )
            .order_by(HousekeepingAssignmentModel.scheduled_date)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            (
                self._to_domain(row[0]),
                f"{row[1].first_name} {row[1].last_name}",
                row[2].guest_name,
            )
            for row in rows
        ]

    async def get_by_staff(
        self,
        staff_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[tuple[HousekeepingAssignment, str]]:
        """Assignments for a staff member in a date range.

        Returns tuples of (assignment, property_name).
        """
        from app.infrastructure.db.models.reservation import ReservationModel
        from app.infrastructure.db.models.property import PropertyModel

        stmt = (
            select(HousekeepingAssignmentModel, PropertyModel)
            .join(ReservationModel, HousekeepingAssignmentModel.reservation_id == ReservationModel.id)
            .join(PropertyModel, ReservationModel.property_id == PropertyModel.id)
            .where(
                and_(
                    HousekeepingAssignmentModel.staff_id == staff_id,
                    HousekeepingAssignmentModel.scheduled_date >= start_date,
                    HousekeepingAssignmentModel.scheduled_date <= end_date,
                )
            )
            .order_by(HousekeepingAssignmentModel.scheduled_date)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            (self._to_domain(row[0]), row[1].name)
            for row in rows
        ]

    async def get_all_in_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[tuple[HousekeepingAssignment, str, str]]:
        """All assignments in a date range.

        Returns tuples of (assignment, staff_name, property_name).
        """
        from app.infrastructure.db.models.reservation import ReservationModel
        from app.infrastructure.db.models.property import PropertyModel

        stmt = (
            select(HousekeepingAssignmentModel, StaffMemberModel, PropertyModel)
            .join(StaffMemberModel, HousekeepingAssignmentModel.staff_id == StaffMemberModel.id)
            .join(ReservationModel, HousekeepingAssignmentModel.reservation_id == ReservationModel.id)
            .join(PropertyModel, ReservationModel.property_id == PropertyModel.id)
            .where(
                and_(
                    HousekeepingAssignmentModel.scheduled_date >= start_date,
                    HousekeepingAssignmentModel.scheduled_date <= end_date,
                )
            )
            .order_by(HousekeepingAssignmentModel.scheduled_date)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            (
                self._to_domain(row[0]),
                f"{row[1].first_name} {row[1].last_name}",
                row[2].name,
            )
            for row in rows
        ]

    async def get_available_on_date(
        self,
        target_date: date,
        limit: int | None = None,
    ) -> list[StaffMember]:
        # Subquery: staff_ids that already have a non-cancelled assignment on target_date
        busy_subquery = (
            select(HousekeepingAssignmentModel.staff_id)
            .where(
                and_(
                    HousekeepingAssignmentModel.scheduled_date == target_date,
                    HousekeepingAssignmentModel.status != AssignmentStatus.CANCELLED.value,
                )
            )
        )

        stmt = (
            select(StaffMemberModel)
            .where(
                StaffMemberModel.is_active.is_(True),
                StaffMemberModel.role == "housekeeper",
                StaffMemberModel.id.not_in(busy_subquery),
            )
            .order_by(StaffMemberModel.first_name)
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self._session.execute(stmt)
        return [self._staff_to_domain(row) for row in result.scalars().all()]

    async def create(self, assignment: HousekeepingAssignment) -> HousekeepingAssignment:
        model = HousekeepingAssignmentModel(
            id=assignment.id,
            reservation_id=assignment.reservation_id,
            staff_id=assignment.staff_id,
            scheduled_date=assignment.scheduled_date,
            notes=assignment.notes,
            status=assignment.status.value,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, assignment_id: UUID) -> bool:
        model = await self._session.get(HousekeepingAssignmentModel, assignment_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
