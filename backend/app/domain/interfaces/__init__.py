"""Domain interface ports (abstract base classes)."""

from app.domain.interfaces.channel_adapter import IChannelAdapter
from app.domain.interfaces.event_store import IEventStore
from app.domain.interfaces.llm_client import ILLMClient
from app.domain.interfaces.repositories import (
    IIncidentRepository,
    IInventoryRepository,
    ILaundryRepository,
    IPropertyRepository,
    IRawMessageRepository,
)

__all__ = [
    "IChannelAdapter",
    "IEventStore",
    "ILLMClient",
    "IIncidentRepository",
    "IInventoryRepository",
    "ILaundryRepository",
    "IPropertyRepository",
    "IRawMessageRepository",
]
