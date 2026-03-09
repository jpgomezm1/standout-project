from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from datetime import date

from app.domain.entities.incident import Incident, IncidentPriority, IncidentStatus
from app.domain.entities.item import InventoryItem
from app.domain.entities.laundry import LaundryFlow, LaundryStatus
from app.domain.entities.message import InboundMessage, ProcessingStatus
from app.domain.entities.property import Property
from app.domain.entities.reservation import Reservation, ReservationStatus
from app.domain.entities.housekeeping import HousekeepingAssignment
from app.domain.entities.staff import StaffMember, StaffRole


class IPropertyRepository(ABC):
    """Port for property persistence operations."""

    @abstractmethod
    async def get_all(self) -> list[Property]:
        """Return every registered property."""
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Property | None:
        """Return a single property by primary key, or ``None``."""
        ...

    @abstractmethod
    async def create(self, property: Property) -> Property:
        """Persist a new property and return the stored record."""
        ...

    @abstractmethod
    async def search_by_name(self, query: str) -> list[Property]:
        """Search properties whose name or aliases match *query*."""
        ...


class IIncidentRepository(ABC):
    """Port for incident persistence operations."""

    @abstractmethod
    async def get_all(
        self,
        property_id: UUID | None = None,
        status: IncidentStatus | None = None,
        priority: IncidentPriority | None = None,
    ) -> list[Incident]:
        """Return incidents, optionally filtered by property, status, or priority."""
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Incident | None:
        """Return a single incident by primary key, or ``None``."""
        ...

    @abstractmethod
    async def create(self, incident: Incident) -> Incident:
        """Persist a new incident and return the stored record."""
        ...

    @abstractmethod
    async def update_status(
        self,
        id: UUID,
        status: IncidentStatus,
        resolved_at: datetime | None = None,
    ) -> Incident | None:
        """Transition an incident to a new status, optionally setting resolved_at."""
        ...

    @abstractmethod
    async def get_latest_open_by_property(
        self,
        property_id: UUID,
        item_name: str | None = None,
    ) -> Incident | None:
        """Return the most recent non-resolved incident for a property.

        If *item_name* is provided, prefer incidents whose title contains it.
        """
        ...


class IInventoryRepository(ABC):
    """Port for inventory item persistence operations."""

    @abstractmethod
    async def get_by_property(self, property_id: UUID) -> list[InventoryItem]:
        """Return all inventory items belonging to a property."""
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> InventoryItem | None:
        """Return a single inventory item by primary key, or ``None``."""
        ...

    @abstractmethod
    async def create(self, item: InventoryItem) -> InventoryItem:
        """Persist a new inventory item and return the stored record."""
        ...

    @abstractmethod
    async def get_current_quantities(
        self,
        property_id: UUID,
    ) -> list[dict]:
        """Derive current quantities for each item by replaying relevant events.

        Returns a list of dicts, each containing ``item`` (an InventoryItem)
        and ``current_quantity`` (int) computed from the event log.
        """
        ...


class ILaundryRepository(ABC):
    """Port for laundry-flow persistence operations."""

    @abstractmethod
    async def get_by_property(
        self,
        property_id: UUID,
        status: LaundryStatus | None = None,
    ) -> list[LaundryFlow]:
        """Return laundry flows for a property, optionally filtered by status."""
        ...

    @abstractmethod
    async def get_latest_open_by_property(self, property_id: UUID) -> LaundryFlow | None:
        """Return the most recent non-terminal flow for a property."""
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> LaundryFlow | None:
        """Return a single laundry flow by primary key, or ``None``."""
        ...

    @abstractmethod
    async def create(self, flow: LaundryFlow) -> LaundryFlow:
        """Persist a new laundry flow and return the stored record."""
        ...

    @abstractmethod
    async def update(self, flow: LaundryFlow) -> LaundryFlow:
        """Persist changes to an existing laundry flow."""
        ...


class IRawMessageRepository(ABC):
    """Port for raw inbound-message persistence operations."""

    @abstractmethod
    async def create(self, message: InboundMessage) -> InboundMessage:
        """Persist a new inbound message and return the stored record."""
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> InboundMessage | None:
        """Return a single message by primary key, or ``None``."""
        ...

    @abstractmethod
    async def update_status(
        self,
        id: UUID,
        status: ProcessingStatus,
    ) -> InboundMessage | None:
        """Update the processing status of an inbound message."""
        ...

    @abstractmethod
    async def get_pending_retry(self) -> list[InboundMessage]:
        """Return all messages with ``PENDING_RETRY`` status."""
        ...


class IReservationRepository(ABC):
    """Port for reservation persistence operations."""

    @abstractmethod
    async def get_by_property(
        self,
        property_id: UUID,
        status: ReservationStatus | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Reservation]:
        """Return reservations for a property, optionally filtered by status and date overlap."""
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Reservation | None:
        """Return a single reservation by primary key, or ``None``."""
        ...

    @abstractmethod
    async def create(self, reservation: Reservation) -> Reservation:
        """Persist a new reservation and return the stored record."""
        ...


class IStaffRepository(ABC):
    """Port for staff member persistence operations."""

    @abstractmethod
    async def get_all(self) -> list[StaffMember]:
        """Return all staff members."""
        ...

    @abstractmethod
    async def get_all_housekeepers(self) -> list[StaffMember]:
        """Return all active housekeepers."""
        ...

    @abstractmethod
    async def get_by_property(
        self,
        property_id: UUID,
        role: StaffRole | None = None,
    ) -> list[StaffMember]:
        """Return staff members assigned to a property, optionally filtered by role."""
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> StaffMember | None:
        """Return a single staff member by primary key, or ``None``."""
        ...

    @abstractmethod
    async def create(
        self,
        staff: StaffMember,
        property_id: UUID | None = None,
    ) -> StaffMember:
        """Persist a new staff member with optional property assignment."""
        ...

    @abstractmethod
    async def get_property_ids_for_staff(self, staff_id: UUID) -> list[UUID]:
        """Return all property IDs assigned to a staff member."""
        ...


class IHousekeepingRepository(ABC):
    """Port for housekeeping assignment persistence operations."""

    @abstractmethod
    async def get_by_reservation(self, reservation_id: UUID) -> list[HousekeepingAssignment]:
        """Return all housekeeping assignments for a reservation."""
        ...

    @abstractmethod
    async def get_available_on_date(self, target_date: date, limit: int | None = None) -> list[StaffMember]:
        """Return housekeepers without a non-cancelled assignment on the given date."""
        ...

    @abstractmethod
    async def create(self, assignment: HousekeepingAssignment) -> HousekeepingAssignment:
        """Persist a new housekeeping assignment."""
        ...

    @abstractmethod
    async def delete(self, assignment_id: UUID) -> bool:
        """Delete a housekeeping assignment. Returns True if deleted."""
        ...
