import Link from "next/link";
import { notFound } from "next/navigation";
import { compileMDX } from "next-mdx-remote/rsc";
import { Badge, Button, Callout } from "@neuraforge/ui";
import {
  AttentionVisualizer,
  GradientDescentPlayground,
  MatrixMultiplyStepper,
  TokenizerPlayground,
} from "@neuraforge/viz-widgets";
import { CodeCell } from "@/features/lesson/CodeCell";
import { ExerciseCell } from "@/features/lesson/ExerciseCell";
import { LessonOutline } from "@/features/lesson/LessonOutline";
import { MathBlock } from "@/features/lesson/MathBlock";
import { QuizCard } from "@/features/lesson/QuizCard";
import { getAdjacentLessons, getLessonSource } from "@/lib/content";
import { fetchExerciseForLesson, fetchQuizForLesson } from "@/lib/assessment";

// Custom components available inside every .mdx lesson body (content/lessons/).
const mdxComponents = {
  Callout,
  MathBlock,
  CodeCell,
  ExerciseCell,
  QuizCard,
  AttentionVisualizer,
  MatrixMultiplyStepper,
  TokenizerPlayground,
  GradientDescentPlayground,
};

export default async function LessonPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const source = getLessonSource(slug);
  if (!source) notFound();
  const { frontmatter, content: raw } = source;

  // Server-fetched IDs are handed into the MDX body via `scope` rather than
  // hardcoded in the .mdx file — exercise/quiz UUIDs are DB-generated and
  // differ per environment, so authors reference `exerciseId`/`quizId` as
  // bare identifiers and get whatever this deployment's real ID is.
  const [exercise, quiz] = await Promise.all([
    fetchExerciseForLesson(slug).catch(() => null),
    fetchQuizForLesson(slug).catch(() => null),
  ]);

  const { content } = await compileMDX({
    source: raw,
    components: mdxComponents,
    options: {
      parseFrontmatter: false,
      scope: { exerciseId: exercise?.id, quizId: quiz?.id },
      // next-mdx-remote defaults to stripping all {jsExpression} props as an
      // XSS guard for untrusted remote MDX (found live-testing: it silently
      // drops component props rather than erroring, e.g. <CodeCell
      // code={"..."} /> renders with code=undefined). This content is
      // trusted — authored in-repo, reviewed via git, never user-submitted —
      // so that guard is the wrong default here.
      blockJS: false,
    },
  });

  const { prev, next } = getAdjacentLessons(slug);
  const outlineSections = frontmatter.sections.map((s) => ({ ...s, done: false }));

  return (
    <div className="mx-auto flex max-w-6xl gap-10 px-6 py-8">
      <LessonOutline
        sections={outlineSections}
        minutes={frontmatter.minutes}
        spent={0}
        difficulty={frontmatter.difficulty}
      />

      <article className="nf-prose min-w-0 flex-1">
        <p className="font-mono text-xs text-brand-cyan">LESSON {frontmatter.code}</p>
        <h1 className="font-display mt-1 text-3xl font-bold tracking-tight">{frontmatter.title}</h1>
        <div className="mt-3 flex flex-wrap gap-2">
          <Badge tone="neutral">⏱ {frontmatter.minutes} min</Badge>
          <Badge tone="neutral">
            {"★".repeat(frontmatter.difficulty)}{"☆".repeat(5 - frontmatter.difficulty)}
          </Badge>
          {frontmatter.prereqs.map((p) => (
            <Badge key={p} tone="success">{p}</Badge>
          ))}
        </div>

        <h2 id="objectives">🎯 After this lesson you can…</h2>
        <ul className="list-disc space-y-1 pl-5 text-ink">
          {frontmatter.objectives.map((o) => (
            <li key={o}>{o}</li>
          ))}
        </ul>

        {content}

        {quiz && (
          <Callout kind="tip" title="Graded mini-quiz available">
            This lesson has a {quiz.question_count}-question graded quiz (pass at{" "}
            {quiz.pass_threshold}%, awards XP). Take it from{" "}
            <Link href="/practice" className="underline">Practice Banks</Link>.
          </Callout>
        )}

        <div className="mt-10 flex items-center justify-between border-t border-line pt-6">
          {prev ? (
            <Link href={`/learn/${prev.slug}`}>
              <Button variant="ghost">← {prev.code} {prev.title}</Button>
            </Link>
          ) : (
            <span />
          )}
          {next ? (
            <Link href={`/learn/${next.slug}`}>
              <Button>{next.code} {next.title} →</Button>
            </Link>
          ) : (
            <Button disabled>Month complete 🔨</Button>
          )}
        </div>
      </article>
    </div>
  );
}
