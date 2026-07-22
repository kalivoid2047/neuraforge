/**
 * Client for the Phase 11 assessment endpoints (questions, quizzes, exercises,
 * projects). Follows lib/api.ts's typed-fetch convention for browsable lists
 * (mock fallback so pages still render offline, P-6), but mutations
 * (submitting an answer, exercise code, or a project) have no sensible mock
 * equivalent — callers surface those failures the way review/page.tsx does
 * (an explicit "offline" state), not a silent mock substitute.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API = `${API_BASE}/api/v1`;

export type QuestionPublic = {
  id: string;
  qtype: string;
  bank: string;
  body: { stem: string; options?: { id: string; text: string }[] };
  topic_tags: string[];
  difficulty: number;
  bloom: string | null;
};

export type QuizOut = {
  id: string;
  kind: string;
  lesson_id: string | null;
  pass_threshold: number;
  time_limit_s: number | null;
  question_count: number;
};

export type AttemptStart = {
  attempt_id: string;
  quiz_id: string;
  questions: QuestionPublic[];
  time_limit_s: number | null;
};

export type AnswerResult = { correct: boolean | null; message: string };

export type AttemptFinishResult = {
  score: number;
  passed: boolean;
  pass_threshold: number;
  xp_awarded: boolean;
  explanations: Record<string, Record<string, string>>;
};

export type ExercisePublic = {
  id: string;
  lesson_id: string;
  title: string;
  brief: string;
  starter_code: string;
  hints: string[];
};

export type TestResultOut = { name: string; passed: boolean; message: string };

export type SubmissionResult = {
  submission_id: string;
  status: string;
  stdout: string;
  error: string | null;
  tests: TestResultOut[] | null;
  xp_awarded: boolean;
  ms: number;
};

export type ProjectOut = {
  id: string;
  kind: "weekly" | "forge";
  month: number;
  week: number | null;
  title: string;
  brief_md: string;
  rubric: string[];
};

export type ProjectSubmissionOut = {
  id: string;
  project_id: string;
  artifact_url: string;
  self_assessment: Record<string, boolean>;
  check_results: Record<string, boolean>;
  status: string;
  submitted_at: string;
};

// ── browsable lists (mock fallback, P-6) ────────────────────────────────

const mockProjects: ProjectOut[] = [
  {
    id: "mock-forge-7", kind: "forge", month: 7, week: null,
    title: "Transformer From Scratch",
    brief_md: "Implement a full encoder-decoder Transformer and train it on a small translation task.",
    rubric: [
      "Multi-head attention implemented and unit-tested",
      "Positional encoding implemented",
      "Encoder and decoder blocks compose correctly",
      "Model trains and loss decreases over epochs",
      "README explains architecture and results",
    ],
  },
];

export async function fetchProjects(
  kind?: "weekly" | "forge"
): Promise<{ projects: ProjectOut[]; source: "api" | "mock" }> {
  try {
    const qs = kind ? `?kind=${kind}` : "";
    const res = await fetch(`${API}/projects${qs}`, { cache: "no-store", signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error(`API ${res.status}`);
    return { projects: (await res.json()) as ProjectOut[], source: "api" };
  } catch {
    return { projects: kind ? mockProjects.filter((p) => p.kind === kind) : mockProjects, source: "mock" };
  }
}

const mockQuestions: QuestionPublic[] = [
  {
    id: "mock-1", qtype: "mcq_single", bank: "practice",
    body: { stem: "Why scale attention scores by 1/√d_k?" },
    topic_tags: ["attention"], difficulty: 3, bloom: "understand",
  },
  {
    id: "mock-2", qtype: "numeric", bank: "practice",
    body: { stem: "8 heads, d_model = 512. What is d_k per head?" },
    topic_tags: ["attention"], difficulty: 2, bloom: "apply",
  },
];

export async function fetchQuestions(
  params: { bank?: string; difficulty?: number } = {}
): Promise<{ questions: QuestionPublic[]; source: "api" | "mock" }> {
  try {
    const qs = new URLSearchParams();
    if (params.bank) qs.set("bank", params.bank);
    if (params.difficulty) qs.set("difficulty", String(params.difficulty));
    const res = await fetch(`${API}/questions?${qs}`, { cache: "no-store", signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error(`API ${res.status}`);
    return { questions: (await res.json()) as QuestionPublic[], source: "api" };
  } catch {
    return { questions: mockQuestions, source: "mock" };
  }
}

// ── quizzes ──────────────────────────────────────────────────────────────

export async function fetchQuizForLesson(slug: string): Promise<QuizOut | null> {
  const res = await fetch(`${API}/quizzes/lessons/${slug}`, { cache: "no-store" });
  if (!res.ok) return null;
  return (await res.json()) as QuizOut;
}

export async function startAttempt(quizId: string): Promise<AttemptStart> {
  const res = await fetch(`${API}/quizzes/${quizId}/attempts`, { method: "POST" });
  if (!res.ok) throw new Error(`Could not start attempt (${res.status})`);
  return (await res.json()) as AttemptStart;
}

export async function answerQuestion(
  attemptId: string, questionId: string, answer: Record<string, unknown>
): Promise<AnswerResult> {
  const res = await fetch(`${API}/attempts/${attemptId}/answers/${questionId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answer }),
  });
  if (!res.ok) throw new Error(`Could not submit answer (${res.status})`);
  return (await res.json()) as AnswerResult;
}

export async function finishAttempt(attemptId: string): Promise<AttemptFinishResult> {
  const res = await fetch(`${API}/attempts/${attemptId}/finish`, { method: "POST" });
  if (!res.ok) throw new Error(`Could not finish attempt (${res.status})`);
  return (await res.json()) as AttemptFinishResult;
}

// ── exercises (server-side authoritative grading) ──────────────────────

export async function fetchExerciseForLesson(slug: string): Promise<ExercisePublic | null> {
  const res = await fetch(`${API}/exercises/lessons/${slug}`, { cache: "no-store" });
  if (!res.ok) return null;
  return (await res.json()) as ExercisePublic;
}

export async function submitExerciseCode(exerciseId: string, code: string): Promise<SubmissionResult> {
  const res = await fetch(`${API}/exercises/${exerciseId}/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) throw new Error(`Could not submit code (${res.status})`);
  return (await res.json()) as SubmissionResult;
}

// ── projects ────────────────────────────────────────────────────────────

export async function submitProject(
  projectId: string, artifactUrl: string, selfAssessment: Record<string, boolean>
): Promise<ProjectSubmissionOut> {
  const res = await fetch(`${API}/projects/${projectId}/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ artifact_url: artifactUrl, self_assessment: selfAssessment }),
  });
  if (!res.ok) throw new Error(`Could not submit project (${res.status})`);
  return (await res.json()) as ProjectSubmissionOut;
}
