import { Card } from "@neuraforge/ui";

export function ComingSoon({ title, phase }: { title: string; phase: string }) {
  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <Card className="py-12 text-center">
        <p aria-hidden className="text-3xl">🔨</p>
        <h1 className="font-display mt-3 text-xl font-bold">{title}</h1>
        <p className="mt-2 text-sm text-ink-2">
          On the anvil — arrives in {phase} of the build plan.
        </p>
      </Card>
    </div>
  );
}
