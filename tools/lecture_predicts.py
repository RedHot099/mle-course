"""Run a lecture's "predict" blocks in CPython and compare with the keyed answer.

Usage: ``python tools/lecture_predicts.py lectures/02-functions [...]``.

Each block's output (or the name of the exception it raises) is printed next
to the option marked ``data-correct``. A block passes when the keyed option,
stripped of its explanation, equals the output (lines may be joined with
", ") or names the raised exception.
Exercises (``.pyrun``) are not solved here: that needs a human.
"""

import contextlib
import html
import io
import os
import re
import sys
import tempfile
from pathlib import Path

_BLOCK = re.compile(r'<div class="predict" id="(?P<id>[^"]+)".*?</div>', re.S)
_CODE = re.compile(r"<pre><code[^>]*>(?P<code>.*?)</code></pre>", re.S)
_KEYED = re.compile(r"<li data-correct>(?P<text>.*?)<span class=\"why\">", re.S)
_TAG = re.compile(r"<[^>]+>")


def _text(fragment: str) -> str:
    return html.unescape(_TAG.sub("", fragment)).strip()


def run(code: str) -> str:
    """Return what ``code`` prints, or the name of the exception it raises."""
    buffer = io.StringIO()
    with tempfile.TemporaryDirectory() as scratch, contextlib.redirect_stdout(buffer):
        before = Path.cwd()
        os.chdir(scratch)
        try:
            exec(compile(code, "<predict>", "exec"), {"__name__": "__predict__"})  # noqa: S102
        except Exception as error:  # noqa: BLE001 - the exception is the answer
            print(type(error).__name__)
        finally:
            os.chdir(before)
    return buffer.getvalue().strip()


def main() -> int:
    failed = 0
    for folder in sys.argv[1:]:
        page = Path(folder) / "index.html"
        source = page.read_text(encoding="utf-8")
        for block in _BLOCK.finditer(source):
            found = _CODE.search(block.group(0))
            if found is None:
                print(f"NO CODE {page.parent.name} {block['id']}")
                failed += 1
                continue
            code = _text(found["code"])
            keyed = _KEYED.search(block.group(0))
            wanted = _text(keyed["text"]) if keyed else "?"
            got = run(code)
            lines = got.splitlines()
            ok = wanted in (got, ", ".join(lines), lines[-1] if lines else "")
            failed += not ok
            print(
                f"{'ok  ' if ok else 'DIFF'} {page.parent.name} {block['id']}: {got!r}"
                + ("" if ok else f" (klucz: {wanted!r})")
            )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
