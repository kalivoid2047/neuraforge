import uuid
from datetime import date, datetime

from sqlalchemy import JSON, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db import Base
from ..core.ids import uuid7

JsonDict = JSON().with_variant(JSONB(), "postgresql")


class TutorThread(Base):
    __tablename__ = "tutor_threads"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str | None] = mapped_column(String(200), default=None)
    context: Mapped[dict] = mapped_column(JsonDict, default=dict)  # lesson scope, depth mode
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    messages: Mapped[list["TutorMessage"]] = relationship(
        back_populates="thread", order_by="TutorMessage.created_at",
        cascade="all, delete-orphan",
    )


class TutorMessage(Base):
    __tablename__ = "tutor_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tutor_threads.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(16))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[list] = mapped_column(JsonDict, default=list)
    fallback: Mapped[bool] = mapped_column(default=False)  # true = non-AI retrieval answer
    tokens_in: Mapped[int] = mapped_column(default=0)
    tokens_out: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    thread: Mapped[TutorThread] = relationship(back_populates="messages")


class TutorUsageDaily(Base):
    """Budget enforcement (FR-TUTOR-8)."""

    __tablename__ = "tutor_usage_daily"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    for_date: Mapped[date] = mapped_column(primary_key=True)
    tokens: Mapped[int] = mapped_column(default=0)
