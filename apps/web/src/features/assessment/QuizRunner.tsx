"use client";

import * as React from "react";
import { Badge, Button, Card, ProgressBar } from "@neuraforge/ui";
import { Check, X } from "lucide-react";
import {
  answerQuestion, finishAttempt, startAttempt,
  type AnswerResult, type AttemptFinishResult, type AttemptStart, type QuestionPublic,
} from "@/lib/assessment";

type Answer = Record<string, unknown>;

function QuestionInput({
  question, value, onChange, disabled,
}: { question: QuestionPublic; value: Answer; onChange: (a: Answer) => void; disabled: boolean }) {
  const options = question.body.options ?? [];

  if (question.qtype === "mcq_single") {
    return (
      <div className="mt-3 grid gap-2" role="radiogroup" aria-label="Answer options">
        {options.map((o) => (
          <button
            key={o.id}
            disabled={disabled}
            onClick={() => onChange({ selected: o.id })}
            aria-pressed={value.selected === o.id}
            className={`rounded-xl border px-4 py-2.5 text-left text-sm transition-colors focus-visible:outline-2 focus-visible:outline-brand disabled:pointer-events-none ${
              value.selected === o.id ? "border-brand/60 bg-brand/10 text-ink" : "border-line bg-base hover:border-brand/40"
            }`}
          >
            {o.text}
          </button>
        ))}
      </div>
    );
  }

  if (question.qtype === "mcq_multi") {
    const selected = new Set((value.selected as string[]) ?? []);
    const toggle = (id: string) => {
      const next = new Set(selected);
      next.has(id) ? next.delete(id) : next.add(id);
      onChange({ selected: Array.from(next) });
    };
    return (
      <div className="mt-3 grid gap-2">
        {options.map((o) => (
          <button
            key={o.id}
            disabled={disabled}
            onClick={() => toggle(o.id)}
            aria-pressed={selected.has(o.id)}
            className={`flex items-center gap-2 rounded-xl border px-4 py-2.5 text-left text-sm transition-colors focus-visible:outline-2 focus-visible:outline-brand disabled:pointer-events-none ${
              selected.has(o.id) ? "border-brand/60 bg-brand/10 text-ink" : "border-line bg-base hover:border-brand/40"
            }`}
          >
            <span
              className={`flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                selected.has(o.id) ? "border-brand bg-brand text-white" : "border-line"
              }`}
            >
              {selected.has(o.id) && <Check size={11} aria-hidden />}
            </span>
            {o.text}
          </button>
        ))}
      </div>
    );
  }

  if (question.qtype === "numeric") {
    return (
      <input
        type="number"
        disabled={disabled}
        value={(value.value as number | string) ?? ""}
        onChange={(e) => onChange({ value: e.target.valueAsNumber })}
        className="mt-3 w-40 rounded-xl border border-line bg-base px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-brand disabled:opacity-60"
        aria-label="Numeric answer"
      />
    );
  }

  // fill_blank / free_text
  return (
    <input
      type="text"
      disabled={disabled}
      value={(value.text as string) ?? ""}
      onChange={(e) => onChange({ text: e.target.value })}
      className="mt-3 w-full rounded-xl border border-line bg-base px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-brand disabled:opacity-60"
      aria-label="Text answer"
    />
  );
}

export function QuizRunner({ quizId, onExit }: { quizId: string; onExit?: () => void }) {
  const [attempt, setAttempt] = React.useState<AttemptStart | null>(null);
  const [index, setIndex] = React.useState(0);
  const [drafts, setDrafts] = React.useState<Record<string, Answer>>({});
  const [results, setResults] = React.useState<Record<string, AnswerResult>>({});
  const [finished, setFinished] = React.useState<AttemptFinishResult | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;
    startAttempt(quizId)
      .then((a) => { if (!cancelled) setAttempt(a); })
      .catch(() => { if (!cancelled) setError("Couldn't start the quiz — the forge API may be offline."); });
    return () => { cancelled = true; };
  }, [quizId]);

  if (error) {
    return (
      <Card className="py-8 text-center">
        <p className="text-sm text-danger">{error}</p>
        {onExit && <Button className="mt-4" variant="secondary" onClick={onExit}>Back</Button>}
      </Card>
    );
  }

  if (!attempt) {
    return (
      <Card className="py-8 text-center">
        <p className="text-sm text-ink-2">Starting quiz…</p>
      </Card>
    );
  }

  if (finished) {
    return (
      <Card className={finished.passed ? "border-success/40" : "border-warning/40"}>
        <p className="font-mono text-xs text-brand-cyan">QUIZ RESULT</p>
        <p className="font-display mt-1 text-xl font-bold">
          {finished.passed ? "Forged. 🔨" : "Not quite — try again."}
        </p>
        <p className="mt-1 text-sm text-ink-2">
          {finished.score}% · pass threshold {finished.pass_threshold}%
          {finished.xp_awarded && " · +30 XP"}
        </p>
        {onExit && <Button className="mt-4" onClick={onExit}>Done</Button>}
      </Card>
    );
  }

  const question = attempt.questions[index];
  const draft = drafts[question.id] ?? {};
  const result = results[question.id];
  const isLast = index === attempt.questions.length - 1;

  const check = async () => {
    setBusy(true);
    try {
      const r = await answerQuestion(attempt.attempt_id, question.id, draft);
      setResults((prev) => ({ ...prev, [question.id]: r }));
    } catch {
      setError("Couldn't submit that answer — the forge API may be offline.");
    } finally {
      setBusy(false);
    }
  };

  const next = async () => {
    if (!isLast) {
      setIndex((i) => i + 1);
      return;
    }
    setBusy(true);
    try {
      setFinished(await finishAttempt(attempt.attempt_id));
    } catch {
      setError("Couldn't finish the quiz — the forge API may be offline.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <div className="flex items-center justify-between text-xs text-ink-2">
        <span>Question {index + 1} of {attempt.questions.length}</span>
        <Badge tone="neutral">{question.difficulty}/5 difficulty</Badge>
      </div>
      <ProgressBar
        className="mt-2"
        value={(100 * index) / attempt.questions.length}
        label="Quiz progress"
      />
      <p className="font-display mt-4 font-bold">{question.body.stem}</p>

      <QuestionInput question={question} value={draft} disabled={!!result}
        onChange={(a) => setDrafts((prev) => ({ ...prev, [question.id]: a }))} />

      {result && (
        <p
          aria-live="polite"
          className={`mt-4 flex items-center gap-2 text-sm font-medium ${
            result.correct ? "text-success" : result.correct === false ? "text-danger" : "text-ink-2"
          }`}
        >
          {result.correct === true && <Check size={15} aria-hidden />}
          {result.correct === false && <X size={15} aria-hidden />}
          {result.correct === null ? "Recorded — pending review." : result.message}
        </p>
      )}

      <div className="mt-5 flex justify-end gap-2">
        {!result ? (
          <Button size="sm" onClick={() => void check()} disabled={busy}>
            Check answer
          </Button>
        ) : (
          <Button size="sm" onClick={() => void next()} disabled={busy}>
            {isLast ? "Finish quiz" : "Next question"}
          </Button>
        )}
      </div>
    </Card>
  );
}
