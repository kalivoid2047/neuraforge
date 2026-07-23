"""Spaced-repetition scheduler + revision planner (FR-LEARN-2/3).

Scheduler: FSRS-inspired v1 — stability (interval, days) and difficulty (1–10)
updated per grade (1 again · 2 hard · 3 good · 4 easy). Deliberately simple and
monotonic; the parameters are per-function so upgrading to full FSRS weights is
a local change that migrates cleanly over the same ReviewState columns.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.errors import NotFoundError
from ..gamification import service as game
from .models import FlashCard, ReviewLog, ReviewState, Spark, SparkAssignment


def _now() -> datetime:
    return datetime.now(UTC)


def schedule(state: ReviewState, grade: int) -> ReviewState:
    """Pure update rule — unit-testable without a database."""
    if grade == 1:  # again
        state.lapses += 1
        state.stability = max(0.1, state.stability * 0.3)
        state.difficulty = min(10.0, state.difficulty + 1.5)
    elif grade == 2:  # hard
        state.stability = max(0.5, state.stability * 1.2)
        state.difficulty = min(10.0, state.difficulty + 0.5)
    elif grade == 3:  # good
        state.stability = max(1.0, state.stability * (2.2 - 0.08 * state.difficulty))
    else:  # easy
        state.stability = max(2.0, state.stability * (3.0 - 0.08 * state.difficulty))
        state.difficulty = max(1.0, state.difficulty - 0.5)

    state.reps += 1
    state.last_review = _now()
    state.due_at = _now() + timedelta(days=state.stability)
    return state


async def ensure_states_for_system_decks(session: AsyncSession, user_id: uuid.UUID) -> None:
    """New cards become due immediately: create missing ReviewStates lazily."""
    cards = (await session.scalars(
        select(FlashCard.id).where(FlashCard.owner_id.is_(None))
    )).all()
    existing = set(await session.scalars(
        select(ReviewState.card_id).where(ReviewState.user_id == user_id)
    ))
    for card_id in cards:
        if card_id not in existing:
            session.add(ReviewState(
                user_id=user_id, card_id=card_id, stability=0.0, due_at=_now(),
            ))
    await session.commit()


async def due_queue(session: AsyncSession, user_id: uuid.UUID, limit: int = 50) -> list[dict]:
    await ensure_states_for_system_decks(session, user_id)
    rows = (await session.execute(
        select(ReviewState, FlashCard)
        .join(FlashCard, FlashCard.id == ReviewState.card_id)
        .where(ReviewState.user_id == user_id, ReviewState.due_at <= _now())
        .order_by(ReviewState.due_at)
        .limit(limit)
    )).all()
    return [
        {
            "card_id": str(card.id),
            "front_md": card.front_md,
            "back_md": card.back_md,
            "reps": state.reps,
            "lapses": state.lapses,
        }
        for state, card in rows
    ]


async def grade_card(
    session: AsyncSession, user_id: uuid.UUID, card_id: uuid.UUID, grade: int
) -> dict:
    state = await session.get(ReviewState, (user_id, card_id))
    if state is None:
        raise NotFoundError("No review state for this card.")
    schedule(state, grade)
    session.add(ReviewLog(user_id=user_id, card_id=card_id, grade=grade))
    await session.commit()
    # capture before award_xp: its duplicate-award rollback expires ORM objects
    next_due, interval = state.due_at, round(state.stability, 2)

    # Review session XP: once per user per day (ref = date)
    awarded = await game.award_xp(
        session, user_id,
        reason="review_session", ref_type="review_day",
        ref_id=_now().date().isoformat(),
    )
    return {
        "card_id": str(card_id),
        "next_due": next_due,
        "interval_days": interval,
        "xp_awarded": awarded,
    }


# ── Daily Spark (FR-LEARN-5) ────────────────────────────────────────────


async def today_spark(session: AsyncSession, user_id: uuid.UUID, tz: str) -> dict:
    today = game._user_today(tz)
    assignment = await session.get(SparkAssignment, (user_id, today))
    if assignment is None:
        sparks = (await session.scalars(select(Spark).order_by(Spark.id))).all()
        if not sparks:
            raise NotFoundError("Spark pool is empty.")
        # deterministic per (user, date): stable under retries, varied across days
        pick = sparks[hash((str(user_id), today.toordinal())) % len(sparks)]
        assignment = SparkAssignment(user_id=user_id, for_date=today, spark_id=pick.id)
        session.add(assignment)
        await session.commit()

    spark = await session.get(Spark, assignment.spark_id)
    assert spark is not None
    return {
        "title": spark.title,
        "detail": spark.detail,
        "minutes": spark.minutes,
        "date": today,
        "completed": assignment.completed_at is not None,
    }


async def complete_spark(session: AsyncSession, user_id: uuid.UUID, tz: str) -> dict:
    today = game._user_today(tz)
    assignment = await session.get(SparkAssignment, (user_id, today))
    if assignment is None:
        raise NotFoundError("No spark assigned today — fetch it first.")
    if assignment.completed_at is None:
        assignment.completed_at = _now()
        await session.commit()
        await game.award_xp(
            session, user_id,
            reason="daily_spark", ref_type="spark_day", ref_id=today.isoformat(),
        )
        await game.record_activity(session, user_id, tz)
    return {"completed": True, "date": today}


# ── Planner (FR-LEARN-3) ────────────────────────────────────────────────


async def planner_today(session: AsyncSession, user_id: uuid.UUID, tz: str) -> dict:
    queue = await due_queue(session, user_id)
    spark = await today_spark(session, user_id, tz)
    est = len(queue) * 0.5 + (0 if spark["completed"] else spark["minutes"])
    return {
        "cards_due": len(queue),
        "spark": spark,
        "estimated_minutes": round(est),
        "items": [
            {"kind": "spark", "label": spark["title"], "done": spark["completed"]},
            {"kind": "reviews", "label": f"{len(queue)} flash cards due", "done": len(queue) == 0},
        ],
    }
