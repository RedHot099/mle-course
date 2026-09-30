"""Build the learner view (branch ``main``) from the authoring tree.

Author-only tool. Run from the repository root on the ``solutions`` branch:

    uv run --group authoring python tools/release.py

The result lands in ``_main/``, a git worktree of the ``main`` branch. Review
it, then commit there. Nothing is committed or pushed by this script.

What the build does:

- every solution block becomes its stub (see ``coursekit.markers``),
- every ``*.lab.py`` becomes a notebook with stubs,
- files listed in ``AUTHOR_ONLY`` are left out,
- the content of ``learner/`` is copied to the root of the learner view.

On the authoring side it also refreshes ``*.solution.ipynb`` next to each
``*.lab.py``.
"""

import fnmatch
import shutil
import subprocess
from pathlib import Path

import jupytext

from coursekit import markers

ROOT = Path(__file__).resolve().parents[1]
MAIN_DIR = ROOT / "_main"
OVERLAY = "learner"
LAB_SUFFIX = ".lab.py"
# Only learner-owned code holds solution blocks. Course tooling mentions the
# markers in its documentation and must be copied untouched.
STUB_ROOTS = ("src/freshcast/", "tests/", "shelfwise/")
AUTHOR_ONLY = [
    "tools/*",
    "docs/design.md",
    "docs/authoring.md",
    "AGENTS.md",
    "CLAUDE.md",
    "*.solution.ipynb",
    ".github/workflows/course-ci.yml",
]
_KERNEL = {"display_name": "Python 3", "language": "python", "name": "python3"}


def _git(*args: str, cwd: Path = ROOT) -> str:
    done = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout


def source_files() -> list[Path]:
    """Return tracked and untracked-but-not-ignored files, relative to the root."""
    listing = _git("ls-files", "--cached", "--others", "--exclude-standard")
    files = [Path(line) for line in listing.splitlines() if line]
    return sorted(path for path in files if (ROOT / path).is_file())


def is_author_only(path: Path) -> bool:
    """Tell whether a file stays out of the learner view."""
    name = path.as_posix()
    return any(fnmatch.fnmatch(name, pattern) for pattern in AUTHOR_ONLY)


def has_blocks(source: Path) -> bool:
    """Tell whether a Python file contains at least one solution block."""
    return bool(markers.task_ids(source.read_text(encoding="utf-8")))


def notebook_from_lab(text: str, *, solved: bool) -> str:
    """Convert a percent-format lab to notebook JSON, stubbed or solved."""
    rendered = markers.render(text, lambda _task: solved)
    notebook = jupytext.reads(rendered, fmt="py:percent")
    notebook.metadata["kernelspec"] = _KERNEL
    notebook.metadata.pop("jupytext", None)
    return str(jupytext.writes(notebook, fmt="ipynb"))


def ensure_worktree() -> None:
    """Create the ``_main`` worktree on first use."""
    if (MAIN_DIR / ".git").exists():
        return
    branches = _git("branch", "--list", "main")
    if branches.strip():
        _git("worktree", "add", str(MAIN_DIR), "main")
    else:
        _git("worktree", "add", "--orphan", "-b", "main", str(MAIN_DIR))


def clear(dest: Path) -> None:
    """Remove everything from a learner view except its git link."""
    for child in dest.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def _write(dest: Path, relative: Path, content: str | bytes) -> None:
    target = dest / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        target.write_bytes(content)
    else:
        target.write_text(content, encoding="utf-8")


def build(dest: Path = MAIN_DIR) -> dict[str, int]:
    """Write the learner view to ``dest`` and refresh the solved notebooks.

    ``dest`` defaults to the ``_main`` worktree. Any other directory is
    treated as a scratch copy: it is created if missing and gets no git link.
    """
    if dest == MAIN_DIR:
        ensure_worktree()
    dest.mkdir(parents=True, exist_ok=True)
    clear(dest)
    counts = {"copied": 0, "stubbed": 0, "notebooks": 0, "skipped": 0}
    stubbed: list[Path] = []

    for path in source_files():
        source = ROOT / path
        name = path.as_posix()

        if name.endswith(LAB_SUFFIX):
            text = source.read_text(encoding="utf-8")
            stem = name.removesuffix(LAB_SUFFIX)
            _write(dest, Path(f"{stem}.ipynb"), notebook_from_lab(text, solved=False))
            solved = ROOT / f"{stem}.solution.ipynb"
            solved.write_text(notebook_from_lab(text, solved=True), encoding="utf-8")
            counts["notebooks"] += 1
        elif path.parts[0] == OVERLAY:
            _write(dest, Path(*path.parts[1:]), source.read_bytes())
            counts["copied"] += 1
        elif is_author_only(path):
            counts["skipped"] += 1
        elif (
            name.startswith(STUB_ROOTS) and path.suffix == ".py" and has_blocks(source)
        ):
            text = source.read_text(encoding="utf-8")
            _write(dest, path, markers.render(text, lambda _task: False))
            stubbed.append(path)
        else:
            _write(dest, path, source.read_bytes())
            counts["copied"] += 1

    tidy_stubs(dest, stubbed)
    counts["stubbed"] = len(stubbed)
    return counts


def tidy_stubs(dest: Path, stubbed: list[Path]) -> None:
    """Drop imports that only the removed reference code used, then format.

    Without this, every stub would fail ``ruff check`` with unused imports
    until the learner reaches that task.
    """
    if not stubbed:
        return
    files = [str(path) for path in stubbed]
    subprocess.run(  # noqa: S603
        ["ruff", "check", "--select", "F401,I", "--fix", "--quiet", *files],  # noqa: S607
        cwd=dest,
        check=True,
    )
    subprocess.run(  # noqa: S603
        ["ruff", "format", "--quiet", *files],  # noqa: S607
        cwd=dest,
        check=True,
    )


def main() -> None:
    counts = build()
    print(f"Learner view written to {MAIN_DIR.relative_to(ROOT)}/")
    for label, count in counts.items():
        print(f"  {label:<10} {count}")


if __name__ == "__main__":
    main()
