import Link from "next/link";
import { Badge, Button, Callout } from "@neuraforge/ui";
import { AttentionVisualizer, MatrixMultiplyStepper } from "@neuraforge/viz-widgets";
import { CodeCell } from "@/features/lesson/CodeCell";
import { ExerciseCell } from "@/features/lesson/ExerciseCell";
import { LessonOutline } from "@/features/lesson/LessonOutline";
import { MathBlock } from "@/features/lesson/MathBlock";
import { QuizCard } from "@/features/lesson/QuizCard";
import { lesson } from "@/lib/mock";
import { fetchExerciseForLesson } from "@/lib/assessment";

export default async function LessonPage() {
  const L = lesson; // Phase 6: fetch by params.slug via the API client
  // Phase 11: resolve the backend Exercise id so ExerciseCell can replay
  // this submission against the hidden, authoritative test suite. Falls
  // back to client-only (Tier-1) grading if the API is unreachable (P-6).
  const exercise = await fetchExerciseForLesson("multi-head-attention").catch(() => null);

  return (
    <div className="mx-auto flex max-w-6xl gap-10 px-6 py-8">
      <LessonOutline sections={L.sections} minutes={L.minutes} spent={38} difficulty={L.difficulty} />

      <article className="nf-prose min-w-0 flex-1">
        <p className="font-mono text-xs text-brand-cyan">LESSON {L.code}</p>
        <h1 className="font-display mt-1 text-3xl font-bold tracking-tight">{L.title}</h1>
        <div className="mt-3 flex flex-wrap gap-2">
          <Badge tone="neutral">⏱ {L.minutes} min</Badge>
          <Badge tone="neutral">{"★".repeat(L.difficulty)}{"☆".repeat(5 - L.difficulty)}</Badge>
          {L.prereqs.map((p) => (
            <Badge key={p} tone="success">{p}</Badge>
          ))}
        </div>

        <h2 id="objectives">🎯 After this lesson you can…</h2>
        <ul className="list-disc space-y-1 pl-5 text-ink">
          {L.objectives.map((o) => (
            <li key={o}>{o}</li>
          ))}
        </ul>

        <h2 id="intuition">One head is a spotlight. You need a lighting rig.</h2>
        <p>
          A single attention head computes <em>one</em> notion of relevance: perhaps
          “which earlier word does this pronoun refer to?” But language needs many
          notions <em>at once</em> — syntax, coreference, position, topic. Multi-head
          attention runs <code>h</code> small attention operations in parallel, each in
          its own learned subspace, then concatenates what they found.
        </p>
        <Callout kind="tip" title="The core intuition">
          Don&apos;t think “8 copies of the same thing.” Think 8 <em>specialists</em>,
          each with a cheap, low-dimensional view — a syntax head, a coreference head,
          a position head — whose reports are stitched together.
        </Callout>

        <h2 id="history">History</h2>
        <Callout kind="history" title="2017 — “Attention Is All You Need”">
          Vaswani et al. found that multiple heads let the model attend to information
          from different representation subspaces at different positions — with{" "}
          <em>the same total compute</em> as one big head, because each head works in
          dimension d_model/h.
        </Callout>

        <h2 id="math">The math, derived</h2>
        <p>
          Recall single-head attention. With queries Q, keys K, and values V:
        </p>
        <MathBlock tex={String.raw`\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V`} />
        <p>
          Multi-head splits the model dimension into <code>h</code> subspaces. Head{" "}
          <code>i</code> gets its own learned projections:
        </p>
        <MathBlock tex={String.raw`\mathrm{head}_i=\mathrm{Attention}(XW_i^{Q},\,XW_i^{K},\,XW_i^{V}),\qquad W_i^{Q},W_i^{K},W_i^{V}\in\mathbb{R}^{d_{\text{model}}\times d_k}`} />
        <MathBlock tex={String.raw`\mathrm{MultiHead}(X)=\mathrm{Concat}(\mathrm{head}_1,\dots,\mathrm{head}_h)\,W^{O},\qquad d_k=\frac{d_{\text{model}}}{h}`} />
        <p>
          Every equation above is just matrix multiplication — the operation you
          mastered in Month 1. Step through one to feel the shapes:
        </p>
        <MatrixMultiplyStepper />

        <h2 id="visualizer">See what the heads learn</h2>
        <p>
          Below is attention from a small trained model. Pick a head, then click a
          token to see where it looks. Head 3 is the famous one — select{" "}
          <code>it</code>.
        </p>
        <AttentionVisualizer />

        <h2 id="python">Pure Python first. Always.</h2>
        <p>
          Before PyTorch does it for you, build it yourself. Edit and run — the shapes
          are the whole story:
        </p>
        <CodeCell code={L.starterCode} output={L.starterOutput} />

        <ExerciseCell
          spec={{
            id: "7.2.3-ex1",
            exerciseId: exercise?.id,
            title: "Implement softmax from scratch",
            brief:
              "Pure Python, no numpy: softmax(xs) returns probabilities. Subtract the max first — the tests check numerical stability.",
            starterCode: `import math

def softmax(xs):
    """Return the softmax of a list of floats."""
    # your code here
    ...
`,
            tests: [
              { name: "sums to 1", code: "assert abs(sum(softmax([2.0, 1.0, 0.1])) - 1.0) < 1e-9" },
              { name: "order preserved", code: "p = softmax([2.0, 1.0, 0.1]); assert p[0] > p[1] > p[2]" },
              { name: "uniform on equal logits", code: "p = softmax([3.0, 3.0]); assert abs(p[0] - 0.5) < 1e-9" },
              { name: "numerically stable at 1000", code: "p = softmax([1000.0, 1000.0]); assert abs(sum(p) - 1.0) < 1e-9" },
            ],
            hints: [
              "exp(x_i) / sum(exp(x_j)) — start with the direct translation.",
              "exp(1000) overflows. softmax(xs) == softmax(xs - max(xs)) — prove it, then use it.",
              "m = max(xs); es = [math.exp(x - m) for x in xs]; return [e / sum(es) for e in es]",
            ],
          }}
        />

        <Callout kind="warning" title="Common bug">
          If your softmax normalizes over the <em>query</em> axis instead of the{" "}
          <em>key</em> axis, rows won&apos;t sum to 1 and training silently diverges.
          The test <code>np.allclose(w.sum(-1), 1.0)</code> catches it.
        </Callout>

        <h2 id="quiz">Check yourself</h2>
        <QuizCard
          question="Why does splitting d_model=512 into 8 heads of d_k=64 cost roughly the same FLOPs as one 512-dim head?"
          correct={1}
          options={[
            { text: "Because attention is O(1) in dimension", why: "Attention scales linearly in d_k — dimension matters." },
            { text: "Each head's QK^T is seq²×64; eight of them ≈ one seq²×512", why: "Exactly: h heads of size d/h sum to the same multiply-add count." },
            { text: "Because the W_O projection absorbs the cost", why: "W_O adds cost; it doesn't offset the per-head attention." },
            { text: "It doesn't — multi-head is 8× more expensive", why: "Per-head dimension shrinks by h, keeping total cost constant." },
          ]}
        />

        <div className="mt-10 flex items-center justify-between border-t border-line pt-6">
          <Link href="/learn">
            <Button variant="ghost">← 7.2.2 Projections</Button>
          </Link>
          <Button>Mark section &amp; continue →</Button>
        </div>
      </article>
    </div>
  );
}
