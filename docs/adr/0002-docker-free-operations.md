# ADR-0002: Docker-free build, CI, and deployment

**Status:** Accepted (records binding SRS constraint C-1) · **Date:** 2026-07-16 · **Phase:** 2

## Context
The product mandate prohibits Docker and all container tooling in development, CI, and
production — both as an engineering constraint and as pedagogy: Month 12 teaches learners to
deploy AI systems on a native Python/Linux stack, and the platform itself must be the reference
implementation.

## Decision
Reproducibility and isolation are achieved with:
- **Environments:** `uv` lockfiles per service (`uv sync --frozen`), pinned Python via `uv python install`, pinned apt package list checked by `scripts/drift-check.sh`.
- **Artifacts:** GitHub Actions builds versioned tarballs (Python wheel/sdist + `next build` output + content artifact) — no registries, no images.
- **Deployment:** `releases/<ts>` + `current` symlink; idempotent `provision.sh` / `deploy.sh`; systemd units in `infra/` (declarative, in-repo).
- **Isolation:** systemd unit hardening + `systemd-run` transient scopes (ADR-0006) instead of container namespaces.
- **Parity:** staging is a scripted clone of production; CI runs services natively (apt-installed Postgres/Redis on runners).

## Consequences
- ✅ Simpler mental model; the whole stack is teachable in Month 12.
- ✅ No image build/pull pipeline; deploys are rsync-fast.
- ⚠️ Environment drift is a managed risk (R-7): mitigated by lockfiles, drift-check in CI, and staging mirror.
- ⚠️ Dependencies with system libs (e.g. torch) are pinned to wheels; any future dep requiring compilation gets a documented apt recipe in `infra/apt-packages.txt`.
