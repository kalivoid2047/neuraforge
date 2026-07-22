"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, BookOpen, Hammer, ListChecks, RotateCcw,
  LineChart, NotebookPen,
} from "lucide-react";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/learn", label: "Learn", icon: BookOpen },
  { href: "/projects", label: "Projects", icon: Hammer },
  { href: "/practice", label: "Practice", icon: ListChecks },
  { href: "/review", label: "Review", icon: RotateCcw },
  { href: "/stats", label: "Stats", icon: LineChart },
  { href: "/notes", label: "Notes", icon: NotebookPen },
];

export function Rail() {
  const pathname = usePathname();
  return (
    <nav
      aria-label="Primary"
      className="fixed inset-y-0 left-0 z-30 hidden w-[72px] flex-col items-center gap-1 border-r border-line bg-base pt-4 md:flex"
    >
      <Link
        href="/"
        aria-label="Neuraforge home"
        className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl text-lg text-spark"
      >
        ◆
      </Link>
      {items.map(({ href, label, icon: Icon }) => {
        const active = pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            aria-current={active ? "page" : undefined}
            className={`group relative flex h-11 w-11 items-center justify-center rounded-xl transition-colors ${
              active
                ? "bg-brand/15 text-brand-cyan"
                : "text-ink-2 hover:bg-raised hover:text-ink"
            }`}
          >
            <Icon size={20} strokeWidth={1.5} aria-hidden />
            <span className="pointer-events-none absolute left-full ml-2 whitespace-nowrap rounded-lg border border-line bg-raised px-2 py-1 text-xs text-ink opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
              {label}
            </span>
            {active ? (
              <span aria-hidden className="absolute -left-[13px] h-6 w-1 rounded-full nf-gradient" />
            ) : null}
          </Link>
        );
      })}
    </nav>
  );
}
