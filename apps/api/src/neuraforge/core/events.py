"""In-process domain events (ARCHITECTURE.md §3).

Modules communicate side effects through events, never by importing each
other's internals — e.g. learning emits LessonCompleted; gamification
(Phase 8) subscribes to award XP. Sync dispatch; Celery fan-out later.
"""

import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger("neuraforge.events")

Handler = Callable[[Any], Awaitable[None]]
_subscribers: dict[type, list[Handler]] = defaultdict(list)


@dataclass(frozen=True)
class Event:
    pass


@dataclass(frozen=True)
class SectionCompleted(Event):
    user_id: str
    lesson_slug: str
    anchor: str


@dataclass(frozen=True)
class LessonCompleted(Event):
    user_id: str
    lesson_slug: str
    payload: dict = field(default_factory=dict)


def subscribe(event_type: type) -> Callable[[Handler], Handler]:
    def register(handler: Handler) -> Handler:
        _subscribers[event_type].append(handler)
        return handler

    return register


async def emit(event: Event) -> None:
    for handler in _subscribers[type(event)]:
        try:
            await handler(event)
        except Exception:  # handler failure never breaks the emitting use-case (P-6)
            log.exception("event handler failed for %s", type(event).__name__)
