---
name: explain
description: Explain a course concept at the current lesson level.
---

# Explain

Find `$ARGUMENTS` in `lectures/foundations/` with `rg` and consult `docs/glossary.md`. Read the first lesson introducing the concept and the learner's current lesson.

1. Ask what the learner expects unless already stated.
2. Explain one idea in at most six sentences using the taught vocabulary.
3. Give a short runnable example on different toy data. Ask for a prediction before running it when the result is surprising. Show the output and relate it to the prediction.
4. Ask one question requiring application to new data. If the answer shows confusion, change the example or representation.
5. Link the relevant lesson section and record a recurring misconception in `.course/progress.md`.

The learner writes graded task code. An explanation demonstrates a concept without supplying that task's implementation.
