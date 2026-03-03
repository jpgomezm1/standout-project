"""PostgreSQL-backed implementation of :class:`IRawMessageRepository`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.message import (
    InboundMessage,
    MessageType,
    ProcessingStatus,
)
from app.domain.interfaces.repositories import IRawMessageRepository
from app.infrastructure.db.models.raw_message import RawMessageModel


class RawMessageRepository(IRawMessageRepository):
    """Async SQLAlchemy adapter for raw inbound-message persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Mapping helpers -----------------------------------------------------

    @staticmethod
    def _to_domain(model: RawMessageModel) -> InboundMessage:
        return InboundMessage(
            id=model.id,
            telegram_chat_id=model.telegram_chat_id,
            telegram_message_id=model.telegram_message_id,
            telegram_user_id=model.telegram_user_id or 0,
            message_type=MessageType(model.message_type.upper()),
            content_text=model.content_text,
            file_references=model.file_references or [],
            raw_payload=model.raw_payload or {},
            processing_status=ProcessingStatus(model.processing_status.upper()),
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(entity: InboundMessage) -> RawMessageModel:
        return RawMessageModel(
            id=entity.id,
            telegram_chat_id=entity.telegram_chat_id,
            telegram_message_id=entity.telegram_message_id,
            telegram_user_id=entity.telegram_user_id,
            message_type=entity.message_type.value.lower(),
            content_text=entity.content_text,
            file_references=entity.file_references,
            raw_payload=entity.raw_payload,
            processing_status=entity.processing_status.value.lower(),
        )

    # -- Interface implementation --------------------------------------------

    async def create(self, message: InboundMessage) -> InboundMessage:
        model = self._to_model(message)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, id: UUID) -> InboundMessage | None:
        model = await self._session.get(RawMessageModel, id)
        return self._to_domain(model) if model else None

    async def update_status(
        self,
        id: UUID,
        status: ProcessingStatus,
    ) -> InboundMessage | None:
        model = await self._session.get(RawMessageModel, id)
        if model is None:
            return None

        model.processing_status = status.value.lower()

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_pending_retry(self) -> list[InboundMessage]:
        """Return all messages with ``PENDING_RETRY`` status.

        Uses the partial index ``ix_raw_messages_pending_processing`` for
        efficient retrieval.
        """
        stmt = (
            select(RawMessageModel)
            .where(RawMessageModel.processing_status == "pending_retry")
            .order_by(RawMessageModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]
