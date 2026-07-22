"""Event subscriptions: how gamification learns about learning (ARCHITECTURE.md §3).

Imported for side effects by interfaces/http.py — the learning module never
imports gamification.
"""

import uuid

from sqlalchemy import select

from ..auth.models import User
from ..core import events
from ..core.db import SessionLocal
from . import service


@events.subscribe(events.LessonCompleted)
async def on_lesson_completed(event: events.LessonCompleted) -> None:
    async with SessionLocal() as session:
        user_id = uuid.UUID(event.user_id)
        await service.award_xp(
            session, user_id,
            reason="lesson_complete", ref_type="lesson", ref_id=event.lesson_slug,
        )


@events.subscribe(events.SectionCompleted)
async def on_section_completed(event: events.SectionCompleted) -> None:
    async with SessionLocal() as session:
        user_id = uuid.UUID(event.user_id)
        user = await session.scalar(select(User).where(User.id == user_id))
        if user:
            await service.record_activity(session, user_id, user.tz)
