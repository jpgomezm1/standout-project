"""Async SQLAlchemy engine and session factory -- singleton management.

Provides ``get_engine`` / ``get_session_factory`` helpers that lazily create
and cache a single :class:`AsyncEngine` and its matching session factory.
The ``init_engine`` convenience function is kept for backward-compat with the
FastAPI lifespan hook.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_engine(
    database_url: str,
    *,
    pool_size: int = 10,
    max_overflow: int = 20,
    echo: bool = False,
) -> AsyncEngine:
    """Return a cached :class:`AsyncEngine`, creating it on first call.

    The engine is stored as a module-level singleton so that the same pool is
    reused across the entire application process.
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Return a cached :class:`async_sessionmaker` bound to *engine*.

    Like ``get_engine``, the factory is stored as a module-level singleton.
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


def init_engine(
    database_url: str,
    *,
    pool_size: int = 10,
    max_overflow: int = 20,
    echo: bool = False,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Convenience wrapper used by the FastAPI lifespan hook.

    Returns
    -------
    tuple[AsyncEngine, async_sessionmaker[AsyncSession]]
        The engine and the session factory (to be stored on ``app.state``).
    """
    engine = get_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        echo=echo,
    )
    factory = get_session_factory(engine)
    return engine, factory


async def dispose_engine(engine: AsyncEngine | None = None) -> None:
    """Gracefully dispose of the async engine, closing all pooled connections.

    If *engine* is ``None`` the module-level singleton is disposed instead.
    """
    global _engine, _session_factory

    target = engine or _engine
    if target is not None:
        await target.dispose()

    # Reset singletons so a subsequent ``get_engine`` call creates a fresh one.
    if target is _engine:
        _engine = None
        _session_factory = None
