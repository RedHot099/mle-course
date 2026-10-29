"""Validate A–D pilot starters and real notebook checker execution.

No learner implementations are provided or read. Positive checker tests use
expected values and Mock outputs for finite fixtures, not a working solution.
The original starters must fail; this is not a learner completion command.
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat import NotebookNode

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "labs"
SUPPORT_FILES = {
    "practice/summary.py",
    "practice/test_summary.py",
    "practice/features.py",
    "practice/test_features.py",
    "practice/metrics.py",
    "practice/test_metrics.py",
}
TEST_STARTERS = {
    "test_summary.py": ("summary.py", 5),
    "test_features.py": ("features.py", 3),
    "test_metrics.py": ("metrics.py", 3),
}


def assignment(values: dict) -> str:
    return "\n".join(f"{key} = {value!r}" for key, value in values.items())


def fixture_files(files: dict) -> str:
    lines = []
    for name, contents in files.items():
        relative = Path(name)
        assert relative.parts[0] == "results" and ".." not in relative.parts
        lines.append(f"Path({name!r}).write_text({contents!r}, encoding='utf-8')")
    return "\n".join(lines) + "\n"


def positive_fixture(meta: dict) -> str:
    lines = assignment(meta["positive"]) + "\n" + str(meta.get("positive_code", ""))
    lines += "\n" + fixture_files(meta.get("positive_files", {}))
    if fixture := meta.get("callable_fixture"):
        returns = []
        for value in fixture["returns"]:
            if isinstance(value, dict) and "error" in value:
                assert value["error"] == "ValueError"
                returns.append(f"ValueError({value['message']!r})")
            else:
                returns.append(repr(value))
        lines += (
            "\nfrom unittest.mock import Mock\n"
            f"{fixture['name']} = Mock(side_effect=[{', '.join(returns)}])"
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
            wrong = assignment(meta["negative"]) + "\n" + meta.get("negative_code", "")
            wrong += "\n" + fixture_files(meta.get("negative_files", {}))
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


def prepare_workspace(lab: dict, path: Path, directory: Path) -> Path:
    cwd = directory / "labs"
    cwd.mkdir(parents=True)
    shutil.copyfile(path, cwd / path.name)
    for name in lab["data"]:
        relative = Path(name)
        assert relative.parts[0] == "data" and ".." not in relative.parts
        assert relative.name != "project-holdout.csv"
        target = cwd / relative
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(LABS / relative, target)
    for name in lab.get("support", []):
        assert name in SUPPORT_FILES
        target = directory / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return cwd


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
    with tempfile.TemporaryDirectory(dir=ROOT) as directory:
        for mode in ("positive", "starter", "negative"):
            cwd = prepare_workspace(lab, path, Path(directory) / mode)
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
    with tempfile.TemporaryDirectory(dir=ROOT) as directory:
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


def check_test_starter(test_name: str, module_name: str, failures: int) -> None:
    """Prove the unfinished learner tests are discovered and fail clearly."""
    with tempfile.TemporaryDirectory(dir=ROOT) as directory:
        cwd = Path(directory)
        for name in (module_name, test_name):
            shutil.copyfile(ROOT / "practice" / name, cwd / name)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", test_name],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1, result.stdout
        assert f"{failures} failed" in result.stdout, result.stdout
        assert "Write a test" in result.stdout, result.stdout
    print(f"{test_name}: all {failures} unfinished learner tests fail clearly.")


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
    assert set(coverage) == {key for key in lessons if key[0] in {"A", "B", "C", "D"}}
    check_restart()
    for test_name, (module_name, failures) in TEST_STARTERS.items():
        check_test_starter(test_name, module_name, failures)
    print(
        f"A–D pilot: {len(seen)} labs, all {len(coverage)} lessons mapped, "
        f"{checks} checked tasks."
    )
    print("Human explanations and learner-authored implementations require a pilot.")


if __name__ == "__main__":
    main()
