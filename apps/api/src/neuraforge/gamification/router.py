from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.deps import CurrentUser
from ..core.db import get_session
from . import service

router = APIRouter(tags=["gamification"])
Session = Annotated[AsyncSession, Depends(get_session)]


class XPEventOut(BaseModel):
    amount: int
    reason: str
    ref_type: str
    ref_id: str
    created_at: datetime


class XPOut(BaseModel):
    total: int
    recent: list[XPEventOut]


class StreakOut(BaseModel):
    current: int
    longest: int
    freezes: int
    last_active_date: date | None


@router.get("/xp", response_model=XPOut)
async def get_xp(session: Session, user: CurrentUser) -> XPOut:
    total = await service.xp_total(session, user.id)
    recent = await service.recent_events(session, user.id)
    return XPOut(
        total=total,
        recent=[XPEventOut.model_validate(e, from_attributes=True) for e in recent],
    )


@router.get("/streak", response_model=StreakOut)
async def get_streak(session: Session, user: CurrentUser) -> StreakOut:
    streak = await service.get_streak(session, user.id)
    return StreakOut.model_validate(streak, from_attributes=True)
