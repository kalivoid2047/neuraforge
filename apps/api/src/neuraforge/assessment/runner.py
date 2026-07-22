"""Server-side authoritative exercise runner (FR-ASSESS-5, ADR-0006 Tier-2).

Scope decision (Phase 11): a lightweight, cross-platform subprocess sandbox —
timeout + output caps + (POSIX-only) resource limits via `resource.setrlimit`.
The full container-free OS sandbox described in SRS §9 (systemd-run scopes,
seccomp, cgroups) is Linux-only production-deployment hardening and is
deferred to Phase 12; it would not even run on this Windows dev host. This
module is the thing Phase 12 hardens, not a finished replacement for it.

Uses blocking `subprocess.run` inside `asyncio.to_thread` rather than
`asyncio.create_subprocess_exec` — simpler, and avoids relying on
ProactorEventLoop's IOCP subprocess transport being available/well-behaved
on every host this runs on (Windows dev, Linux prod, under uvicorn or tests).

Output shape matches apps/web/src/lib/runner.ts's RunResult/TestResult so
ExerciseCell can treat the server tier as a drop-in for the Pyodide tier.
"""

import asyncio
import json
import subprocess
import sys
import time

_SCRIPT = """
import sys, json, io, contextlib

payload = json.loads(sys.stdin.read())
code = payload["code"]
tests = payload["tests"]

buf = io.StringIO()
result = {"ok": True, "tests": []}
g: dict = {}
try:
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        exec(compile(code, "<submission>", "exec"), g)
        for t in tests:
            try:
                exec(compile(t["code"], "<test>", "exec"), g)
                result["tests"].append({"name": t["name"], "passed": True, "message": "ok"})
            except Exception as e:
                result["tests"].append(
                    {"name": t["name"], "passed": False, "message": f"{type(e).__name__}: {e}"}
                )
except Exception as e:
    result["ok"] = False
    result["error"] = f"{type(e).__name__}: {e}"

result["stdout"] = buf.getvalue()
sys.stdout.write("###RESULT###" + json.dumps(result))
"""


def _preexec(mem_mb: int):
    """POSIX-only best-effort resource cap; not used on Windows (see module docstring)."""
    import resource

    def _limit():
        mem_bytes = mem_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))

    return _limit


def _run_blocking(payload: str, wall_s: float, mem_mb: int) -> dict:
    """Runs synchronously in a worker thread (see module docstring)."""
    kwargs: dict = {}
    if sys.platform != "win32":
        kwargs["preexec_fn"] = _preexec(mem_mb)

    started = time.monotonic()
    try:
        # -I: isolated mode (ignores env vars, no user site dir) — deliberately
        # NOT -S, which would also drop the venv's site-packages and break
        # numpy/torch imports in submitted exercise code (FR-RUN-2).
        proc = subprocess.run(
            [sys.executable, "-I", "-c", _SCRIPT],
            input=payload, capture_output=True, text=True, timeout=wall_s, **kwargs,
        )
    except subprocess.TimeoutExpired:
        ms = int((time.monotonic() - started) * 1000)
        return {"ok": False, "stdout": "", "error": f"timed out after {wall_s}s", "ms": ms}
    except OSError as e:
        return {"ok": False, "stdout": "", "error": f"runner unavailable: {e}", "ms": 0}

    ms = int((time.monotonic() - started) * 1000)
    marker = proc.stdout.rfind("###RESULT###")
    if marker == -1:
        detail = (proc.stderr or proc.stdout)[:4000]
        return {"ok": False, "stdout": "", "error": detail or "no output", "ms": ms}

    try:
        parsed = json.loads(proc.stdout[marker + len("###RESULT###"):])
    except json.JSONDecodeError:
        return {"ok": False, "stdout": "", "error": "malformed runner output", "ms": ms}

    parsed["ms"] = ms
    return parsed


async def run_submission(
    code: str, tests: list[dict], *, wall_s: float = 10.0, mem_mb: int = 256, output_cap: int = 4000
) -> dict:
    """Runs `code` then each test against its globals in a fresh subprocess.

    Returns {"ok", "stdout", "error"?, "tests"?: [{name, passed, message}], "ms"}.
    Never raises — execution failures degrade to ok=False (P-6).
    """
    payload = json.dumps({"code": code, "tests": tests})
    result = await asyncio.to_thread(_run_blocking, payload, wall_s, mem_mb)
    result["stdout"] = result.get("stdout", "")[:output_cap]
    return result
