# Tutor routing for the A–F core

Use this note when the learner names an ID from `lectures/foundations/curriculum.json`, follows the course, or asks to start from zero. The catalogue is ordered and lists prerequisites. Read the current lesson HTML before helping: its example, task, starter, check, transfer question and rubric are the task specification.

For A and B, also use `tutor/notes/foundations.md`. Its browser-progress and hint guidance still applies. C–F use the same one-rung-per-request hint ladder. Learners write their exercise code, test additions and project implementations. Do not read the solutions branch.

## Determine completion from evidence

1. Identify the lesson ID and check its explicit prerequisites. A learner may demonstrate a prerequisite without repeating its whole lesson. E17 is required for writing a network class; it does not gate F18 or F19.
2. Ask for the learner's code, output or written reasoning when they are not available. Browser progress is localStorage; it is not written to repository progress files.
3. For an editor exercise, run the supplied check and ask for a different small input. For a notebook or reasoning task, use the lesson's visible rubric. Require the requested artefact, a justified calculation and an explanation of one limitation. Do not replace this with keyword matching or a quiz counter.
4. If a requirement is missing, name the concrete missing evidence. Give the next hint only; do not implement the learner's task.
5. Record the ID, evidence, sticking point and hint rung in `.course/progress.md`. Record only evidence the learner has demonstrated. An environment problem can be deferred without cancelling demonstrated concepts.

## Core-specific pitfalls

| Lessons | What to inspect first |
|---|---|
| C8–C10 | Index labels versus positions; unchanged input; zero versus missing; ddof=0 in the stated descriptive calculation; group versus row output; join cardinality and missing matches |
| C11–C12 | Sorted, complete series; lag inside the series; feature availability at the forecast origin; rolling daily evaluation versus frozen multi-step evaluation; scaler and encoder fit only on training |
| D13 | Hand calculation before matrix notation; common old parameters for all partial derivatives; shape (n,k), (k,), (n,); mean over examples, not features |
| D14–D15 | Shared evaluation rows; explicit bias convention; denominator-zero policy; paired folds; change one setting; direct versus recursive protocol |
| D16 | Base frequency before a decision; future label at the right date; last unknown label stays unknown; both classes in logistic training; probability versus alarm |
| E17 | Separate instance state; predict before fit; zero is fitted; reproduce after kernel restart; enough metadata to identify data and settings |
| F18 | Model family versus optimiser; training result versus future error; small sample versus shift; number of tried variants; no promise that more data fixes every failure |
| F19 | Conditional denominator; likelihood is not posterior; log probability of the observed class; conditional-independence assumption; calibration versus ranking; expected cost versus causal effect |
| F20 | Scale before distance; centred projection; lost information in PCA; chain rule before autograd; zero gradients before a new training step; source of labels; tokens before embeddings and attention; no future token access |
| F21 | State must contain relevant information; sum of path costs; posterior before action; return and horizon; known-model planning versus learning from experience; exploration has cost |

PyTorch examples are local CPU work. No GPU, cloud account, paid API or training framework is a core prerequisite. The tiny demonstrations prove the operation shown, not general forecasting quality. Use only the prerequisites named by the current lesson.

## Preserve the final evaluation

C12 starts a small, separate project with synthetic `data/project-development.csv`: days 1–42 training, 43–49 validation. `project-holdout.csv` contains days 50–56 and is introduced only in F21.5. Do not inspect or suggest its outcomes while coaching model selection. The fully visible Freshcast series in A4 is a different teaching example.

Before opening the holdout, have the learner record a frozen model, features, settings and forecast protocol. The C12 protocol is rolling daily prediction: yesterday's observed sale is available tomorrow, without refitting on test outcomes. D15.4 is a separately labelled frozen multi-step experiment. Evaluate the frozen final choice and baseline on identical rows once. If the learner already viewed the file, record the disclosure and do not call the result an independent test.

The final task combines the small report with new reasoning cases about prediction, inference, search, language-model reliability and delayed consequences. It does not require an extra deployment capstone.
