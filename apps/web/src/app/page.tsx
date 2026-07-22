import Link from "next/link";
import { Button, Badge } from "@neuraforge/ui";
import { AttentionVisualizer } from "@neuraforge/viz-widgets";

const months = [
  "Matrix Calculator", "Neural Net From Scratch", "Backprop Engine",
  "Image Classifier", "Text Classifier", "Word2Vec",
  "Transformer From Scratch", "GPT From Scratch", "Fine-Tune Llama",
  "RAG System", "AI Agent", "Deploy a Production LM",
];

export default function Landing() {
  return (
    <main className="mx-auto max-w-5xl px-6 pb-24">
      <header className="flex items-center justify-between py-6">
        <p className="font-display text-lg font-bold tracking-wide">
          <span aria-hidden className="mr-2 text-spark">◆</span>
          NEURA<span className="text-brand">FORGE</span>
        </p>
        <nav className="flex items-center gap-3">
          <Link href="/learn" className="text-sm text-ink-2 hover:text-ink">
            Syllabus
          </Link>
          <Link href="/auth/login">
            <Button variant="secondary" size="sm">Sign in</Button>
          </Link>
        </nav>
      </header>

      <section className="py-16 text-center">
        <Badge tone="spark" className="mb-6">12-month interactive program</Badge>
        <h1 className="font-display mx-auto max-w-3xl text-5xl font-bold leading-tight tracking-tight">
          Forge intelligence from{" "}
          <span className="nf-gradient-text">first principles</span>.
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-lg text-ink-2">
          Build a production GPT from scratch in 12 months — every matrix, every
          gradient, every deploy script. No Docker. No magic. Every line, yours.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link href="/dashboard">
            <Button size="lg">Start forging — free</Button>
          </Link>
          <Link href="/learn">
            <Button size="lg" variant="secondary">Browse syllabus</Button>
          </Link>
        </div>
      </section>

      <section aria-label="Live demo" className="mx-auto max-w-3xl">
        <p className="mb-2 text-center text-sm text-ink-2">
          This isn&apos;t a screenshot — drag it. Lesson 7.2.3, live:
        </p>
        <AttentionVisualizer />
      </section>

      <section className="mt-16">
        <h2 className="font-display mb-6 text-center text-2xl font-bold">
          12 months · 240 lessons · 12 Forge Projects
        </h2>
        <ol className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {months.map((m, i) => (
            <li
              key={m}
              className="rounded-2xl border border-line bg-raised p-4 transition-colors hover:border-brand/50"
            >
              <p className="font-mono text-xs text-brand-cyan">M{i + 1}</p>
              <p className="mt-1 text-sm font-medium">{m}</p>
            </li>
          ))}
        </ol>
      </section>
    </main>
  );
}
