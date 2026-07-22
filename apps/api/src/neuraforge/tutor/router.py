import json
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.deps import CurrentUser
from ..core.db import get_session
from . import service

router = APIRouter(prefix="/tutor", tags=["tutor"])
Session = Annotated[AsyncSession, Depends(get_session)]


class ThreadIn(BaseModel):
    context: dict = Field(default_factory=dict)  # {"lesson_slug": "..."} scope


class ThreadOut(BaseModel):
    id: uuid.UUID
    title: str | None
    context: dict
    created_at: datetime


class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


@router.post("/threads", response_model=ThreadOut, status_code=201)
async def create_thread(session: Session, user: CurrentUser, body: ThreadIn) -> ThreadOut:
    thread = await service.create_thread(session, user.id, body.context)
    return ThreadOut.model_validate(thread, from_attributes=True)


@router.get("/threads", response_model=list[ThreadOut])
async def list_threads(session: Session, user: CurrentUser) -> list[ThreadOut]:
    rows = await service.list_threads(session, user.id)
    return [ThreadOut.model_validate(t, from_attributes=True) for t in rows]


@router.delete("/threads/{thread_id}", status_code=204)
async def delete_thread(session: Session, user: CurrentUser, thread_id: uuid.UUID) -> None:
    await service.delete_thread(session, user.id, thread_id)


@router.post("/threads/{thread_id}/messages")
async def send_message(
    session: Session, user: CurrentUser, thread_id: uuid.UUID, body: MessageIn
) -> StreamingResponse:
    """Server-Sent Events stream: meta → token* → done (ADR-0010 SSE mirror).

    Guardrails (404 / 429 budget / 503 disabled) run in prepare_message so
    they return problem+json — only a valid request starts the stream.
    """
    prep = await service.prepare_message(session, user.id, thread_id, body.text)

    async def sse():
        async for event in service.stream_message(session, prep):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
