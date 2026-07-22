import uuid
from datetime import UTC, datetime
from urllib.parse import urlparse

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..content.models import Lesson
from ..core.config import get_settings
from ..core.errors import DomainError, NotFoundError
from ..gamification import service as game
from . import grading, runner
from .models import Exercise, Project, ProjectSubmission, Question, Quiz, QuizAttempt, Submission
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
    TestResultOut,
)


class AttemptFinished(DomainError):
    status = 409
    title = "Attempt already finished"


class TooManyAttempts(DomainError):
    status = 429
    title = "Attempt limit reached"


# ── quizzes ──────────────────────────────────────────────────────────────


async def list_questions(
    session: AsyncSession, *, bank: str | None, difficulty: int | None, limit: int, offset: int
) -> list[QuestionPublic]:
    query = select(Question).where(Question.status == "published")
    if bank:
        query = query.where(Question.bank == bank)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
    rows = await session.scalars(query.order_by(Question.difficulty).offset(offset).limit(limit))
    return [QuestionPublic.model_validate(q, from_attributes=True) for q in rows]


async def get_quiz_for_lesson(session: AsyncSession, slug: str) -> QuizOut:
    lesson = await session.scalar(select(Lesson).where(Lesson.slug == slug))
    if lesson is None:
        raise NotFoundError(f"Lesson '{slug}' not found")
    quiz = await session.scalar(select(Quiz).where(Quiz.lesson_id == lesson.id, Quiz.kind == "mini"))
    if quiz is None:
        raise NotFoundError(f"No mini-quiz for lesson '{slug}'")
    count = len(quiz.blueprint.get("question_ids", []))
    return QuizOut(
        id=quiz.id, kind=quiz.kind, lesson_id=quiz.lesson_id,
        pass_threshold=quiz.pass_threshold, time_limit_s=quiz.time_limit_s,
        question_count=count,
    )


async def start_attempt(session: AsyncSession, user_id: uuid.UUID, quiz_id: uuid.UUID) -> AttemptStart:
    quiz = await session.get(Quiz, quiz_id)
    if quiz is None:
        raise NotFoundError("Quiz not found.")
    questions = await grading.select_questions(session, quiz.blueprint)
    if not questions:
        raise NotFoundError("No questions available for this quiz yet.")

    attempt = QuizAttempt(quiz_id=quiz.id, user_id=user_id, question_ids=[str(q.id) for q in questions])
    session.add(attempt)
    await session.commit()
    return AttemptStart(
        attempt_id=attempt.id, quiz_id=quiz.id,
        questions=[QuestionPublic.model_validate(q, from_attributes=True) for q in questions],
        time_limit_s=quiz.time_limit_s,
    )


async def answer_question(
    session: AsyncSession, user_id: uuid.UUID, attempt_id: uuid.UUID, question_id: uuid.UUID, answer: dict
) -> AnswerResult:
    attempt = await session.get(QuizAttempt, attempt_id)
    if attempt is None or attempt.user_id != user_id:
        raise NotFoundError("Attempt not found.")
    if attempt.finished_at is not None:
        raise AttemptFinished("This attempt is already finished.")
    if str(question_id) not in attempt.question_ids:
        raise NotFoundError("Question is not part of this attempt.")

    question = await session.get(Question, question_id)
    if question is None:
        raise NotFoundError("Question not found.")

    correct, message = grading.grade_objective(question, answer)
    # idempotent upsert of the answer (NFR-REL-3), same pattern as tick_section
    answers = dict(attempt.answers)
    answers[str(question_id)] = {
        "answer": answer, "correct": correct, "answered_at": datetime.now(UTC).isoformat(),
    }
    attempt.answers = answers
    await session.commit()
    return AnswerResult(correct=correct, message=message)


async def finish_attempt(
    session: AsyncSession, user_id: uuid.UUID, attempt_id: uuid.UUID
) -> AttemptFinishResult:
    attempt = await session.get(QuizAttempt, attempt_id)
    if attempt is None or attempt.user_id != user_id:
        raise NotFoundError("Attempt not found.")
    quiz = await session.get(Quiz, attempt.quiz_id)
    if quiz is None:
        raise NotFoundError("Quiz not found.")

    total = len(attempt.question_ids)
    graded = sum(1 for a in attempt.answers.values() if a.get("correct") is True)
    score = round(100 * graded / total, 2) if total else 0.0
    passed = score >= quiz.pass_threshold

    if attempt.finished_at is None:
        attempt.score = score
        attempt.finished_at = datetime.now(UTC)
        await session.commit()

    # fetch everything the response needs BEFORE award_xp: on a duplicate
    # award its rollback (uq_xp_once conflict) expires the whole identity
    # map even with expire_on_commit=False, same trap documented in
    # learning/review.py — accessing ORM attributes afterward would 500.
    explanations: dict[str, dict] = {}
    for qid in attempt.question_ids:
        q = await session.get(Question, uuid.UUID(qid))
        if q:
            explanations[qid] = q.explanation
    quiz_id, pass_threshold = quiz.id, quiz.pass_threshold

    # awards once per (user, quiz) regardless of re-finish or retake (uq_xp_once)
    xp_awarded = await game.award_xp(
        session, user_id, reason="quiz_complete", ref_type="quiz", ref_id=str(quiz_id)
    )

    return AttemptFinishResult(
        score=score, passed=passed, pass_threshold=pass_threshold,
        xp_awarded=xp_awarded, explanations=explanations,
    )


# ── exercises (server-side authoritative grading, FR-ASSESS-5) ────────────


async def get_exercise_for_lesson(session: AsyncSession, slug: str) -> ExercisePublic:
    lesson = await session.scalar(select(Lesson).where(Lesson.slug == slug))
    if lesson is None:
        raise NotFoundError(f"Lesson '{slug}' not found")
    exercise = await session.scalar(
        select(Exercise).where(Exercise.lesson_id == lesson.id).order_by(Exercise.ord)
    )
    if exercise is None:
        raise NotFoundError(f"No exercise for lesson '{slug}'")
    return ExercisePublic(
        id=exercise.id, lesson_id=exercise.lesson_id, title=exercise.title,
        brief=exercise.brief, starter_code=exercise.starter_code, hints=exercise.hints,
    )


async def submit_exercise(
    session: AsyncSession, user_id: uuid.UUID, exercise_id: uuid.UUID, code: str
) -> SubmissionResult:
    exercise = await session.get(Exercise, exercise_id)
    if exercise is None:
        raise NotFoundError("Exercise not found.")

    settings = get_settings()
    prior = await session.scalar(
        select(func.count()).select_from(Submission).where(
            Submission.exercise_id == exercise_id, Submission.user_id == user_id
        )
    )
    if prior >= settings.assess_max_attempts_per_exercise:
        raise TooManyAttempts("You've used all attempts for this exercise.")

    result = await runner.run_submission(
        code, exercise.tests,
        wall_s=exercise.limits.get("wall_s", settings.assess_submission_wall_s),
        mem_mb=exercise.limits.get("mem_mb", settings.assess_submission_mem_mb),
        output_cap=settings.assess_submission_output_cap,
    )
    tests = result.get("tests")
    all_passed = bool(tests) and all(t["passed"] for t in tests)
    status = "passed" if all_passed else ("error" if not result.get("ok", False) else "failed")

    submission = Submission(
        exercise_id=exercise.id, user_id=user_id, code=code, attempt_no=prior + 1,
        status=status, results=tests or [], stdout=result.get("stdout", ""),
        graded_at=datetime.now(UTC),
    )
    session.add(submission)
    await session.commit()
    submission_id = submission.id  # captured before award_xp — see finish_attempt comment

    xp_awarded = False
    if all_passed:
        xp_awarded = await game.award_xp(
            session, user_id, reason="exercise_solved", ref_type="exercise", ref_id=str(exercise.id)
        )

    return SubmissionResult(
        submission_id=submission_id, status=status, stdout=result.get("stdout", ""),
        error=result.get("error"),
        tests=[TestResultOut(**t) for t in tests] if tests else None,
        xp_awarded=xp_awarded, ms=result.get("ms", 0),
    )


# ── projects (FR-ASSESS-6) ─────────────────────────────────────────────────


async def list_projects(session: AsyncSession, kind: str | None) -> list[ProjectOut]:
    query = select(Project)
    if kind:
        query = query.where(Project.kind == kind)
    rows = await session.scalars(query.order_by(Project.month, Project.week))
    return [ProjectOut.model_validate(p, from_attributes=True) for p in rows]


async def submit_project(
    session: AsyncSession, user_id: uuid.UUID, project_id: uuid.UUID,
    artifact_url: str, self_assessment: dict[str, bool],
) -> ProjectSubmissionOut:
    project = await session.get(Project, project_id)
    if project is None:
        raise NotFoundError("Project not found.")

    parsed = urlparse(artifact_url)
    url_ok = parsed.scheme in ("http", "https") and bool(parsed.netloc)
    checks = {
        "artifact_url_valid": url_ok,
        "self_assessment_complete": len(self_assessment) >= len(project.rubric),
    }
    status = "submitted" if url_ok else "needs_work"

    submission = ProjectSubmission(
        project_id=project.id, user_id=user_id, artifact_url=artifact_url,
        self_assessment=self_assessment, check_results=checks, status=status,
    )
    session.add(submission)
    await session.commit()
    out = ProjectSubmissionOut.model_validate(submission, from_attributes=True)  # before award_xp

    if url_ok:
        await game.award_xp(
            session, user_id, reason="project_submitted", ref_type="project", ref_id=str(project.id)
        )
    return out
