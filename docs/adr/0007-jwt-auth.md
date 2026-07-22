# ADR-0007: JWT access + rotating refresh cookie auth

**Status:** Accepted (realizes FR-AUTH-3) · **Date:** 2026-07-16 · **Phase:** 2

## Context
Stateless app tier (P-4) rules out server-side sessions as the primary mechanism; XSS and CSRF
must both be addressed; WebSockets need auth without tokens in URLs.

## Decision
- **Access token:** EdDSA (Ed25519) JWT, ≤15 min TTL, delivered in response body, held in memory only (never localStorage). Claims: `sub`, `role`, `ver` (token-version for global revoke), `jti`.
- **Refresh token:** opaque, rotating, httpOnly + Secure + SameSite=Lax cookie path-scoped to `/api/v1/auth`; family stored server-side (PG); **reuse detection revokes the family**.
- **CSRF:** double-submit token on cookie-bearing endpoints.
- **WS auth:** `POST /auth/ws-ticket` issues a 30 s single-use ticket presented in the WS handshake.
- **Revocation:** logout-all bumps `ver`; role changes and suspensions take effect within one access-token TTL, immediately for refresh.

## Consequences
- ✅ Horizontal scaling with no sticky sessions; XSS cannot exfiltrate refresh tokens; replayed refresh tokens self-destruct the session family.
- ⚠️ 15-min revocation lag on access tokens accepted; admin-critical routes double-check `ver` against Redis.
