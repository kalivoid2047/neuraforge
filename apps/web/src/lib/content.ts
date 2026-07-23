import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

/**
 * Lightweight content-as-code loader (ADR-0005, scoped down — see the ADR's
 * "lightweight" note). Reads .mdx files with YAML frontmatter directly from
 * content/lessons/ at request time; no schema validation, versioning,
 * anchor-migration, or publish-artifact pipeline yet. Good enough to get
 * lessons out of hardcoded JSX and into reviewable, authorable files.
 */

const CONTENT_DIR = path.join(process.cwd(), "..", "..", "content", "lessons");

export type LessonSection = { anchor: string; title: string };

export type LessonFrontmatter = {
  slug: string;
  month: number;
  week: number;
  ord: number;
  title: string;
  code: string; // e.g. "7.1.1"
  minutes: number;
  difficulty: number; // 1-5
  objectives: string[];
  prereqs: string[];
  sections: LessonSection[];
};

function readAllFrontmatter(): LessonFrontmatter[] {
  const files = fs.readdirSync(CONTENT_DIR).filter((f) => f.endsWith(".mdx"));
  return files
    .map((file) => {
      const raw = fs.readFileSync(path.join(CONTENT_DIR, file), "utf8");
      const { data } = matter(raw);
      return data as LessonFrontmatter;
    })
    .sort((a, b) => a.month - b.month || a.week - b.week || a.ord - b.ord);
}

export function listLessons(): LessonFrontmatter[] {
  return readAllFrontmatter();
}

export function getLessonSource(slug: string): { frontmatter: LessonFrontmatter; content: string } | null {
  const file = path.join(CONTENT_DIR, `${slug}.mdx`);
  if (!fs.existsSync(file)) return null;
  const raw = fs.readFileSync(file, "utf8");
  const { data, content } = matter(raw);
  return { frontmatter: data as LessonFrontmatter, content };
}

export function getAdjacentLessons(slug: string): {
  prev: LessonFrontmatter | null;
  next: LessonFrontmatter | null;
} {
  const all = readAllFrontmatter();
  const index = all.findIndex((l) => l.slug === slug);
  if (index === -1) return { prev: null, next: null };
  return {
    prev: index > 0 ? all[index - 1] : null,
    next: index < all.length - 1 ? all[index + 1] : null,
  };
}
