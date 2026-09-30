"""Reference solutions of the exercises in lecture 16."""

SOLUTIONS = {
    "e1": """
def dockerfile_problems(text):
    lines = [line.strip() for line in text.splitlines()]
    problems = []
    if not any(line.startswith("USER ") for line in lines):
        problems.append("root")
    if any("uv sync" in line and "--locked" not in line for line in lines):
        problems.append("unlocked")
    if any(line.startswith("COPY") and " data" in line for line in lines):
        problems.append("data")
    return problems
""",
    "e2": """
def missing_checks(workflow):
    commands = " ".join(
        step.get("run", "")
        for job in workflow.get("jobs", {}).values()
        for step in job.get("steps", [])
    )
    return sorted(tool for tool in ("mypy", "pytest", "ruff") if tool not in commands)
""",
}
