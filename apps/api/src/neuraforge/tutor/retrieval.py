"""Curriculum retrieval for Ember grounding (FR-TUTOR-6).

v1: keyword-overlap scoring over lesson metadata, sections, and system flash
cards — portable across SQLite/PG. Sits behind `retrieve()` so the pgvector
hybrid retriever (ADR-0008) replaces the internals without touching callers.
"""

import re
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..content.models import Lesson, Section
from ..learning.models import Deck, FlashCard

_STOP = {
    "the", "a", "an", "is", "are", "was", "what", "why", "how", "do", "does",
    "in", "of", "to", "for", "and", "or", "it", "i", "me", "my", "we", "you",
    "explain", "tell", "about", "please", "can",
}


def _terms(text: str) -> set[str]:
    return {
        w for w in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())
        if w not in _STOP and len(w) > 1
    }


@dataclass
class Chunk:
    source: str          # "lesson" | "card"
    lesson_slug: str | None
    anchor: str | None
    title: str
    body: str
    score: float = 0.0

    def citation(self) -> dict:
        return {
            "source": self.source,
            "lesson_slug": self.lesson_slug,
            "anchor": self.anchor,
            "title": self.title,
        }


async def _corpus(session: AsyncSession, scope_lesson: str | None) -> list[Chunk]:
    chunks: list[Chunk] = []

    lessons = (await session.scalars(select(Lesson))).all()
    lesson_by_id: dict[uuid.UUID, Lesson] = {ls.id: ls for ls in lessons}
    for lesson in lessons:
        objectives = lesson.meta.get("objectives", [])
        body = f"{lesson.title}. " + " ".join(objectives)
        chunks.append(Chunk("lesson", lesson.slug, None, lesson.title, body))

    sections = (await session.scalars(select(Section))).all()
    for s in sections:
        lesson = lesson_by_id.get(s.lesson_id)
        if lesson:
            chunks.append(Chunk(
                "lesson", lesson.slug, s.anchor,
                f"{lesson.title} § {s.title}", f"{s.title} ({s.kind}) in {lesson.title}",
            ))

    cards = (await session.execute(
        select(FlashCard, Deck).join(Deck, Deck.id == FlashCard.deck_id)
        .where(FlashCard.owner_id.is_(None))
    )).all()
    for card, deck in cards:
        lesson = lesson_by_id.get(deck.lesson_id) if deck.lesson_id else None
        chunks.append(Chunk(
            "card", lesson.slug if lesson else None, None,
            deck.title, f"{card.front_md} {card.back_md}",
        ))

    if scope_lesson:  # lesson-scope boost (ARCHITECTURE.md §10)
        for c in chunks:
            if c.lesson_slug == scope_lesson:
                c.score += 0.5
    return chunks


async def retrieve(
    session: AsyncSession, query: str, *, scope_lesson: str | None = None, k: int = 4
) -> list[Chunk]:
    q_terms = _terms(query)
    if not q_terms:
        return []
    chunks = await _corpus(session, scope_lesson)
    for c in chunks:
        overlap = q_terms & _terms(c.body)
        c.score += len(overlap) / max(3, len(q_terms))
    ranked = sorted((c for c in chunks if c.score > 0.15), key=lambda c: -c.score)
    return ranked[:k]
