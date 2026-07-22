import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..content.models import Lesson
from ..core import events
from ..core.errors import NotFoundError
from .models import LessonProgress
from .schemas import ContinueTarget, ProgressSummary, TickResult


async def progress_map(session: AsyncSession, user_id: uuid.UUID) -> dict[uuid.UUID, LessonProgress]:
    rows = await session.scalars(
        select(LessonProgress).where(LessonProgress.user_id == user_id)
    )
    return {p.lesson_id: p for p in rows}


async def tick_section(
    session: AsyncSession, user_id: uuid.UUID, slug: str, anchor: str
) -> TickResult:
    lesson = await session.scalar(
        select(Lesson).where(Lesson.slug == slug).options(selectinload(Lesson.sections))
    )
    if lesson is None:
        raise NotFoundError(f"Lesson '{slug}' not found")
    anchors = {s.anchor for s in lesson.sections}
    if anchor not in anchors:
        raise NotFoundError(f"Section '{anchor}' not in lesson '{slug}'")

    progress = await session.get(LessonProgress, (user_id, lesson.id))
    now = datetime.now(UTC)
    if progress is None:
        progress = LessonProgress(user_id=user_id, lesson_id=lesson.id, started_at=now)
        session.add(progress)

    # idempotent upsert of the tick (NFR-REL-3: retries never corrupt state)
    ticks = dict(progress.section_ticks)
    ticks.setdefault(anchor, now.isoformat())
    progress.section_ticks = ticks
    progress.resume_anchor = anchor

    completed = anchors <= set(ticks)
    was_completed = progress.status == "completed"
    progress.status = "completed" if completed else "in_progress"
    if completed and progress.completed_at is None:
        progress.completed_at = now
    await session.commit()

    await events.emit(events.SectionCompleted(str(user_id), slug, anchor))
    if completed and not was_completed:
        # Phase 8 gamification subscribes to this for XP (FR-GAME-1)
        await events.emit(events.LessonCompleted(str(user_id), slug))

    return TickResult(
        lesson_slug=slug,
        anchor=anchor,
        lesson_status=progress.status,
        ticked_sections=len(set(ticks) & anchors),
        total_sections=len(anchors),
    )


async def summary(session: AsyncSession, user_id: uuid.UUID) -> ProgressSummary:
    lessons = (
        await session.scalars(
            select(Lesson)
            .where(Lesson.status == "published")
            .options(selectinload(Lesson.sections))
            .order_by(Lesson.month, Lesson.week, Lesson.ord)
        )
    ).all()
    pmap = await progress_map(session, user_id)

    done = sum(1 for l in lessons if pmap.get(l.id) and pmap[l.id].status == "completed")
    current: ContinueTarget | None = None
    for lesson in lessons:
        p = pmap.get(lesson.id)
        if p is None or p.status != "completed":
            total = max(1, len(lesson.sections))
            ticked = len(set(p.section_ticks) & {s.anchor for s in lesson.sections}) if p else 0
            current = ContinueTarget(
                slug=lesson.slug,
                code=f"M{lesson.month} · W{lesson.week} · L{lesson.ord}",
                title=lesson.title,
                progress_pct=round(100 * ticked / total),
                resume_anchor=p.resume_anchor if p else None,
            )
            break

    total_lessons = len(lessons)
    return ProgressSummary(
        lessons_completed=done,
        lessons_total=total_lessons,
        overall_pct=round(100 * done / total_lessons) if total_lessons else 0,
        current=current,
    )
