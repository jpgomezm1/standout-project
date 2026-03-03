"""Domain entity models."""

from app.domain.entities.event import EventType, OperationalEvent
from app.domain.entities.housekeeping import AssignmentStatus, HousekeepingAssignment
from app.domain.entities.incident import Incident, IncidentPriority, IncidentStatus
from app.domain.entities.item import InventoryItem, ItemCategory
from app.domain.entities.laundry import LaundryFlow, LaundryStatus
from app.domain.entities.message import InboundMessage, MessageType, ProcessingStatus
from app.domain.entities.property import Property
from app.domain.entities.reservation import BookingChannel, Reservation, ReservationStatus
from app.domain.entities.staff import StaffMember, StaffRole

__all__ = [
    "AssignmentStatus",
    "EventType",
    "HousekeepingAssignment",
    "OperationalEvent",
    "Incident",
    "IncidentPriority",
    "IncidentStatus",
    "InventoryItem",
    "ItemCategory",
    "LaundryFlow",
    "LaundryStatus",
    "InboundMessage",
    "MessageType",
    "ProcessingStatus",
    "Property",
    "Reservation",
    "ReservationStatus",
    "BookingChannel",
    "StaffMember",
    "StaffRole",
]
