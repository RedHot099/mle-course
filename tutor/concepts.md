# Forecasting concepts: where explained, where first used

One row per concept the course needs before the learner writes code that
depends on it. "Explained" is the lecture section that defines the concept.
"First used" is the task that first depends on it. The explanation must come
earlier than the use. Add a row when a module introduces a concept; fix the
order when a row shows a use before its explanation.

Lecture sections are `lectures/NN-*/index.html#id`. Tasks are lab ids.

| Concept | Explained | First used | Notes |
|---|---|---|---|
| missing vs zero demand | 01 (Tylko znane wartości, `demand_stats`) | 01.1, 01.4 | |
| ADI, CV², demand types | lab 01 (01.4 docstring), lab 02 (02.4), lab 03 notebook (03.2, Syntetos-Boylan table) | 01.4, 02.4, 03.2 | defined in the labs, not in a lecture |
| forecast, history, horizon | 03 `#prognoza` | 03.3 | before this change: never defined; `horizon` appeared only in the `demand.py` stub |
| naive, seasonal naive, moving average | 03 `#prognoza` | 03.3, 03.4 | before: seasonal naive first explained in lecture 04 |
| `fit` as "remember the history" | 03 `#prognoza`, `#dziedziczenie` | 03.3 | glossary entry `fit`; lecture 08 `#model` contrasts it with fitting parameters |
| holdout | 03 `#prognoza` | 03.5 | before: a subsection inside `#dziedziczenie`, after `fit`/`predict` |
| MAE | 03 `#prognoza` | 03.5 | |
| baseline | 03 `#prognoza`, 08 `#baseline` | 03.6, 08.2 | 08 refers back to the class moved in 04.1 and tested in 04.2 |
| why MAE rewards under-forecasting; WAPE, bias | 03 `#prognoza` (named), 05 (Metryki błędu prognozy) | 03.6, 05.3 | 03 names the metrics, 05 defines them |
| test as a contract, not an accuracy check | 04 `#umowa` | 04.1, 04.2 | |
| loss, parameters, training | 08 `#model` | 08.3 | |
| train / validation / test split by time | 08 (Podział po czasie) | 08.1 | same idea as the holdout of 03, with three parts |
| leakage | 07 (Pułapka druga: dzień bieżący), 08 (Leakage) | 07.5, 08.6 | 07 names and defines leakage on the `shift` example; 08 expands it to the three common sources and the rule ids C2, C4 |
| features from the series' own past (lag, rolling) | 07 (Czas w panelu) | 07.5 | the word "cecha" is used in 07 before 08 defines a feature; acceptable, 07 says what it means in place |
| features known at forecast time | 08 (Leakage: "za krótkie spojrzenie wstecz"), 09 (Cechy znane w chwili prognozy) | 08.6, 09.1 | 08 states the rule for lags, 09 generalises it |
| regularisation, hyperparameter | 08 (Regularyzacja) | 08.7 | |
