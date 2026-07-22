import * as React from "react";

export function Stat({
  value,
  label,
  hint,
}: {
  value: React.ReactNode;
  label: string;
  hint?: string;
}) {
  return (
    <div className="rounded-2xl border border-line bg-raised px-4 py-3">
      <p className="font-display text-2xl font-bold tracking-tight text-ink">
        {value}
      </p>
      <p className="text-xs font-medium uppercase tracking-wide text-ink-2">
        {label}
      </p>
      {hint ? <p className="mt-0.5 text-xs text-ink-2/80">{hint}</p> : null}
    </div>
  );
}
