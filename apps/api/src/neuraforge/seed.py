"""Dev seed: demo learner + Month 7 curriculum (mirrors apps/web mock data).

Production curriculum arrives via the content-artifact publish job (ADR-0005);
this seed exists so the API is demonstrable end-to-end from first boot.
"""

from datetime import UTC, datetime

from sqlalchemy import select

from .auth.models import User
from .content.models import Lesson, Section
from .core.db import SessionLocal
from .learning.models import Deck, Enrollment, FlashCard, LessonProgress, Spark

MONTH_TITLE = "Transformers From Scratch"

WEEKS: list[tuple[str, list[tuple[str, str, int, int]]]] = [
    ("Attention Intuition", [
        ("why-attention", "Why Attention?", 60, 3),
        ("queries-keys-values", "Queries, Keys, Values", 75, 3),
        ("scaled-dot-product", "Scaled Dot-Product Attention", 90, 3),
        ("attention-in-numpy", "Attention in NumPy", 90, 3),
        ("causal-masking", "Causal Masking", 60, 3),
    ]),
    ("Multi-Head & Positional", [
        ("attention-heads", "What a Head Learns", 60, 3),
        ("projections", "Linear Projections W_Q W_K W_V", 75, 4),
        ("multi-head-attention", "Multi-Head Attention", 90, 4),
        ("positional-encoding", "Positional Encoding", 75, 4),
        ("rope", "Rotary Embeddings (RoPE)", 90, 5),
    ]),
    ("Encoder & Decoder Blocks", [
        ("layernorm-residuals", "LayerNorm & Residuals", 75, 4),
        ("ffn", "Feed-Forward Networks", 60, 3),
        ("encoder-block", "The Encoder Block", 90, 4),
        ("decoder-block", "The Decoder Block", 90, 4),
        ("cross-attention", "Cross-Attention", 75, 4),
    ]),
    ("Training Your Transformer", [
        ("training-setup", "Data & Training Setup", 90, 4),
        ("training-loop", "The Training Loop", 120, 4),
        ("label-smoothing", "Label Smoothing & Schedules", 75, 4),
        ("greedy-vs-beam", "Greedy vs Beam Decoding", 75, 4),
        ("evaluate-bleu", "Evaluating with BLEU", 60, 3),
    ]),
]

MHA_SECTIONS = [
    ("objectives", "theory", "Objectives"),
    ("intuition", "theory", "Intuition"),
    ("history", "history", "History"),
    ("math", "derivation", "The Math"),
    ("visualizer", "viz", "Visualizer"),
    ("python", "walkthrough", "Pure Python"),
    ("quiz", "quiz", "Mini Quiz"),
]

MHA_META = {
    "objectives": [
        "Explain why multiple attention heads beat one big head",
        "Derive the shapes of Q, K, V under h-way head splitting",
        "Implement multi-head attention in pure NumPy, then PyTorch",
        "Inspect what individual heads learn on real text",
    ],
    "prereqs": ["Scaled Dot-Product Attention ✓", "Linear Projections ✓"],
}

# Demo progress: weeks 1 fully done, week 2 done through 'projections',
# multi-head-attention in progress (first 3 sections ticked).
DONE_SLUGS = {s for _, lessons in WEEKS[:1] for s, *_ in lessons} | {"attention-heads", "projections"}
CURRENT_SLUG = "multi-head-attention"
CURRENT_TICKED = ["objectives", "intuition", "history"]

MHA_CARDS = [
    ("What does multi-head attention buy over a single head, at equal FLOPs?",
     "h parallel low-dim heads learn *different* relations (syntax, coreference, position); "
     "d_k = d_model/h keeps total cost constant."),
    ("Shapes: X is (seq, d_model), 8 heads. What is each head's Q?",
     "(seq, d_k) with d_k = d_model/8 — after X·W_i^Q, W_i^Q ∈ R^{d_model×d_k}."),
    ("Why scale scores by 1/√d_k?",
     "Dot products grow with d_k; unscaled logits saturate softmax → vanishing gradients."),
    ("What does W^O do after concatenation?",
     "Projects the concatenated heads (seq, d_model) back into the residual stream, mixing head outputs."),
    ("Which axis must softmax normalize over, and the classic bug?",
     "The *key* axis (last). Normalizing over queries makes rows not sum to 1 and silently diverges."),
    ("In causal attention, which weights are masked?",
     "w[q][k] for k > q — a token may not attend to the future."),
]

SPARKS = [
    ("Softmax by hand", "Compute softmax([2, 1, 0.1]) without a calculator — then verify in code.", 10),
    ("Shape gymnastics", "X:(6,512), 8 heads. Write every tensor shape from X to MultiHead(X).", 8),
    ("Spot the bug", "`w = np.exp(s); w /= w.sum(0)` — what's wrong for attention weights?", 5),
    ("One-liner mask", "Write the causal mask for seq=5 as a NumPy one-liner.", 5),
    ("Explain to a friend", "In 3 sentences, no math: why do transformers need positional information?", 10),
]


async def seed_if_empty() -> None:
    async with SessionLocal() as session:
        if await session.scalar(select(Lesson.id).limit(1)):
            return

        from .auth.security import hash_password

        user = User(
            email="amina@neuraforge.dev",
            display_name="Amina",
            tz="Europe/Berlin",
            password_hash=hash_password("forge-me-a-gpt"),  # dev demo credentials
            email_verified_at=datetime.now(UTC),
        )
        session.add(user)
        await session.flush()  # materialize user.id before FK use
        session.add(Enrollment(user_id=user.id))

        now = datetime.now(UTC)
        current_lesson_id = None
        for week_no, (week_title, lessons) in enumerate(WEEKS, start=1):
            for ord_, (slug, title, minutes, difficulty) in enumerate(lessons, start=1):
                meta: dict = {"month_title": MONTH_TITLE, "week_title": week_title}
                if slug == CURRENT_SLUG:
                    meta |= MHA_META
                lesson = Lesson(
                    slug=slug, month=7, week=week_no, ord=ord_, title=title,
                    difficulty=difficulty, est_minutes=minutes, meta=meta,
                )
                if slug == CURRENT_SLUG:
                    lesson.sections = [
                        Section(anchor=a, kind=k, ord=i, title=t)
                        for i, (a, k, t) in enumerate(MHA_SECTIONS, start=1)
                    ]
                else:
                    lesson.sections = [
                        Section(anchor="content", kind="theory", ord=1, title="Lesson"),
                    ]
                session.add(lesson)
                await session.flush()  # materialize lesson.id before FK use
                if slug == CURRENT_SLUG:
                    current_lesson_id = lesson.id

                if slug in DONE_SLUGS:
                    ticks = {s.anchor: now.isoformat() for s in lesson.sections}
                    session.add(LessonProgress(
                        user_id=user.id, lesson_id=lesson.id, status="completed",
                        section_ticks=ticks, started_at=now, completed_at=now,
                    ))
                elif slug == CURRENT_SLUG:
                    session.add(LessonProgress(
                        user_id=user.id, lesson_id=lesson.id, status="in_progress",
                        section_ticks={a: now.isoformat() for a in CURRENT_TICKED},
                        resume_anchor="math", started_at=now,
                    ))
                    # system flash-card deck for the current lesson
                    deck = Deck(lesson_id=lesson.id, title=f"Deck · {title}")
                    deck.cards = [
                        FlashCard(deck_id=deck.id, front_md=f, back_md=b)
                        for f, b in MHA_CARDS
                    ]
                    session.add(deck)

        for title, detail, minutes in SPARKS:
            session.add(Spark(title=title, detail=detail, minutes=minutes, month=7))

        await _seed_assessment(session, current_lesson_id)
        await session.commit()


async def _seed_assessment(session, current_lesson_id) -> None:
    """Phase 11 demo content: a mini-quiz, a graded exercise, and a Forge
    Project tied to the seeded Month 7 curriculum (mirrors the pattern above)."""
    from .assessment.models import Exercise, Project, Question, Quiz

    questions = [
        Question(
            qtype="mcq_single", bank="practice",
            body={
                "stem": "Why scale attention scores by 1/√d_k?",
                "options": [
                    {"id": "a", "text": "To keep logits from saturating softmax"},
                    {"id": "b", "text": "To normalize the output to [0,1]"},
                    {"id": "c", "text": "To match PyTorch defaults"},
                    {"id": "d", "text": "It isn't necessary, just convention"},
                ],
            },
            answer_key={"correct": "a"},
            explanation={
                "a": "Unscaled dot products grow with d_k and saturate softmax → vanishing gradients.",
                "b": "Softmax already normalizes the output, not the input logits.",
            },
            topic_tags=["attention", "transformers"], month=7, week=1, difficulty=3, bloom="understand",
        ),
        Question(
            qtype="mcq_multi", bank="practice",
            body={
                "stem": "Which are true of multi-head attention?",
                "options": [
                    {"id": "a", "text": "Each head has its own W_Q, W_K, W_V"},
                    {"id": "b", "text": "Heads run in parallel at ~equal FLOPs to one big head"},
                    {"id": "c", "text": "W^O mixes concatenated head outputs back into d_model"},
                    {"id": "d", "text": "More heads always improve accuracy"},
                ],
            },
            answer_key={"correct": ["a", "b", "c"]},
            explanation={"d": "Head count is a tuned hyperparameter, not a monotonic win."},
            topic_tags=["attention", "transformers"], month=7, week=2, difficulty=4, bloom="analyze",
        ),
        Question(
            qtype="numeric", bank="practice",
            body={"stem": "8 heads, d_model = 512. What is d_k per head?"},
            answer_key={"value": 64, "tolerance": 0},
            explanation={}, topic_tags=["attention"], month=7, week=2, difficulty=2, bloom="apply",
        ),
        Question(
            qtype="fill_blank", bank="practice",
            body={"stem": "In causal attention, a token may not attend to the ____."},
            answer_key={"text": "future"},
            explanation={}, topic_tags=["attention", "masking"], month=7, week=1, difficulty=2, bloom="remember",
        ),
    ]
    session.add_all(questions)
    await session.flush()  # materialize question ids for the blueprint below

    if current_lesson_id is None:
        return

    session.add(Quiz(
        kind="mini", lesson_id=current_lesson_id, month=7, week=2,
        blueprint={"question_ids": [str(q.id) for q in questions]},
        pass_threshold=70, time_limit_s=600,
    ))

    # Matches apps/web's static ExerciseCell for this lesson exactly (same
    # function contract) so the client's Tier-1 tests and this hidden,
    # authoritative Tier-2 suite grade the same submission coherently.
    session.add(Exercise(
        lesson_id=current_lesson_id, ord=1,
        title="Implement softmax from scratch",
        brief="Pure Python, no numpy: softmax(xs) returns probabilities, numerically stable.",
        starter_code=(
            "import math\n\n"
            "def softmax(xs):\n"
            '    """Return the softmax of a list of floats."""\n'
            "    # your code here\n"
            "    ...\n"
        ),
        tests=[
            {"name": "sums to 1", "code": (
                "assert abs(sum(softmax([2.0, 1.0, 0.1])) - 1.0) < 1e-9\n"
            )},
            {"name": "order preserved", "code": (
                "p = softmax([2.0, 1.0, 0.1]); assert p[0] > p[1] > p[2]\n"
            )},
            {"name": "handles large negative logits", "code": (
                "p = softmax([-1000.0, -1000.0]); assert abs(sum(p) - 1.0) < 1e-9\n"
            )},
            {"name": "single element is certain", "code": (
                "p = softmax([5.0]); assert abs(p[0] - 1.0) < 1e-9\n"
            )},
        ],
        hints=[
            "exp(x_i) / sum(exp(x_j)) — start with the direct translation.",
            "exp(1000) overflows. softmax(xs) == softmax(xs - max(xs)) — prove it, then use it.",
            "m = max(xs); es = [math.exp(x - m) for x in xs]; return [e / sum(es) for e in es]",
        ],
        limits={"wall_s": 10, "mem_mb": 256},
    ))

    session.add(Project(
        kind="forge", month=7, week=None, title="Transformer From Scratch",
        brief_md=(
            "Implement a full encoder-decoder Transformer and train it on a small "
            "translation task. Submit a link to your repo."
        ),
        rubric=[
            "Multi-head attention implemented and unit-tested",
            "Positional encoding implemented",
            "Encoder and decoder blocks compose correctly",
            "Model trains and loss decreases over epochs",
            "README explains architecture and results",
        ],
        checks=["artifact_url_valid", "self_assessment_complete"],
    ))
