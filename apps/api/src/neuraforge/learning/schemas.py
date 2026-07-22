from pydantic import BaseModel


class TickResult(BaseModel):
    lesson_slug: str
    anchor: str
    lesson_status: str
    ticked_sections: int
    total_sections: int


class ContinueTarget(BaseModel):
    slug: str
    code: str
    title: str
    progress_pct: int
    resume_anchor: str | None


class ProgressSummary(BaseModel):
    lessons_completed: int
    lessons_total: int
    overall_pct: int
    current: ContinueTarget | None
