# %% [markdown]
# # Lab 17: dziennik śledztwa
#
# Ten notebook to Twój notatnik śledczego. Tu uruchamiasz `shelfwise`, odtwarzasz objawy z ticketów i sprawdzasz, czy poprawka działa. Poprawki piszesz w plikach `shelfwise/shelfwise/*.py`, a testy w `shelfwise/tests/`.
#
# Po każdej zmianie w kodzie uruchom notebook od początku (Restart i Run All): `shelfwise` nie jest zainstalowany jako pakiet, więc import czyta pliki przy starcie kernela.

# %%
import cProfile
import os
import pstats
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from coursekit import paths
from coursekit.nb import check

SHELFWISE = paths.ROOT / "shelfwise"
os.chdir(SHELFWISE)
sys.path.insert(0, str(SHELFWISE))

if not paths.ONLINE_RETAIL_CACHE.is_file():
    from freshcast.warmup.online_retail import build_cache

    build_cache(paths.ONLINE_RETAIL, paths.ONLINE_RETAIL_CACHE)

from shelfwise import cleaning, cli, features, io, model, report, weekly
from shelfwise.config import load_settings

settings = load_settings(Path("settings.yaml"))

# %%
check("17")

# %% [markdown]
# ## Pierwsze uruchomienie
#
# Zanim cokolwiek zmienisz: jak program działa dziś, ile trwa, co zapisuje?

# %%
summary = cli.run(Path("settings.yaml"))
print({name: round(value, 3) for name, value in summary.items()})
pd.read_csv(settings.output_dir / "report.csv").head()

# %% [markdown]
# ## T1: sumy z faktur
#
# Ticket podaje dla 85123A: 100 749 sprzedanych, 3 638 zwróconych, netto 97 111. Policz te liczby sam, z tych samych surowych linii faktur, które czyta `shelfwise`: sprzedaż to dodatnie ilości na zwykłych fakturach, zwroty to faktury zaczynające się od `C`. Potem porównaj z tym, co liczy `shelfwise`.

# %%
CODE = "85123A"
raw = pd.read_parquet(paths.ONLINE_RETAIL_CACHE)
# >>> SOLUTION 17.1
product = raw.loc[raw["stock_code"] == CODE]
is_return = product["invoice"].str.startswith("C")
sold = int(product.loc[~is_return & (product["quantity"] > 0), "quantity"].sum())
returned = int(-product.loc[is_return, "quantity"].sum())
shelfwise_net = float(weekly.weekly_demand(cleaning.clean(io.read_lines(settings.lines_file)), settings.week_start_day).query("stock_code == @CODE")["units"].sum())
# --- STUB
#| sold = ...
#| returned = ...
#| shelfwise_net = ...
# <<< SOLUTION
print(f"Faktury: sprzedane {sold:,}, zwrócone {returned:,}, netto {sold - returned:,}. shelfwise: {shelfwise_net:,.0f}")

# %% [markdown]
# ## T4: czy walidacja widzi przyszłość
#
# Eksperyment: pomnóż sprzedaż w tygodniach walidacyjnych przez 100 i sprawdź, czy prognoza **pierwszego** tygodnia walidacji się zmieni. W uczciwej walidacji nie może: model w dniu tej prognozy nie znałby tych tygodni.

# %%
demand = weekly.weekly_demand(cleaning.clean(io.read_lines(settings.lines_file)), settings.week_start_day)
demand = demand[demand["stock_code"].isin(weekly.active_products(demand, settings.min_weeks))]
frame = features.build(demand)

# >>> SOLUTION 17.4
validation_start = np.sort(frame["week"].unique())[-settings.validation_weeks]
changed = frame.assign(units=frame["units"].where(frame["week"] < validation_start, frame["units"] * 100))
_, before = model.train_and_validate(frame, settings.validation_weeks, settings.model.alpha)
_, after = model.train_and_validate(changed, settings.validation_weeks, settings.model.alpha)
first_week = before["week"].min()
shift = np.abs(
    before.loc[before["week"] == first_week, "forecast"].to_numpy()
    - after.loc[after["week"] == first_week, "forecast"].to_numpy()
).max()
# --- STUB
#| shift = ...
# <<< SOLUTION
print(f"Największa zmiana prognozy pierwszego tygodnia walidacji: {shift:.6f}")

# %% [markdown]
# ## T6: gdzie idzie czas
#
# Zanim cokolwiek przyspieszysz, zmierz. `cProfile` pokazuje, które funkcje zajmują najwięcej czasu, łącznie z tym, co wołają.

# %%
fitted, _ = model.train_and_validate(frame, settings.validation_weeks, settings.model.alpha)
forecasts = model.predict_next(frame, fitted)
prices = weekly.current_prices(cleaning.clean(io.read_lines(settings.lines_file)), settings.price_lookback_weeks)
catalogue = io.build_catalogue(io.read_lines(settings.lines_file))

profiler = cProfile.Profile()
start = time.perf_counter()
profiler.enable()
table = report.build_report(demand, forecasts, prices, catalogue, settings.cover_weeks)
profiler.disable()
print(f"build_report: {time.perf_counter() - start:.2f} s, {len(table):,} wierszy dla {demand['stock_code'].nunique():,} produktów")
pstats.Stats(profiler).sort_stats("cumulative").print_stats(8)

# %% [markdown]
# ## Raport
#
# Dla każdego zamkniętego ticketu: objaw, przyczyna jednym zdaniem, test, który ją łapie, i link do pull requesta. Dla każdego znaleziska bez ticketu to samo.
#
# *Twój raport:*
