import secrets
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.db import get_session
from . import service
from .deps import CurrentUser
from .schemas import LoginIn, MeOut, RegisterIn, RegisterOut, SessionOut, TokenOut
from .security import hash_opaque
from .service import AuthError

router = APIRouter(prefix="/auth", tags=["auth"])
Session = Annotated[AsyncSession, Depends(get_session)]

REFRESH_COOKIE = "nf_refresh"
CSRF_COOKIE = "nf_csrf"


def _cookie_path() -> str:
    return f"{get_settings().api_prefix}/auth"


def _set_auth_cookies(response: Response, refresh: str) -> None:
    secure = not get_settings().is_dev  # http://localhost in dev
    response.set_cookie(
        REFRESH_COOKIE, refresh,
        httponly=True, secure=secure, samesite="lax",
        path=_cookie_path(), max_age=get_settings().refresh_token_ttl_s,
    )
    # CSRF double-submit: readable cookie, echoed back via X-CSRF-Token header
    response.set_cookie(
        CSRF_COOKIE, secrets.token_urlsafe(24),
        httponly=False, secure=secure, samesite="lax",
        path=_cookie_path(), max_age=get_settings().refresh_token_ttl_s,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE, path=_cookie_path())
    response.delete_cookie(CSRF_COOKIE, path=_cookie_path())


def _check_csrf(request: Request) -> None:
    cookie = request.cookies.get(CSRF_COOKIE)
    header = request.headers.get("X-CSRF-Token")
    if not cookie or not header or not secrets.compare_digest(cookie, header):
        raise AuthError("CSRF check failed.")


@router.post("/register", response_model=RegisterOut, status_code=201)
async def register(session: Session, body: RegisterIn) -> RegisterOut:
    _, token = await service.register(
        session,
        email=body.email, password=body.password,
        display_name=body.display_name, tz=body.tz,
    )
    return RegisterOut(
        message="Account created — verify your email to sign in.",
        dev_verification_token=token if get_settings().is_dev else None,
    )


@router.get("/verify-email")
async def verify_email(session: Session, token: str) -> dict:
    user = await service.verify_email(session, token)
    return {"message": f"Email verified — welcome to the forge, {user.display_name}."}


@router.post("/login", response_model=TokenOut)
async def login(session: Session, body: LoginIn, request: Request, response: Response) -> TokenOut:
    _, access, refresh = await service.login(
        session,
        email=body.email, password=body.password,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    _set_auth_cookies(response, refresh)
    return TokenOut(access_token=access, expires_in=get_settings().access_token_ttl_s)


@router.post("/refresh", response_model=TokenOut)
async def refresh(session: Session, request: Request, response: Response) -> TokenOut:
    _check_csrf(request)
    presented = request.cookies.get(REFRESH_COOKIE)
    if not presented:
        raise AuthError("No session cookie.")
    _, access, new_refresh = await service.refresh(
        session,
        presented=presented,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    _set_auth_cookies(response, new_refresh)
    return TokenOut(access_token=access, expires_in=get_settings().access_token_ttl_s)


@router.post("/logout", status_code=204)
async def logout(session: Session, request: Request, response: Response) -> None:
    _check_csrf(request)
    await service.logout(session, request.cookies.get(REFRESH_COOKIE))
    _clear_auth_cookies(response)


@router.get("/sessions", response_model=list[SessionOut])
async def sessions(session: Session, user: CurrentUser, request: Request) -> list[SessionOut]:
    presented = request.cookies.get(REFRESH_COOKIE)
    rows = await service.list_sessions(
        session, user.id, hash_opaque(presented) if presented else None
    )
    return [SessionOut(**r) for r in rows]


@router.delete("/sessions/{family_id}", status_code=204)
async def revoke_session(session: Session, user: CurrentUser, family_id: uuid.UUID) -> None:
    await service.revoke_session(session, user.id, family_id)


@router.get("/me", response_model=MeOut)
async def me(user: CurrentUser) -> MeOut:
    return MeOut(
        id=user.id, email=user.email, display_name=user.display_name,
        role=user.role, tz=user.tz, email_verified=user.email_verified_at is not None,
    )
