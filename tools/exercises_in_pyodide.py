"""Run a lecture's exercises in Pyodide with given solutions.

Usage::

    python tools/exercises_in_pyodide.py lectures/05-numpy \\
        tools/lecture_solutions/l05.py

The solutions file defines ``SOLUTIONS = {"e1": "...code...", ...}``.
Each solution runs followed by the exercise's hidden test, as the page does
when the learner clicks "Sprawdź".
"""

import json
import runpy
import subprocess
import sys
from pathlib import Path

EXPRESSION = Path(__file__).with_suffix(".js").read_text(encoding="utf-8")


def main() -> int:
    lecture, solutions_file = Path(sys.argv[1]), sys.argv[2]
    solutions = runpy.run_path(solutions_file)["SOLUTIONS"]
    url = (lecture / "index.html").resolve().as_uri()
    expression = EXPRESSION.replace("__SOLUTIONS__", json.dumps(solutions))
    done = subprocess.run(
        ["node", "tools/browser_eval.mjs", url, expression, "240"],
        capture_output=True,
        text=True,
        check=False,
    )
    print(done.stdout.strip())
    return 0 if "FAIL" not in done.stdout and "ERROR" not in done.stdout else 1


if __name__ == "__main__":
    sys.exit(main())
