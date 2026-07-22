"use client";

/**
 * Client for the Tier-1 Pyodide runner worker (ADR-0006).
 * Singleton worker, promise-per-run, hard timeout. Any failure mode
 * (CDN unreachable, WASM unsupported, timeout) rejects cleanly so the
 * UI can degrade to its non-live fallback (P-6: degrade, never block).
 */

export type TestResult = { name: string; passed: boolean; message: string };
export type RunResult = {
  ok: boolean;
  stdout: string;
  error?: string;
  tests?: TestResult[];
  ms: number;
};

type Pending = {
  resolve: (r: RunResult) => void;
  reject: (e: Error) => void;
  timer: number;
};

let worker: Worker | null = null;
let seq = 0;
const pending = new Map<number, Pending>();

function getWorker(): Worker {
  if (!worker) {
    worker = new Worker("/pyodide.worker.js");
    worker.onmessage = (e: MessageEvent) => {
      const { id, ...result } = e.data;
      const p = pending.get(id);
      if (p) {
        window.clearTimeout(p.timer);
        pending.delete(id);
        p.resolve(result as RunResult);
      }
    };
    worker.onerror = () => {
      for (const [id, p] of pending) {
        window.clearTimeout(p.timer);
        pending.delete(id);
        p.reject(new Error("Runner worker failed to start."));
      }
      worker?.terminate();
      worker = null; // next run retries a fresh worker
    };
  }
  return worker;
}

export function runPython(
  code: string,
  tests?: { name: string; code: string }[],
  timeoutMs = 60_000, // first run includes the Pyodide download
): Promise<RunResult> {
  const id = ++seq;
  return new Promise<RunResult>((resolve, reject) => {
    const timer = window.setTimeout(() => {
      pending.delete(id);
      worker?.terminate();
      worker = null;
      reject(new Error("Run timed out (30 s execution limit)."));
    }, timeoutMs);
    pending.set(id, { resolve, reject, timer });
    getWorker().postMessage({ id, code, tests });
  });
}

/** Warm the interpreter as soon as a lesson with exercises opens. */
export function preloadRunner(): void {
  try {
    getWorker();
  } catch {
    /* degrade silently */
  }
}
