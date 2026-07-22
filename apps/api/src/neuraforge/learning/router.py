import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.deps import CurrentUser
from ..core.db import get_session
from . import review, service
from .schemas import ProgressSummary, TickResult

router = APIRouter(tags=["learning"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.put("/progress/lessons/{slug}/sections/{anchor}", response_model=TickResult)
async def tick(session: Session, user: CurrentUser, slug: str, anchor: str) -> TickResult:
    return await service.tick_section(session, user.id, slug, anchor)


@router.get("/progress/summary", response_model=ProgressSummary)
async def get_summary(session: Session, user: CurrentUser) -> ProgressSummary:
    return await service.summary(session, user.id)


# ── review & planner (FR-LEARN-2/3/5) ──────────────────────────────────


class GradeIn(BaseModel):
    grade: int = Field(ge=1, le=4)  # 1 again · 2 hard · 3 good · 4 easy


@router.get("/reviews/queue")
async def reviews_queue(session: Session, user: CurrentUser) -> list[dict]:
    return await review.due_queue(session, user.id)


@router.post("/reviews/{card_id}/grade")
async def grade(session: Session, user: CurrentUser, card_id: uuid.UUID, body: GradeIn) -> dict:
    return await review.grade_card(session, user.id, card_id, body.grade)


@router.get("/sparks/today")
async def spark_today(session: Session, user: CurrentUser) -> dict:
    return await review.today_spark(session, user.id, user.tz)


@router.post("/sparks/today/complete")
async def spark_complete(session: Session, user: CurrentUser) -> dict:
    return await review.complete_spark(session, user.id, user.tz)


@router.get("/planner/today")
async def planner(session: Session, user: CurrentUser) -> dict:
    return await review.planner_today(session, user.id, user.tz)
