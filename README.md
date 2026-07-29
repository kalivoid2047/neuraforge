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

Month 10 (Retrieval & Knowledge Systems → a RAG system over this curriculum) is complete,
20/20 lessons: embeddings and vector search (cosine vs dot product, exact search, IVF/ANN),
document preparation (chunking, overlap, BM25 and hybrid search, metadata filters, ingestion),
RAG architectures (grounded prompts, context budgets, cross-encoder reranking, query
transformation), and evaluation — closing with a capstone that indexes 18 real lessons from this
course and answers questions about them with citations and abstention. It is also the month with
the most negative results: paraphrased queries drop recall@10 to 0.571, term-overlap
groundedness cannot separate a grounded answer (0.69) from a hallucinated one (0.60), hybrid
search merely ties with a single method, and reranking changes nothing. All four are reported as
measured, with the reason they do not generalize, rather than tuned away.

Month 11 (Agents & Tooling → a tool-using research agent with MCP) is complete, 20/20 lessons:
the agent loop and function calling, memory systems and the Model Context Protocol, planning and
reflection, and agent safety and evaluation — closing with a capstone that discovers its tools at
runtime over MCP, plans, retrieves, critiques, and blocks a live prompt-injection attempt on
provenance rather than content.

The month is built around measurements that constrain agent design rather than flatter it: the
transcript is resent every step, so tokens processed grow `O(n²)` — a 50-step run ends at 6,400
tokens having sent 173,000 (`27×`); per-step reliability compounds as `p^n`, so a 95% step
completes a 20-step task 35.8% of the time; a recency-only summarizer retained 1 of 5 needed
facts against plain truncation's 2 of 5; and a weak critic (detection 0.3, false positives 0.3)
moved success by −0.2 and −0.0 points for ~39% more calls, against a strong critic's 0.275 →
0.852. The capstone ablation is equally blunt: reading several candidates helped, pseudo-relevance
feedback paid only in combination, and turning the critic off entirely scored the same 3/4 as the
best configured version — so the chapter concludes that agent architecture buys control, not
accuracy.

Month 12 (Production AI Engineering → deploy a production language model on a Docker-free Python
stack) is complete, 20/20 lessons: the serving stack and queueing, batching and KV-bounded
concurrency, systemd/nginx/atomic deploys/CI gates, logs-to-metrics, percentiles and SLOs,
backups, and performance/cost/canary/drift — closing with a capstone that derives a capacity,
cost and rollout plan from a written SLO.

Weeks two's lessons audit **this repository's own deployment artifacts** rather than invented
examples: the real [systemd unit](deploy/systemd/neuraforge-api.service),
[nginx config](deploy/nginx/neuraforge.conf) and [CI workflow](.github/workflows/ci.yml) are
embedded verbatim and parsed in the lesson. The hardening audit scores the real unit at 12/13,
and reports the one absent directive (`MemoryDenyWriteExecute`) together with the comment
explaining why it was omitted deliberately.

The measurements again constrain rather than flatter: `W = S/(1-ρ)` doubles latency between 80%
and 90% utilization; continuous batching recovers 51.3% of slot-steps that static batching
wastes; a 32k context leaves *zero* concurrent capacity where 1k leaves 16; fan-out turns a
1%-slow backend into 63.4% slow pages; caching at an 80% hit rate cuts the mean 4.8× and moves
p99 not at all; serving configuration spans 36× on unit cost; and detecting a doubled 0.1% error
rate needs 23,510 requests per arm, so a ten-minute canary cannot see it. The capstone's two
headline findings are both failures: the stated latency SLO is infeasible at any fleet size
(service time alone is 6.88s against a 3,000 ms target), and the budget supports 0.81 rps against
a stated 25 — both discovered in arithmetic before any hardware is provisioned.

**The curriculum is complete: 240/240 lessons, Months 1 through 12, with no gaps.**
`/learn/[slug]` presents every month-to-month transition as a normal "next lesson," and the
final lesson (12.4.5) closes the sequence.

Every code cell in Months 10–12 was executed in CPython and re-executed through the project's
own [Pyodide worker](apps/web/public/pyodide.worker.js); outputs are byte-identical in both
runtimes, including the Monte Carlo simulations, which reproduce exactly because
`numpy.random.default_rng(seed)` is deterministic across platforms.

## License

Intended for release as open source (license to be finalized in Phase 1 review — recommendation: MIT for code, CC BY-SA 4.0 for curriculum content).
