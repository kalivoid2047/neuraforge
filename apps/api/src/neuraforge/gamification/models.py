import uuid
from datetime import date, datetime

from sqlalchemy import ForeignKey, Index, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db import Base
from ..core.ids import uuid7


class XPEvent(Base):
    """Server-authoritative XP ledger (FR-GAME-1, DATABASE.md §7)."""

    __tablename__ = "xp_events"
    __table_args__ = (
        # One award per (user, reason, ref): double-award impossible at the DB
        # layer. Repeatable charges (hint costs) carry unique ref_ids ("ex:hint:2").
        Index("uq_xp_once", "user_id", "reason", "ref_type", "ref_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[int]
    reason: Mapped[str] = mapped_column(String(32))
    ref_type: Mapped[str] = mapped_column(String(32))
    ref_id: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Streak(Base):
    """Forge Streak (FR-GAME-2). Timezone-aware: dates are in the user's tz."""

    __tablename__ = "streaks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    current: Mapped[int] = mapped_column(default=0)
    longest: Mapped[int] = mapped_column(default=0)
    freezes: Mapped[int] = mapped_column(SmallInteger, default=1)
    last_active_date: Mapped[date | None] = mapped_column(default=None)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
