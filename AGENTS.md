# Authoring "ML Engineering from Scratch"

You are on the `solutions` branch: the authoring tree and the single source of truth for the course. The learner view (branch `main`) is generated from it by `tools/release.py` into `_main/`. Edit here, never in `_main/`.

The tutor instructions that learners get live in `learner/` and are copied to the root of the learner view. This file never reaches learners.

## Before changing anything

- `docs/design.md`: decisions, syllabus, package plan, what is out of scope. Settled decisions stay settled.
- `docs/authoring.md`: how a module is built, file by file, with module 07 as the worked example.

## Verify

```bash
uv run --group authoring python tools/verify.py
```

It lints both trees, rebuilds the learner view, runs every check against the reference (all must pass) and against the learner view (all must report "not done"), and executes every lab notebook solved. A change is finished when this prints `ALL GOOD`.

Lectures are checked in a browser: serve the repository (`python3 -m http.server`) and click through every quiz and widget; the console must stay free of errors.

## Rules that are easy to break

- Course prose is Polish; identifiers, code comments and agent-facing files are English. Technical terms stay English, with the Polish meaning in `docs/glossary.md`.
- Every number stated about the data is measured, not remembered. Run it.
- Learner-facing text never names or describes any private codebase.
- Reference code follows `docs/standard.md` to the letter: learners read it after catching up.
- A check message says what is wrong, never how to fix it, and checks hold no second implementation of the task: expected values are constants measured on the fixture.
- Commit and push only when the author asks.
