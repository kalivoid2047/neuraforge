# ADR-0005: Content-as-code — MDX + YAML compiled via content-CI

**Status:** Accepted (realizes SRS C-4, FR-CMS-*) · **Date:** 2026-07-16 · **Phase:** 2

## Context
240 lessons with 22-part anatomy, 2,000+ questions, runnable code samples, math, and diagrams
must stay correct across years of edits. A database-backed WYSIWYG CMS makes content unreviewable
and unverifiable; risk R-1 says content volume is the project's biggest risk.

## Decision
All curriculum lives in `content/` as **MDX (prose + components) + YAML (metadata, questions,
decks, exercises)** validated against JSON Schemas in `content/schema/`. A Python compiler
(`tools/content-ci/`) runs in CI and at publish:
1. **Validate:** schema conformance, internal links, prerequisite DAG acyclicity, KaTeX/Mermaid compilation, quiz answer keys, stable-anchor preservation (`migrates-to` map required for removals).
2. **Execute:** every code sample and exercise reference solution runs against its runtime profile; failures fail the build.
3. **Compile:** MDX → RSC payloads, section index, search documents, flash-card decks; emit a versioned content artifact consumed by the publish job (§11 of ARCHITECTURE.md).

Authoring UX = branch + live preview app (FR-CMS-3) + PR review, like code.

## Consequences
- ✅ Broken content cannot ship; content changes get diffs, review, and rollback for free.
- ✅ Learner progress survives edits via stable anchors (FR-CMS-4).
- ⚠️ Non-technical authors need onboarding; mitigated by templates, schema errors with file/line, and the preview app.
