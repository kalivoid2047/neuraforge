import { month7, type LessonStatus } from "./mock";

/**
 * Thin server-side API client for Phase 6 endpoints.
 * Phase 6+ replaces this with the OpenAPI-generated packages/api-client;
 * until then: typed fetch with graceful fallback to mock data (P-6:
 * degrade, never block — the curriculum must render even if the API is down).
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type CurriculumMonth = {
  number: number;
  title: string;
  progress: number;
  weeks: {
    number: number;
    title: string;
    lessons: {
      slug: string;
      title: string;
      ord: number;
      minutes: number;
      difficulty: number;
      status: LessonStatus;
    }[];
  }[];
};

export type Curriculum = { months: CurriculumMonth[]; source: "api" | "mock" };

const mockCurriculum: Curriculum = {
  source: "mock",
  months: [
    {
      number: month7.number,
      title: month7.title,
      progress: month7.progress,
      weeks: month7.weeks.map((w, i) => ({
        number: i + 1,
        title: w.title,
        lessons: w.lessons.map((l, j) => ({ ...l, ord: j + 1 })),
      })),
    },
  ],
};

export async function fetchCurriculum(): Promise<Curriculum> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/curriculum`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    });
    if (!res.ok) throw new Error(`API ${res.status}`);
    const data = (await res.json()) as { months: CurriculumMonth[] };
    return { months: data.months, source: "api" };
  } catch {
    return mockCurriculum;
  }
}
