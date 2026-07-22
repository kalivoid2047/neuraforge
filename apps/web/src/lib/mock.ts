/**
 * Mock data for the Phase 5 frontend MVP.
 * Replaced by the generated API client (packages/api-client) in Phase 6.
 */

export const learner = {
  name: "Amina",
  streak: 14,
  freezes: 1,
  xp: 2340,
  monthProgress: 58,
  overallProgress: 54,
  projectedFinish: "Jun 2027",
};

export const continueLesson = {
  slug: "multi-head-attention",
  code: "M7 · W2 · L3",
  title: "Multi-Head Attention",
  progress: 68,
  remaining: "quiz + 1 exercise left",
};

export const dailySpark = {
  title: "Softmax by hand",
  minutes: 10,
  detail: "Compute softmax([2, 1, 0.1]) without a calculator — then verify in code.",
};

export const reviewQueue = { cardsDue: 23, weakTopics: ["KL divergence", "positional encoding", "LayerNorm", "beam search"] };

export const upNext = [
  { label: "W2 weekly quiz", due: "today" },
  { label: "Weekly Project: attention from scratch", due: "Sunday" },
  { label: "🔨 Forge P7: Transformer From Scratch", due: "in 2 weeks" },
];

export const achievements = [
  { icon: "🔥", title: "Fortnight Fire", tier: "steel" },
  { icon: "🧠", title: "First Backprop", tier: "bronze" },
  { icon: "⚡", title: "2,000 XP", tier: "bronze" },
];

/** 12 weeks × 7 days of activity intensity 0..4 (deterministic mock). */
export function activityHeatmap(): number[][] {
  const weeks: number[][] = [];
  for (let w = 0; w < 12; w++) {
    const days: number[] = [];
    for (let d = 0; d < 7; d++) {
      const x = Math.sin(w * 2.7 + d * 1.3) + Math.cos(w * 0.9 - d * 2.1);
      days.push(Math.max(0, Math.min(4, Math.round(x * 1.6 + 1.4))));
    }
    weeks.push(days);
  }
  return weeks;
}

export type LessonStatus = "done" | "current" | "todo";

export const month7 = {
  number: 7,
  title: "Transformers From Scratch",
  progress: 58,
  weeks: [
    {
      title: "Attention Intuition",
      lessons: [
        { slug: "why-attention", title: "Why Attention?", status: "done" as LessonStatus, minutes: 60, difficulty: 3 },
        { slug: "queries-keys-values", title: "Queries, Keys, Values", status: "done" as LessonStatus, minutes: 75, difficulty: 3 },
        { slug: "scaled-dot-product", title: "Scaled Dot-Product Attention", status: "done" as LessonStatus, minutes: 90, difficulty: 3 },
        { slug: "attention-in-numpy", title: "Attention in NumPy", status: "done" as LessonStatus, minutes: 90, difficulty: 3 },
        { slug: "causal-masking", title: "Causal Masking", status: "done" as LessonStatus, minutes: 60, difficulty: 3 },
      ],
    },
    {
      title: "Multi-Head & Positional",
      lessons: [
        { slug: "attention-heads", title: "What a Head Learns", status: "done" as LessonStatus, minutes: 60, difficulty: 3 },
        { slug: "projections", title: "Linear Projections W_Q W_K W_V", status: "done" as LessonStatus, minutes: 75, difficulty: 4 },
        { slug: "multi-head-attention", title: "Multi-Head Attention", status: "current" as LessonStatus, minutes: 90, difficulty: 4 },
        { slug: "positional-encoding", title: "Positional Encoding", status: "todo" as LessonStatus, minutes: 75, difficulty: 4 },
        { slug: "rope", title: "Rotary Embeddings (RoPE)", status: "todo" as LessonStatus, minutes: 90, difficulty: 5 },
      ],
    },
    {
      title: "Encoder & Decoder Blocks",
      lessons: [
        { slug: "layernorm-residuals", title: "LayerNorm & Residuals", status: "todo" as LessonStatus, minutes: 75, difficulty: 4 },
        { slug: "ffn", title: "Feed-Forward Networks", status: "todo" as LessonStatus, minutes: 60, difficulty: 3 },
        { slug: "encoder-block", title: "The Encoder Block", status: "todo" as LessonStatus, minutes: 90, difficulty: 4 },
        { slug: "decoder-block", title: "The Decoder Block", status: "todo" as LessonStatus, minutes: 90, difficulty: 4 },
        { slug: "cross-attention", title: "Cross-Attention", status: "todo" as LessonStatus, minutes: 75, difficulty: 4 },
      ],
    },
    {
      title: "Training Your Transformer",
      lessons: [
        { slug: "training-setup", title: "Data & Training Setup", status: "todo" as LessonStatus, minutes: 90, difficulty: 4 },
        { slug: "training-loop", title: "The Training Loop", status: "todo" as LessonStatus, minutes: 120, difficulty: 4 },
        { slug: "label-smoothing", title: "Label Smoothing & Schedules", status: "todo" as LessonStatus, minutes: 75, difficulty: 4 },
        { slug: "greedy-vs-beam", title: "Greedy vs Beam Decoding", status: "todo" as LessonStatus, minutes: 75, difficulty: 4 },
        { slug: "evaluate-bleu", title: "Evaluating with BLEU", status: "todo" as LessonStatus, minutes: 60, difficulty: 3 },
      ],
    },
  ],
};

export const lesson = {
  slug: "multi-head-attention",
  code: "7.2.3",
  title: "Multi-Head Attention",
  minutes: 90,
  difficulty: 4,
  prereqs: ["Scaled Dot-Product Attention ✓", "Linear Projections ✓"],
  objectives: [
    "Explain why multiple attention heads beat one big head",
    "Derive the shapes of Q, K, V under h-way head splitting",
    "Implement multi-head attention in pure NumPy, then PyTorch",
    "Inspect what individual heads learn on real text",
  ],
  sections: [
    { anchor: "objectives", title: "Objectives", done: true },
    { anchor: "intuition", title: "Intuition", done: true },
    { anchor: "history", title: "History", done: true },
    { anchor: "math", title: "The Math", done: false, current: true },
    { anchor: "visualizer", title: "Visualizer", done: false },
    { anchor: "python", title: "Pure Python", done: false },
    { anchor: "quiz", title: "Mini Quiz", done: false },
  ],
  starterCode: `import numpy as np

def multi_head_attention(X, W_q, W_k, W_v, W_o, n_heads):
    """X: (seq, d_model). Split into n_heads, attend, concat, project."""
    seq, d_model = X.shape
    d_k = d_model // n_heads

    Q = X @ W_q   # (seq, d_model)
    K = X @ W_k
    V = X @ W_v

    # reshape to (n_heads, seq, d_k)
    Q = Q.reshape(seq, n_heads, d_k).transpose(1, 0, 2)
    K = K.reshape(seq, n_heads, d_k).transpose(1, 0, 2)
    V = V.reshape(seq, n_heads, d_k).transpose(1, 0, 2)

    scores = Q @ K.transpose(0, 2, 1) / np.sqrt(d_k)
    weights = np.exp(scores - scores.max(-1, keepdims=True))
    weights = weights / weights.sum(-1, keepdims=True)

    out = weights @ V                              # (n_heads, seq, d_k)
    out = out.transpose(1, 0, 2).reshape(seq, d_model)
    return out @ W_o, weights

rng = np.random.default_rng(0)
X = rng.standard_normal((6, 8))
W = [rng.standard_normal((8, 8)) * 0.5 for _ in range(4)]
out, w = multi_head_attention(X, *W, n_heads=2)
print("output:", out.shape, "| weights:", w.shape)
print("rows sum to 1:", np.allclose(w.sum(-1), 1.0))`,
  starterOutput: `output: (6, 8) | weights: (2, 6, 6)
rows sum to 1: True`,
};
