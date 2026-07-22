import * as React from "react";

type Kind = "info" | "tip" | "warning" | "danger" | "history";

const kinds: Record<Kind, { border: string; icon: string; label: string }> = {
  info: { border: "border-info/40", icon: "ℹ", label: "Note" },
  tip: { border: "border-success/40", icon: "◆", label: "Tip" },
  warning: { border: "border-warning/40", icon: "⚠", label: "Careful" },
  danger: { border: "border-danger/40", icon: "✕", label: "Pitfall" },
  history: { border: "border-brand/40", icon: "◷", label: "History" },
};

export function Callout({
  kind = "info",
  title,
  children,
}: {
  kind?: Kind;
  title?: string;
  children: React.ReactNode;
}) {
  const k = kinds[kind];
  return (
    <aside
      className={`my-4 rounded-xl border-l-4 ${k.border} bg-raised px-4 py-3`}
      role="note"
    >
      <p className="mb-1 text-sm font-semibold text-ink">
        <span aria-hidden className="mr-1.5">{k.icon}</span>
        {title ?? k.label}
      </p>
      <div className="text-sm leading-relaxed text-ink-2">{children}</div>
    </aside>
  );
}
