# ADR-0009: Celery + Redis for background jobs and scheduling

**Status:** Accepted · **Date:** 2026-07-16 · **Phase:** 2

## Context
Grading, emails, certificates, embeddings, per-timezone streak rollovers, FSRS queue builds,
and analytics rollups all need queued/scheduled execution (ARCHITECTURE.md §8). Candidates:
Celery, RQ, arq, Dramatiq; Kafka-class brokers rejected outright (ops weight, no ordering needs).

## Decision
**Celery 5 with Redis** as broker; durable job *outcomes* persisted to PostgreSQL by the jobs
themselves (Redis result backend used only for transient chaining). Queues: `grading`, `ai`,
`default`, plus **Celery Beat** (singleton via Redis lock) for periodic work. Workers are
templated systemd units (`neuraforge-worker@grading.service`) sharing the API codebase. All
tasks idempotent (natural keys/upserts); retries with exponential backoff + dead-letter queue
surfaced in the admin console (FR-ADMIN-2).

## Consequences
- ✅ Reuses Redis (already present); per-queue scaling by starting more unit instances; beat covers all cron-like needs without OS crontabs.
- ⚠️ Redis broker = at-least-once with possible redelivery; idempotency is therefore a task-authoring rule enforced in review, and a broker outage pauses (not loses) durable work since sources of truth live in PG.
