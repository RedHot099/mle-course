"""Validate A pilot starters and real notebook checker execution.

No learner implementations are provided or read. Positive checker tests use
expected values and Mock outputs for finite fixtures, not a working solution.
The original starters must fail; this is not a learner completion command.
"""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat import NotebookNode

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "labs"


def assignment(values: dict) -> str:
    return "\n".join(f"{key} = {value!r}" for key, value in values.items())


def positive_fixture(meta: dict) -> str:
    lines = assignment(meta["positive"])
    if fixture := meta.get("callable_fixture"):
        lines += (
            "\nfrom unittest.mock import Mock\n"
            f"{fixture['name']} = Mock(side_effect={fixture['returns']!r})"
        )
    return lines + "\n"


def require_failure(source: str) -> str:
    indented = "\n".join("    " + line for line in source.splitlines())
    return (
        "try:\n" + indented + "\nexcept AssertionError as error:\n"
        "    assert str(error), 'Check failed without a helpful message'\n"
        "else:\n    raise AssertionError('Incorrect work passed the check')\n"
    )


def verification_notebook(notebook: NotebookNode, mode: str) -> NotebookNode:
    result = copy.deepcopy(notebook)
    for cell in result.cells:
        meta = cell.metadata.get("course", {})
        if meta.get("role") != "check":
            continue
        original = cell.source
        correct = positive_fixture(meta)
        if mode == "positive":
            cell.source = correct + original
        elif mode == "starter":
            cell.source = require_failure(original) + correct + original
        else:
            wrong = assignment(meta["negative"])
            if fixture := meta.get("callable_fixture"):
                wrong = (
                    "from unittest.mock import Mock\n"
                    f"{fixture['name']} = Mock(return_value=None)"
                )
            cell.source = (
                correct + wrong + "\n" + require_failure(original) + correct + original
            )
    return result


def execute(notebook: NotebookNode, cwd: Path) -> NotebookNode:
    return NotebookClient(
        notebook,
        timeout=60,
        kernel_name="python3",
        resources={"metadata": {"path": str(cwd)}},
    ).execute()


def check_notebook(lab: dict, lessons: dict[str, dict], seen: set[str]) -> int:
    path = LABS / lab["notebook"]
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    assert set(lab["requires_labs"]) <= seen, lab["id"]
    assert notebook.metadata["course"]["lessons"] == lab["lessons"]
    assert set(lab["lessons"]) <= lessons.keys()
    assert lab["lesson_prerequisites"] == {
        key: lessons[key]["requires"] for key in lab["lessons"]
    }
    tasks: set[str] = set()
    checks = 0
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        assert cell.outputs == [] and cell.execution_count is None, cell.id
        compile(cell.source, f"{lab['id']}:{cell.id}", "exec")
        meta = cell.metadata["course"]
        if meta["role"] == "task":
            tasks.add(cell.id)
        if meta["role"] == "check":
            assert meta["task_id"] in tasks, cell.id
            assert {"positive", "negative"} <= meta.keys(), cell.id
            checks += 1
    assert tasks == set(lab["tasks"]), lab["id"]
    with tempfile.TemporaryDirectory() as directory:
        cwd = Path(directory) / "labs"
        cwd.mkdir()
        shutil.copyfile(path, cwd / path.name)
        for name in lab["data"]:
            relative = Path(name)
            assert relative.parts[0] == "data" and ".." not in relative.parts
            assert relative.name != "project-holdout.csv"
            target = cwd / relative
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(LABS / relative, target)
        for mode in ("positive", "starter", "negative"):
            execute(verification_notebook(notebook, mode), cwd)
    if checks:
        print(f"{lab['id']}: {checks} checkers verified in three modes.")
    else:
        print(f"{lab['id']}: setup/examples run; human observation rubric required.")
    return checks


def check_restart() -> None:
    first = nbformat.v4.new_notebook(
        cells=[nbformat.v4.new_code_cell("stock = 6\nprint(stock + 2)")]
    )
    with tempfile.TemporaryDirectory() as directory:
        executed = execute(first, Path(directory))
        assert executed.cells[0].outputs[0]["text"].strip() == "8"
        fresh = nbformat.v4.new_notebook(
            cells=[nbformat.v4.new_code_cell("print(stock)")]
        )
        client = NotebookClient(
            fresh,
            allow_errors=True,
            resources={"metadata": {"path": directory}},
            kernel_name="python3",
        )
        result = client.execute()
        assert result.cells[0].outputs[0]["ename"] == "NameError"
    print("Fresh-kernel experiment: saved code runs; memory is not shared.")


def main() -> None:
    manifest = json.loads((LABS / "manifest.json").read_text())
    lessons = {
        lesson["id"]: lesson
        for lesson in json.loads((ROOT / "lectures/curriculum.json").read_text())
    }
    seen: set[str] = set()
    coverage: list[str] = []
    checks = 0
    for lab in manifest["labs"]:
        assert lab["id"] not in seen
        checks += check_notebook(lab, lessons, seen)
        coverage.extend(lab["lessons"])
        seen.add(lab["id"])
    assert len(coverage) == len(set(coverage))
    assert set(coverage) == {key for key in lessons if key.startswith("A")}
    check_restart()
    print(f"A pilot: {len(seen)} labs, all 9 lessons mapped, {checks} checked tasks.")
    print("Human explanations and learner-authored implementations require a pilot.")


if __name__ == "__main__":
    main()
