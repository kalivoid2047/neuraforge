"use client";

import * as React from "react";

/**
 * Shared chrome for every Neuraforge visualizer (UIUX §6):
 * title bar, controls slot, reset, and an aria-live description region
 * so the current visual state always has a textual equivalent (FR-VIZ-3).
 */
export function WidgetFrame({
  title,
  controls,
  description,
  onReset,
  children,
}: {
  title: string;
  controls?: React.ReactNode;
  description: string;
  onReset?: () => void;
  children: React.ReactNode;
}) {
  return (
    <figure
      role="group"
      aria-label={`Interactive visualization: ${title}`}
      className="my-6 overflow-hidden rounded-2xl border border-line bg-raised"
    >
      <div className="flex flex-wrap items-center gap-3 border-b border-line px-4 py-2.5">
        <p className="font-display text-sm font-semibold text-ink">
          <span aria-hidden className="mr-1.5 text-brand-cyan">◈</span>
          {title}
        </p>
        <div className="ml-auto flex flex-wrap items-center gap-3">
          {controls}
          {onReset ? (
            <button
              onClick={onReset}
              className="rounded-lg px-2 py-1 text-xs text-ink-2 transition-colors hover:bg-base hover:text-ink focus-visible:outline-2 focus-visible:outline-brand"
            >
              ↺ Reset
            </button>
          ) : null}
        </div>
      </div>
      <div className="p-4">{children}</div>
      <figcaption
        aria-live="polite"
        className="border-t border-line bg-base/60 px-4 py-2 font-mono text-xs text-ink-2"
      >
        {description}
      </figcaption>
    </figure>
  );
}
