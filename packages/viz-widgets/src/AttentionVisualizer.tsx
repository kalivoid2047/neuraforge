"use client";

import * as React from "react";
import { WidgetFrame } from "./WidgetFrame";

const SENTENCE = ["The", "animal", "didn't", "cross", "the", "street", "because", "it", "was", "too", "tired"];

/**
 * Mock multi-head attention with distinct, pedagogically meaningful patterns
 * per head (real tensors arrive when the Runner lands — FR-VIZ-4).
 *  head 0: previous-token   head 1: self+neighbors
 *  head 2: coreference ("it" → "animal")   head 3: broad/uniform
 */
function attentionWeights(head: number): number[][] {
  const n = SENTENCE.length;
  const w: number[][] = [];
  for (let q = 0; q < n; q++) {
    const row = new Array(n).fill(0).map((_, k) => {
      if (k > q) return 0; // causal mask
      switch (head) {
        case 0: return k === q - 1 ? 8 : k === q ? 2 : 0.3;
        case 1: return Math.exp(-Math.abs(q - k) / 1.2) * 5;
        case 2:
          if (q === 7 && k === 1) return 12;            // it → animal
          if (q === 10 && k === 7) return 6;            // tired → it
          return k === q ? 3 : 0.4;
        default: return 1 + 0.15 * Math.sin(q * 3.1 + k * 1.7);
      }
    });
    const sum = row.reduce((a, b) => a + b, 0);
    w.push(row.map((x) => x / sum));
  }
  return w;
}

export function AttentionVisualizer() {
  const [head, setHead] = React.useState(2);
  const [query, setQuery] = React.useState(7);
  const weights = React.useMemo(() => attentionWeights(head), [head]);

  const row = weights[query];
  const top = row.indexOf(Math.max(...row.slice(0, query + 1)));
  const description = `Head ${head + 1}, query token “${SENTENCE[query]}”: strongest attention → “${SENTENCE[top]}” (${Math.round(row[top] * 100)}%). Arrow keys change the query token.`;

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowRight") { setQuery((q) => Math.min(SENTENCE.length - 1, q + 1)); e.preventDefault(); }
    if (e.key === "ArrowLeft") { setQuery((q) => Math.max(0, q - 1)); e.preventDefault(); }
  };

  return (
    <WidgetFrame
      title="Attention Visualizer"
      description={description}
      onReset={() => { setHead(2); setQuery(7); }}
      controls={
        <div className="flex items-center gap-1" role="radiogroup" aria-label="Attention head">
          {[0, 1, 2, 3].map((h) => (
            <button
              key={h}
              role="radio"
              aria-checked={head === h}
              onClick={() => setHead(h)}
              className={`h-7 w-7 rounded-lg text-xs font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-brand ${
                head === h ? "bg-brand text-white" : "bg-base text-ink-2 hover:text-ink"
              }`}
            >
              {h + 1}
            </button>
          ))}
        </div>
      }
    >
      {/* token row: pick a query token */}
      <div className="mb-4 flex flex-wrap gap-1.5" role="listbox" aria-label="Query token" tabIndex={0} onKeyDown={onKey}>
        {SENTENCE.map((t, i) => (
          <button
            key={i}
            role="option"
            aria-selected={query === i}
            onClick={() => setQuery(i)}
            className={`rounded-lg px-2 py-1 font-mono text-sm transition-colors focus-visible:outline-2 focus-visible:outline-brand ${
              query === i
                ? "bg-brand-cyan/20 text-brand-cyan ring-1 ring-brand-cyan"
                : "bg-base text-ink-2 hover:text-ink"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* attention bars from selected query token */}
      <div className="space-y-1" aria-hidden>
        {SENTENCE.map((t, k) => (
          <div key={k} className="flex items-center gap-2">
            <span className={`w-16 shrink-0 text-right font-mono text-xs ${k === top && k <= query ? "text-spark" : "text-ink-2"}`}>
              {t}
            </span>
            <div className="h-4 flex-1 overflow-hidden rounded bg-base">
              <div
                className={`h-full rounded transition-[width] duration-300 ${k === top ? "bg-spark" : "bg-brand/70"}`}
                style={{ width: `${(k <= query ? weights[query][k] : 0) * 100}%` }}
              />
            </div>
            <span className="w-10 shrink-0 font-mono text-[11px] text-ink-2">
              {k <= query ? `${(weights[query][k] * 100).toFixed(0)}%` : "—"}
            </span>
          </div>
        ))}
      </div>
      <p className="mt-3 text-xs text-ink-2">
        Softmax rows sum to 100%. Future tokens are masked (causal decoder). Try head 3 on “it”.
      </p>
    </WidgetFrame>
  );
}
