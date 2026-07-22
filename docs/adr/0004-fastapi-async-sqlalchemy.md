# ADR-0004: FastAPI + async SQLAlchemy 2.0 + Pydantic v2

**Status:** Accepted · **Date:** 2026-07-16 · **Phase:** 2

## Context
Stack is fixed to FastAPI (SRS C-2). Open choices: sync vs async DB access, ORM style,
serving model.

## Decision
- **Async end-to-end:** asyncpg driver, SQLAlchemy 2.0 async sessions, async routers; Gunicorn with `UvicornWorker` (2·CPU+1 workers, per-worker DB pool ≈15, capped via PgBouncer when scaled).
- **SQLAlchemy 2.0 declarative** models with typed `Mapped[]` annotations; Alembic autogenerate + hand-reviewed migrations (expand-migrate-contract discipline for zero-downtime, §13).
- **Pydantic v2** for all I/O schemas and `pydantic-settings` for `.env` config validation at boot.
- CPU-bound work (grading orchestration, PDF render, embeddings) never runs in the event loop — Celery (ADR-0009) or `run_in_executor`.

## Consequences
- ✅ Meets NFR-PERF-2 latencies with high connection efficiency for WS + streaming workloads.
- ⚠️ Async discipline required (no sync drivers/libraries in request path); enforced by ruff rule set + review checklist.
