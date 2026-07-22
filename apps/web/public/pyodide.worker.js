/**
 * Tier-1 Runner: Pyodide (WebAssembly) in a Web Worker (ADR-0006).
 * Real CPython 3.12 in the browser — zero server risk, works offline once cached.
 *
 * Messages in:  { id, code, tests?: [{ name, code }] }
 * Messages out: { id, ok, stdout, error?, tests?: [{ name, passed, message }], ms }
 */

/* global loadPyodide, importScripts */

importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js");

const pyodideReady = loadPyodide({
  indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/",
});

self.onmessage = async (event) => {
  const { id, code, tests } = event.data;
  const started = Date.now();
  let stdout = "";

  try {
    const py = await pyodideReady;
    py.setStdout({ batched: (s) => { stdout += s + "\n"; } });
    py.setStderr({ batched: (s) => { stdout += s + "\n"; } });

    // fresh globals per run: exercises must not leak state into each other
    const globals = py.globals.get("dict")();

    await py.loadPackagesFromImports(code); // numpy etc., on demand
    await py.runPythonAsync(code, { globals });

    let testResults;
    if (Array.isArray(tests) && tests.length) {
      testResults = [];
      for (const t of tests) {
        try {
          await py.runPythonAsync(t.code, { globals });
          testResults.push({ name: t.name, passed: true, message: "ok" });
        } catch (err) {
          const msg = String(err.message || err)
            .split("\n")
            .filter((l) => l.includes("AssertionError") || l.includes("Error"))
            .slice(-1)[0] || "failed";
          testResults.push({ name: t.name, passed: false, message: msg.trim() });
        }
      }
    }
    globals.destroy();

    self.postMessage({
      id, ok: true, stdout: stdout.trimEnd(),
      tests: testResults, ms: Date.now() - started,
    });
  } catch (err) {
    self.postMessage({
      id, ok: false, stdout: stdout.trimEnd(),
      error: String(err.message || err), ms: Date.now() - started,
    });
  }
};
