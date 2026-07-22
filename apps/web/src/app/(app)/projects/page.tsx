"use client";

import * as React from "react";
import { Badge, Button, Card } from "@neuraforge/ui";
import { Check } from "lucide-react";
import {
  fetchProjects, submitProject,
  type ProjectOut, type ProjectSubmissionOut,
} from "@/lib/assessment";

function ProjectCard({ project }: { project: ProjectOut }) {
  const [artifactUrl, setArtifactUrl] = React.useState("");
  const [checked, setChecked] = React.useState<Record<string, boolean>>({});
  const [busy, setBusy] = React.useState(false);
  const [result, setResult] = React.useState<ProjectSubmissionOut | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const toggle = (criterion: string) =>
    setChecked((prev) => ({ ...prev, [criterion]: !prev[criterion] }));

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      setResult(await submitProject(project.id, artifactUrl, checked));
    } catch {
      setError("Couldn't submit — the forge API may be offline.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <Badge tone={project.kind === "forge" ? "spark" : "brand"}>
            {project.kind === "forge" ? "🔨 Forge Project" : "Weekly Project"} · Month {project.month}
            {project.week ? ` · Week ${project.week}` : ""}
          </Badge>
          <p className="font-display mt-2 font-bold">{project.title}</p>
        </div>
      </div>
      <p className="mt-2 text-sm text-ink-2">{project.brief_md}</p>

      {result ? (
        <div className="mt-4 rounded-xl border border-line bg-base p-4">
          <p className={`text-sm font-medium ${result.status === "submitted" ? "text-success" : "text-warning"}`}>
            {result.status === "submitted" ? "✓ Submitted" : "Needs work"}
          </p>
          <p className="mt-1 text-xs text-ink-2">{result.artifact_url}</p>
        </div>
      ) : (
        <>
          <div className="mt-4 grid gap-1.5" role="group" aria-label="Self-assessment checklist">
            {project.rubric.map((criterion) => (
              <button
                key={criterion}
                onClick={() => toggle(criterion)}
                aria-pressed={!!checked[criterion]}
                className="flex items-center gap-2 rounded-lg border border-line bg-base px-3 py-2 text-left text-sm transition-colors hover:border-brand/40 focus-visible:outline-2 focus-visible:outline-brand"
              >
                <span
                  className={`flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                    checked[criterion] ? "border-brand bg-brand text-white" : "border-line"
                  }`}
                >
                  {checked[criterion] && <Check size={11} aria-hidden />}
                </span>
                {criterion}
              </button>
            ))}
          </div>

          <label className="mt-4 block text-xs font-medium uppercase tracking-wide text-ink-2">
            Repo / PR link
            <input
              type="url"
              value={artifactUrl}
              onChange={(e) => setArtifactUrl(e.target.value)}
              placeholder="https://github.com/you/your-repo"
              className="mt-1 w-full rounded-xl border border-line bg-base px-3 py-2 text-sm normal-case text-ink focus-visible:outline-2 focus-visible:outline-brand"
            />
          </label>

          {error && <p className="mt-2 text-sm text-danger">{error}</p>}

          <Button size="sm" className="mt-3" disabled={busy || !artifactUrl} onClick={() => void submit()}>
            {busy ? "Submitting…" : "Submit project"}
          </Button>
        </>
      )}
    </Card>
  );
}

export default function ProjectsPage() {
  const [projects, setProjects] = React.useState<ProjectOut[]>([]);
  const [source, setSource] = React.useState<"api" | "mock">("mock");

  React.useEffect(() => {
    void fetchProjects().then(({ projects, source }) => {
      setProjects(projects);
      setSource(source);
    });
  }, []);

  return (
    <div className="mx-auto max-w-2xl px-6 py-8">
      <div className="flex items-center gap-3">
        <h1 className="font-display text-2xl font-bold tracking-tight">Weekly &amp; Forge Projects</h1>
        <Badge tone={source === "api" ? "success" : "warning"} className="ml-auto">
          {source === "api" ? "live data" : "offline — cached view"}
        </Badge>
      </div>
      <p className="mt-1 text-sm text-ink-2">
        Submit a link to your work — autograding runs URL/checklist checks now; deeper CI-style
        checks arrive with the content pipeline (FR-ASSESS-6).
      </p>

      <div className="mt-6 grid gap-4">
        {projects.map((p) => (
          <ProjectCard key={p.id} project={p} />
        ))}
        {projects.length === 0 && (
          <p className="py-10 text-center text-sm text-ink-2">No projects published yet.</p>
        )}
      </div>
    </div>
  );
}
