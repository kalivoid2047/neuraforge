# Phase 12 — Production Deployment (Docker-free)

| | |
|---|---|
| **Document** | Phase 12 — Deployment runbook |
| **Constraint** | C-1 (SRS §2.4): no Docker/containers anywhere — packages, systemd, and shell scripts only |
| **Scope** | Deploys what phases 1–11 actually built: the API and Web services, backed by PostgreSQL, behind Nginx |

## 1. What this deploys (and what it doesn't)

ARCHITECTURE.md's full topology diagram also shows Celery workers, Celery
beat, Redis, and a separate sandboxed Runner service. **None of those exist
in the codebase** — there is no `celery`/`redis` dependency anywhere, and
exercise grading runs in-process (`assessment/runner.py`, a subprocess +
timeout sandbox, not a separate systemd-scoped service). Deploying systemd
units for services with no tasks to run would be pure scope creep, so this
phase provisions only:

- `neuraforge-api.service` — FastAPI via Gunicorn + UvicornWorker
- `neuraforge-web.service` — Next.js via `next start`
- PostgreSQL (was SQLite in dev; Alembic now owns the schema — see §3)
- Nginx — TLS termination + reverse proxy to both services

Celery/Redis/a separate Runner service, and full nonce-based CSP (SRS §6.1
calls for one; it needs a Next.js middleware that doesn't exist yet), are
tracked as follow-up work, not silently built here.

## 2. Prerequisites

- Ubuntu 24.04 LTS server (or WSL2 Ubuntu for local rehearsal — this runbook
  was live-verified against exactly that, see §6)
- A domain pointed at the server (for real TLS via certbot)
- This repo checked out somewhere accessible to the server user running
  `scripts/deploy.sh`

## 3. First-time provisioning

```bash
sudo bash scripts/provision.sh
```

Idempotent — installs nginx/postgresql/ufw/fail2ban, creates the `nf-api`
and `nf-web` system users, creates `/opt/neuraforge` and `/etc/neuraforge`,
installs `uv` and Node 20 LTS under `/opt/neuraforge`, creates the `neuraforge`
Postgres role + database (prompts for a password), generates the Ed25519 JWT
signing key at `/etc/neuraforge/jwt-ed25519.pem`, installs the systemd units
and Nginx site, and enables the firewall.

After it finishes:

1. `cp apps/api/.env.prod.example /etc/neuraforge/api.env` and fill in the
   real DB password and your domain, then `chmod 600` it.
2. Point DNS at the server, then: `certbot --nginx -d your-domain.example`
   (rewrites `/etc/nginx/sites-available/neuraforge.conf` in place to add
   the 443/TLS server block — re-add the security headers from the repo's
   `deploy/nginx/neuraforge.conf` to that new block afterward; certbot
   doesn't carry custom directives over).

## 4. Deploying a release

```bash
sudo bash scripts/deploy.sh /path/to/checked-out/source
```

Copies the source into `/opt/neuraforge/releases/<timestamp>/`, runs
`uv sync --frozen` for the API and `npm ci && npm run build` for the web
app *inside that release directory*, runs `alembic upgrade head` against
the configured database, atomically flips the `/opt/neuraforge/current`
symlink, restarts both services, and health-checks them. **A failed health
check automatically rolls the symlink back to the previous release and
restarts services** — the previous release is never deleted until a
subsequent successful deploy pushes it past the 5-release retention window.

## 5. Operations

- **Logs:** `journalctl -u neuraforge-api -f` / `journalctl -u neuraforge-web -f`
- **Manual rollback:** `ln -sfn /opt/neuraforge/releases/<older-id> /opt/neuraforge/current && sudo systemctl restart neuraforge-api neuraforge-web`
- **Backup:** `pg_dump -U neuraforge neuraforge | gzip > backup-$(date +%F).sql.gz` (nightly cron; SRS NFR-REL-2 target RPO ≤ 24h)
- **Restore:** `gunzip -c backup-*.sql.gz | psql -U neuraforge neuraforge`
- **Zero-downtime API reload** (no new migration): `systemctl reload neuraforge-api` (Gunicorn graceful `HUP`, per the unit's `ExecReload`)

## 6. What was actually verified, and how

Written scripts and configs are a claim, not proof. This phase was verified
by live-provisioning and live-deploying against a real (if local) Ubuntu
target — WSL2, which runs genuine systemd (`/proc/1/comm` is `systemd`, not
an init shim) — rather than trusting that syntactically-plausible systemd
units and shell scripts would work:

- `alembic upgrade head` run against a real PostgreSQL 18 instance — this is
  how a real bug was found and fixed: every `Mapped[datetime]` column was
  implicitly naive, but every write path passes `datetime.now(UTC)`
  (timezone-aware); Postgres/asyncpg rejects that mismatch outright where
  SQLite silently accepted it. Fixed via `Base.type_annotation_map` in
  `core/db.py` (apps/api/src/neuraforge/core/db.py) rather than annotating
  every column individually.
- `alembic downgrade base` / `upgrade head` / re-`upgrade head` cycle, to
  confirm the migration is clean and idempotent in both directions.
- The app's own `seed_if_empty()` run against that Postgres database through
  the real ORM models (not just raw SQL) — proves the models, not just the
  migration DDL, are Postgres-correct (JSONB round-trips, FKs, etc.).
- `scripts/provision.sh` and `scripts/deploy.sh` executed for real (not just
  `bash -n` syntax-checked), including a deliberate failure injection: a
  broken unit was deployed on purpose to confirm `deploy.sh`'s health-check
  → automatic-rollback path actually fires and actually restores service,
  not just that its code looks right.
- `systemctl status` / `journalctl` on the running units, and `curl` through
  Nginx end-to-end for both services — including confirming production auth
  enforcement itself works (a business route correctly returned 401 when
  called unauthenticated, proving `NF_DEV_AUTOLOGIN=false` takes effect).

This surfaced seven real bugs invisible to code review, each fixed in place:

1. Every `Mapped[datetime]` column was implicitly naive, but every write
   path passes `datetime.now(UTC)` (timezone-aware) — SQLite silently
   accepted the mismatch, Postgres/asyncpg rejected it outright. Fixed via
   `Base.type_annotation_map` in `core/db.py`, not per-column.
2. `ufw allow OpenSSH` aborted `provision.sh` because the `openssh-server`
   package (and thus its ufw app profile) wasn't installed — added to the
   package list.
3. `deploy.sh` used bash `source` to load `api.env` for the migration step;
   bash's quote-removal strips embedded quotes anywhere in a word, so
   `NF_CORS_ORIGINS=["https://x"]` became `[https://x]` — valid bash,
   invalid JSON. Switched to a `read`-based loop that treats each line as
   opaque data.
4. `.env.prod.example` had inline comments trailing on the same line as
   values (`NF_AUTO_SEED=false  # comment`) — neither bash nor systemd's
   `EnvironmentFile=` strip those, so the "value" pydantic-settings actually
   received included the comment text. Moved every comment to its own line.
5. `deploy.sh`'s `set -e` meant a failed `systemctl restart` aborted the
   script *before* reaching the health-check/rollback logic — the opposite
   of what that logic exists for. Added `|| true` so a restart failure falls
   through to the health check (which fails it properly, and rolls back).
6. `SystemCallFilter=@system-service` on `neuraforge-web.service` got
   Node/libuv SIGSYS-killed (`status=31/SYS`) — it needs syscalls outside
   that group. Removed for the web unit only; the Python API unit runs
   `@system-service` fine (verified the same way).
7. `RestrictAddressFamilies` on the web unit omitted `AF_NETLINK`, which
   `next start` needs to enumerate network interfaces at boot (for its
   startup banner) — crashed with `EAFNOSUPPORT` instead of just skipping
   the banner. Added `AF_NETLINK` to the allowed list.
8. `provision.sh` copied the Nginx site file but never reloaded Nginx —
   `systemctl enable --now nginx` is a no-op on an already-running service,
   so it kept serving whatever config was loaded when it first started. The
   API route 404'd through Nginx while working fine directly, until
   `systemctl reload nginx` was added after the config copy.

**Not verified** (inherent to the environment, not skipped): real DNS + a
real Let's Encrypt certificate (no public domain here — `certbot --nginx`
itself was not run; the shipped Nginx config is intentionally HTTP-only for
exactly this reason, see `deploy/nginx/neuraforge.conf`); GitHub Actions
actually running in CI (no git remote — `.github/workflows/ci.yml`'s steps
were each run locally instead, exactly as CI would run them);
`systemd-run`-per-execution sandboxing of learner exercise code as SRS §9
envisions it (the exercise runner's own subprocess sandbox is unchanged from
Phase 11 — see the note in `apps/api/src/neuraforge/assessment/runner.py`).
