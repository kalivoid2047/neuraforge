# ADR-0006: Two-tier code execution — Pyodide + systemd-run sandbox

**Status:** Accepted (realizes C-3, FR-RUN-*) · **Date:** 2026-07-16 · **Phase:** 2

## Context
Learners run arbitrary Python. Containers are prohibited (C-1). Rejected: gVisor and
Firecracker (container-adjacent tooling and ops weight), remote third-party sandboxes (offline
requirement C-5), Jupyter kernels (no isolation).

## Decision
**Tier 1 — Pyodide (default):** exercises whose deps fit WebAssembly (pure Python, numpy) run
in a browser Web Worker. Zero server risk. Server replays the *final* submission on Tier 2
before awarding XP (anti-cheat + result integrity).

**Tier 2 — server Runner:** a small service (own uid `nf-runner-svc`) that executes each run as
uid `nf-runner-exec` inside a `systemd-run` transient scope:

```
MemoryMax=512M CPUQuota=100% TasksMax=64 RuntimeMaxSec=30
NoNewPrivileges=yes PrivateTmp=yes ProtectSystem=strict ProtectHome=yes
IPAddressDeny=any RestrictAddressFamilies=AF_UNIX
SystemCallFilter=@system-service SystemCallFilter=~@privileged @mount @debug
ReadOnlyPaths=/opt/neuraforge/runtimes InaccessiblePaths=<hidden-tests dir>
WorkingDirectory=<ephemeral tmpfs, wiped post-run>
```

Dependency sets are **runtime profiles**: read-only uv-locked venvs at
`/opt/neuraforge/runtimes/{base,torch-cpu,viz}`, swapped atomically by symlink. Hidden pytest
suites live outside the sandbox mount; output sanitizer strips paths and test bodies. Quotas
(FR-RUN-6) enforced in Redis; global concurrency semaphore; long jobs (FR-RUN-7) same mechanism
with `RuntimeMaxSec=600` via the grading queue.

## Consequences
- ✅ Most executions never touch the server; server tier has no network, no persistence, two-uid separation, kernel-enforced (cgroups+seccomp) limits.
- ✅ Scale-out = move Runner to a dedicated node; API talks to it over a private, token-authed HTTP API either way.
- ⚠️ Weaker isolation than VMs: kernel 0-days are the residual risk. Accepted for this threat model (authenticated learners, quotas, anomaly alerts) and continuously exercised by the CI sandbox-escape suite (SRS §8.2).
- ⚠️ Pyodide cold start (~2–3 s) — mitigated by lazy preload on lesson open and worker reuse.
