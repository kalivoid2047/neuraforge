"use client";

import * as React from "react";
import { Check, Copy, Play, RotateCcw } from "lucide-react";
import { runPython } from "@/lib/runner";
import { EditorHost } from "./EditorHost";

/**
 * Editable, runnable code cell (FR-LESSON-4).
 * Phase 9: Monaco editor + REAL execution via the Pyodide worker.
 * `fallbackOutput` renders if the runner is unavailable (offline/CDN blocked).
 */
export function CodeCell({
  code,
  output,
  language = "python",
}: {
  code: string;
  output?: string; // fallback output when the live runner can't load
  language?: string;
}) {
  const [value, setValue] = React.useState(code);
  const [result, setResult] = React.useState<string | null>(null);
  const [status, setStatus] = React.useState<"idle" | "running" | "ok" | "error" | "fallback">("idle");
  const [ms, setMs] = React.useState<number | null>(null);
  const [copied, setCopied] = React.useState(false);
  const edited = value !== code;

  const run = async () => {
    setStatus("running");
    setResult(null);
    setMs(null);
    try {
      const r = await runPython(value);
      setResult(r.ok ? (r.stdout || "(no output)") : `${r.stdout}\n${r.error}`.trim());
      setStatus(r.ok ? "ok" : "error");
      setMs(r.ms);
    } catch (err) {
      if (output && !edited) {
        setResult(output);
        setStatus("fallback");
      } else {
        setResult(err instanceof Error ? err.message : "Runner unavailable.");
        setStatus("error");
      }
    }
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {}
  };

  return (
    <div className="my-5 overflow-hidden rounded-2xl border border-line bg-raised">
      <div className="flex items-center gap-2 border-b border-line px-4 py-2">
        <span className="font-mono text-xs text-ink-2">{language}</span>
        <span className="font-mono text-[11px] text-brand-cyan">pyodide · runs in your browser</span>
        {edited ? (
          <span className="font-mono text-[11px] text-warning">● edited</span>
        ) : null}
        <div className="ml-auto flex items-center gap-1">
          <button
            onClick={copy}
            aria-label="Copy code"
            className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-2 hover:bg-base hover:text-ink focus-visible:outline-2 focus-visible:outline-brand"
          >
            {copied ? <Check size={14} className="text-success" aria-hidden /> : <Copy size={14} aria-hidden />}
          </button>
          <button
            onClick={() => { setValue(code); setResult(null); setStatus("idle"); }}
            aria-label="Reset to original code"
            disabled={!edited}
            className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-2 hover:bg-base hover:text-ink disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-brand"
          >
            <RotateCcw size={14} aria-hidden />
          </button>
          <button
            onClick={() => void run()}
            disabled={status === "running"}
            className="ml-1 flex h-7 items-center gap-1.5 rounded-lg bg-brand px-3 text-xs font-medium text-white transition-colors hover:bg-brand/90 disabled:opacity-60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
          >
            <Play size={12} aria-hidden /> {status === "running" ? "Running…" : "Run"}
          </button>
        </div>
      </div>

      <EditorHost value={value} onChange={setValue} />

      {(status !== "idle") && (
        <div
          aria-live="polite"
          className="border-t border-line bg-base/70 px-4 py-3 font-mono text-[13px]"
        >
          {status === "running" ? (
            <span className="text-ink-2">▸ running… (first run downloads Python — ~10 s)</span>
          ) : (
            <>
              <pre className={`whitespace-pre-wrap ${status === "error" ? "text-danger" : "text-brand-cyan"}`}>
                {result}
              </pre>
              <p className="mt-1 text-[11px] text-ink-2">
                {status === "fallback"
                  ? "runner unavailable — showing recorded output for the original code"
                  : ms !== null ? `finished in ${ms} ms` : null}
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
