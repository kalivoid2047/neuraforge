import * as React from "react";

type Tone = "brand" | "spark" | "success" | "warning" | "danger" | "neutral";

const tones: Record<Tone, string> = {
  brand: "bg-brand/15 text-brand-cyan border-brand/30",
  spark: "bg-spark/15 text-spark border-spark/30",
  success: "bg-success/15 text-success border-success/30",
  warning: "bg-warning/15 text-warning border-warning/30",
  danger: "bg-danger/15 text-danger border-danger/30",
  neutral: "bg-raised text-ink-2 border-line",
};

export function Badge({
  tone = "neutral",
  className = "",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium ${tones[tone]} ${className}`}
      {...props}
    />
  );
}
