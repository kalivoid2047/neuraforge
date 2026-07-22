import Link from "next/link";
import { Badge, Card, ProgressBar } from "@neuraforge/ui";
import { fetchCurriculum } from "@/lib/api";
import type { LessonStatus } from "@/lib/mock";

const statusIcon: Record<LessonStatus, string> = {
  done: "✓",
  current: "◉",
  todo: "○",
};

export default async function Learn() {
  const curriculum = await fetchCurriculum();
  const month = curriculum.months[0];

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <div className="flex items-center gap-3">
        <h1 className="font-display text-2xl font-bold tracking-tight">Your path</h1>
        <Badge tone={curriculum.source === "api" ? "success" : "warning"}>
          {curriculum.source === "api" ? "live data" : "offline — cached view"}
        </Badge>
      </div>

      {/* month timeline strip */}
      <ol className="mt-4 flex flex-wrap items-center gap-2 text-xs font-medium" aria-label="12-month timeline">
        {Array.from({ length: 12 }).map((_, i) => {
          const m = i + 1;
          const state = m < month.number ? "done" : m === month.number ? "current" : "todo";
          return (
            <li
              key={m}
              aria-current={state === "current" ? "step" : undefined}
              className={`flex h-8 w-8 items-center justify-center rounded-full border ${
                state === "done"
                  ? "border-success/50 bg-success/10 text-success"
                  : state === "current"
                    ? "nf-gradient border-transparent text-white"
                    : "border-line text-ink-2"
              }`}
            >
              {state === "done" ? "✓" : m}
            </li>
          );
        })}
      </ol>

      <Card className="mt-6">
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="font-display text-lg font-bold">
            Month {month.number} — {month.title}
          </h2>
          <div className="ml-auto flex w-40 items-center gap-2">
            <ProgressBar value={month.progress} label="Month progress" />
            <span className="font-mono text-xs text-ink-2">{month.progress}%</span>
          </div>
        </div>

        <div className="mt-5 space-y-6">
          {month.weeks.map((week) => (
            <section key={week.number}>
              <h3 className="mb-2 text-sm font-semibold text-ink-2">
                Week {week.number} · {week.title}
              </h3>
              <ul className="space-y-1">
                {week.lessons.map((l) => (
                  <li key={l.slug}>
                    <Link
                      href={l.status === "current" ? `/learn/${l.slug}` : "#"}
                      aria-disabled={l.status === "todo"}
                      className={`flex items-center gap-3 rounded-xl border px-4 py-2.5 text-sm transition-colors ${
                        l.status === "current"
                          ? "border-brand/60 bg-brand/10 hover:bg-brand/15"
                          : l.status === "done"
                            ? "border-transparent text-ink-2 hover:bg-raised"
                            : "border-transparent text-ink-2/60"
                      }`}
                    >
                      <span aria-hidden className={l.status === "done" ? "text-success" : l.status === "current" ? "text-brand-cyan" : "text-line"}>
                        {statusIcon[l.status]}
                      </span>
                      <span className={l.status === "current" ? "font-medium text-ink" : ""}>
                        {l.title}
                      </span>
                      <span className="ml-auto flex items-center gap-3 font-mono text-xs">
                        <span>⏱{l.minutes}m</span>
                        <span aria-label={`difficulty ${l.difficulty} of 5`}>
                          {"★".repeat(l.difficulty)}{"☆".repeat(5 - l.difficulty)}
                        </span>
                        {l.status === "current" ? <Badge tone="brand">you are here</Badge> : null}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>

        <div className="mt-6 flex flex-wrap gap-3 border-t border-line pt-4 text-sm">
          <Badge tone="neutral">Weekly Project: Attention from scratch ○</Badge>
          <Badge tone="spark">🔨 FORGE: Transformer From Scratch ○</Badge>
        </div>
      </Card>
    </div>
  );
}
