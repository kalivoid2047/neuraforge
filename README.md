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
| 12 | Production Deployment — [runbook](docs/phase-12-deployment/DEPLOYMENT.md), [systemd units](deploy/systemd/) + [Nginx](deploy/nginx/), [provision](scripts/provision.sh)/[deploy](scripts/deploy.sh) scripts, [CI](.github/workflows/ci.yml), live-verified end-to-end | ✅ Approved |

## Curriculum content status

The 12 build phases above are the *platform*; the curriculum itself (SRS §4.4: 240 lessons,
1,000+ practice questions, 48 weekly + 12 Forge projects, ...) is separate, ongoing content
work, authored as [`.mdx` files](content/lessons/) per a lightweight version of
[ADR-0005](docs/adr/0005-content-as-code.md) (no schema validation/versioning/publish pipeline
yet — see the ADR for what's deliberately deferred).

**Months 1–7 complete: 140/240 lessons — and now contiguous.** Month 1 (Python & Math
Foundations → Matrix Calculator), Month 2 (Linear Algebra & Neural Nets I → Neural Network From
Scratch), Month 3 (Calculus, Optimization & Backprop → Backpropagation Engine, a from-scratch
micrograd-style autograd library that trains a real MLP to solve XOR), Month 4 (Deep Learning
with PyTorch → Image Classifier, a from-scratch conv/pool/linear network trained on synthetic
images — PyTorch snippets are reference-only since Pyodide doesn't ship `torch`, with every
interactive cell verified via an equivalent NumPy implementation instead), Month 5 (Probability,
Statistics & NLP I → Text Classifier, covering probability/information theory through to a
from-scratch classical NLP pipeline — bag-of-words, TF-IDF, Naive Bayes — plus a neural
classifier, compared fairly via cross-validated precision/recall/F1), Month 6 (Embeddings &
Language Modeling I → Word2Vec from scratch with an evaluation suite, covering subword
tokenization (BPE/WordPiece/SentencePiece), embeddings, n-gram and RNN language models,
perplexity, and the vanishing-gradient limitation that motivates attention), and Month 7
(Transformers From Scratch) are each fully authored, 20/20 lessons.

Month 8 (GPT & Training at Scale → GPT From Scratch) is also complete, 20/20 lessons: the
decoder-only architecture, training at scale (packing, mixed precision, gradient accumulation
and checkpointing, DDP/FSDP), decoding strategies and the KV cache, and scaling laws — closing
with a capstone that derives backpropagation through a Transformer by hand, verifies every
gradient against finite differences to ~1e-10, trains to perplexity 1.43, and generates coherent
text.

Month 9 (Fine-Tuning & Alignment → a fine-tune with a real evaluation report) is complete,
20/20 lessons: transfer learning and catastrophic forgetting, PEFT/LoRA/quantization/QLoRA,
instruction tuning through reward models, RLHF and DPO, and evaluation covering target, retained,
and safety capabilities — closing with a capstone that adapts a pretrained model two ways and
shows LoRA matching full fine-tuning on the target task (both 1.000) while retaining 1.000
against full fine-tuning's 0.880.

**Months 1 through 9 run end to end with no gaps: 180/240 lessons.** `/learn/[slug]` presents
each month-to-month transition as a normal "next lesson." Months 10–12 (60 lessons) are not yet
authored; the navigation flags a genuine month gap explicitly rather than presenting a skip as
the next lesson in sequence.

## License

Intended for release as open source (license to be finalized in Phase 1 review — recommendation: MIT for code, CC BY-SA 4.0 for curriculum content).
