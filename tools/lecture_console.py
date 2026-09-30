"""Open lectures in headless Chromium and print their console messages.

Usage: ``python tools/lecture_console.py lectures/01-python-data [...]``.
Exits with 1 when any lecture logs to the console: a clean lecture logs nothing.
"""

import subprocess
import sys
from pathlib import Path


def console_lines(page: Path) -> list[str]:
    """Return the console messages Chromium logs while loading ``page``."""
    result = subprocess.run(
        [
            "chromium",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--enable-logging=stderr",
            "--v=0",
            "--virtual-time-budget=8000",
            "--dump-dom",
            page.resolve().as_uri(),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return [line for line in result.stderr.splitlines() if ":CONSOLE:" in line]


def main() -> int:
    dirty = False
    for folder in sys.argv[1:]:
        page = Path(folder) / "index.html" if Path(folder).is_dir() else Path(folder)
        lines = console_lines(page)
        dirty |= bool(lines)
        print(f"{'ok   ' if not lines else 'LOGS '} {page}")
        for line in lines:
            print(f"      {line.split('] ', 1)[-1]}")
    return 1 if dirty else 0


if __name__ == "__main__":
    sys.exit(main())
