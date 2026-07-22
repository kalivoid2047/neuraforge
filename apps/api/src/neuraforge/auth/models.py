import uuid
from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db import Base, TimestampMixin
from ..core.ids import uuid7

JsonDict = JSON().with_variant(JSONB(), "postgresql")


class User(Base, TimestampMixin):
    """Identity (DATABASE.md §3). OAuth + TOTP columns land with those features."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), default=None)
    display_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(16), default="learner")
    tz: Mapped[str] = mapped_column(String(64), default="UTC")
    settings: Mapped[dict] = mapped_column(JsonDict, default=dict)
    token_version: Mapped[int] = mapped_column(default=1)  # global revoke (ADR-0007)
    email_verified_at: Mapped[datetime | None] = mapped_column(default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)


class EmailToken(Base):
    """Verification / reset tokens — stored hashed, single-use (DATABASE.md §3)."""

    __tablename__ = "email_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    purpose: Mapped[str] = mapped_column(String(32))  # verify_email | password_reset
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime]
    consumed_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class RefreshToken(Base):
    """Rotating refresh-token families with reuse detection (ADR-0007).

    rotated_at set ⇒ superseded; presenting it again is reuse ⇒ revoke family.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    family_id: Mapped[uuid.UUID] = mapped_column(index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    ip: Mapped[str | None] = mapped_column(String(45), default=None)
    user_agent: Mapped[str | None] = mapped_column(String(400), default=None)
    expires_at: Mapped[datetime]
    rotated_at: Mapped[datetime | None] = mapped_column(default=None)
    revoked_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
