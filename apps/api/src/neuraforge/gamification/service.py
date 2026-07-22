import uuid
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Streak, XPEvent

# XP rule table (server-authoritative, FR-GAME-1)
XP_RULES = {
    "lesson_complete": 50,
    "review_session": 10,
    "daily_spark": 15,
    "quiz_complete": 30,
    "exercise_solved": 20,
    "project_submitted": 100,
}


def _user_today(tz_name: str) -> date:
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz = UTC  # unknown tz string degrades to UTC, never errors
    return datetime.now(tz).date()


async def award_xp(
    session: AsyncSession, user_id: uuid.UUID, *, reason: str, ref_type: str, ref_id: str,
    amount: int | None = None,
) -> bool:
    """Idempotent XP award; returns False if this (reason, ref) was already awarded.

    Uses a SAVEPOINT so the unique-index no-op doesn't poison the caller's
    transaction. The DB index is the authority (DATABASE.md §7).
    """
    value = amount if amount is not None else XP_RULES[reason]
    try:
        async with session.begin_nested():
            session.add(XPEvent(
                user_id=user_id, amount=value,
                reason=reason, ref_type=ref_type, ref_id=ref_id,
            ))
        await session.commit()
        return True
    except IntegrityError:
        await session.rollback()
        return False


async def xp_total(session: AsyncSession, user_id: uuid.UUID) -> int:
    return (
        await session.scalar(
            select(func.coalesce(func.sum(XPEvent.amount), 0)).where(XPEvent.user_id == user_id)
        )
    ) or 0


async def recent_events(session: AsyncSession, user_id: uuid.UUID, limit: int = 20) -> list[XPEvent]:
    return list(await session.scalars(
        select(XPEvent).where(XPEvent.user_id == user_id)
        .order_by(XPEvent.created_at.desc()).limit(limit)
    ))


async def record_activity(session: AsyncSession, user_id: uuid.UUID, tz_name: str) -> Streak:
    """Advance the Forge Streak for 'today' in the user's timezone (FR-GAME-2).

    Lazy evaluation (v1): gaps are settled at the next activity — a 1-day gap
    consumes a freeze, longer gaps reset. The Celery-beat rollover job
    (ARCHITECTURE.md §8) will take over proactive settling in the ops phase.
    """
    streak = await session.get(Streak, user_id)
    if streak is None:
        streak = Streak(user_id=user_id, current=0, longest=0, freezes=1)
        session.add(streak)

    today = _user_today(tz_name)
    last = streak.last_active_date

    if last == today:
        pass  # already counted today
    elif last == today - timedelta(days=1):
        streak.current += 1
    elif last is not None and last == today - timedelta(days=2) and streak.freezes > 0:
        streak.freezes -= 1  # freeze silently covers the single missed day
        streak.current += 1
    elif last is None:
        streak.current = 1
    else:
        streak.current = 1  # gap too large — the fire went out
    streak.last_active_date = today
    streak.longest = max(streak.longest, streak.current)
    await session.commit()
    return streak


async def get_streak(session: AsyncSession, user_id: uuid.UUID) -> Streak:
    streak = await session.get(Streak, user_id)
    if streak is None:
        streak = Streak(user_id=user_id, current=0, longest=0, freezes=1)
        session.add(streak)
        await session.commit()
    return streak
