import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.errors import NotFoundError
from ..learning.service import progress_map
from .models import Lesson
from .schemas import (
    CurriculumOut,
    LessonDetail,
    LessonSummary,
    MonthOut,
    SectionOut,
    WeekOut,
)


def _learner_status(progress_status: str | None, first_incomplete: bool) -> str:
    if progress_status == "completed":
        return "done"
    return "current" if first_incomplete else "todo"


async def curriculum(session: AsyncSession, user_id: uuid.UUID) -> CurriculumOut:
    lessons = (
        await session.scalars(
            select(Lesson)
            .where(Lesson.status == "published")
            .order_by(Lesson.month, Lesson.week, Lesson.ord)
        )
    ).all()
    pmap = await progress_map(session, user_id)

    by_month: dict[int, list[Lesson]] = defaultdict(list)
    for lesson in lessons:
        by_month[lesson.month].append(lesson)

    months: list[MonthOut] = []
    marked_current = False
    for month_no in sorted(by_month):
        month_lessons = by_month[month_no]
        by_week: dict[int, list[Lesson]] = defaultdict(list)
        for lesson in month_lessons:
            by_week[lesson.week].append(lesson)

        weeks: list[WeekOut] = []
        for week_no in sorted(by_week):
            summaries: list[LessonSummary] = []
            for lesson in by_week[week_no]:
                p = pmap.get(lesson.id)
                status = p.status if p else None
                is_current = not marked_current and status != "completed"
                if is_current:
                    marked_current = True
                summaries.append(
                    LessonSummary(
                        slug=lesson.slug,
                        title=lesson.title,
                        ord=lesson.ord,
                        minutes=lesson.est_minutes,
                        difficulty=lesson.difficulty,
                        status=_learner_status(status, is_current),
                    )
                )
            weeks.append(
                WeekOut(
                    number=week_no,
                    title=by_week[week_no][0].meta.get("week_title", f"Week {week_no}"),
                    lessons=summaries,
                )
            )

        done = sum(1 for ml in month_lessons if pmap.get(ml.id) and pmap[ml.id].status == "completed")
        months.append(
            MonthOut(
                number=month_no,
                title=month_lessons[0].meta.get("month_title", f"Month {month_no}"),
                progress=round(100 * done / len(month_lessons)),
                weeks=weeks,
            )
        )
    return CurriculumOut(months=months)


async def lesson_detail(session: AsyncSession, user_id: uuid.UUID, slug: str) -> LessonDetail:
    lesson = await session.scalar(
        select(Lesson).where(Lesson.slug == slug).options(selectinload(Lesson.sections))
    )
    if lesson is None:
        raise NotFoundError(f"Lesson '{slug}' not found")
    p = (await progress_map(session, user_id)).get(lesson.id)
    ticks = set(p.section_ticks) if p else set()

    return LessonDetail(
        slug=lesson.slug,
        code=f"{lesson.month}.{lesson.week}.{lesson.ord}",
        title=lesson.title,
        minutes=lesson.est_minutes,
        difficulty=lesson.difficulty,
        prereqs=lesson.meta.get("prereqs", []),
        objectives=lesson.meta.get("objectives", []),
        sections=[
            SectionOut(anchor=s.anchor, kind=s.kind, title=s.title, done=s.anchor in ticks)
            for s in lesson.sections
        ],
        progress_status=p.status if p else "not_started",
        resume_anchor=p.resume_anchor if p else None,
    )
