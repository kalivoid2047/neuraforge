"use client";

import * as React from "react";
import { Button } from "@neuraforge/ui";

type Option = { text: string; why: string };

/** Mini-quiz single question MVP (FR-ASSESS-2): instant feedback + per-option explanation. */
export function QuizCard({
  question,
  options,
  correct,
}: {
  question: string;
  options: Option[];
  correct: number;
}) {
  const [picked, setPicked] = React.useState<number | null>(null);
  const [checked, setChecked] = React.useState(false);

  return (
    <div className="my-5 rounded-2xl border border-line bg-raised p-5">
      <p className="mb-1 font-mono text-xs text-brand-cyan">MINI QUIZ · 1 of 8</p>
      <p className="font-medium">{question}</p>
      <div role="radiogroup" aria-label="Answer options" className="mt-4 space-y-2">
        {options.map((o, i) => {
          const state = !checked
            ? picked === i ? "picked" : "idle"
            : i === correct ? "right" : picked === i ? "wrong" : "idle";
          const styles = {
            idle: "border-line hover:border-brand/50",
            picked: "border-brand bg-brand/10",
            right: "border-success bg-success/10",
            wrong: "border-danger bg-danger/10",
          }[state];
          return (
            <label
              key={i}
              className={`flex cursor-pointer items-start gap-3 rounded-xl border px-4 py-3 text-sm transition-colors ${styles}`}
            >
              <input
                type="radio"
                name="quiz"
                checked={picked === i}
                disabled={checked}
                onChange={() => setPicked(i)}
                className="mt-0.5 accent-[#6366F1]"
              />
              <span>
                {o.text}
                {checked && (i === correct || picked === i) ? (
                  <span className={`mt-1 block text-xs ${i === correct ? "text-success" : "text-danger"}`}>
                    {i === correct ? "✓ " : "✗ "}{o.why}
                  </span>
                ) : null}
              </span>
            </label>
          );
        })}
      </div>
      <div aria-live="assertive" className="sr-only">
        {checked ? (picked === correct ? "Correct." : "Incorrect.") : ""}
      </div>
      <div className="mt-4 flex items-center gap-3">
        {!checked ? (
          <Button size="sm" disabled={picked === null} onClick={() => setChecked(true)}>
            Check ✓
          </Button>
        ) : (
          <>
            <p className={`text-sm font-medium ${picked === correct ? "text-success" : "text-danger"}`}>
              {picked === correct
                ? "Correct — forged. 🔨"
                : "Not quite. Missed questions join your review queue."}
            </p>
            <Button size="sm" variant="secondary" onClick={() => { setChecked(false); setPicked(null); }}>
              Try again
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
