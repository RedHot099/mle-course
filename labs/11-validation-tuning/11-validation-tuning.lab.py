# %% [markdown]
# # Lab 11: backtest, strojenie i dziennik eksperymentów
#
# Do tej pory każdą decyzję podejmowałeś na jednym tygodniu walidacji. Jeden tydzień to jedna próbka: może trafić na święto, na promocję, na upał. W tym labie zamieniasz go na **backtest**: ten sam model uczony i oceniany na kilku kolejnych tygodniach, tak jakbyś prognozował co tydzień w przeszłości.
#
# Na backteście podejmiesz dwie decyzje z poprzednich modułów jeszcze raz, porządnie. Potem przeszukasz ustawienia LightGBM Optuną, każdą próbę zapiszesz w MLflow i dopiero na końcu, raz, spojrzysz na test.
#
# Lab kończy się **punktem kontrolnym 2**.
#
# **Czas:** około 6 godzin.
#
# | Zadanie | Co | Czas |
# |---|---|---|
# | 11.1 | `Fold`, `rolling_origin_folds` w `split.py` | 30 min |
# | 11.2 | `backtest` w `evaluation/backtest.py` | 60 min |
# | 11.4 | Baseline'y i decyzja o wierszach treningu na backteście | 40 min |
# | 11.5 | Losowy K-fold kontra podział po czasie | 30 min |
# | 11.3 | `suggest_params`, `tune` w `tuning.py`, MLflow | 90 min |
# | 11.6 | Test, raz | 20 min |
# | PK2 | Pull request z modułami 05-11 i review | 60 min |

# %%
# %load_ext autoreload
# %autoreload 2

import logging
import time
import warnings

import numpy as np
import pandas as pd

from coursekit import paths
from coursekit.nb import check
from freshcast.data.prepare import load_processed
from freshcast.data.schema import DATE, OOS_HOURS, TARGET
from freshcast.evaluation.scores import score_forecast
from freshcast.features import catalog
from freshcast.models.gbm import LightGBMForecaster
from freshcast.split import last_days_start, split_by_date

logging.getLogger("mlflow").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", message="IProgress not found")
daily = load_processed(paths.PROCESSED_DIR)
table = catalog.build_feature_table(daily)
FEATURES = [*catalog.NUMERIC_FEATURES, *catalog.CATEGORICAL_FEATURES]
CATEGORICAL = catalog.CATEGORICAL_FEATURES

# The last week stays locked until the end of the lab.
rest, test = split_by_date(table, last_days_start(table, 7))
in_stock = rest[OOS_HOURS] == 0
print(f"Do backtestu: {len(rest):,} wierszy do {rest[DATE].max().date()}. Test: {test[DATE].min().date()}..{test[DATE].max().date()}")

# %% [markdown]
# ## 11.1 Foldy rolling origin
#
# Fold to jedno okno walidacji i wszystko, co było przed nim, jako trening. Kolejne foldy cofają się o tydzień:
#
# ```
# fold 1: trening ...................... | walidacja 7 dni |
# fold 2: trening ............................................ | walidacja 7 dni |
# ...
# ```
#
# W `src/freshcast/split.py` napisz `Fold.split(df)` i `rolling_origin_folds(last_date, n_folds, horizon)` według docstringów. Foldy zwracasz od najstarszego.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Ostatni fold kończy się w `last_date`. Każdy wcześniejszy kończy się `horizon` dni przed następnym.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Pętla po liczbie kroków wstecz, od `n_folds - 1` do 0: koniec okna to `last_date - kroki * horizon` dni, początek to koniec minus `horizon - 1` dni.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# for steps_back in range(n_folds - 1, -1, -1):
#     valid_end = last_date - pd.Timedelta(days=steps_back * horizon)
#     valid_start = valid_end - pd.Timedelta(days=horizon - 1)
#     folds.append(Fold(valid_start, valid_end))
# ```
#
# </details>

# %%
check("11.1")

# %%
from freshcast.split import rolling_origin_folds

folds = rolling_origin_folds(rest[DATE].max(), n_folds=4, horizon=7)
for number, fold in enumerate(folds, start=1):
    fold_train, fold_valid = fold.split(rest)
    print(f"fold {number}: trening do {fold_train[DATE].max().date()} ({len(fold_train):,}), walidacja {fold.valid_start.date()}..{fold.valid_end.date()} ({len(fold_valid):,})")

# %% [markdown]
# ## 11.2 Backtest
#
# Napisz `backtest(make_model, table, folds, fit_mask=None)` w `src/freshcast/evaluation/backtest.py`: na każdym foldzie świeży model, trening na wierszach przed oknem (i tylko tych dozwolonych przez `fit_mask`), ocena `score_forecast` na całym oknie. Wynik to tabela z wierszem na fold.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `make_model` wołasz osobno na każdym foldzie. Model z poprzedniego foldu nie może przenieść niczego do następnego.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `fit_mask` ma indeks całej tabeli. Po `fold.split` wybierz z niej wiersze treningu: `fit_mask.loc[train.index]`. Pusty trening albo pusta walidacja to `ValueError` z datami foldu.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# for fold in folds:
#     train, valid = fold.split(table)
#     if fit_mask is not None:
#         train = train.loc[fit_mask.loc[train.index]]
#     model = make_model().fit(train, train[TARGET])
#     scores = score_forecast(valid[TARGET], model.predict(valid), in_stock=valid[OOS_HOURS] == 0)
#     results.append({"valid_start": fold.valid_start, ..., **scores})
# ```
#
# </details>

# %%
check("11.2")

# %% [markdown]
# ## 11.4 Stare decyzje, nowy pomiar
#
# Cztery modele na tych samych foldach:
#
# - baseline naiwny sezonowy z modułu 08,
# - średnia z czterech tych samych dni tygodnia, czyli cecha `same_weekday_mean` użyta wprost jako prognoza. Do tego potrzebny jest "model", który nic nie trenuje: napisz go w notebooku jako `PanelForecaster`,
# - LightGBM uczony na wszystkich dniach i LightGBM uczony tylko na dniach bez braków (decyzja z modułu 09).

# %%
from freshcast.evaluation.backtest import backtest
from freshcast.models.local import SeasonalNaiveForecaster
from freshcast.models.panel import PanelForecaster, PerSeriesForecaster

# >>> SOLUTION 11.4
class FeatureForecaster(PanelForecaster):
    """Uses one feature column as the forecast; learns nothing."""

    def __init__(self, column):
        self.column = column

    def fit(self, X, y):
        return self

    def predict(self, X):
        return X[self.column].fillna(0.0).to_numpy(dtype=float)


def lightgbm():
    """LightGBM with the settings of module 10."""
    return LightGBMForecaster(FEATURES, CATEGORICAL, rounds=260)


start = time.perf_counter()
backtests = {
    "naiwna sezonowa": backtest(lambda: PerSeriesForecaster(lambda: SeasonalNaiveForecaster(7)), rest, folds),
    "średnia 4 tych samych dni": backtest(lambda: FeatureForecaster("same_weekday_mean"), rest, folds),
    "LightGBM, wszystkie dni": backtest(lightgbm, rest, folds),
    "LightGBM, dni bez braków": backtest(lightgbm, rest, folds, fit_mask=in_stock),
}
seconds = time.perf_counter() - start
# --- STUB
#| class FeatureForecaster(PanelForecaster):
#|     ...
#|
#|
#| backtests = ...
# <<< SOLUTION
summary = pd.DataFrame(
    {
        name: {
            **{f"fold {i}": value for i, value in enumerate(result["wape_in_stock"], start=1)},
            "średnio": result["wape_in_stock"].mean(),
            "bias": result["bias_in_stock"].mean(),
        }
        for name, result in backtests.items()
    }
).T
summary.round(3)

# %% [markdown]
# Spójrz na kolumny foldów. O ile wyniki jednego modelu różnią się między tygodniami? Czy różnica między dwoma wariantami LightGBM jest większa od tego rozrzutu?
#
# *Twoja odpowiedź:*

# %% [markdown]
# ## 11.5 Losowy K-fold
#
# Standardowa walidacja krzyżowa z podręczników dzieli wiersze losowo na 5 części. Sprawdź, co pokaże na tych samych danych i tym samym modelu.

# %%
from sklearn.model_selection import KFold

# >>> SOLUTION 11.5
rows = rest.loc[in_stock]
kfold_wape = []
for train_index, valid_index in KFold(n_splits=5, shuffle=True, random_state=0).split(rows):
    fold_train, fold_valid = rows.iloc[train_index], rows.iloc[valid_index]
    model = lightgbm().fit(fold_train, fold_train[TARGET])
    kfold_wape.append(score_forecast(fold_valid[TARGET], model.predict(fold_valid), fold_valid[OOS_HOURS] == 0)["wape_in_stock"])
# --- STUB
#| kfold_wape = ...
# <<< SOLUTION
print(f"Losowy K-fold: WAPE {np.mean(kfold_wape):.3f}; backtest po czasie: {backtests['LightGBM, dni bez braków']['wape_in_stock'].mean():.3f}")

# %% [markdown]
# Który wynik jest bliżej tego, co zobaczysz w produkcji, i dlaczego drugi jest lepszy?
#
# *Twoja odpowiedź:*

# %% [markdown]
# ## 11.3 Strojenie z Optuną i MLflow
#
# LightGBM ma kilkanaście ustawień. Zamiast zgadywać, przeszukaj je: Optuna proponuje zestaw, backtest go ocenia, Optuna na tej podstawie proponuje następny. Każda próba ląduje w MLflow: parametry, średnie metryki i tabela wyników per fold. Za miesiąc będziesz wiedzieć, co już sprawdziłeś i z jakim skutkiem.
#
# W `src/freshcast/tuning.py` napisz:
#
# - `suggest_params(trial)`: jeden zestaw parametrów z przestrzeni opisanej w docstringu,
# - `tune(...)`: badanie Optuny, w którym każda próba to backtest zapisany jako jeden run MLflow.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `trial.suggest_float(nazwa, od, do, log=True)` i `trial.suggest_int(...)`. Skala logarytmiczna dla parametrów, których sensowne wartości rozciągają się na rzędy wielkości.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Funkcja celu Optuny dostaje `trial`, losuje parametry, robi backtest wewnątrz `with mlflow.start_run(...)`, loguje parametry, średnie metryk i tabelę (`mlflow.log_table`) i zwraca średni `wape_in_stock`. Sampler z ziarnem, żeby wynik dało się powtórzyć.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# def objective(trial):
#     params = suggest_params(trial)
#     with mlflow.start_run(run_name=f"trial-{trial.number}"):
#         results = backtest(lambda: LightGBMForecaster(features, categorical, params, rounds=rounds), table, folds, fit_mask=fit_mask)
#         means = {name: float(results[name].mean()) for name in LOGGED_METRICS}
#         mlflow.log_params(...)
#         mlflow.log_metrics(means)
#     return means[OBJECTIVE_METRIC]
#
# study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed))
# study.optimize(objective, n_trials=n_trials)
# ```
#
# </details>

# %%
check("11.3")

# %% [markdown]
# Uruchom strojenie: 15 prób na trzech ostatnich foldach. Potrwa około minuty.

# %%
from freshcast import tracking, tuning

tracking_uri = tracking.use_local_tracking(paths.DATA_DIR / "mlflow", "freshcast-tuning")
start = time.perf_counter()
# >>> SOLUTION 11.3
study = tuning.tune(rest, folds[-3:], FEATURES, CATEGORICAL, n_trials=15, fit_mask=in_stock, rounds=300)
# --- STUB
#| study = ...
# <<< SOLUTION
print(f"{time.perf_counter() - start:.0f} s; najlepsza próba: WAPE {study.best_value:.3f}")
study.best_params

# %% [markdown]
# Dla porównania: domyślny model na tych samych trzech foldach.

# %%
default_score = backtests["LightGBM, dni bez braków"]["wape_in_stock"].iloc[-3:].mean()
trial_scores = sorted(trial.value for trial in study.trials)
print(f"Domyślne ustawienia: {default_score:.3f}. Próby Optuny od {trial_scores[0]:.3f} do {trial_scores[-1]:.3f}")

# %% [markdown]
# Runy są w MLflow. Możesz je przeglądać z kodu:

# %%
import mlflow

runs = mlflow.search_runs(experiment_names=["freshcast-tuning"], order_by=["metrics.wape_in_stock ASC"])
runs[["tags.mlflow.runName", "metrics.wape_in_stock", "metrics.bias_in_stock", "params.learning_rate", "params.num_leaves"]].head(5)

# %% [markdown]
# albo w przeglądarce. W terminalu, w katalogu repozytorium:
#
# ```bash
# uv run mlflow ui --backend-store-uri sqlite:///data/mlflow/mlflow.db
# ```
#
# i otwórz adres, który wypisze. Porównaj dwa runy: zaznacz je i kliknij "Compare". W zakładce "Artifacts" każdego runu jest `backtest.json` z wynikami per fold.

# %% [markdown]
# ## 11.6 Test, raz
#
# Decyzje zapadły na backteście: uczysz tylko na dniach bez braków, a ustawienia bierzesz z Optuny. Teraz jedyny raz w tym labie zaglądasz do testu: domyślny i dostrojony LightGBM, oba uczone na całej historii przed testem, obok baseline'u.

# %%
# >>> SOLUTION 11.6
fit_rows = rest.loc[in_stock]
final_models = {
    "naiwna sezonowa": PerSeriesForecaster(lambda: SeasonalNaiveForecaster(7)).fit(rest, rest[TARGET]),
    "LightGBM domyślny": lightgbm().fit(fit_rows, fit_rows[TARGET]),
    "LightGBM dostrojony": LightGBMForecaster(FEATURES, CATEGORICAL, study.best_params, rounds=300).fit(fit_rows, fit_rows[TARGET]),
}
test_results = pd.DataFrame(
    {name: score_forecast(test[TARGET], model.predict(test), test[OOS_HOURS] == 0) for name, model in final_models.items()}
).T[["wape_in_stock", "bias_in_stock", "wape"]]
# --- STUB
#| test_results = ...
# <<< SOLUTION
test_results.round(3)

# %% [markdown]
# ## Pytania
#
# Bez sprawdzeń. Odpowiedz krótko.
#
# 1. Backtest pokazał, że trening na dniach bez braków daje lepsze WAPE, ale bias zmienił znak. Który model wybierasz dla sklepu, który bardziej boi się pustej półki niż wyrzuconego towaru?
# 2. Strojenie dało niewiele w porównaniu z decyzją o danych treningowych. Gdzie w takim razie warto spędzić następny tydzień pracy?
# 3. Optuna wybrała parametry na trzech foldach. Czy wynik najlepszej próby to uczciwa ocena modelu? Co nią jest?
# 4. MLflow zapisuje parametry i metryki. Czego brakuje, żeby ktoś inny odtworzył Twój najlepszy model za pół roku?
#
# *Twoje odpowiedzi:*

# %% [markdown]
# ## Punkt kontrolny 2
#
# Moduły 05-11 są za Tobą: od metryk, przez dane, cechy i modele, po backtest. Pull request i review jak w punkcie kontrolnym 1:
#
# ```bash
# uv run ruff format --check . && uv run ruff check . && uv run mypy && uv run pytest && uv run course check 11
# uv run jupyter nbconvert --clear-output --inplace labs/0[5-9]-*/*.ipynb labs/1[01]-*/*.ipynb
# git switch -c checkpoint/02
# git add labs src tests
# git commit -m "Add features, models and backtest"
# git push -u origin checkpoint/02
# gh pr create --fill
# ```
#
# Potem `/review` w Claude Code albo samodzielne review według `docs/standard.md`, z regułami, które obowiązują od modułów do 11 włącznie. Szczególnie uważnie sprawdź reguły C1-C6: w tej części kursu łatwo o wyciek.
