import * as React from "react";

export function ProgressBar({
  value,
  label,
  className = "",
}: {
  value: number; // 0..100
  label?: string;
  className?: string;
}) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(v)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
      className={`h-2 w-full overflow-hidden rounded-full bg-line/60 ${className}`}
    >
      <div
        className="h-full rounded-full bg-gradient-to-r from-brand via-brand-violet to-brand-cyan transition-[width] duration-300"
        style={{ width: `${v}%` }}
      />
    </div>
  );
}
