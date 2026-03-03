"""SQLAlchemy ORM models package.

Import every model module here so that Alembic's ``target_metadata`` can
discover them via a single import of this package::

    from app.infrastructure.db.models import Base  # brings all tables along
"""

from app.infrastructure.db.models.base import Base
from app.infrastructure.db.models.condition_report import ConditionReportModel, ConditionReportSessionModel
from app.infrastructure.db.models.event import EventModel
from app.infrastructure.db.models.idempotency_key import IdempotencyKeyModel
from app.infrastructure.db.models.incident import IncidentModel
from app.infrastructure.db.models.inventory_item import InventoryItemModel
from app.infrastructure.db.models.laundry_flow import LaundryFlowModel
from app.infrastructure.db.models.pending_clarification import PendingClarificationModel
from app.infrastructure.db.models.property import PropertyModel
from app.infrastructure.db.models.raw_message import RawMessageModel
from app.infrastructure.db.models.reservation import ReservationModel
from app.infrastructure.db.models.staff import HousekeepingAssignmentModel, PropertyStaffAssignmentModel, StaffMemberModel
from app.infrastructure.db.models.telegram_user import TelegramUserModel

__all__ = [
    "Base",
    "ConditionReportModel",
    "ConditionReportSessionModel",
    "EventModel",
    "IdempotencyKeyModel",
    "IncidentModel",
    "InventoryItemModel",
    "LaundryFlowModel",
    "PendingClarificationModel",
    "HousekeepingAssignmentModel",
    "PropertyModel",
    "PropertyStaffAssignmentModel",
    "RawMessageModel",
    "ReservationModel",
    "StaffMemberModel",
    "TelegramUserModel",
]
