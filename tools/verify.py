"""Verify the course end to end. Author-only tool.

    uv run --group authoring python tools/verify.py

For one module only, while others are being written:

    uv run --group authoring python tools/verify.py --module 12

Steps of the full run:

1. ruff and mypy on the authoring tree,
2. build the learner view,
3. every task check passes on the reference code,
4. every task check reports "not implemented" on the learner view,
5. every lab notebook, solved, executes top to bottom,
6. ruff and mypy pass on the learner view too (stubs must stay valid code).
"""

import os
import shutil
import subprocess
import sys
import tempfile
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
        "bad = [r for r in results if r.status != r.task.starts_as]\n"
        "for r in bad:\n"
        "    print(f'{r.task.id}: expected {r.task.starts_as}, got {r.status}: '\n"
        "          f'{r.message}')\n"
        "print(f'{len(results) - len(bad)} of {len(results)} tasks start unsolved')\n"
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


def module_files(module: int) -> list[Path]:
    """Return the source files that hold solution blocks of one module."""
    found = []
    for path in release.source_files():
        name = path.as_posix()
        if not (name.startswith(release.STUB_ROOTS) and path.suffix == ".py"):
            continue
        tasks = markers.task_ids((ROOT / path).read_text(encoding="utf-8"))
        if any(markers.module_of(task) == module for task in tasks):
            found.append(path)
    return found


def verify_module(module: int) -> int:
    """Check one module in isolation, without touching the shared learner view.

    Meant for working on a module while other modules are in flux: it lints
    only this module's files and stubs only this module's blocks, in a
    scratch copy of ``src`` and ``tests``.
    """
    files = module_files(module)
    check_file = Path(f"src/coursekit/checks/m{module:02d}.py")
    own = [str(path) for path in [*files, check_file]]
    print(f"Module {module:02d}: {len(files)} files with solution blocks")
    for name in own:
        print(f"  {name}")
    failed = []

    _step("Lint: this module's files")
    ok = _run("ruff", "check", *own)
    ok &= _run("ruff", "format", "--check", *own)
    ok &= _run("mypy", "--follow-imports=silent", *own)
    if not ok:
        failed.append("lint")

    selector = f"{module:02d}"
    code = (
        "import sys\n"
        "from coursekit import checking\n"
        f"tasks = [t for t in checking.select({selector!r}) if t.graded]\n"
        "results = checking.run(tasks)\n"
        "print(checking.report(results))\n"
        "solved = sys.argv[1] == 'ok'\n"
        "wanted = [('ok' if solved else r.task.starts_as) for r in results]\n"
        "good = [r.status == w for r, w in zip(results, wanted, strict=True)]\n"
        "sys.exit(0 if results and all(good) else 1)\n"
    )

    _step("Checks pass on the reference")
    if not _run(sys.executable, "-c", code, "ok"):
        failed.append("reference does not pass")

    _step("Checks report todo once this module is stubbed")
    with tempfile.TemporaryDirectory() as scratch:
        view = Path(scratch)
        for folder in ("src", "tests", "shelfwise"):
            if (ROOT / folder).is_dir():
                shutil.copytree(ROOT / folder, view / folder)
        for path in files:
            text = (ROOT / path).read_text(encoding="utf-8")
            stubbed = markers.render(
                text, lambda task: markers.module_of(task) != module
            )
            (view / path).write_text(stubbed, encoding="utf-8")
        env = {**os.environ, "PYTHONPATH": str(view / "src")}
        if not _run(sys.executable, "-c", code, "unsolved", env=env, cwd=view):
            failed.append("stubbed module does not start unsolved")

    print("\n" + ("MODULE GOOD" if not failed else "FAILED: " + "; ".join(failed)))
    return 1 if failed else 0


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--module":
        return verify_module(int(sys.argv[2]))
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
