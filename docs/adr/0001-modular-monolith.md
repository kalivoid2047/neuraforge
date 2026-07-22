# ADR-0001: Modular monolith over microservices

**Status:** Accepted · **Date:** 2026-07-16 · **Phase:** 2

## Context
Neuraforge has ~13 functional modules (SRS §3), a small team, and a Docker-free ops constraint
(C-1) that makes every additional deployable a real systemd/Nginx/monitoring cost. Untrusted
code execution is the only workload with a fundamentally different risk profile.

## Decision
One FastAPI deployable (`apps/api`) containing all domain modules with enforced internal
boundaries (import-linter contracts; routers → service → repository layering; cross-module side
effects only via in-process domain events). Exactly one additional service: the Code Runner
(ADR-0006). Celery workers run the same codebase under different unit files.

## Consequences
- ✅ One release artifact, one migration stream, simple transactions across modules.
- ✅ Blast-radius isolation preserved where it matters (Runner).
- ⚠️ Module discipline must be enforced by CI (import-linter, per-module DB roles), not habit.
- Future extraction path: any module already communicating via events/services can be split out
  behind the same interface if scale demands (§13 scale-out).
