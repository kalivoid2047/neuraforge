import {
  AttentionVisualizer,
  GradientDescentPlayground,
  MatrixMultiplyStepper,
  TokenizerPlayground,
} from "@neuraforge/viz-widgets";

export const metadata = { title: "Playgrounds — Neuraforge" };

export default function Playgrounds() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <h1 className="font-display text-2xl font-bold tracking-tight">Playgrounds</h1>
      <p className="mt-1 text-sm text-ink-2">
        The interactive widget library, standalone. Every one of these is embedded in
        lessons where the concept first appears.
      </p>
      <div className="mt-6">
        <GradientDescentPlayground />
        <TokenizerPlayground />
        <AttentionVisualizer />
        <MatrixMultiplyStepper />
      </div>
    </div>
  );
}
