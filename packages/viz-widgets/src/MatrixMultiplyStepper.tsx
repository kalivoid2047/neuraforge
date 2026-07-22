"use client";

import * as React from "react";
import { WidgetFrame } from "./WidgetFrame";

const A = [
  [2, 1, 3],
  [0, 4, 1],
];
const B = [
  [1, 2],
  [0, 1],
  [3, 0],
];
// C = A(2×3) · B(3×2) → 2×2, stepped one output cell at a time.

export function MatrixMultiplyStepper() {
  const [step, setStep] = React.useState(0); // 0..4 (4 = all done)
  const total = 4;
  const i = Math.min(step, total - 1) >> 1; // row of C
  const j = Math.min(step, total - 1) & 1;  // col of C

  const terms = A[i].map((a, k) => `${a}·${B[k][j]}`);
  const value = A[i].reduce((s, a, k) => s + a * B[k][j], 0);
  const done = (r: number, c: number) => step > r * 2 + c || step === total;
  const active = (r: number, c: number) => step < total && r === i && c === j;

  const description =
    step === total
      ? "All four output cells computed. C = [[11, 5], [3, 4]]."
      : `Computing C[${i}][${j}]: row ${i + 1} of A · column ${j + 1} of B = ${terms.join(" + ")} = ${value}. Step ${step + 1} of ${total}.`;

  const Cell = ({ v, hl, dim }: { v: number | string; hl?: boolean; dim?: boolean }) => (
    <td
      className={`h-10 w-12 rounded-lg text-center font-mono text-sm transition-colors duration-300 ${
        hl ? "bg-brand/25 text-brand-cyan ring-1 ring-brand" : dim ? "text-ink-2/40" : "text-ink"
      }`}
    >
      {v}
    </td>
  );

  return (
    <WidgetFrame
      title="Matrix Multiply, Step by Step"
      description={description}
      onReset={() => setStep(0)}
      controls={
        <div className="flex items-center gap-2">
          <button
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            aria-label="Previous step"
            className="rounded-lg bg-base px-2.5 py-1 text-xs text-ink-2 hover:text-ink disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-brand"
          >
            ◂ back
          </button>
          <button
            onClick={() => setStep((s) => Math.min(total, s + 1))}
            disabled={step === total}
            aria-label="Next step"
            className="rounded-lg bg-brand px-2.5 py-1 text-xs font-medium text-white disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
          >
            step ▸
          </button>
        </div>
      }
    >
      <div className="flex flex-wrap items-center justify-center gap-6">
        <table aria-label="Matrix A, 2 by 3"><tbody>
          {A.map((row, r) => (
            <tr key={r}>{row.map((v, c) => (
              <Cell key={c} v={v} hl={step < total && r === i} />
            ))}</tr>
          ))}
        </tbody></table>
        <span className="font-display text-xl text-ink-2">×</span>
        <table aria-label="Matrix B, 3 by 2"><tbody>
          {B.map((row, r) => (
            <tr key={r}>{row.map((v, c) => (
              <Cell key={c} v={v} hl={step < total && c === j} />
            ))}</tr>
          ))}
        </tbody></table>
        <span className="font-display text-xl text-ink-2">=</span>
        <table aria-label="Result matrix C, 2 by 2"><tbody>
          {[0, 1].map((r) => (
            <tr key={r}>{[0, 1].map((c) => (
              <Cell
                key={c}
                v={done(r, c) ? A[r].reduce((s, a, k) => s + a * B[k][c], 0) : active(r, c) ? "?" : "·"}
                hl={active(r, c)}
                dim={!done(r, c) && !active(r, c)}
              />
            ))}</tr>
          ))}
        </tbody></table>
      </div>

      {step < total ? (
        <p className="mt-4 text-center font-mono text-sm text-ink">
          C[{i}][{j}] = {terms.join(" + ")} ={" "}
          <span className="font-bold text-brand-cyan">{value}</span>
        </p>
      ) : (
        <p className="mt-4 text-center text-sm text-success">
          ✓ Every output cell is a dot product: row of A · column of B.
        </p>
      )}
    </WidgetFrame>
  );
}
