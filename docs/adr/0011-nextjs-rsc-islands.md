# ADR-0011: Next.js RSC static-first rendering with interactive islands

**Status:** Accepted · **Date:** 2026-07-16 · **Phase:** 2

## Context
Lessons are long, math/diagram-heavy documents with embedded interactive widgets. LCP budget is
2.5 s p75 (NFR-PERF-1). A full SPA ships megabytes of JS before first paint; fully static sites
can't do per-user progress, runners, or Ember.

## Decision
Next.js App Router with **React Server Components**: lesson MDX compiles (at content-build time,
ADR-0005) to RSC payloads served static/ISR; KaTeX and Mermaid render server-side to HTML/SVG
(no client math/diagram JS on the critical path). Interactive islands hydrate on demand:
`CodeCell` (Monaco, lazy), `Widget` (viz library, lazy per widget), `Quiz`, `TutorPanel`.
Per-user data (progress ticks, XP) fetched client-side via the generated API client — lesson
HTML stays cacheable for all users. Pyodide loads in a Web Worker only on lessons that declare
Tier-1 exercises; Nginx sets COOP/COEP on those routes only.

## Consequences
- ✅ Text/math/diagrams paint fast and cheap; JS cost scales with interactivity actually used.
- ✅ ISR invalidation on content publish gives instant updates without full rebuilds.
- ⚠️ Two data paths (static content vs dynamic learner state) must never mix — enforced by keeping learner state out of RSC props and inside client hooks.
- ⚠️ COOP/COEP isolation breaks third-party embeds on Pyodide routes; acceptable (we embed nothing third-party there by policy).
