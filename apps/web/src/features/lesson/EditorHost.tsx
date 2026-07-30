"use client";

import * as React from "react";
import dynamic from "next/dynamic";

const Monaco = dynamic(() => import("@monaco-editor/react"), { ssr: false });

/**
 * Monaco with a hard fallback: if the editor hasn't mounted within 8 s
 * (offline, CDN blocked, low-end device), swap to the accessible textarea —
 * which is also the explicit "accessible editor" preference (UIUX §10.4).
 */
export function EditorHost({
  value,
  onChange,
  forceTextarea = false,
}: {
  value: string;
  onChange: (v: string) => void;
  forceTextarea?: boolean;
}) {
  const [mounted, setMounted] = React.useState(false);
  const [fallback, setFallback] = React.useState(forceTextarea);
  const [dark, setDark] = React.useState(true);

  React.useEffect(() => {
    // Syncing React state to a DOM attribute an inline pre-hydration script
    // (app/layout.tsx's themeScript) already set from localStorage before
    // React mounted; the one-time extra render on mount is intentional and
    // matches <html data-theme="dark" suppressHydrationWarning> in layout.tsx.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setDark(document.documentElement.dataset.theme !== "light");
    if (fallback) return;
    const t = window.setTimeout(() => {
      if (!mounted) setFallback(true);
    }, 8000);
    return () => window.clearTimeout(t);
  }, [mounted, fallback]);

  if (fallback) {
    return (
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        spellCheck={false}
        aria-label="Editable code"
        rows={Math.min(24, value.split("\n").length + 1)}
        className="w-full resize-y bg-transparent px-4 py-3 font-mono text-[13px] leading-relaxed text-ink outline-none"
      />
    );
  }

  return (
    <Monaco
      height={Math.min(480, (value.split("\n").length + 2) * 20)}
      language="python"
      theme={dark ? "vs-dark" : "light"}
      value={value}
      onChange={(v) => onChange(v ?? "")}
      onMount={() => setMounted(true)}
      loading={
        <div className="px-4 py-3 font-mono text-[13px] text-ink-2">
          loading editor…
        </div>
      }
      options={{
        minimap: { enabled: false },
        fontSize: 13,
        fontFamily: "JetBrains Mono, ui-monospace, monospace",
        scrollBeyondLastLine: false,
        lineNumbers: "on",
        renderLineHighlight: "none",
        padding: { top: 12, bottom: 12 },
        automaticLayout: true,
        tabSize: 4,
        ariaLabel: "Editable code",
      }}
    />
  );
}
