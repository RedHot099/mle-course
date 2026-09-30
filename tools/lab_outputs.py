"""Execute a solved lab notebook and print the text output of every code cell.

Usage: ``python tools/lab_outputs.py labs/NN-name/NN-name.lab.py``.
Author-only: for reading what a lab shows before quoting numbers from it.
"""

import sys
from pathlib import Path

import jupytext
from nbclient import NotebookClient

from coursekit import markers


def main() -> None:
    path = Path(sys.argv[1])
    solved = markers.render(path.read_text(encoding="utf-8"), lambda _task: True)
    notebook = jupytext.reads(solved, fmt="py:percent")
    NotebookClient(
        notebook, timeout=900, resources={"metadata": {"path": str(path.parent)}}
    ).execute()
    for number, cell in enumerate(notebook.cells):
        if cell.cell_type != "code":
            continue
        texts = []
        for output in cell.get("outputs", []):
            if "text" in output:
                texts.append(output["text"])
            elif "data" in output and "text/plain" in output["data"]:
                texts.append(output["data"]["text/plain"])
            elif output.get("ename"):
                texts.append(f"{output['ename']}: {output['evalue']}")
        if texts:
            print(f"--- cell {number}\n{''.join(texts)[:1500]}")


if __name__ == "__main__":
    main()
