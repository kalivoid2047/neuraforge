"use client";

import * as React from "react";
import { Flame, Zap, Moon, Sun, Search } from "lucide-react";
import { Kbd } from "@neuraforge/ui";

function ThemeToggle() {
  const [theme, setTheme] = React.useState<"dark" | "light">("dark");
  React.useEffect(() => {
    const t = document.documentElement.dataset.theme;
    // Syncing React state to a DOM attribute an inline pre-hydration script
    // (app/layout.tsx's themeScript) already set from localStorage before
    // React mounted; the one-time extra render on mount is intentional and
    // matches <html data-theme="dark" suppressHydrationWarning> in layout.tsx.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (t === "light" || t === "dark") setTheme(t);
  }, []);
  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("nf-theme", next);
    } catch {}
  };
  return (
    <button
      onClick={toggle}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
      className="flex h-9 w-9 items-center justify-center rounded-xl text-ink-2 transition-colors hover:bg-raised hover:text-ink focus-visible:outline-2 focus-visible:outline-brand"
    >
      {theme === "dark" ? <Sun size={18} aria-hidden /> : <Moon size={18} aria-hidden />}
    </button>
  );
}

export function TopBar({ streak = 14, xp = 2340 }: { streak?: number; xp?: number }) {
  return (
    <header className="sticky top-0 z-40 flex h-14 items-center gap-3 border-b border-line bg-base/80 px-4 backdrop-blur-xl md:pl-[88px]">
      <button
        className="flex h-9 items-center gap-2 rounded-xl border border-line bg-raised px-3 text-sm text-ink-2 transition-colors hover:text-ink focus-visible:outline-2 focus-visible:outline-brand"
        aria-label="Search (Ctrl+K)"
      >
        <Search size={15} aria-hidden />
        <span className="hidden sm:inline">Search lessons, terms…</span>
        <Kbd>Ctrl K</Kbd>
      </button>

      <div className="ml-auto flex items-center gap-2">
        <span
          className="flex items-center gap-1.5 rounded-full border border-spark/30 bg-spark/10 px-3 py-1 text-sm font-semibold text-spark"
          title={`Forge Streak: ${streak} days`}
        >
          <Flame size={15} aria-hidden /> {streak}
          <span className="sr-only">day forge streak</span>
        </span>
        <span
          className="flex items-center gap-1.5 rounded-full border border-line bg-raised px-3 py-1 text-sm font-semibold text-ink"
          title={`${xp.toLocaleString()} XP`}
        >
          <Zap size={15} className="text-brand-cyan" aria-hidden />
          {xp.toLocaleString()}
          <span className="sr-only">experience points</span>
        </span>
        <ThemeToggle />
        <div
          aria-label="Account: Amina"
          className="flex h-9 w-9 items-center justify-center rounded-full nf-gradient font-display text-sm font-bold text-white"
        >
          A
        </div>
      </div>
    </header>
  );
}
