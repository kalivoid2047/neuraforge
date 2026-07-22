import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.errors import DomainError, NotFoundError
from .models import TutorMessage, TutorThread, TutorUsageDaily
from .provider import ProviderUnavailable, stream_chat
from .retrieval import Chunk, retrieve

SYSTEM_PROMPT = """You are Ember, the Neuraforge AI tutor — a brilliant professor who still \
writes code every day. Rigorous, warm, direct, allergic to hand-waving.

Rules (non-negotiable):
- Ground answers in the provided CURRICULUM CONTEXT; cite it. If the context is \
insufficient, say so and answer from first principles, flagged as such.
- Teach intuition before formalism. Offer to go deeper: math, then code.
- NEVER reveal solutions to active graded exercises or exam answers. Guide with \
questions and hints instead.
- Prefer short, precise answers with one concrete example over long lectures."""


class BudgetExceeded(DomainError):
    status = 429
    title = "Daily Ember budget reached"


class TutorDisabled(DomainError):
    status = 503
    title = "Ember is disabled"


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


async def _check_budget(session: AsyncSession, user_id: uuid.UUID) -> TutorUsageDaily:
    today = datetime.now(UTC).date()
    usage = await session.get(TutorUsageDaily, (user_id, today))
    if usage is None:
        usage = TutorUsageDaily(user_id=user_id, for_date=today, tokens=0)
        session.add(usage)
        await session.flush()
    if usage.tokens >= get_settings().ember_daily_token_budget:
        raise BudgetExceeded(
            "You've used today's tutor budget — it resets at midnight UTC. "
            "Non-AI hints and the curriculum remain available."
        )
    return usage


async def create_thread(
    session: AsyncSession, user_id: uuid.UUID, context: dict | None
) -> TutorThread:
    thread = TutorThread(user_id=user_id, context=context or {})
    session.add(thread)
    await session.commit()
    return thread


async def list_threads(session: AsyncSession, user_id: uuid.UUID) -> list[TutorThread]:
    return list(await session.scalars(
        select(TutorThread).where(TutorThread.user_id == user_id)
        .order_by(TutorThread.created_at.desc())
    ))


async def delete_thread(session: AsyncSession, user_id: uuid.UUID, thread_id: uuid.UUID) -> None:
    thread = await session.get(TutorThread, thread_id)
    if thread is None or thread.user_id != user_id:
        raise NotFoundError("Thread not found.")
    await session.delete(thread)
    await session.commit()


def _fallback_answer(question: str, chunks: list[Chunk]) -> str:
    """Non-AI degrade path (P-6): grounded excerpts instead of generation."""
    if not chunks:
        return (
            "Ember's model isn't reachable right now, and I couldn't find curriculum "
            "material matching that question. Try rephrasing with a concept name "
            "(e.g. “softmax”, “attention heads”)."
        )
    lines = [
        "Ember's model isn't reachable right now, so here is what the curriculum "
        "says — retrieved, not generated:",
        "",
    ]
    for i, c in enumerate(chunks, 1):
        lines.append(f"{i}. **{c.title}** — {c.body.strip()}")
    lines.append("")
    lines.append("Open the cited lesson sections for the full treatment.")
    return "\n".join(lines)


class PreparedMessage:
    """Guardrails run in prepare_message (before the response starts) so
    failures surface as problem+json, not a broken stream."""

    def __init__(self, thread: TutorThread, usage: TutorUsageDaily,
                 chunks: list[Chunk], history: list[dict], text: str):
        self.thread = thread
        self.usage = usage
        self.chunks = chunks
        self.history = history
        self.text = text
        self.citations = [c.citation() for c in chunks]


async def prepare_message(
    session: AsyncSession, user_id: uuid.UUID, thread_id: uuid.UUID, text: str
) -> PreparedMessage:
    if not get_settings().ember_enabled:
        raise TutorDisabled("Ember is switched off by the administrator.")

    thread = await session.get(TutorThread, thread_id)
    if thread is None or thread.user_id != user_id:
        raise NotFoundError("Thread not found.")

    usage = await _check_budget(session, user_id)
    scope = thread.context.get("lesson_slug")
    chunks = await retrieve(session, text, scope_lesson=scope)

    session.add(TutorMessage(thread_id=thread.id, role="user", content=text,
                             tokens_in=_estimate_tokens(text)))
    if thread.title is None:
        thread.title = text[:80]
    await session.commit()

    context_block = "\n\n".join(
        f"[{i+1}] {c.title}:\n{c.body}" for i, c in enumerate(chunks)
    ) or "(no matching curriculum content)"

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    prior = (await session.scalars(
        select(TutorMessage).where(TutorMessage.thread_id == thread.id)
        .order_by(TutorMessage.created_at.desc()).limit(10)
    )).all()
    for m in reversed(prior[1:]):  # skip the just-inserted user message
        history.append({"role": m.role, "content": m.content})
    history.append({
        "role": "user",
        "content": f"CURRICULUM CONTEXT:\n{context_block}\n\nQUESTION: {text}",
    })
    return PreparedMessage(thread, usage, chunks, history, text)


async def stream_message(session: AsyncSession, prep: PreparedMessage) -> AsyncIterator[dict]:
    """Yields event dicts: {type: meta|token|done, ...}. Persists the answer."""
    thread, usage, chunks, history, text = (
        prep.thread, prep.usage, prep.chunks, prep.history, prep.text,
    )
    citations = prep.citations
    yield {"type": "meta", "citations": citations, "fallback": False}

    answer_parts: list[str] = []
    fallback = False
    try:
        async for token in stream_chat(history):
            answer_parts.append(token)
            yield {"type": "token", "text": token}
    except ProviderUnavailable:
        fallback = True
        answer = _fallback_answer(text, chunks)
        answer_parts = [answer]
        yield {"type": "meta", "citations": citations, "fallback": True}
        yield {"type": "token", "text": answer}

    answer = "".join(answer_parts)
    tokens_out = _estimate_tokens(answer)
    session.add(TutorMessage(
        thread_id=thread.id, role="assistant", content=answer,
        citations=citations, fallback=fallback, tokens_out=tokens_out,
    ))
    usage.tokens += _estimate_tokens(text) + tokens_out
    await session.commit()
    yield {"type": "done", "fallback": fallback}
