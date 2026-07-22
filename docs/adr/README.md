# Architecture Decision Records — Index

Format: [MADR-lite](https://adr.github.io/). Status lifecycle: Proposed → Accepted → Superseded.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-modular-monolith.md) | Modular monolith over microservices | Accepted (Phase 2) |
| [0002](0002-docker-free-operations.md) | Docker-free build, CI, and deployment | Accepted (constraint C-1) |
| [0003](0003-uv-environment-management.md) | uv for Python environment & dependency management | Accepted |
| [0004](0004-fastapi-async-sqlalchemy.md) | FastAPI + async SQLAlchemy 2.0 + Pydantic v2 | Accepted |
| [0005](0005-content-as-code.md) | Content-as-code: MDX + YAML compiled via content-CI | Accepted |
| [0006](0006-runner-sandbox.md) | Two-tier code execution: Pyodide + systemd-run sandbox | Accepted |
| [0007](0007-jwt-auth.md) | JWT access + rotating refresh cookie auth | Accepted |
| [0008](0008-pgvector.md) | pgvector for embeddings/semantic search (no dedicated vector DB) | Accepted |
| [0009](0009-celery-redis.md) | Celery + Redis for jobs and scheduling | Accepted |
| [0010](0010-websocket-redis-pubsub.md) | Single WS multiplex + Redis pub/sub fan-out | Accepted |
| [0011](0011-nextjs-rsc-islands.md) | Next.js RSC static-first with interactive islands | Accepted |

New ADRs: copy `template.md`, number sequentially, PR with the change that motivates them.
