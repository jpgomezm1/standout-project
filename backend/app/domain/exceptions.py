from __future__ import annotations


class DomainError(Exception):
    """Base exception for all domain-layer errors.

    All custom domain exceptions inherit from this class so that upper
    layers can catch ``DomainError`` as a single except clause when they
    do not need fine-grained handling.
    """

    def __init__(self, message: str = "A domain error occurred") -> None:
        self.message = message
        super().__init__(self.message)


class EventStoreError(DomainError):
    """Raised when the event store encounters a persistence failure."""

    def __init__(self, message: str = "Event store operation failed") -> None:
        super().__init__(message)


class EntityNotFoundError(DomainError):
    """Raised when a requested entity does not exist."""

    def __init__(
        self,
        entity_type: str = "Entity",
        entity_id: str = "",
    ) -> None:
        detail = f"{entity_type} not found"
        if entity_id:
            detail = f"{entity_type} with id '{entity_id}' not found"
        super().__init__(detail)
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateEventError(DomainError):
    """Raised when an event with the same idempotency key already exists."""

    def __init__(self, idempotency_key: str = "") -> None:
        detail = "Duplicate event"
        if idempotency_key:
            detail = f"Duplicate event with idempotency key '{idempotency_key}'"
        super().__init__(detail)
        self.idempotency_key = idempotency_key


class InterpretationError(DomainError):
    """Raised when the LLM fails to interpret a message."""

    def __init__(self, message: str = "Failed to interpret message") -> None:
        super().__init__(message)


class ChannelError(DomainError):
    """Raised when a messaging-channel operation fails."""

    def __init__(self, message: str = "Channel operation failed") -> None:
        super().__init__(message)
