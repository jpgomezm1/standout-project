"""Idempotency check — prevents duplicate processing of the same message.

Uses the ``idempotency_keys`` database table to track which keys have
already been processed.  Each key is stored alongside a reference ID
(typically the inbound message UUID) and a creation timestamp.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class IdempotencyCheck:
    """Database-backed idempotency guard.

    Usage example::

        check = IdempotencyCheck()
        is_new = await check.check_and_set(session, key="tg:123:456", reference_id=msg.id)
        if not is_new:
            return  # duplicate — skip processing
    """

    async def check_and_set(
        self,
        session: AsyncSession,
        key: str,
        reference_id: UUID,
    ) -> bool:
        """Check whether *key* has been seen before and, if not, record it.

        Parameters
        ----------
        session:
            The current async database session (will be flushed but not
            committed by this method — the caller controls the transaction).
        key:
            A unique string that identifies the operation being guarded
            (e.g. ``"telegram:<chat_id>:<message_id>"``).
        reference_id:
            A UUID linking back to the entity that owns this idempotency
            key (typically the :class:`InboundMessage` id).

        Returns
        -------
        bool
            ``True`` if the key is **new** (not a duplicate) and has been
            recorded.  ``False`` if the key already existed (duplicate).
        """
        result = await session.execute(
            text("SELECT key FROM idempotency_keys WHERE key = :key"),
            {"key": key},
        )
        if result.fetchone() is not None:
            logger.info("Duplicate idempotency key detected: %s", key)
            return False

        await session.execute(
            text(
                "INSERT INTO idempotency_keys (key, reference_id, created_at) "
                "VALUES (:key, :ref_id, :now)"
            ),
            {
                "key": key,
                "ref_id": str(reference_id),
                "now": datetime.now(timezone.utc),
            },
        )
        logger.debug("Recorded new idempotency key: %s", key)
        return True
