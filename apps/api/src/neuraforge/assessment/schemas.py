from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class QuestionPublic(BaseModel):
    """Learner-facing view — answer_key is deliberately excluded."""

    id: UUID
    qtype: str
    bank: str
    body: dict
    topic_tags: list[str]
    difficulty: int
    bloom: str | None


class AttemptStart(BaseModel):
    attempt_id: UUID
    quiz_id: UUID
    questions: list[QuestionPublic]
    time_limit_s: int | None


class AnswerResult(BaseModel):
    correct: bool | None
    message: str


class AttemptFinishResult(BaseModel):
    score: float
    passed: bool
    pass_threshold: int
    xp_awarded: bool
    explanations: dict[str, dict]


class QuizOut(BaseModel):
    id: UUID
    kind: str
    lesson_id: UUID | None
    pass_threshold: int
    time_limit_s: int | None
    question_count: int


class TestResultOut(BaseModel):
    name: str
    passed: bool
    message: str


class SubmissionResult(BaseModel):
    submission_id: UUID
    status: str
    stdout: str
    error: str | None = None
    tests: list[TestResultOut] | None = None
    xp_awarded: bool
    ms: int


class ExercisePublic(BaseModel):
    id: UUID
    lesson_id: UUID
    title: str
    brief: str
    starter_code: str
    hints: list[str]


class ProjectOut(BaseModel):
    id: UUID
    kind: str
    month: int
    week: int | None
    title: str
    brief_md: str
    rubric: list[str]


class ProjectSubmissionOut(BaseModel):
    id: UUID
    project_id: UUID
    artifact_url: str
    self_assessment: dict
    check_results: dict
    status: str
    submitted_at: datetime
