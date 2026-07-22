import uuid
from datetime import datetime

from sqlalchemy import JSON, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db import Base
from ..core.ids import uuid7

JsonDict = JSON().with_variant(JSONB(), "postgresql")


class Question(Base):
    """Question bank entry (FR-ASSESS-1/4, DATABASE.md §5).

    `answer_key` is the grading authority and must never be included in a
    response schema shown to learners while a quiz is in progress — mirrors
    the vault/core split in DATABASE.md §5 without a second schema, since
    this monolith has one DB; the boundary is enforced in schemas.py instead.
    """

    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    qtype: Mapped[str] = mapped_column(String(16))  # mcq_single|mcq_multi|numeric|code_output|fill_blank|free_text
    bank: Mapped[str] = mapped_column(String(16))  # practice|interview|research|spark|exam_only
    body: Mapped[dict] = mapped_column(JsonDict)  # stem, options… (shape per qtype)
    answer_key: Mapped[dict] = mapped_column(JsonDict)  # never shipped to the client
    explanation: Mapped[dict] = mapped_column(JsonDict, default=dict)  # per-option explanations (FR-ASSESS-2)
    topic_tags: Mapped[list] = mapped_column(JsonDict, default=list)
    month: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    week: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    difficulty: Mapped[int] = mapped_column(SmallInteger)  # 1..5
    bloom: Mapped[str | None] = mapped_column(String(16), default=None)
    status: Mapped[str] = mapped_column(String(16), default="published")


class Quiz(Base):
    """Mini/weekly/monthly/final quiz shell (FR-ASSESS-2/3).

    `blueprint` is either an explicit selection `{"question_ids": [...]}` (used
    for lesson mini-quizzes, authored by hand) or a random-assembly spec
    `{"bank": "practice", "topic_tags": [...], "difficulty": [1, 5], "count": 10}`
    (used for weekly/monthly/final exams assembled from the bank).
    """

    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    kind: Mapped[str] = mapped_column(String(16))  # mini|weekly|monthly|final
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), default=None
    )
    month: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    week: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    blueprint: Mapped[dict] = mapped_column(JsonDict)
    pass_threshold: Mapped[int] = mapped_column(SmallInteger, default=70)
    time_limit_s: Mapped[int | None] = mapped_column(default=None)


class QuizAttempt(Base):
    """Per-attempt instantiation + answers (FR-ASSESS-7 attempt logging)."""

    __tablename__ = "quiz_attempts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question_ids: Mapped[list] = mapped_column(JsonDict)  # randomized selection, frozen at start
    answers: Mapped[dict] = mapped_column(JsonDict, default=dict)  # qid(str) -> {answer, correct, answered_at}
    score: Mapped[float | None] = mapped_column(default=None)
    hints_used: Mapped[int] = mapped_column(SmallInteger, default=0)
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(default=None)


class Exercise(Base):
    """Graded coding exercise (FR-ASSESS-5). `tests` is the hidden/authoritative
    suite — Phase 9's ExerciseCell ships a *separate*, non-authoritative copy
    to the client for instant Tier-1 feedback; this table is never serialized
    to the client directly (see schemas.ExercisePublic)."""

    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    ord: Mapped[int] = mapped_column(SmallInteger, default=1)
    title: Mapped[str] = mapped_column(String(200))
    brief: Mapped[str] = mapped_column(Text, default="")
    starter_code: Mapped[str] = mapped_column(Text)
    tests: Mapped[list] = mapped_column(JsonDict)  # [{name, code}], hidden from the client
    hints: Mapped[list] = mapped_column(JsonDict, default=list)
    limits: Mapped[dict] = mapped_column(JsonDict, default=lambda: {"wall_s": 10, "mem_mb": 256})


class Submission(Base):
    """Server-side replay of a learner's exercise code (FR-ASSESS-5, tier=server)."""

    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(Text)
    attempt_no: Mapped[int] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(String(16), default="queued")  # queued|passed|failed|error|timeout
    results: Mapped[list] = mapped_column(JsonDict, default=list)  # sanitized per-test verdicts
    stdout: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    graded_at: Mapped[datetime | None] = mapped_column(default=None)


class Project(Base):
    """Weekly/Forge project shell (FR-ASSESS-6). `checks` is a list of
    lightweight, server-evaluable check descriptors (MVP: URL-format /
    presence checks — full autograding pipelines are a later iteration)."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    kind: Mapped[str] = mapped_column(String(16))  # weekly|forge
    month: Mapped[int] = mapped_column(SmallInteger)
    week: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    title: Mapped[str] = mapped_column(String(200))
    brief_md: Mapped[str] = mapped_column(Text)
    rubric: Mapped[list] = mapped_column(JsonDict)  # list of criteria strings
    checks: Mapped[list] = mapped_column(JsonDict, default=list)


class ProjectSubmission(Base):
    """A learner's project handoff. `artifact_url` is a link (e.g. a GitHub
    repo/PR) rather than an uploaded file — no object-storage service exists
    yet in this codebase (Phase 11 scope decision); file upload is deferred."""

    __tablename__ = "project_submissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    artifact_url: Mapped[str] = mapped_column(String(500))
    self_assessment: Mapped[dict] = mapped_column(JsonDict, default=dict)  # {criterion: bool}
    check_results: Mapped[dict] = mapped_column(JsonDict, default=dict)
    status: Mapped[str] = mapped_column(String(16), default="submitted")  # submitted|passed|needs_work
    submitted_at: Mapped[datetime] = mapped_column(server_default=func.now())
