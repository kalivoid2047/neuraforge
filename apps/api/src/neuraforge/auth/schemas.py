from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=200)
    display_name: str = Field(min_length=1, max_length=120)
    tz: str = "UTC"


class RegisterOut(BaseModel):
    message: str
    # Dev only (is_dev): surfaces the verification token since no SMTP is wired.
    dev_verification_token: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeOut(BaseModel):
    id: UUID
    email: str
    display_name: str
    role: str
    tz: str
    email_verified: bool


class SessionOut(BaseModel):
    family_id: UUID
    created_at: datetime
    ip: str | None
    user_agent: str | None
    current: bool
