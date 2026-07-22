"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button, Card } from "@neuraforge/ui";
import { login } from "@/lib/auth-client";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      setBusy(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <Card className="w-full max-w-sm">
        <p className="font-display text-center text-lg font-bold tracking-wide">
          <span aria-hidden className="mr-2 text-spark">◆</span>
          NEURA<span className="text-brand">FORGE</span>
        </p>
        <h1 className="font-display mt-4 text-xl font-bold">Welcome back</h1>
        <p className="mt-1 text-sm text-ink-2">The forge is still warm.</p>

        <form onSubmit={submit} className="mt-5 space-y-3">
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
              type="password" required autoComplete="current-password"
              value={password} onChange={(e) => setPassword(e.target.value)}
              className="h-10 w-full rounded-xl border border-line bg-base px-3 text-ink outline-none focus-visible:border-brand"
            />
          </label>

          {error ? (
            <p role="alert" className="rounded-xl border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
              {error}
            </p>
          ) : null}

          <Button type="submit" disabled={busy} className="w-full">
            {busy ? "Signing in…" : "Sign in"}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-ink-2">
          New to the forge?{" "}
          <Link href="/auth/register" className="text-brand-cyan hover:underline">
            Create an account
          </Link>
        </p>
      </Card>
    </main>
  );
}
