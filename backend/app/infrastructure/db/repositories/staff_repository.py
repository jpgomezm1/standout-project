"""PostgreSQL-backed implementation of :class:`IStaffRepository`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.staff import StaffMember, StaffRole
from app.domain.interfaces.repositories import IStaffRepository
from app.infrastructure.db.models.staff import (
    PropertyStaffAssignmentModel,
    StaffMemberModel,
)


class StaffRepository(IStaffRepository):
    """Async SQLAlchemy adapter for staff member persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Mapping helpers -----------------------------------------------------

    @staticmethod
    def _to_domain(model: StaffMemberModel) -> StaffMember:
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

    async def get_all(self) -> list[StaffMember]:
        stmt = (
            select(StaffMemberModel)
            .where(StaffMemberModel.is_active.is_(True))
            .order_by(StaffMemberModel.role, StaffMemberModel.first_name)
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_all_housekeepers(self) -> list[StaffMember]:
        stmt = (
            select(StaffMemberModel)
            .where(
                StaffMemberModel.is_active.is_(True),
                StaffMemberModel.role == "housekeeper",
            )
            .order_by(StaffMemberModel.first_name)
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_property(
        self,
        property_id: UUID,
        role: StaffRole | None = None,
    ) -> list[StaffMember]:
        stmt = (
            select(StaffMemberModel)
            .join(
                PropertyStaffAssignmentModel,
                StaffMemberModel.id == PropertyStaffAssignmentModel.staff_id,
            )
            .where(PropertyStaffAssignmentModel.property_id == property_id)
            .order_by(StaffMemberModel.role, StaffMemberModel.first_name)
        )

        if role is not None:
            stmt = stmt.where(StaffMemberModel.role == role.value.lower())

        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_id(self, id: UUID) -> StaffMember | None:
        model = await self._session.get(StaffMemberModel, id)
        return self._to_domain(model) if model else None

    async def create(
        self,
        staff: StaffMember,
        property_id: UUID | None = None,
    ) -> StaffMember:
        model = StaffMemberModel(
            id=staff.id,
            first_name=staff.first_name,
            last_name=staff.last_name,
            email=staff.email,
            phone=staff.phone,
            role=staff.role.value.lower(),
            is_active=staff.is_active,
        )
        self._session.add(model)
        await self._session.flush()

        if property_id is not None:
            assignment = PropertyStaffAssignmentModel(
                property_id=property_id,
                staff_id=model.id,
            )
            self._session.add(assignment)
            await self._session.flush()

        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_property_ids_for_staff(self, staff_id: UUID) -> list[UUID]:
        stmt = (
            select(PropertyStaffAssignmentModel.property_id)
            .where(PropertyStaffAssignmentModel.staff_id == staff_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
