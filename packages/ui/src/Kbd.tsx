import * as React from "react";

export function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <kbd className="rounded-md border border-line bg-base px-1.5 py-0.5 font-mono text-[11px] text-ink-2 shadow-[inset_0_-1px_0_var(--border-subtle)]">
      {children}
    </kbd>
  );
}
