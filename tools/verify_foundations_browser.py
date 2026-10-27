"""Smoke-test foundations in Chromium, including the actual Pyodide runtime.

Install the optional browser first:
  uv run --with playwright python -m playwright install chromium --only-shell
Run:
  uv run --with playwright python tools/verify_foundations_browser.py
"""

from playwright.sync_api import Browser, Page, sync_playwright
from verify_foundations import PAGES, Document


def check_layout(browser: Browser, width: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": 844})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    for path in sorted(PAGES.rglob("*.html")):
        page.goto(path.as_uri())
        assert page.locator("h1").count() == 1, path.name
        editors = page.locator(".pyrun").count()
        assert page.locator(".pyrun textarea").count() == editors, path.name
        assert not page.evaluate(
            "document.documentElement.scrollWidth > innerWidth + 1"
        ), f"Horizontal overflow: {width}: {path.name}"
    assert not errors, errors
    context.close()
    print(f"All foundations pages render without overflow or page errors at {width}px.")


def check_diagrams(browser: Browser) -> None:
    for theme in ("light", "dark"):
        context = browser.new_context(
            viewport={"width": 390, "height": 844}, color_scheme=theme
        )
        page = context.new_page()
        for path in sorted((PAGES / "diagrams").glob("*.html")):
            page.goto(path.as_uri())
            assert page.locator('svg[role="img"]').count() == 1
            assert page.evaluate(
                """() => {
                    const svg = document.querySelector('svg');
                    const frame = svg.viewBox.baseVal;
                    return [...svg.querySelectorAll('text')].every(text => {
                        const bounds = text.getBBox();
                        return bounds.x >= 0 && bounds.y >= 0 &&
                            bounds.x + bounds.width <= frame.width &&
                            bounds.y + bounds.height <= frame.height;
                    });
                }"""
            ), f"Clipped diagram text: {path.name}: {theme}"
        context.close()
    print("Diagram labels fit in both color schemes at phone width.")


def visit(page: Page, name: str) -> None:
    page.goto((PAGES / name).as_uri())


def check_quiz_and_runner(page: Page) -> None:
    visit(page, "a1-diagnosis.html")
    page.locator("#first-run button", has_text="Uruchom").click()
    page.wait_for_function(
        "document.querySelector('#first-run .py-output')"
        ".textContent.includes('Mogę zacząć')",
        timeout=60000,
    )
    page.locator("#names li:not([data-correct]) button").first.click()
    assert page.locator("#names .quiz-feedback").inner_text().startswith("To nie to")
    page.locator("#names li[data-correct] button").click()
    page.reload()
    assert page.locator("#names .state").inner_text() == "zaliczone"
    print("Runner and quiz feedback/persistence work.")


def check_exercise_runtime(page: Page) -> None:
    checked = 0
    for path in sorted(PAGES.glob("*.html")):
        for node in Document(path).root.walk():
            if not node.has_class("pyrun"):
                continue
            scripts = {
                n.attrs.get("data-role"): n.text()
                for n in node.walk()
                if n.tag == "script"
            }
            if "test" not in scripts:
                continue
            result = page.evaluate(
                "async (codes) => await window.Course.runPython(codes)",
                [scripts["starter"], scripts["test"]],
            )
            assert "AssertionError" in (result["error"] or ""), (
                path.name,
                result,
            )
            checked += 1
    print(f"{checked} unsolved exercise checks fail as intended in Pyodide.")


def check_editor(page: Page) -> None:
    visit(page, "a2-values.html")
    area = page.locator("#stock textarea")
    area.fill(area.input_value() + "\n# saved work\n")
    page.reload()
    assert "# saved work" in page.locator("#stock textarea").input_value()
    page.locator("#stock button", has_text="Sprawdź").click()
    page.wait_for_function(
        "document.querySelector('#stock .py-output')"
        ".textContent.includes('AssertionError')",
        timeout=60000,
    )
    assert "powinno zostać 16" in page.locator("#stock .py-output").inner_text()
    page.locator("#stock button", has_text="Przywróć kod startowy").click()
    assert "# saved work" not in page.locator("#stock textarea").input_value()
    print("Editor persistence, reset and check feedback work.")


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for width in (1280, 390):
            check_layout(browser, width)
        check_diagrams(browser)
        context = browser.new_context(viewport={"width": 1100, "height": 800})
        page = context.new_page()
        check_quiz_and_runner(page)
        check_exercise_runtime(page)
        check_editor(page)
        visit(page, "a4-forecast.html")
        assert page.locator('svg[role="img"]').count() == 1
        page.locator("#theme-toggle").click()
        assert page.locator("html").get_attribute("data-theme") == "dark"
        context.close()
        browser.close()
    print("Foundations browser smoke test passed.")


if __name__ == "__main__":
    main()
