import uuid
from typing import Annotated

import jwt as pyjwt
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.db import get_session
from ..core.errors import DomainError
from .models import User
from .security import decode_access_token

DEMO_EMAIL = "amina@neuraforge.dev"


class Unauthorized(DomainError):
    status = 401
    title = "Unauthorized"


async def get_current_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Bearer-JWT auth (ADR-0007).

    Dev fallback: with NF_DEV_AUTOLOGIN=true and no Authorization header,
    resolves the seeded demo learner so the UI works pre-token-plumbing.
    Config refuses dev_autologin outside env=dev.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            claims = decode_access_token(auth.removeprefix("Bearer "))
        except pyjwt.PyJWTError:
            raise Unauthorized("Invalid or expired access token.")
        try:
            user_id = uuid.UUID(claims["sub"])
        except (KeyError, ValueError):
            raise Unauthorized("Malformed token subject.")
        user = await session.get(User, user_id)
        if user is None or user.deleted_at is not None:
            raise Unauthorized("Account unavailable.")
        if claims.get("ver") != user.token_version:
            raise Unauthorized("Token superseded — sign in again.")
        return user

    settings = get_settings()
    if settings.is_dev and settings.dev_autologin:
        demo = await session.scalar(select(User).where(User.email == DEMO_EMAIL))
        if demo is not None:
            return demo
    raise Unauthorized("Authentication required.")


CurrentUser = Annotated[User, Depends(get_current_user)]
