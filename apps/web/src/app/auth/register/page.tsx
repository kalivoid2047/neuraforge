"use client";

import * as React from "react";
import Link from "next/link";
import { Button, Card, Callout } from "@neuraforge/ui";
import { register, verifyEmail } from "@/lib/auth-client";

export default function RegisterPage() {
  const [name, setName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [done, setDone] = React.useState<"verified" | "check-email" | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const { devToken } = await register({
        email, password, display_name: name,
      });
      if (devToken) {
        // Dev environment: no SMTP wired — auto-consume the verification token.
        await verifyEmail(devToken);
        setDone("verified");
      } else {
        setDone("check-email");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setBusy(false);
    }
  };

  if (done) {
    return (
      <main className="flex min-h-screen items-center justify-center px-6">
        <Card className="w-full max-w-sm text-center">
          <p aria-hidden className="text-3xl">🔨</p>
          <h1 className="font-display mt-3 text-xl font-bold">
            {done === "verified" ? "Account forged." : "Check your email"}
          </h1>
          <p className="mt-2 text-sm text-ink-2">
            {done === "verified"
              ? "Email verified (dev mode auto-verify). You can sign in now."
              : "We sent a verification link — click it, then sign in."}
          </p>
          <Link href="/auth/login" className="mt-4 inline-block">
            <Button>Go to sign in</Button>
          </Link>
        </Card>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <Card className="w-full max-w-sm">
        <p className="font-display text-center text-lg font-bold tracking-wide">
          <span aria-hidden className="mr-2 text-spark">◆</span>
          NEURA<span className="text-brand">FORGE</span>
        </p>
        <h1 className="font-display mt-4 text-xl font-bold">Start forging</h1>
        <p className="mt-1 text-sm text-ink-2">
          12 months from now, you&apos;ll have built a GPT. Month 1 starts with a
          matrix.
        </p>

        <form onSubmit={submit} className="mt-5 space-y-3">
          <label className="block text-sm">
            <span className="mb-1 block text-ink-2">Display name</span>
            <input
              required maxLength={120} autoComplete="name"
              value={name} onChange={(e) => setName(e.target.value)}
              className="h-10 w-full rounded-xl border border-line bg-base px-3 text-ink outline-none focus-visible:border-brand"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block text-ink-2">Email</span>
            <input
              type="email" required autoComplete="email"
              value={email} onChange={(e) => setEmail(e.target.value)}
              className="h-10 w-full rounded-xl border border-line bg-base px-3 text-ink outline-none focus-visible:border-brand"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block text-ink-2">Password</span>
            <input
              type="password" required minLength={10} autoComplete="new-password"
              value={password} onChange={(e) => setPassword(e.target.value)}
              className="h-10 w-full rounded-xl border border-line bg-base px-3 text-ink outline-none focus-visible:border-brand"
            />
            <span className="mt-1 block text-xs text-ink-2">At least 10 characters.</span>
          </label>

          {error ? (
            <p role="alert" className="rounded-xl border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
              {error}
            </p>
          ) : null}

          <Button type="submit" disabled={busy} className="w-full">
            {busy ? "Forging…" : "Create account"}
          </Button>
        </form>

        <Callout kind="info" title="Your data">
          Self-hosted, no trackers. Export or delete your account any time.
        </Callout>

        <p className="mt-2 text-center text-sm text-ink-2">
          Already forging?{" "}
          <Link href="/auth/login" className="text-brand-cyan hover:underline">
            Sign in
          </Link>
        </p>
      </Card>
    </main>
  );
}
