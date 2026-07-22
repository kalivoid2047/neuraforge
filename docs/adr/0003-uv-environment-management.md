# ADR-0003: uv for Python environment & dependency management

**Status:** Accepted · **Date:** 2026-07-16 · **Phase:** 2

## Context
Without containers (ADR-0002), lockfile-level reproducibility is the backbone of environment
parity across dev (Windows/macOS/Linux), CI, and production. Candidates: pip+pip-tools, Poetry,
PDM, uv.

## Decision
**uv** everywhere: `uv python install 3.12` (interpreter pinning via `.python-version`),
`uv venv`, `pyproject.toml` + `uv.lock`, `uv sync --frozen` in CI/prod, `uv run` for tooling.
Runner runtime profiles (ADR-0006) are also uv-locked environments. Learners use the same tool —
taught in Month 1, Week 1.

## Consequences
- ✅ Single tool for interpreter + venv + lock + resolution; 10–100× faster installs (matters for CI without layer caching).
- ✅ Cross-platform lockfile with markers covers the Windows-dev / Linux-prod split.
- ⚠️ uv is younger than pip/Poetry; mitigation: standard `pyproject.toml` keeps us portable — falling back to pip-tools is a lockfile regeneration, not a rewrite.
