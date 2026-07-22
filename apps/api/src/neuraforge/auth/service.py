import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.errors import DomainError
from .models import EmailToken, RefreshToken, User
from . import security

log = logging.getLogger("neuraforge.auth")


class AuthError(DomainError):
    status = 401
    title = "Authentication failed"


class ConflictError(DomainError):
    status = 409
    title = "Conflict"


def _now() -> datetime:
    return datetime.now(UTC)


# ── registration & verification (FR-AUTH-1) ─────────────────────────────
async def register(
    session: AsyncSession, *, email: str, password: str, display_name: str, tz: str
) -> tuple[User, str]:
    existing = await session.scalar(select(User).where(User.email == email.lower()))
    if existing:
        raise ConflictError("An account with this email already exists.")

    user = User(
        email=email.lower(),
        password_hash=security.hash_password(password),
        display_name=display_name,
        tz=tz,
    )
    session.add(user)
    await session.flush()

    token, token_hash = security.new_opaque_token()
    session.add(EmailToken(
        user_id=user.id,
        purpose="verify_email",
        token_hash=token_hash,
        expires_at=_now() + timedelta(seconds=get_settings().verify_token_ttl_s),
    ))
    await session.commit()

    # SMTP integration lands with the worker tier (Phase 12 ops); dev logs the link.
    log.info("verify link: /auth/verify-email?token=%s (user %s)", token, user.email)
    return user, token


async def verify_email(session: AsyncSession, token: str) -> User:
    row = await session.scalar(
        select(EmailToken).where(
            EmailToken.token_hash == security.hash_opaque(token),
            EmailToken.purpose == "verify_email",
        )
    )
    if row is None or row.consumed_at is not None:
        raise AuthError("Verification link is invalid or already used.")
    expires = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)
    if expires < _now():
        raise AuthError("Verification link expired — register again to get a new one.")

    row.consumed_at = _now()
    user = await session.get(User, row.user_id)
    assert user is not None
    user.email_verified_at = _now()
    await session.commit()
    return user


# ── login & token issue (FR-AUTH-3) ─────────────────────────────────────
async def login(
    session: AsyncSession, *, email: str, password: str,
    ip: str | None, user_agent: str | None,
) -> tuple[User, str, str]:
    """Returns (user, access_jwt, refresh_token_plaintext)."""
    user = await session.scalar(select(User).where(User.email == email.lower()))
    # uniform error: never reveal which factor failed
    if user is None or not user.password_hash or not security.verify_password(
        user.password_hash, password
    ):
        raise AuthError("Invalid email or password.")
    if user.email_verified_at is None:
        raise AuthError("Email not verified — check your inbox for the link.")
    if user.deleted_at is not None:
        raise AuthError("This account is closed.")

    refresh, refresh_hash = security.new_opaque_token()
    session.add(RefreshToken(
        user_id=user.id,
        family_id=uuid.uuid4(),
        token_hash=refresh_hash,
        ip=ip,
        user_agent=(user_agent or "")[:400] or None,
        expires_at=_now() + timedelta(seconds=get_settings().refresh_token_ttl_s),
    ))
    await session.commit()

    access = security.make_access_token(user.id, user.role, user.token_version)
    return user, access, refresh


async def _revoke_family(session: AsyncSession, family_id: uuid.UUID) -> None:
    rows = await session.scalars(
        select(RefreshToken).where(RefreshToken.family_id == family_id)
    )
    now = _now()
    for r in rows:
        if r.revoked_at is None:
            r.revoked_at = now


async def refresh(
    session: AsyncSession, *, presented: str, ip: str | None, user_agent: str | None,
) -> tuple[User, str, str]:
    """Rotate the refresh token. Reuse of a rotated token revokes the family."""
    row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == security.hash_opaque(presented))
    )
    if row is None:
        raise AuthError("Session not found — sign in again.")

    if row.rotated_at is not None:
        # Reuse detected (ADR-0007): kill the whole family.
        await _revoke_family(session, row.family_id)
        await session.commit()
        log.warning("refresh reuse detected — family %s revoked", row.family_id)
        raise AuthError("Session invalidated for safety — sign in again.")
    if row.revoked_at is not None:
        raise AuthError("Session revoked — sign in again.")
    expires = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)
    if expires < _now():
        raise AuthError("Session expired — sign in again.")

    user = await session.get(User, row.user_id)
    if user is None or user.deleted_at is not None:
        raise AuthError("Account unavailable.")

    row.rotated_at = _now()
    new_refresh, new_hash = security.new_opaque_token()
    session.add(RefreshToken(
        user_id=user.id,
        family_id=row.family_id,
        token_hash=new_hash,
        ip=ip,
        user_agent=(user_agent or "")[:400] or None,
        expires_at=_now() + timedelta(seconds=get_settings().refresh_token_ttl_s),
    ))
    await session.commit()

    access = security.make_access_token(user.id, user.role, user.token_version)
    return user, access, new_refresh


async def logout(session: AsyncSession, presented: str | None) -> None:
    if not presented:
        return
    row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == security.hash_opaque(presented))
    )
    if row:
        await _revoke_family(session, row.family_id)
        await session.commit()


# ── sessions (FR-AUTH-7) ────────────────────────────────────────────────
async def list_sessions(
    session: AsyncSession, user_id: uuid.UUID, current_hash: str | None
) -> list[dict]:
    rows = (await session.scalars(
        select(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .order_by(RefreshToken.created_at.desc())
    )).all()
    families: dict[uuid.UUID, RefreshToken] = {}
    current_family = None
    for r in rows:
        families.setdefault(r.family_id, r)
        if current_hash and r.token_hash == current_hash:
            current_family = r.family_id
    return [
        {
            "family_id": fid,
            "created_at": r.created_at,
            "ip": r.ip,
            "user_agent": r.user_agent,
            "current": fid == current_family,
        }
        for fid, r in families.items()
    ]


async def revoke_session(session: AsyncSession, user_id: uuid.UUID, family_id: uuid.UUID) -> None:
    rows = (await session.scalars(
        select(RefreshToken).where(
            RefreshToken.family_id == family_id, RefreshToken.user_id == user_id
        )
    )).all()
    if not rows:
        raise AuthError("Unknown session.")
    await _revoke_family(session, family_id)
    await session.commit()
