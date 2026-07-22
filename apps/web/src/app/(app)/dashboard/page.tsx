import Link from "next/link";
import { ArrowRight, Flame, Snowflake, Zap } from "lucide-react";
import { Badge, Button, Card, ProgressBar, ProgressRing } from "@neuraforge/ui";
import {
  achievements, activityHeatmap, continueLesson, dailySpark,
  learner, reviewQueue, upNext,
} from "@/lib/mock";

const heatColors = ["bg-line/40", "bg-brand/25", "bg-brand/50", "bg-brand/75", "bg-brand"];

export default function Dashboard() {
  const heatmap = activityHeatmap();
  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <h1 className="font-display text-2xl font-bold tracking-tight">
        Good evening, {learner.name}.
      </h1>
      <p className="mt-1 text-sm text-ink-2">
        Day {learner.streak} of your streak. The fire&apos;s still lit.
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Continue card — the single most important element (US-02) */}
        <Card className="lg:col-span-2 flex flex-col justify-between border-brand/40">
          <div>
            <p className="font-mono text-xs text-brand-cyan">{continueLesson.code}</p>
            <h2 className="font-display mt-1 text-xl font-bold">{continueLesson.title}</h2>
            <p className="mt-1 text-sm text-ink-2">{continueLesson.remaining}</p>
          </div>
          <div className="mt-4 flex items-center gap-4">
            <ProgressBar value={continueLesson.progress} label="Lesson progress" className="flex-1" />
            <span className="font-mono text-sm text-ink-2">{continueLesson.progress}%</span>
            <Link href={`/learn/${continueLesson.slug}`}>
              <Button>
                Resume <ArrowRight size={16} aria-hidden />
              </Button>
            </Link>
          </div>
        </Card>

        {/* Streak */}
        <Card>
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-ink-2">Forge Streak</p>
            <Badge tone="spark">
              <Snowflake size={11} aria-hidden /> {learner.freezes} freeze
            </Badge>
          </div>
          <p className="font-display mt-2 flex items-center gap-2 text-3xl font-bold">
            <Flame className="text-spark" aria-hidden /> {learner.streak} days
          </p>
          <div className="mt-3 flex gap-1" aria-hidden>
            {Array.from({ length: 14 }).map((_, i) => (
              <span key={i} className="h-2 flex-1 rounded-full bg-spark/80" />
            ))}
          </div>
        </Card>

        {/* Month ring + review queue */}
        <Card className="flex items-center gap-5">
          <ProgressRing value={learner.monthProgress} label="Month 7 progress" size={104} />
          <div>
            <p className="font-display font-bold">Month 7</p>
            <p className="text-sm text-ink-2">Transformers From Scratch</p>
            <p className="mt-1 text-xs text-ink-2">
              projected finish: {learner.projectedFinish}
            </p>
          </div>
        </Card>

        <Card>
          <p className="text-sm font-medium text-ink-2">Review queue</p>
          <p className="font-display mt-2 text-3xl font-bold">
            {reviewQueue.cardsDue} <span className="text-base font-medium text-ink-2">cards due</span>
          </p>
          <p className="mt-2 text-xs text-ink-2">
            weak: {reviewQueue.weakTopics.slice(0, 2).join(", ")} +{reviewQueue.weakTopics.length - 2}
          </p>
          <Link href="/review" className="mt-3 inline-block">
            <Button variant="secondary" size="sm">Start reviewing</Button>
          </Link>
        </Card>

        {/* Daily Spark */}
        <Card className="border-spark/40">
          <div className="flex items-center justify-between">
            <p className="flex items-center gap-1.5 text-sm font-medium text-spark">
              <Zap size={15} aria-hidden /> Daily Spark
            </p>
            <span className="text-xs text-ink-2">~{dailySpark.minutes} min</span>
          </div>
          <p className="font-display mt-2 font-bold">{dailySpark.title}</p>
          <p className="mt-1 text-sm text-ink-2">{dailySpark.detail}</p>
          <Button size="sm" className="mt-3">Go</Button>
        </Card>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Heatmap */}
        <Card className="lg:col-span-2">
          <p className="mb-3 text-sm font-medium text-ink-2">Last 12 weeks</p>
          <div className="flex gap-1" role="img" aria-label="Activity heatmap: 12 weeks of daily study activity">
            {heatmap.map((week, w) => (
              <div key={w} className="flex flex-1 flex-col gap-1">
                {week.map((v, d) => (
                  <span key={d} className={`aspect-square rounded ${heatColors[v]}`} />
                ))}
              </div>
            ))}
          </div>
        </Card>

        {/* Up next + achievements */}
        <div className="space-y-4">
          <Card>
            <p className="mb-2 text-sm font-medium text-ink-2">Up next</p>
            <ul className="space-y-2">
              {upNext.map((u) => (
                <li key={u.label} className="flex items-center justify-between gap-2 text-sm">
                  <span>{u.label}</span>
                  <Badge tone={u.due === "today" ? "warning" : "neutral"}>{u.due}</Badge>
                </li>
              ))}
            </ul>
          </Card>
          <Card>
            <p className="mb-2 text-sm font-medium text-ink-2">Recent achievements</p>
            <div className="flex gap-2">
              {achievements.map((a) => (
                <span key={a.title} title={`${a.title} (${a.tier})`}
                  className="flex h-10 w-10 items-center justify-center rounded-xl border border-line bg-base text-lg">
                  {a.icon}
                </span>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
