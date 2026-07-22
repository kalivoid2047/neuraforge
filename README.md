# Neuraforge

**Build Large Language Models From Scratch — A 12-Month Interactive AI Engineering Program**

Neuraforge is an open-source, interactive web-based learning platform that takes a student from
absolute beginner to advanced LLM researcher and engineer over a structured 12-month curriculum.
It combines the academic rigor of MIT OpenCourseWare, the polish of DeepLearning.AI and Coursera,
and the hands-on philosophy of Fast.ai — in a single self-hostable application.

> **Motto:** *Forge intelligence from first principles.*

## What learners build

| Month | Capstone Project |
|-------|------------------|
| 1  | Matrix Calculator |
| 2  | Neural Network From Scratch |
| 3  | Backpropagation Engine |
| 4  | Image Classifier |
| 5  | Text Classifier |
| 6  | Word2Vec |
| 7  | Transformer From Scratch |
| 8  | GPT From Scratch |
| 9  | Fine-Tune Llama |
| 10 | Retrieval-Augmented Generation (RAG) System |
| 11 | AI Agent |
| 12 | Train & Deploy a Production Language Model (Python-native stack, **no Docker**) |

## Tech stack (summary)

- **Frontend:** Next.js, React, TypeScript, TailwindCSS, Framer Motion, D3.js, Chart.js, Three.js, Monaco Editor, KaTeX
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic, Pydantic, PostgreSQL, Redis, Celery, WebSockets, JWT
- **AI:** PyTorch, HuggingFace Transformers, SentenceTransformers, LlamaIndex, LangChain, Ollama, llama.cpp, vLLM
- **Deployment (Docker-free by design):** uv/venv, Gunicorn + Uvicorn workers, Nginx, systemd, Ubuntu Server, Let's Encrypt, GitHub Actions

## Project documentation

Development proceeds in 12 reviewed phases. Each phase is documented under [`docs/`](docs/):

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1  | [Software Requirements Specification](docs/phase-01-srs/SRS.md) + [Branding Guide](docs/branding/BRANDING.md) | ✅ Approved |
| 2  | [System Architecture](docs/phase-02-architecture/ARCHITECTURE.md) + [ADRs 0001–0011](docs/adr/README.md) | ✅ Approved |
| 3  | [Database Design](docs/phase-03-database/DATABASE.md) | ✅ Approved |
| 4  | [UI/UX Design](docs/phase-04-uiux/UIUX.md) | ✅ Approved |
| 5  | Frontend Development — monorepo scaffold, tokens, [ui](packages/ui/), [viz-widgets](packages/viz-widgets/), [app shell + lesson player MVP](apps/web/) | ✅ Approved |
| 6  | Backend Development — [FastAPI modular monolith](apps/api/) (core · content · learning), Alembic, seeds, tests, `/learn` wired live | ✅ Approved |
| 7  | Authentication — Argon2id, EdDSA JWT, [rotating refresh + reuse detection](apps/api/src/neuraforge/auth/), sessions, [login/register pages](apps/web/src/app/auth/) | ✅ Approved |
| 8  | Learning Engine — [spaced repetition + planner + sparks](apps/api/src/neuraforge/learning/review.py), [gamification via events](apps/api/src/neuraforge/gamification/), live [/review page](apps/web/src/app/(app)/review/page.tsx) | ✅ Approved |
| 9  | Interactive Components — Monaco, [Pyodide runner](apps/web/public/pyodide.worker.js), [graded exercises](apps/web/src/features/lesson/ExerciseCell.tsx), [4-widget playground](apps/web/src/app/(app)/playgrounds/page.tsx) | ✅ Approved |
| 10 | AI Tutor — [Ember backend](apps/api/src/neuraforge/tutor/) (provider-agnostic, retrieval-grounded, budgets, SSE) + [chat panel](apps/web/src/features/tutor/EmberPanel.tsx) | ✅ Approved |
| 11 | Assessment Engine — [question bank, quizzes, server-graded exercises, projects](apps/api/src/neuraforge/assessment/) + [practice](apps/web/src/app/(app)/practice/page.tsx)/[projects](apps/web/src/app/(app)/projects/page.tsx) pages | ✅ Approved |
| 12 | Production Deployment | ⬜ |

## License

Intended for release as open source (license to be finalized in Phase 1 review — recommendation: MIT for code, CC BY-SA 4.0 for curriculum content).
