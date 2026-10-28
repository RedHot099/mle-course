---
name: check
description: Interpret a failing lesson check with the learner.
---

# Check

Resolve the lesson ID from `$ARGUMENTS` or `.course/progress.md`. Read the task, starter and supplied test in its HTML. Obtain the learner's code and exact message when browser state is unavailable.

For browser tasks use **Sprawdź**, or reproduce that task's supplied check locally with the learner's code. For local tasks run only the commands taught in that lesson, in the learner's project directory. Notebook and reasoning tasks use the visible **Sprawdź swoją pracę** criteria; they have no automatic passing counter.

1. Ask the learner to restate the failed requirement.
2. Read an exception from its type and the learner's line back to the triggering value. For a wrong result, reproduce one failing input and compare expected with actual.
3. Ask which operation produces the difference. Continue with the next rung in `.claude/skills/hint/SKILL.md`.
4. Record evidence and the sticking point in `.course/progress.md`.

A passing supplied check covers its cases. Ask for a new small case before treating the concept as demonstrated. Hard-coding expected outputs does not satisfy the task.
