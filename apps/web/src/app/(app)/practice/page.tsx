"use client";

import * as React from "react";
import { Badge, Button, Card } from "@neuraforge/ui";
import { fetchQuestions, fetchQuizForLesson, type QuestionPublic, type QuizOut } from "@/lib/assessment";
import { QuizRunner } from "@/features/assessment/QuizRunner";

// Demo scope (Phase 5+ convention, see mock.ts): the seeded curriculum only
// populates Month 7's current lesson with a mini-quiz + exercise.
const DEMO_LESSON_SLUG = "multi-head-attention";

export default function PracticePage() {
  const [quiz, setQuiz] = React.useState<QuizOut | null>(null);
  const [questions, setQuestions] = React.useState<QuestionPublic[]>([]);
  const [source, setSource] = React.useState<"api" | "mock">("mock");
  const [running, setRunning] = React.useState(false);

  React.useEffect(() => {
    void fetchQuizForLesson(DEMO_LESSON_SLUG).then(setQuiz);
    void fetchQuestions({ bank: "practice" }).then(({ questions, source }) => {
      setQuestions(questions);
      setSource(source);
    });
  }, []);

  return (
    <div className="mx-auto max-w-2xl px-6 py-8">
      <div className="flex items-center gap-3">
        <h1 className="font-display text-2xl font-bold tracking-tight">Practice Banks</h1>
        <Badge tone={source === "api" ? "success" : "warning"} className="ml-auto">
          {source === "api" ? "live data" : "offline — cached view"}
        </Badge>
      </div>
      <p className="mt-1 text-sm text-ink-2">Mini-quizzes, question banks, and coding exercises (FR-ASSESS-1..5).</p>

      {quiz && !running && (
        <Card className="mt-6 border-brand/40">
          <p className="font-mono text-xs text-brand-cyan">MINI QUIZ · {DEMO_LESSON_SLUG}</p>
          <p className="font-display mt-1 font-bold">
            {quiz.question_count} questions · pass at {quiz.pass_threshold}%
          </p>
          <Button size="sm" className="mt-3" onClick={() => setRunning(true)}>
            Start quiz
          </Button>
        </Card>
      )}

      {running && quiz && (
        <div className="mt-6">
          <QuizRunner quizId={quiz.id} onExit={() => setRunning(false)} />
        </div>
      )}

      <h2 className="font-display mt-8 text-lg font-bold">Question bank</h2>
      <div className="mt-3 grid gap-2">
        {questions.map((q) => (
          <Card key={q.id} className="py-3">
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm">{q.body.stem}</p>
              <Badge tone="neutral" className="shrink-0">{q.difficulty}/5</Badge>
            </div>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {q.topic_tags.map((t) => (
                <Badge key={t} tone="brand">{t}</Badge>
              ))}
            </div>
          </Card>
        ))}
        {questions.length === 0 && (
          <p className="py-6 text-center text-sm text-ink-2">No practice questions published yet.</p>
        )}
      </div>
    </div>
  );
}
