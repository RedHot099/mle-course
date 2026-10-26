# 0001: Forecasting concepts come before the model interface; lab order stays fixed

Date: 2026-10-26

## Context

Module 03 teaches classes on three naive forecasters. Until now the lecture
introduced `fit`, `predict`, `ABC` and `Protocol` first and explained holdout
and MAE afterwards, inside the inheritance section. Learners met the model
interface before anyone told them what a forecast, a horizon or a holdout is.
Module 08 then re-introduced baseline and time split as if they were new.

Two remedies were on the table:

1. Restructure modules 01-08 so that a "forecasting basics" block precedes
   classes and the package.
2. Keep the lab chain and numbering, and move the explanations to where the
   concepts are first used.

## Decision

Option 2. Every forecasting concept is explained in the lecture of the module
that first uses it, before the code that uses it. Lecture 03 opens with a
section on forecasts, horizon, holdout, MAE and baseline, then introduces
classes as the way to organise three recipes with the same shape. Lectures 04
and 08 refer back to that section instead of re-introducing the ideas.
`tutor/concepts.md` records, per concept, where it is explained and where it
is first used, so the order can be checked when modules change.

The lab chain (car parts in 01-03, package in 04, pandas in the package from
06, models in 08) and the module numbering do not change.

## Consequences

- Naive forecasts stay in module 03. They are arithmetic on a list and need no
  ML theory; the theory they need is now in front of them.
- A reorder that moves classes after pandas would have to reinvent where the
  `freshcast` package is born, and rewrite 04-07. That cost is why option 1
  was rejected.
- New concepts added to a module must come with an entry in
  `tutor/concepts.md` and an explanation earlier in the same lecture than the
  code that uses them.
