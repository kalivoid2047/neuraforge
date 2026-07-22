"use client";

import * as React from "react";
import { Badge, Button, Card } from "@neuraforge/ui";
import { Flame, Zap } from "lucide-react";

const API = `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1`;

type QueueCard = { card_id: string; front_md: string; back_md: string; reps: number; lapses: number };
type Planner = {
  cards_due: number;
  estimated_minutes: number;
  spark: { title: string; detail: string; minutes: number; completed: boolean };
};

const GRADES = [
  { grade: 1, label: "again", key: "1", cls: "border-danger/40 text-danger hover:bg-danger/10" },
  { grade: 2, label: "hard", key: "2", cls: "border-warning/40 text-warning hover:bg-warning/10" },
  { grade: 3, label: "good", key: "3", cls: "border-brand/40 text-brand-cyan hover:bg-brand/10" },
  { grade: 4, label: "easy", key: "4", cls: "border-success/40 text-success hover:bg-success/10" },
];

export default function ReviewPage() {
  const [planner, setPlanner] = React.useState<Planner | null>(null);
  const [queue, setQueue] = React.useState<QueueCard[]>([]);
  const [flipped, setFlipped] = React.useState(false);
  const [xp, setXp] = React.useState<number | null>(null);
  const [streak, setStreak] = React.useState<number | null>(null);
  const [offline, setOffline] = React.useState(false);
  const [lastInterval, setLastInterval] = React.useState<number | null>(null);

  const refresh = React.useCallback(async () => {
    try {
      const [p, q, x, s] = await Promise.all([
        fetch(`${API}/planner/today`).then((r) => r.json()),
        fetch(`${API}/reviews/queue`).then((r) => r.json()),
        fetch(`${API}/xp`).then((r) => r.json()),
        fetch(`${API}/streak`).then((r) => r.json()),
      ]);
      setPlanner(p); setQueue(q); setXp(x.total); setStreak(s.current);
      setOffline(false);
    } catch {
      setOffline(true);
    }
  }, []);

  React.useEffect(() => { void refresh(); }, [refresh]);

  const card = queue[0];

  const grade = async (g: number) => {
    if (!card) return;
    const res = await fetch(`${API}/reviews/${card.card_id}/grade`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grade: g }),
    });
    if (res.ok) setLastInterval((await res.json()).interval_days);
    setFlipped(false);
    void refresh();
  };

  const completeSpark = async () => {
    await fetch(`${API}/sparks/today/complete`, { method: "POST" });
    void refresh();
  };

  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === " ") { e.preventDefault(); setFlipped((f) => !f); }
      if (flipped && ["1", "2", "3", "4"].includes(e.key)) void grade(Number(e.key));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [flipped, card?.card_id]);

  if (offline) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-16">
        <Card className="py-10 text-center">
          <p className="font-display text-lg font-bold">The forge API is cold.</p>
          <p className="mt-2 text-sm text-ink-2">
            Start it: <code className="font-mono text-xs">uv run uvicorn neuraforge.main:app --app-dir src --port 8000</code>
          </p>
          <Button className="mt-4" variant="secondary" onClick={() => void refresh()}>Retry</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-8">
      <div className="flex items-center gap-3">
        <h1 className="font-display text-2xl font-bold tracking-tight">Today&apos;s forge-work</h1>
        <span className="ml-auto flex items-center gap-2 text-sm">
          {streak !== null && (
            <Badge tone="spark"><Flame size={11} aria-hidden /> {streak}</Badge>
          )}
          {xp !== null && (
            <Badge tone="brand"><Zap size={11} aria-hidden /> {xp.toLocaleString()} XP</Badge>
          )}
        </span>
      </div>
      {planner && (
        <p className="mt-1 text-sm text-ink-2">
          {planner.cards_due} cards due · ~{planner.estimated_minutes} min total
        </p>
      )}

      {/* Daily Spark */}
      {planner && (
        <Card className={`mt-6 ${planner.spark.completed ? "opacity-70" : "border-spark/40"}`}>
          <div className="flex items-center justify-between">
            <p className="flex items-center gap-1.5 text-sm font-medium text-spark">
              <Zap size={15} aria-hidden /> Daily Spark
            </p>
            <span className="text-xs text-ink-2">~{planner.spark.minutes} min</span>
          </div>
          <p className="font-display mt-2 font-bold">{planner.spark.title}</p>
          <p className="mt-1 text-sm text-ink-2">{planner.spark.detail}</p>
          {planner.spark.completed ? (
            <p className="mt-3 text-sm font-medium text-success">✓ Forged today (+15 XP)</p>
          ) : (
            <Button size="sm" className="mt-3" onClick={() => void completeSpark()}>
              Mark complete
            </Button>
          )}
        </Card>
      )}

      {/* Flash card stage */}
      <Card className="mt-4">
        {card ? (
          <>
            <div className="mb-3 flex items-center justify-between text-xs text-ink-2">
              <span>{queue.length} left · reps {card.reps} · lapses {card.lapses}</span>
              {lastInterval !== null && <span>last card: next review in {lastInterval}d</span>}
            </div>
            <button
              onClick={() => setFlipped((f) => !f)}
              className="min-h-40 w-full rounded-xl border border-line bg-base p-6 text-left transition-colors hover:border-brand/40 focus-visible:outline-2 focus-visible:outline-brand"
              aria-label={flipped ? "Card back — grade it" : "Card front — press space to flip"}
            >
              <p className="text-xs font-medium uppercase tracking-wide text-ink-2">
                {flipped ? "Answer" : "Prompt · space to flip"}
              </p>
              <p className="mt-3 leading-relaxed">
                {flipped ? card.back_md : card.front_md}
              </p>
            </button>
            {flipped && (
              <div className="mt-4 grid grid-cols-4 gap-2" role="group" aria-label="Grade this card">
                {GRADES.map((g) => (
                  <button
                    key={g.grade}
                    onClick={() => void grade(g.grade)}
                    className={`rounded-xl border px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-brand ${g.cls}`}
                  >
                    {g.label} <kbd className="ml-1 text-xs opacity-60">{g.key}</kbd>
                  </button>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="py-10 text-center">
            <p aria-hidden className="text-2xl">🔨</p>
            <p className="font-display mt-2 font-bold">Nothing due. The fire holds.</p>
            <p className="mt-1 text-sm text-ink-2">Graded cards return when the scheduler says so.</p>
          </div>
        )}
      </Card>
    </div>
  );
}
