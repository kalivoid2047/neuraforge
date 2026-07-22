# ADR-0010: Single multiplexed WebSocket + Redis pub/sub fan-out

**Status:** Accepted · **Date:** 2026-07-16 · **Phase:** 2

## Context
Three real-time streams (runner logs, Ember tokens, gamification events) must reach a browser
that may be connected to any API worker/instance (stateless tier, P-4).

## Decision
One WebSocket per client (`/ws`, ticket-authed per ADR-0007) multiplexing typed channels
(`run.*`, `tutor.*`, `game`); producers publish to **Redis pub/sub** topics; every API instance
subscribes and forwards to its local sockets. Versioned message envelope `{v, type, data}`.
SSE mirrors for `tutor.*`/`run.*` and polling endpoints as graceful fallbacks. Client reconnect
with resume: on reconnect the client re-fetches authoritative state via REST (queries are the
source of truth; WS is advisory/invalidation), so missed messages never corrupt state.

## Consequences
- ✅ Any-instance delivery without sticky sessions; one connection per tab keeps Nginx/file-descriptor budgets predictable.
- ⚠️ Redis pub/sub is fire-and-forget — acceptable because WS is a cache-invalidation/UX layer, never the system of record; anything durable is in PostgreSQL first.
