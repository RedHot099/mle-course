---
name: hint
description: One hint for a lesson task, never the solution.
---

# Hint

For lab IDs, resolve labs/manifest.json, read that notebook's task and check cells, and obtain the learner's working copy. Use its visible checks and rubric. A3 is a manual environment experiment. B6/B7 use the learner-owned practice/summary.py and practice/test_summary.py; C11 adds practice/features.py and practice/test_features.py, D14 adds practice/metrics.py and practice/test_metrics.py. B7, C11 and D14 include manual tool/Git checks. Source starters and tools/verify_labs.py are author materials, not learner grades.

Resolve `$ARGUMENTS` as a lesson ID, for example C11.1. If absent, use `.course/progress.md` and the learner's current task. Read the lesson HTML, learner code and `tutor/notes/core.md` before responding. For A/B also use `tutor/notes/foundations.md`.

Ask what they tried and expected unless already supplied. Establish whether the obstacle is a missing concept, a wrong mental model or a local code detail. Give one rung per request and record it in progress.md:

| Rung | Help |
|---|---|
| 1 | Point to the relevant concept or lesson section and ask a leading question. |
| 2 | Describe the steps in words, name a relevant operation and identify the pitfall. |
| 3 | Show the shape of the operation with its decisive part left open, or ask about the exact wrong line. |
| 4 | Work through the technique on different toy data and a different problem, then return to the learner's task. |

A repeated request advances one rung. The learner still writes the solution. If the concept itself is unclear, use `.claude/skills/explain/SKILL.md`. If code already passes, ask for one new input and one explanation against the task criteria. End with one concrete action or question.
