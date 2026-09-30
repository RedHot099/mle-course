// Expression for tools/browser_eval.mjs: runs every predict block of the
// open lecture in Pyodide and compares the output with the keyed option.
// Returns "" until done, then one line per block.
(() => {
  if (!window.__predicts) {
    window.__predicts = { done: "" };
    (async () => {
      const lines = [];
      for (const block of document.querySelectorAll(".predict")) {
        const code = block.querySelector("pre > code").textContent;
        const keyed = block.querySelector("li[data-correct]");
        const why = keyed.querySelector(".why");
        const wanted = keyed.textContent.replace(why ? why.textContent : "", "").trim().replace(/^[A-F](?=\S)/, "");
        const result = await Course.runPython([code]);
        const out = (result.error ? result.error.trim().split("\n").pop().split(":")[0] : result.output).trim();
        const joined = out.split("\n").join(", ");
        const last = out.split("\n").pop();
        const ok = [out, joined, last].includes(wanted);
        lines.push(`${ok ? "ok  " : "DIFF"} ${block.id}: ${JSON.stringify(out)}${ok ? "" : " (klucz: " + JSON.stringify(wanted) + ")"}`);
      }
      window.__predicts.done = lines.join("\n");
    })().catch((error) => (window.__predicts.done = "ERROR " + error));
  }
  return window.__predicts.done;
})()
