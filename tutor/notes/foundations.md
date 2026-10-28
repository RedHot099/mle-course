# Foundations A and B

Read this when the learner names an A/B lesson, asks to start from zero, or progress.md records foundations. Start at `lectures/index.html`.

## A pilot laboratories

Read labs/manifest.json for lab-a3 through lab-a4-1-a4-2. Each notebook owns its full task, checks, hints and rubric. The learner works in their own repository copy; A notebooks are directly under labs/ and data under labs/data/. Ask for that copy or its output; source starters do not show learner progress. Record lab and task ID in progress.md. Do not edit the learner's task body.

A3 requires performing the restart experiment, without a written report. A2.1–A2.3–A4.1–A4.2 have eight checked tasks in total plus manual transfer examples. The author verification uses finite expected values and mocks to check checker behavior; it is not evidence that the learner has implemented a general function. For A2.4–A2.5 inspect the actual function on a sixth input. Do not request written explanations or prediction notes. For A4.1–A4.2 use the frozen_forecast copy created before evaluation and distinguish the fully public example from the final project holdout.

## Route checks and hints

1. Find the lesson in the table below. Read its HTML specification, starter and check before helping. Completion means the learner can perform the listed action and explain a new example.
2. For browser work, ask for the learner's code and observed output if they are not available. Browser code and quiz progress live in that browser, not in repository files. Do not infer failure from an empty CLI progress log.
3. Use the hint ladder, one rung per request. Run the lesson's **Sprawdź** action or reproduce the supplied check locally.
4. For B6.2 onward, read and run the learner's own small module and tests when accessible. Use its directory, not the whole course test suite. Use only the files relevant to the current lesson.
5. Record the lesson, evidence and sticking point in `.course/progress.md`, including whether an infrastructure step was deferred. Do not infer browser state from local files.

The learner writes exercise bodies and test additions. The complete examples in the lessons demonstrate other problems. Use the lesson examples and learner material.

## Lessons and evidence

| ID | File in lectures/foundations | Evidence of readiness |
|---|---|---|
| A1 | a1-diagnosis.html | Runs the first expression, predicts examples, identifies specific topics to revisit |
| A2.1 | a2-values.html | Distinguishes a number from a string; computes a changed stock and a share |
| A2.2 | a2-conditions.html | Handles None, zero and a positive number using the correct branch |
| A2.3 | a2-loops.html | Traces accumulator values and counts zeros as known observations |
| A2.4 | a2-records.html | Selects records by field and preserves unknown values as unknown |
| A2.5 | a2-functions.html | Writes count_known and explains return on new data |
| A3 | a3-environment.html | Saves and restarts a notebook; distinguishes terminal, editor and kernel |
| A4.1 | a4-metrics.html | Computes MAE by hand and explains history, horizon and availability |
| A4.2 | a4-forecast.html | Freezes a seven-day forecast from history, scores aligned days, explains sales versus demand |
| B5.1 | b5-collections.html | Builds a new list without removing zeros or changing the input |
| B5.2 | b5-files.html | Locates a file, reads it with with and encoding, writes a separate report |
| B5.3 | b5-errors.html | Reproduces a ValueError on one input; distinguishes corruption from missing data |
| B6.1 | b6-functions.html | Writes mean_known, rejects no-known-values explicitly and leaves input unchanged |
| B6.2 | b6-tests.html | Tests results, errors and input preservation; detects a deliberate bug in summary.py, then restores the backup |
| B7.1 | b7-modules.html | Imports their module and runs scoped format, lint, mypy and pytest checks |
| B7.2 | b7-git.html | Reads the staged diff and explains commit, PR and provided CI; access problems may be deferred |

## Common sticking points

- **Names and types.** If a learner expects `"7" + "2"` to sum, ask what type each value has. Use a different string pair before returning to the task.
- **None and zero.** If zeros vanish, ask which input the condition is intended to reject. Do not suggest replacing missing observations with zero.
- **Loops.** Ask for the accumulator after each iteration. Check placement of initialisation and return before introducing comprehensions.
- **Functions.** If the screen shows a number but a check sees None, ask who printed it and who received a return value.
- **Files.** Check `Path.cwd()` and the exact path before discussing installations. Browser files are temporary Pyodide files, not downloads on disk.
- **Exceptions.** `?` is an agreed missing marker; `blue` is corrupt numeric input. Ask how the caller will distinguish them after a broad except.
- **Forecasting.** The forecast is made once on 3 April, not updated daily from the evaluation week. A zero sale on a stockout day does not establish zero demand.
- **Metrics.** Ask for one day's absolute error before discussing the average. Include all aligned days; round displayed output rather than intermediate values.
- **Tests.** Ask for a concrete broken behaviour the test would detect. A self-comparison does not provide an independent expectation.
- **Imports.** For stale code, restart the notebook kernel. Terminal pytest uses a fresh process. Do not reinstall Python to refresh an imported file.
- **Types.** Basic signatures are enough here. ParamSpec, ABC, Protocol, decorator factories and strict typing of higher-order functions belong later.
- **Git and CI.** The small exercise repo starts with a GitHub README on main and a separate learning branch. The provided workflow is copied, not implemented as a graded task. Keep private data and credentials out of the diff.

## Review scope

For B6.2-B7.2, review `summary.py`, `test_summary.py`, the small project's pyproject.toml, .python-version, lock and README. In B7.2 also review the supplied workflow and gitignore placement. Apply K2, K4, K9, T2, T3 and G4 at the taught level. Do not demand a complete production package or checks for concepts not taught yet.

Success requires both working behaviour and a new small example explained without copying. A failed account setup is an environment issue; it does not cancel demonstrated Python skills. A green quiz counter alone does not establish mastery.
