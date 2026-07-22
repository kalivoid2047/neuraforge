"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import { Flame, Send, X } from "lucide-react";
import { GlassPanel } from "@neuraforge/ui";

const API = `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1`;

type Citation = { source: string; lesson_slug: string | null; anchor: string | null; title: string };
type Msg = { role: "user" | "assistant"; content: string; citations?: Citation[]; fallback?: boolean };

export function EmberPanel() {
  const pathname = usePathname();
  const [open, setOpen] = React.useState(false);
  const [threadId, setThreadId] = React.useState<string | null>(null);
  const [messages, setMessages] = React.useState<Msg[]>([]);
  const [input, setInput] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  const lessonSlug = pathname.match(/^\/learn\/([^/]+)/)?.[1] ?? null;

  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === ".") {
        e.preventDefault();
        setOpen((o) => !o);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  React.useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  const ensureThread = async (): Promise<string> => {
    if (threadId) return threadId;
    const res = await fetch(`${API}/tutor/threads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ context: lessonSlug ? { lesson_slug: lessonSlug } : {} }),
    });
    if (!res.ok) throw new Error("Could not start a tutor thread.");
    const id = (await res.json()).id as string;
    setThreadId(id);
    return id;
  };

  const send = async () => {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setError(null);
    setBusy(true);
    setMessages((m) => [...m, { role: "user", content: text }, { role: "assistant", content: "" }]);

    try {
      const id = await ensureThread();
      const res = await fetch(`${API}/tutor/threads/${id}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) {
        const detail = (await res.json().catch(() => null))?.detail ?? `Error ${res.status}`;
        throw new Error(detail);
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const event = JSON.parse(line.slice(5));
          setMessages((m) => {
            const out = [...m];
            const last = { ...out[out.length - 1] } as Msg;
            if (event.type === "meta") {
              last.citations = event.citations;
              last.fallback = event.fallback;
            } else if (event.type === "token") {
              last.content += event.text;
            }
            out[out.length - 1] = last;
            return out;
          });
        }
      }
    } catch (err) {
      setMessages((m) => m.slice(0, -1)); // drop the empty assistant bubble
      setError(err instanceof Error ? err.message : "Ember is unreachable.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Close Ember tutor" : "Open Ember tutor (Ctrl+.)"}
        className="fixed bottom-5 right-5 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-spark text-white shadow-lg transition-transform hover:scale-105 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-spark"
      >
        {open ? <X size={20} aria-hidden /> : <Flame size={20} aria-hidden />}
      </button>

      {open && (
        <GlassPanel
          role="dialog"
          aria-label="Ember AI tutor"
          className="fixed bottom-20 right-5 z-50 flex h-[min(560px,75vh)] w-[min(380px,calc(100vw-40px))] flex-col overflow-hidden"
        >
          <div className="flex items-center gap-2 border-b border-white/10 px-4 py-3">
            <Flame size={16} className="text-spark" aria-hidden />
            <p className="font-display text-sm font-bold">Ember</p>
            <span className="text-xs text-ink-2">
              {lessonSlug ? `context: ${lessonSlug}` : "general"}
            </span>
          </div>

          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
            {messages.length === 0 && (
              <div className="mt-6 text-center text-sm text-ink-2">
                <p className="font-medium text-ink">Ask me anything from the forge.</p>
                <div className="mt-3 flex flex-wrap justify-center gap-2">
                  {["Why √d_k?", "Explain softmax simply", "Quiz me on attention"].map((s) => (
                    <button
                      key={s}
                      onClick={() => setInput(s)}
                      className="rounded-full border border-line bg-raised px-3 py-1 text-xs hover:border-brand/50"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={m.role === "user" ? "text-right" : ""}>
                {m.fallback && (
                  <p className="mb-1 inline-block rounded-full border border-warning/40 bg-warning/10 px-2 py-0.5 text-[11px] text-warning">
                    model offline — curriculum excerpts
                  </p>
                )}
                <div
                  className={`inline-block max-w-[85%] whitespace-pre-wrap rounded-2xl px-3.5 py-2 text-left text-sm leading-relaxed ${
                    m.role === "user"
                      ? "bg-brand text-white"
                      : "border border-line bg-raised text-ink"
                  }`}
                >
                  {m.content || (busy && i === messages.length - 1 ? "…" : "")}
                </div>
                {m.citations && m.citations.length > 0 && (
                  <p className="mt-1 flex flex-wrap gap-1">
                    {m.citations.map((c, j) => (
                      <a
                        key={j}
                        href={c.lesson_slug ? `/learn/${c.lesson_slug}${c.anchor ? `#${c.anchor}` : ""}` : "#"}
                        className="rounded-md border border-brand/30 bg-brand/10 px-1.5 py-0.5 text-[11px] text-brand-cyan hover:underline"
                      >
                        {j + 1}· {c.title.slice(0, 32)}
                      </a>
                    ))}
                  </p>
                )}
              </div>
            ))}
            {error && (
              <p role="alert" className="rounded-xl border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
                {error}
              </p>
            )}
          </div>

          <form
            onSubmit={(e) => { e.preventDefault(); void send(); }}
            className="flex items-center gap-2 border-t border-white/10 px-3 py-2.5"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="ask anything…"
              aria-label="Message Ember"
              className="h-9 flex-1 rounded-xl border border-line bg-base px-3 text-sm text-ink outline-none focus-visible:border-brand"
            />
            <button
              type="submit"
              disabled={busy || !input.trim()}
              aria-label="Send"
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand text-white disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
            >
              <Send size={15} aria-hidden />
            </button>
          </form>
        </GlassPanel>
      )}
    </>
  );
}
