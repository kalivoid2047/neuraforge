"use client";

import * as React from "react";
import { Check, ChevronRight, Lightbulb, Play, X } from "lucide-react";
import { Button } from "@neuraforge/ui";
import { runPython, type TestResult } from "@/lib/runner";
import { submitExerciseCode } from "@/lib/assessment";
import { EditorHost } from "./EditorHost";

export type ExerciseSpec = {
  id: string;
  title: string;
  brief: string;
  starterCode: string;
  /** Tier-1: instant client-side feedback (Pyodide, ADR-0006). Not authoritative. */
  tests: { name: string; code: string }[];
  hints: string[];
  /** Phase 11: backend Exercise id. When present, every successful client
   *  run is replayed server-side against the hidden/authoritative suite —
   *  that server verdict, not this one, is what awards XP. Omit to keep
   *  this cell purely client-graded (e.g. lessons with no backend record). */
  exerciseId?: string;
};

type ServerState = "idle" | "checking" | "passed" | "failed" | "offline";

export function ExerciseCell({ spec }: { spec: ExerciseSpec }) {
  const [value, setValue] = React.useState(spec.starterCode);
  const [results, setResults] = React.useState<TestResult[] | null>(null);
  const [stdout, setStdout] = React.useState("");
  const [running, setRunning] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [hintsOpen, setHintsOpen] = React.useState(0);
  const [attempts, setAttempts] = React.useState(0);
  const [serverState, setServerState] = React.useState<ServerState>("idle");
  const [xpAwarded, setXpAwarded] = React.useState(false);

  const passed = results !== null && results.every((r) => r.passed);

  // Tier-2: authoritative replay against the hidden suite (FR-ASSESS-5).
  // Fire-and-forget from run()'s perspective — a slow/offline API must never
  // block the instant Tier-1 feedback the learner already has (P-6).
  const verifyServerSide = React.useCallback(async () => {
    if (!spec.exerciseId) return;
    setServerState("checking");
    try {
      const r = await submitExerciseCode(spec.exerciseId, value);
      setServerState(r.status === "passed" ? "passed" : "failed");
      setXpAwarded(r.xp_awarded);
    } catch {
      setServerState("offline");
    }
  }, [spec.exerciseId, value]);

  const run = async () => {
    setRunning(true);
    setError(null);
    setServerState("idle");
    try {
      const r = await runPython(value, spec.tests);
      setStdout(r.stdout);
      if (!r.ok) {
        setError(r.error ?? "Execution failed");
        setResults(null);
      } else {
        setResults(r.tests ?? []);
        void verifyServerSide();
      }
      setAttempts((a) => a + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Runner unavailable — try again online.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="my-6 overflow-hidden rounded-2xl border border-brand/40 bg-raised">
      <div className="border-b border-line px-5 py-3">
        <p className="font-mono text-xs text-brand-cyan">GRADED EXERCISE · {spec.id}</p>
        <p className="font-display mt-1 font-bold">{spec.title}</p>
        <p className="mt-1 text-sm text-ink-2">{spec.brief}</p>
      </div>

      <EditorHost value={value} onChange={setValue} />

      <div className="flex flex-wrap items-center gap-2 border-t border-line px-4 py-2.5">
        <Button size="sm" onClick={() => void run()} disabled={running}>
          <Play size={13} aria-hidden />
          {running ? "Testing…" : "Run tests"}
        </Button>
        {hintsOpen < spec.hints.length && (
          <Button size="sm" variant="ghost" onClick={() => setHintsOpen((h) => h + 1)}>
            <Lightbulb size={13} aria-hidden />
            Hint {hintsOpen + 1}/{spec.hints.length}
          </Button>
        )}
        <span className="ml-auto font-mono text-xs text-ink-2">attempts: {attempts}</span>
      </div>

      {spec.hints.slice(0, hintsOpen).map((h, i) => (
        <p key={i} className="border-t border-line bg-base/50 px-5 py-2.5 text-sm text-ink-2">
          <span className="font-medium text-warning">Hint {i + 1}:</span> {h}
        </p>
      ))}

      {error && (
        <pre className="whitespace-pre-wrap border-t border-line bg-base/70 px-5 py-3 font-mono text-[13px] text-danger">
          {error}
        </pre>
      )}

      {results && (
        <div aria-live="polite" className="border-t border-line bg-base/70 px-5 py-3">
          {results.map((r) => (
            <p key={r.name} className="flex items-start gap-2 py-0.5 font-mono text-[13px]">
              {r.passed ? (
                <Check size={15} className="mt-0.5 shrink-0 text-success" aria-hidden />
              ) : (
                <X size={15} className="mt-0.5 shrink-0 text-danger" aria-hidden />
              )}
              <span className={r.passed ? "text-ink" : "text-danger"}>
                {r.name}
                {!r.passed && <span className="block text-xs opacity-80">{r.message}</span>}
              </span>
            </p>
          ))}
          {stdout && (
            <pre className="mt-2 whitespace-pre-wrap font-mono text-xs text-ink-2">{stdout}</pre>
          )}
          <p className={`mt-2 text-sm font-medium ${passed ? "text-success" : "text-ink-2"}`}>
            {passed ? (
              "All tests passed — forged. 🔨"
            ) : (
              <>
                {results.filter((r) => r.passed).length}/{results.length} passing
                <ChevronRight size={13} className="inline" aria-hidden /> read the first
                failure, fix, re-run.
              </>
            )}
          </p>
          {spec.exerciseId && serverState !== "idle" && (
            <p aria-live="polite" className="mt-1.5 text-xs text-ink-2">
              {serverState === "checking" && "Verifying against the hidden test suite…"}
              {serverState === "passed" && (
                <span className="text-success">✓ Server-verified{xpAwarded && " · +20 XP"}</span>
              )}
              {serverState === "failed" && (
                <span className="text-warning">Hidden tests caught an edge case — Tier-1 passed, server didn&apos;t.</span>
              )}
              {serverState === "offline" && "Server verification unavailable — Tier-1 result stands for now."}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
