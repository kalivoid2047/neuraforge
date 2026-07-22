"use client";

/**
 * Client-side auth per ADR-0007: access token lives in memory only —
 * never localStorage. The refresh token is an httpOnly cookie the JS
 * can't read; silent refresh re-arms memory after reloads.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

function readCsrf(): string {
  const m = document.cookie.match(/(?:^|;\s*)nf_csrf=([^;]+)/);
  return m ? decodeURIComponent(m[1]) : "";
}

type ApiError = { detail?: string; title?: string };

async function post(path: string, body?: unknown, csrf = false): Promise<Response> {
  return fetch(`${API_BASE}/api/v1${path}`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(csrf ? { "X-CSRF-Token": readCsrf() } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export async function register(input: {
  email: string;
  password: string;
  display_name: string;
}): Promise<{ devToken: string | null }> {
  const res = await post("/auth/register", input);
  if (!res.ok) throw new Error(((await res.json()) as ApiError).detail ?? "Registration failed");
  const data = await res.json();
  return { devToken: data.dev_verification_token ?? null };
}

export async function verifyEmail(token: string): Promise<void> {
  const res = await fetch(
    `${API_BASE}/api/v1/auth/verify-email?token=${encodeURIComponent(token)}`,
    { credentials: "include" },
  );
  if (!res.ok) throw new Error(((await res.json()) as ApiError).detail ?? "Verification failed");
}

export async function login(email: string, password: string): Promise<void> {
  const res = await post("/auth/login", { email, password });
  if (!res.ok) throw new Error(((await res.json()) as ApiError).detail ?? "Login failed");
  accessToken = (await res.json()).access_token;
}

export async function silentRefresh(): Promise<boolean> {
  try {
    const res = await post("/auth/refresh", undefined, true);
    if (!res.ok) return false;
    accessToken = (await res.json()).access_token;
    return true;
  } catch {
    return false;
  }
}

export async function logout(): Promise<void> {
  await post("/auth/logout", undefined, true);
  accessToken = null;
}

export async function me(): Promise<{ display_name: string; email: string } | null> {
  if (!accessToken) return null;
  const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.ok ? res.json() : null;
}
