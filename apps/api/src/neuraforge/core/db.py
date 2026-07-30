from collections.abc import AsyncIterator
from datetime import datetime
from typing import ClassVar

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .config import get_settings

# Deterministic constraint names → clean Alembic autogenerate diffs (DATABASE.md §1)
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    # Every `datetime.now(...)` call in this codebase passes UTC (tz-aware).
    # SQLite silently accepts either; Postgres/asyncpg rejects tz-aware values
    # against a naive TIMESTAMP column (found live-testing Phase 12 against
    # real Postgres). Map every Mapped[datetime] to TIMESTAMPTZ so both
    # dialects agree on one convention, instead of annotating every column.
    # ClassVar so it is configuration rather than a mapped column; SQLAlchemy
    # reads this off the class and explicitly ignores ClassVar annotations.
    type_annotation_map: ClassVar[dict] = {datetime: DateTime(timezone=True)}


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


engine = create_async_engine(get_settings().database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def create_all_dev() -> None:
    """Dev bootstrap only. Production schema is owned by Alembic (DATABASE.md §12)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
