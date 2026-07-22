"use client";

import * as React from "react";

export function LessonOutline({
  sections,
  minutes,
  spent,
  difficulty,
}: {
  sections: { anchor: string; title: string; done: boolean; current?: boolean }[];
  minutes: number;
  spent: number;
  difficulty: number;
}) {
  return (
    <nav
      aria-label="Lesson outline"
      className="sticky top-20 hidden w-60 shrink-0 self-start lg:block"
    >
      <ul className="space-y-0.5 border-l border-line">
        {sections.map((s) => (
          <li key={s.anchor}>
            <a
              href={`#${s.anchor}`}
              aria-current={s.current ? "location" : undefined}
              className={`-ml-px flex items-center gap-2 border-l-2 py-1.5 pl-4 pr-2 text-sm transition-colors ${
                s.current
                  ? "border-brand text-ink"
                  : s.done
                    ? "border-transparent text-ink-2 hover:text-ink"
                    : "border-transparent text-ink-2/70 hover:text-ink"
              }`}
            >
              <span aria-hidden className={`text-xs ${s.done ? "text-success" : s.current ? "text-brand-cyan" : "text-line"}`}>
                {s.done ? "✓" : s.current ? "◉" : "○"}
              </span>
              {s.title}
              {s.done ? <span className="sr-only">(complete)</span> : null}
            </a>
          </li>
        ))}
      </ul>
      <div className="mt-4 space-y-1 pl-4 text-xs text-ink-2">
        <p>⏱ {spent}/{minutes} min</p>
        <p aria-label={`Difficulty ${difficulty} of 5`}>
          {"★".repeat(difficulty)}{"☆".repeat(5 - difficulty)}
        </p>
      </div>
    </nav>
  );
}
