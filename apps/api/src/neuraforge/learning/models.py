import uuid
from datetime import date, datetime

from sqlalchemy import JSON, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db import Base
from ..core.ids import uuid7

JsonDict = JSON().with_variant(JSONB(), "postgresql")


class Enrollment(Base):
    __tablename__ = "enrollments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    started_on: Mapped[datetime] = mapped_column(server_default=func.now())
    pace: Mapped[dict] = mapped_column(JsonDict, default=lambda: {"lessons_per_week": 5})


class LessonProgress(Base):
    """Per-learner lesson state (DATABASE.md §6). section_ticks: anchor → ISO timestamp."""

    __tablename__ = "lesson_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[str] = mapped_column(String(16), default="not_started")
    section_ticks: Mapped[dict] = mapped_column(JsonDict, default=dict)
    resume_anchor: Mapped[str | None] = mapped_column(String(100), default=None)
    started_at: Mapped[datetime | None] = mapped_column(default=None)
    completed_at: Mapped[datetime | None] = mapped_column(default=None)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


# ── spaced repetition (FR-LEARN-2/3, DATABASE.md §6) ────────────────────


class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), default=None
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), default=None
    )  # NULL owner = system deck
    title: Mapped[str] = mapped_column(String(200))

    cards: Mapped[list["FlashCard"]] = relationship(
        back_populates="deck", cascade="all, delete-orphan"
    )


class FlashCard(Base):
    __tablename__ = "flash_cards"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    deck_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"))
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    front_md: Mapped[str] = mapped_column(Text)
    back_md: Mapped[str] = mapped_column(Text)

    deck: Mapped[Deck] = relationship(back_populates="cards")


class ReviewState(Base):
    """Per-(user, card) scheduler state. `stability` is the current interval
    in days, `difficulty` 1–10; see review.py for the update rules."""

    __tablename__ = "review_states"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("flash_cards.id", ondelete="CASCADE"), primary_key=True
    )
    stability: Mapped[float] = mapped_column(default=0.0)
    difficulty: Mapped[float] = mapped_column(default=5.0)
    due_at: Mapped[datetime]
    reps: Mapped[int] = mapped_column(default=0)
    lapses: Mapped[int] = mapped_column(default=0)
    last_review: Mapped[datetime | None] = mapped_column(default=None)


class ReviewLog(Base):
    __tablename__ = "review_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    card_id: Mapped[uuid.UUID]
    grade: Mapped[int] = mapped_column(SmallInteger)  # 1 again · 2 hard · 3 good · 4 easy
    reviewed_at: Mapped[datetime] = mapped_column(server_default=func.now())


# ── Daily Sparks (FR-LEARN-5) ───────────────────────────────────────────


class Spark(Base):
    """Pool of short daily challenges; the question-bank integration (Phase 11)
    will extend refs to real exercises."""

    __tablename__ = "sparks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    title: Mapped[str] = mapped_column(String(200))
    detail: Mapped[str] = mapped_column(Text)
    minutes: Mapped[int] = mapped_column(SmallInteger, default=10)
    month: Mapped[int] = mapped_column(SmallInteger)  # difficulty-matched to curriculum month


class SparkAssignment(Base):
    __tablename__ = "spark_assignments"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    for_date: Mapped[date] = mapped_column(primary_key=True)  # in the user's tz
    spark_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sparks.id", ondelete="CASCADE"))
    completed_at: Mapped[datetime | None] = mapped_column(default=None)
