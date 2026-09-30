"""Verify the course end to end. Author-only tool.

    uv run --group authoring python tools/verify.py

Steps:

1. ruff and mypy on the authoring tree,
2. build the learner view,
3. every task check passes on the reference code,
4. every task check reports "not implemented" on the learner view,
5. every lab notebook, solved, executes top to bottom,
6. ruff and mypy pass on the learner view too (stubs must stay valid code).
"""

import os
import subprocess
import sys
from pathlib import Path

import jupytext
import release
from nbclient import NotebookClient

from coursekit import checking, markers

ROOT = release.ROOT


def _step(title: str) -> None:
    print(f"\n== {title}")


def _run(*command: str, cwd: Path = ROOT, env: dict[str, str] | None = None) -> bool:
    done = subprocess.run(command, cwd=cwd, env=env, check=False)  # noqa: S603
    return done.returncode == 0


def lint(cwd: Path, *targets: str) -> bool:
    """Run ruff and mypy in ``cwd`` with the authoring environment."""
    ok = _run("ruff", "check", ".", cwd=cwd)
    ok &= _run("ruff", "format", "--check", ".", cwd=cwd)
    ok &= _run("mypy", *targets, cwd=cwd)
    return ok


def reference_passes() -> bool:
    """Run all checks in-process against the reference code."""
    graded = [task for task in checking.select(None) if task.graded]
    results = checking.run(graded)
    print(checking.report(results))
    return all(result.status == "ok" for result in results)


def learner_view_is_unsolved() -> bool:
    """Run all checks in a subprocess that imports the learner view's code."""
    code = (
        "import sys\n"
        "from coursekit import checking\n"
        "graded = [t for t in checking.select(None) if t.graded]\n"
        "results = checking.run(graded)\n"
        "bad = [r for r in results if r.status != 'todo']\n"
        "for r in bad:\n"
        "    print(f'{r.task.id}: expected todo, got {r.status}: {r.message}')\n"
        "print(f'{len(results) - len(bad)} of {len(results)} tasks report todo')\n"
        "sys.exit(1 if bad else 0)\n"
    )
    env = {**os.environ, "PYTHONPATH": str(release.MAIN_DIR / "src")}
    return _run(sys.executable, "-c", code, env=env)


def notebooks_execute() -> bool:
    """Execute every lab, solved, in its own directory."""
    ok = True
    for path in release.source_files():
        if not path.as_posix().endswith(release.LAB_SUFFIX):
            continue
        text = (ROOT / path).read_text(encoding="utf-8")
        notebook = jupytext.reads(
            markers.render(text, lambda _task: True), fmt="py:percent"
        )
        client = NotebookClient(
            notebook,
            timeout=900,
            kernel_name="python3",
            resources={"metadata": {"path": str((ROOT / path).parent)}},
        )
        try:
            client.execute()
            print(f"ok    {path}")
        except Exception as error:  # noqa: BLE001 - report and keep going
            ok = False
            print(f"FAIL  {path}\n{error}")
    return ok


def main() -> int:
    steps = [
        ("Lint: authoring tree", lambda: lint(ROOT, "src", "tools")),
        ("Build learner view", lambda: bool(release.build())),
        ("Checks pass on the reference", reference_passes),
        ("Checks report todo on the learner view", learner_view_is_unsolved),
        ("Solved notebooks execute", notebooks_execute),
        ("Lint: learner view", lambda: lint(release.MAIN_DIR)),
    ]
    failed = []
    for title, step in steps:
        _step(title)
        if not step():
            failed.append(title)
    print("\n" + ("ALL GOOD" if not failed else "FAILED: " + "; ".join(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
