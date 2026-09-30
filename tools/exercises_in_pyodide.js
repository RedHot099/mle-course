// Expression for tools/browser_eval.mjs, filled in by exercises_in_pyodide.py:
// runs each solution followed by the exercise's hidden test.
(() => {
  if (!window.__exercises) {
    window.__exercises = { done: "" };
    const solutions = __SOLUTIONS__;
    (async () => {
      const lines = [];
      for (const [id, solution] of Object.entries(solutions)) {
        const test = document.querySelector(`#${id} script[data-role="test"]`).textContent;
        const result = await Course.runPython([solution, test]);
        lines.push(`${result.error ? "FAIL" : "ok  "} ${id}${result.error ? ": " + result.error : ""}`);
      }
      window.__exercises.done = lines.join("\n");
    })().catch((error) => (window.__exercises.done = "ERROR " + error));
  }
  return window.__exercises.done;
})()
