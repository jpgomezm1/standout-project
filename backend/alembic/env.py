"""Alembic environment configuration for async PostgreSQL migrations."""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the backend directory so DATABASE_URL is available.
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env")

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Alembic Config object — provides access to alembic.ini values
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging (unless we're in autogenerate)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import all ORM models so that Base.metadata contains every table.
# The models/__init__.py re-exports everything Alembic needs.
# ---------------------------------------------------------------------------
import app.infrastructure.db.models  # noqa: F401, E402
from app.infrastructure.db.models.base import Base  # noqa: E402

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Override the sqlalchemy.url from the DATABASE_URL env var
# ---------------------------------------------------------------------------

def _get_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Set it before running Alembic migrations."
        )
    return url


# ---------------------------------------------------------------------------
# Offline migrations (emit SQL to stdout)
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.  By
    skipping Engine creation we don't even need a DB to be available.
    Calls to ``context.execute()`` emit the given string to the script
    output.
    """
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migrations (connect to the live database)
# ---------------------------------------------------------------------------

def do_run_migrations(connection) -> None:  # noqa: ANN001
    """Helper that configures the context and runs migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations within a connection."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
