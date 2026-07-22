from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.deps import CurrentUser
from ..core.db import get_session
from . import service
from .schemas import CurriculumOut, LessonDetail

router = APIRouter(tags=["curriculum"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("/curriculum", response_model=CurriculumOut)
async def get_curriculum(session: Session, user: CurrentUser) -> CurriculumOut:
    return await service.curriculum(session, user.id)


@router.get("/lessons/{slug}", response_model=LessonDetail)
async def get_lesson(session: Session, user: CurrentUser, slug: str) -> LessonDetail:
    return await service.lesson_detail(session, user.id, slug)
