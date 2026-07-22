"use client";

import * as React from "react";
import { WidgetFrame } from "./WidgetFrame";

/** f(x) = x⁴ − 3x² + x : non-convex, two minima — lr choice really matters. */
const f = (x: number) => x ** 4 - 3 * x ** 2 + x;
const df = (x: number) => 4 * x ** 3 - 6 * x + 1;

const X_MIN = -2.2, X_MAX = 2.2, W = 560, H = 240, PAD = 18;
const Y_MIN = -3.4, Y_MAX = 4.5;

const sx = (x: number) => PAD + ((x - X_MIN) / (X_MAX - X_MIN)) * (W - 2 * PAD);
const sy = (y: number) => H - PAD - ((y - Y_MIN) / (Y_MAX - Y_MIN)) * (H - 2 * PAD);

const LRS = [0.005, 0.02, 0.05, 0.12, 0.3];
const START = 0.15; // near the local max: descent direction is decided by lr+noiseless gradient

export function GradientDescentPlayground() {
  const [lrIdx, setLrIdx] = React.useState(1);
  const [path, setPath] = React.useState<number[]>([START]);
  const [playing, setPlaying] = React.useState(false);
  const lr = LRS[lrIdx];
  const x = path[path.length - 1];

  const step = React.useCallback(() => {
    setPath((p) => {
      const cur = p[p.length - 1];
      const next = cur - LRS[lrIdx] * df(cur);
      return p.length > 60 || !Number.isFinite(next) || Math.abs(next) > 10
        ? p
        : [...p, next];
    });
  }, [lrIdx]);

  React.useEffect(() => {
    if (!playing) return;
    const t = window.setInterval(step, 350);
    return () => window.clearInterval(t);
  }, [playing, step]);

  const diverged = Math.abs(x) > 2.4;
  const converged = !diverged && Math.abs(df(x)) < 0.02 && path.length > 1;
  const description = diverged
    ? `Diverged after ${path.length - 1} steps — lr=${lr} overshoots: each step lands higher than the last.`
    : converged
      ? `Converged near x=${x.toFixed(2)} (f=${f(x).toFixed(2)}) in ${path.length - 1} steps at lr=${lr}. Which minimum you reach depends on lr!`
      : `Step ${path.length - 1}: x=${x.toFixed(3)}, f(x)=${f(x).toFixed(3)}, gradient=${df(x).toFixed(2)}, lr=${lr}.`;

  const curve = Array.from({ length: 120 }, (_, i) => {
    const cx = X_MIN + (i / 119) * (X_MAX - X_MIN);
    return `${sx(cx)},${sy(f(cx))}`;
  }).join(" ");

  return (
    <WidgetFrame
      title="Gradient-Descent Playground"
      description={description}
      onReset={() => { setPath([START]); setPlaying(false); }}
      controls={
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1.5 text-xs text-ink-2">
            lr
            <input
              type="range" min={0} max={LRS.length - 1} step={1}
              value={lrIdx}
              onChange={(e) => { setLrIdx(Number(e.target.value)); setPath([START]); setPlaying(false); }}
              aria-label="Learning rate"
              aria-valuetext={String(lr)}
              className="w-24 accent-[#6366F1]"
            />
            <span className="w-10 font-mono text-brand-cyan">{lr}</span>
          </label>
          <button
            onClick={step}
            className="rounded-lg bg-base px-2.5 py-1 text-xs text-ink-2 hover:text-ink focus-visible:outline-2 focus-visible:outline-brand"
          >
            step ▸
          </button>
          <button
            onClick={() => setPlaying((p) => !p)}
            className="rounded-lg bg-brand px-2.5 py-1 text-xs font-medium text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
          >
            {playing ? "pause" : "play"}
          </button>
        </div>
      }
    >
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img"
        aria-label="Loss curve with gradient descent path">
        <polyline points={curve} fill="none" stroke="#6366F1" strokeWidth="2" opacity="0.8" />
        {path.map((px, i) =>
          i === 0 ? null : (
            <line
              key={i}
              x1={sx(path[i - 1])} y1={sy(f(path[i - 1]))}
              x2={sx(px)} y2={sy(f(px))}
              stroke="#F97316" strokeWidth="1.5" opacity={0.35 + (0.65 * i) / path.length}
            />
          ),
        )}
        {path.map((px, i) => (
          <circle
            key={i}
            cx={sx(px)} cy={sy(f(px))}
            r={i === path.length - 1 ? 7 : 3}
            fill={i === path.length - 1 ? "#F97316" : "#FBBF24"}
            opacity={i === path.length - 1 ? 1 : 0.5}
          />
        ))}
      </svg>
      <p className="mt-2 text-xs text-ink-2">
        Same start, different lr: 0.005 crawls, 0.02 finds the shallow minimum, 0.12 hops
        the hump into the deep one, 0.3 explodes. This is why learning-rate schedules exist.
      </p>
    </WidgetFrame>
  );
}
