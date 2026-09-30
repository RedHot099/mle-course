# %% [markdown]
# # Lab 19: capstone
#
# Brief i kryteria są w `README.md` tego katalogu. Ten notebook liczy wszystkie liczby do raportu: porównanie modeli w jednym backteście, zapisane w MLflow, opis tygodnia testowego i jedną, końcową ocenę na teście.
#
# Kolejność ma znaczenie. Najpierw backtest i wybór modelu, dopiero potem test. Jeśli po obejrzeniu testu zmienisz model, test przestaje być testem.

# %%
import logging
import os
import warnings

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
warnings.filterwarnings("ignore", message="IProgress not found")

import mlflow  # noqa: E402 - after the variable that silences its start-up hint
import numpy as np
import pandas as pd

from coursekit import paths
from coursekit.nb import check
from freshcast import pipeline, tracking
from freshcast.config import load_settings
from freshcast.data.prepare import load_processed, prepare_daily
from freshcast.data.schema import DATE, OOS_HOURS
from freshcast.features import catalog
from freshcast.split import rolling_origin_folds

os.chdir(paths.ROOT)
logging.getLogger("mlflow").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", message=".*does not have many workers.*")
profile = paths.active_profile().name
settings = load_settings(paths.ROOT / "configs" / f"{'standard' if profile == 'full' else profile}.yaml")
tracking.use_local_tracking(paths.DATA_DIR / "mlflow", "freshcast-capstone")
print("Profil:", profile, "| miasta:", settings.data.cities)

# %%
check("19")

# %% [markdown]
# ## Backtest wszystkich kandydatów
#
# Te same cztery tygodnie dla każdego modelu. LightGBM uczy się na dniach bez braków, GRU na wszystkich dniach z maską w stracie, baseline na całej historii.

# %%
from freshcast.evaluation.final import compare_models
from freshcast.models.gbm import LightGBMForecaster
from freshcast.models.local import SeasonalNaiveForecaster
from freshcast.models.neural import GRUForecaster
from freshcast.models.panel import PerSeriesForecaster

daily = load_processed(paths.PROCESSED_DIR)
table = catalog.build_feature_table(daily)
folds = rolling_origin_folds(table[DATE].max(), settings.backtest.folds, settings.backtest.horizon)
training_rows = pipeline.training_mask(table, in_stock_only=True)

# >>> SOLUTION 19.1
candidates = {
    "naiwna sezonowa": lambda: PerSeriesForecaster(lambda: SeasonalNaiveForecaster(7)),
    "LightGBM": lambda: LightGBMForecaster(catalog.MODEL_FEATURES, catalog.CATEGORICAL_FEATURES, rounds=settings.model.rounds),
    "GRU": GRUForecaster,
}
comparison = compare_models(candidates, table, folds, fit_masks={"LightGBM": training_rows})
# --- STUB
#| candidates = ...
#| comparison = ...
# <<< SOLUTION
summary = comparison.groupby("model")[["wape_in_stock", "bias_in_stock", "wape"]].agg(["mean", "std"]).round(3)
summary

# %% [markdown]
# Każdy model to jeden run w MLflow: średnie metryki i tabela per fold.

# %%
for name, rows in comparison.groupby("model"):
    with mlflow.start_run(run_name=name):
        mlflow.log_param("model", name)
        mlflow.log_param("folds", len(folds))
        mlflow.log_metrics({metric: float(rows[metric].mean()) for metric in ["wape_in_stock", "bias_in_stock", "wape"]})
        mlflow.log_table(rows.astype({"valid_start": str, "valid_end": str}), "backtest.json")
mlflow.search_runs(experiment_names=["freshcast-capstone"])[["tags.mlflow.runName", "metrics.wape_in_stock", "metrics.bias_in_stock"]].head(6)

# %% [markdown]
# Wyniki fold po foldzie: czy przewaga zwycięzcy powtarza się w każdym tygodniu?

# %%
comparison.pivot(index="valid_start", columns="model", values="wape_in_stock").round(3)

# %% [markdown]
# ## Tydzień testowy
#
# Zanim go ocenisz, opisz go. Czym różni się od danych, na których model się uczył?

# %%
# >>> SOLUTION 19.2
test_days = prepare_daily(paths.FRN_EVAL, cities=settings.data.cities)
test_temperature = test_days["avg_temperature"].mean()
colder_share = (daily["avg_temperature"] < test_temperature).mean()
# --- STUB
#| test_days = ...
#| test_temperature = ...
#| colder_share = ...
# <<< SOLUTION
print(f"Tydzień testowy: {test_days[DATE].min().date()}..{test_days[DATE].max().date()}, średnia temperatura {test_temperature:.1f} °C")
print(f"Dni treningowe chłodniejsze niż średnia tygodnia testowego: {colder_share:.1%}")
print(f"Udział dni z promocją: trening {daily['activity_flag'].mean():.1%}, test {test_days['activity_flag'].mean():.1%}")
print(f"Udział dni bez braków: trening {(daily[OOS_HOURS] == 0).mean():.1%}, test {(test_days[OOS_HOURS] == 0).mean():.1%}")

# %% [markdown]
# ## Jedna ocena na teście
#
# Model z pipeline'u (LightGBM, ustawienia z konfiguracji) uczony na całej historii prognozuje tydzień testowy (`forecast`), a `evaluate` ocenia tę prognozę obok prognozy naiwnej sezonowej na tych samych wierszach. To jest liczba do raportu. Uruchamiasz to raz.

# %%
# >>> SOLUTION 19.3
result = pipeline.train(settings)
pipeline.forecast(settings, result.model_dir, paths.FRN_EVAL)
test_table = pipeline.evaluate(settings, result.model_dir, paths.FRN_EVAL)
# --- STUB
#| result = ...
#| test_table = ...
# <<< SOLUTION
print("Model:", result.model_dir)
test_table.round(3)

# %% [markdown]
# ## Raport
#
# Skopiuj `labs/19-capstone/report-template.md` do `reports/capstone.md` i wypełnij go liczbami z tego notebooka. Potem `uv run course check 19.4` i punkt kontrolny 4.
