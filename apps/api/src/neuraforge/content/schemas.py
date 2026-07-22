from pydantic import BaseModel


class SectionOut(BaseModel):
    anchor: str
    kind: str
    title: str
    done: bool = False


class LessonSummary(BaseModel):
    slug: str
    title: str
    ord: int
    minutes: int
    difficulty: int
    status: str  # learner status: done | current | todo


class WeekOut(BaseModel):
    number: int
    title: str
    lessons: list[LessonSummary]


class MonthOut(BaseModel):
    number: int
    title: str
    progress: int  # % of lessons completed
    weeks: list[WeekOut]


class CurriculumOut(BaseModel):
    months: list[MonthOut]


class LessonDetail(BaseModel):
    slug: str
    code: str  # "7.2.3"
    title: str
    minutes: int
    difficulty: int
    prereqs: list[str]
    objectives: list[str]
    sections: list[SectionOut]
    progress_status: str
    resume_anchor: str | None
