import uuid

from sqlalchemy import JSON, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db import Base
from ..core.ids import uuid7

JsonDict = JSON().with_variant(JSONB(), "postgresql")


class Lesson(Base):
    """Curriculum index row (DATABASE.md §4). Content bodies live in the
    content artifact (ADR-0005); this table is the queryable index."""

    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("month", "week", "ord"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    month: Mapped[int] = mapped_column(SmallInteger)
    week: Mapped[int] = mapped_column(SmallInteger)
    ord: Mapped[int] = mapped_column(SmallInteger)
    title: Mapped[str] = mapped_column(String(200))
    difficulty: Mapped[int] = mapped_column(SmallInteger)
    est_minutes: Mapped[int] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(String(16), default="published")
    meta: Mapped[dict] = mapped_column(JsonDict, default=dict)  # month/week titles, objectives…

    sections: Mapped[list["Section"]] = relationship(
        back_populates="lesson", order_by="Section.ord", cascade="all, delete-orphan"
    )


class Section(Base):
    __tablename__ = "sections"
    __table_args__ = (UniqueConstraint("lesson_id", "anchor"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    anchor: Mapped[str] = mapped_column(String(100))
    kind: Mapped[str] = mapped_column(String(32))
    ord: Mapped[int] = mapped_column(SmallInteger)
    title: Mapped[str] = mapped_column(String(200))

    lesson: Mapped[Lesson] = relationship(back_populates="sections")


class LessonPrereq(Base):
    __tablename__ = "lesson_prereqs"

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True
    )
    prereq_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True
    )
