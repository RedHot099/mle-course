"""Check foundations pages, links and supplied examples without learner solutions.

Run from the repository root: uv run python tools/verify_foundations.py
Only supplied examples execute. Exercise starters must remain unsolved.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "lectures"
VOID = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "source",
    "wbr",
}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Node | str] = field(default_factory=list)

    def text(self) -> str:
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)

    def walk(self) -> Iterator[Node]:
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def has_class(self, name: str) -> bool:
        return name in self.attrs.get("class", "").split()


class Document(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]
        self.feed(path.read_text(encoding="utf-8"))
        self.close()
        assert len(self.stack) == 1, f"Unclosed HTML: {path.name}"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {key: value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID:
            return
        assert self.stack[-1].tag == tag, f"Unbalanced HTML: {tag}"
        self.stack.pop()

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def check_links(path: Path, document: Node) -> None:
    ids = [n.attrs["id"] for n in document.walk() if "id" in n.attrs]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {path.name}"
    for node in document.walk():
        for attribute in ("href", "src"):
            if attribute in node.attrs:
                check_target(path, node.attrs[attribute])


def check_target(path: Path, target: str) -> None:
    url = urlsplit(target)
    if url.scheme or url.netloc:
        return
    destination = (path.parent / unquote(url.path)).resolve() if url.path else path
    assert destination.exists(), f"Broken link: {path.name}: {target}"
    if url.fragment and destination.suffix == ".html":
        ids = {n.attrs.get("id") for n in Document(destination).root.walk()}
        assert unquote(url.fragment) in ids, f"Missing anchor: {path.name}: {target}"


def check_diagrams(path: Path, document: Node) -> None:
    for node in document.walk():
        if "data-diagram-source" not in node.attrs:
            continue
        source = path.parent / node.attrs["data-diagram-source"]
        original = next(n for n in Document(source).root.walk() if n.tag == "svg")
        embedded = next(n for n in node.walk() if n.tag == "svg")
        assert embedded == original, f"Diagram differs from its source: {path.name}"
        labels = embedded.attrs.get("aria-labelledby", "").split()
        assert embedded.attrs.get("role") == "img" and len(labels) == 2
        children = [n for n in embedded.children if isinstance(n, Node)]
        assert children[0].tag == "title", f"SVG title must come first: {path.name}"
        for name in labels:
            labelled = next(n for n in embedded.walk() if n.attrs.get("id") == name)
            assert labelled.text().strip(), f"Empty accessible label: {path.name}"


def run_example(source: str, expected_error: str | None) -> str:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        try:
            exec(compile(source, "<supplied-example>", "exec"), {})
        except Exception as error:
            assert type(error).__name__ == expected_error, str(error)
        else:
            assert expected_error is None, f"Expected {expected_error}"
    return output.getvalue().strip()


def check_content(path: Path, document: Node) -> tuple[int, int, int]:
    quizzes = exercises = examples = 0
    for node in document.walk():
        if node.has_class("quiz") or node.has_class("predict"):
            correct = [n for n in node.walk() if "data-correct" in n.attrs]
            assert len(correct) == 1, f"Quiz answer count: {path.name}"
            quizzes += 1
        if node.has_class("pyrun"):
            check_exercise(path, node)
            exercises += 1
        if node.tag == "code" and "language-python" in node.attrs.get("class", ""):
            source = node.text()
            compile(source, f"{path.name}:example", "exec")
            if "data-needs-learner" not in node.attrs:
                run_example(source, node.attrs.get("data-expected-error"))
                examples += 1
        if "data-expected-output" in node.attrs:
            source = next(n.text() for n in node.walk() if n.tag == "code")
            assert run_example(source, None) == node.attrs["data-expected-output"]
    return quizzes, exercises, examples


def check_exercise(path: Path, node: Node) -> None:
    scripts = {
        n.attrs.get("data-role"): n.text() for n in node.walk() if n.tag == "script"
    }
    assert "starter" in scripts, f"Missing starter: {path.name}"
    for role, source in scripts.items():
        compile(source, f"{path.name}:{role}", "exec")
    if "test" not in scripts:
        return
    namespace: dict[str, object] = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(scripts["starter"], "<starter>", "exec"), namespace)
    try:
        exec(compile(scripts["test"], "<exercise-check>", "exec"), namespace)
    except AssertionError as error:
        assert str(error), f"Unhelpful empty check failure: {path.name}"
    else:
        raise AssertionError(f"Unsolved exercise already passes: {path.name}")


def check_curriculum() -> None:
    """Validate the authored route against its IDs and prerequisite order."""
    lessons = json.loads((PAGES / "curriculum.json").read_text())
    seen: set[str] = set()
    files: set[str] = set()
    blocks: set[int] = set()
    for lesson in lessons:
        identifier = lesson["id"]
        assert identifier not in seen, f"Duplicate lesson: {identifier}"
        assert set(lesson["requires"]) <= seen, (
            f"Missing or later prerequisite: {identifier}"
        )
        slug = lesson["slug"]
        assert slug not in files, f"Duplicate lesson file: {slug}"
        document = Document(PAGES / f"{slug}.html").root
        headings = [node.text() for node in document.walk() if node.tag == "h1"]
        assert headings == [lesson["title"]], f"Catalogue title: {identifier}"
        seen.add(identifier)
        files.add(slug)
        match = re.fullmatch(r"[A-F](\d+)(?:\.\d+)?", identifier)
        assert match is not None, f"Invalid lesson ID: {identifier}"
        blocks.add(int(match[1]))
    assert {identifier[0] for identifier in seen} == set("ABCDEF")
    assert blocks == set(range(1, 22)), "The core must cover plan blocks 1–21"
    authored = {path.stem for path in PAGES.glob("*.html")} - {"index"}
    assert authored == files, "Catalogue and authored lesson files differ"
    print(f"Curriculum: {len(lessons)} lessons; blocks 1–21; prerequisites ordered.")


def check_current_materials() -> None:
    """Check entry points, manual task rubrics and the single course route."""
    for path in ROOT.joinpath("lectures").iterdir():
        assert (
            path.name in {"assets", "diagrams", "resources", "curriculum.json"}
            or path.suffix == ".html"
        ), f"Unexpected course material: {path.name}"
    entry = ROOT / "lectures" / "index.html"
    check_links(entry, Document(entry).root)
    lab_index = ROOT / "labs" / "index.html"
    check_links(lab_index, Document(lab_index).root)
    rubrics = 0
    for path in PAGES.glob("*.html"):
        document = Document(path).root
        if "według kryteriów poniżej" not in document.text():
            continue
        task = next(n for n in document.walk() if n.attrs.get("id") == "zadanie")
        rubric = next(n for n in task.walk() if n.attrs.get("id") == "self-assessment")
        assert sum(n.tag == "li" for n in rubric.walk()) >= 3, path.name
        rubrics += 1
    assert rubrics == 11, f"Expected 11 notebook/reasoning rubrics, found {rubrics}"
    print("Current entry links and all 11 manual task rubrics are present.")


def main() -> None:
    check_curriculum()
    check_current_materials()
    quizzes = exercises = examples = 0
    pages = sorted(PAGES.rglob("*.html"))
    previous = Path.cwd()
    with tempfile.TemporaryDirectory() as directory:
        os.chdir(directory)
        try:
            for path in pages:
                document = Document(path).root
                check_links(path, document)
                check_diagrams(path, document)
                q, e, x = check_content(path, document)
                quizzes += q
                exercises += e
                examples += x
        finally:
            os.chdir(previous)
    print(
        f"OK: {len(pages)} pages, {quizzes} quizzes, "
        f"{exercises} editors, {examples} examples"
    )
    print(
        "Links and anchors resolve; examples run; unsolved starters fail with messages."
    )


if __name__ == "__main__":
    main()
