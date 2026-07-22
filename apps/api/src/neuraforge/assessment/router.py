import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.deps import CurrentUser
from ..core.db import get_session
from . import service
from .schemas import (
    AnswerResult,
    AttemptFinishResult,
    AttemptStart,
    ExercisePublic,
    ProjectOut,
    ProjectSubmissionOut,
    QuestionPublic,
    QuizOut,
    SubmissionResult,
)

router = APIRouter(tags=["assessment"])
Session = Annotated[AsyncSession, Depends(get_session)]


# ── question bank ────────────────────────────────────────────────────────


@router.get("/questions", response_model=list[QuestionPublic])
async def list_questions(
    session: Session, user: CurrentUser,
    bank: str | None = None, difficulty: int | None = None, limit: int = 20, offset: int = 0,
) -> list[QuestionPublic]:
    return await service.list_questions(session, bank=bank, difficulty=difficulty, limit=limit, offset=offset)


# ── quizzes ──────────────────────────────────────────────────────────────


@router.get("/quizzes/lessons/{slug}", response_model=QuizOut)
async def quiz_for_lesson(session: Session, user: CurrentUser, slug: str) -> QuizOut:
    return await service.get_quiz_for_lesson(session, slug)


@router.post("/quizzes/{quiz_id}/attempts", response_model=AttemptStart, status_code=201)
async def start_attempt(session: Session, user: CurrentUser, quiz_id: uuid.UUID) -> AttemptStart:
    return await service.start_attempt(session, user.id, quiz_id)


class AnswerIn(BaseModel):
    answer: dict


@router.patch("/attempts/{attempt_id}/answers/{question_id}", response_model=AnswerResult)
async def answer(
    session: Session, user: CurrentUser, attempt_id: uuid.UUID, question_id: uuid.UUID, body: AnswerIn
) -> AnswerResult:
    return await service.answer_question(session, user.id, attempt_id, question_id, body.answer)


@router.post("/attempts/{attempt_id}/finish", response_model=AttemptFinishResult)
async def finish(session: Session, user: CurrentUser, attempt_id: uuid.UUID) -> AttemptFinishResult:
    return await service.finish_attempt(session, user.id, attempt_id)


# ── exercises (server-side authoritative grading) ──────────────────────────


@router.get("/exercises/lessons/{slug}", response_model=ExercisePublic)
async def exercise_for_lesson(session: Session, user: CurrentUser, slug: str) -> ExercisePublic:
    return await service.get_exercise_for_lesson(session, slug)


class SubmissionIn(BaseModel):
    code: str


@router.post("/exercises/{exercise_id}/submissions", response_model=SubmissionResult, status_code=201)
async def submit_exercise(
    session: Session, user: CurrentUser, exercise_id: uuid.UUID, body: SubmissionIn
) -> SubmissionResult:
    return await service.submit_exercise(session, user.id, exercise_id, body.code)


# ── projects ────────────────────────────────────────────────────────────


@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(session: Session, user: CurrentUser, kind: str | None = None) -> list[ProjectOut]:
    return await service.list_projects(session, kind)


class ProjectSubmissionIn(BaseModel):
    artifact_url: str
    self_assessment: dict[str, bool] = {}


@router.post("/projects/{project_id}/submissions", response_model=ProjectSubmissionOut, status_code=201)
async def submit_project(
    session: Session, user: CurrentUser, project_id: uuid.UUID, body: ProjectSubmissionIn
) -> ProjectSubmissionOut:
    return await service.submit_project(session, user.id, project_id, body.artifact_url, body.self_assessment)
