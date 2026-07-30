"""Alembic environment — async engine, metadata from the app models.

Initial PostgreSQL migration is generated with `alembic revision --autogenerate`
against a real PostgreSQL instance (Phase 12 provisioning); dev uses
create_all (core/db.py). Discipline: DATABASE.md §12 (expand-migrate-contract).
"""

import asyncio
import os

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from neuraforge.assessment import models as _assessment_models  # noqa: F401

# Import every module's models so metadata is complete:
from neuraforge.auth import models as _auth_models  # noqa: F401
from neuraforge.content import models as _content_models  # noqa: F401
from neuraforge.core.db import Base
from neuraforge.gamification import models as _gamification_models  # noqa: F401
from neuraforge.learning import models as _learning_models  # noqa: F401
from neuraforge.tutor import models as _tutor_models  # noqa: F401

config = context.config
url = os.environ.get("NF_DATABASE_URL", "")
if url:
    config.set_main_option("sqlalchemy.url", url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _run_sync_migrations(connection) -> None:
    context.configure(
        connection=connection, target_metadata=target_metadata, compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with engine.connect() as connection:
        await connection.run_sync(_run_sync_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
