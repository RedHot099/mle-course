---
name: review
description: Review completed learner work using the current lesson criteria.
---

# Review

For lab IDs, resolve labs/manifest.json, read that notebook's task and check cells, and obtain the learner's working copy. Use its visible checks and rubric. A3 is a manual environment experiment. B6/B7 use the learner-owned practice/summary.py and practice/test_summary.py; C11 adds practice/features.py and practice/test_features.py. B7 and C11 include manual tool/Git checks. Source starters and tools/verify_labs.py are author materials, not learner grades.

Review `$ARGUMENTS` or the current lesson. The learner writes every correction.

1. Read the lesson requirements, task and rubric. For B6.2–B7.2 inspect the learner's practice/summary.py, practice/test_summary.py and project configuration; in C11 also practice/features.py and practice/test_features.py. Run the scoped commands from those lessons in that project. For C–F inspect the requested notebook, lab results file or report and reproduce the relevant small calculation.
2. Check every visible completion criterion. Apply `docs/standard.md` only from the lesson where each rule begins. Use `tutor/notes/core.md` for project and holdout policy. Do not open the final holdout while reviewing model selection.
3. Report in Polish: ready or needs changes, each missing criterion with observed evidence, and a next question or hint. For code findings cite file and line, rule ID where applicable, and a concrete failing input. State checks that could not run.
4. Record the verdict and missing evidence in `.course/progress.md`.

Browser quiz scores alone do not establish completion. Account or installation problems may be deferred without discarding demonstrated concepts. Author verification scripts test course materials and are not learner checks.
