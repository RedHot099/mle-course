# %% [markdown]
# # Lab 14: przebieg pipeline'u i raport
#
# Tickety są w `README.md` tego katalogu. Ten notebook uruchamia to, co zbudowałeś, i pozwala obejrzeć wynik. Nic tu nie liczy się "po swojemu": wszystko idzie przez funkcje pakietu, tak jak w CLI.
#
# Ścieżki w plikach konfiguracji są względne wobec katalogu głównego repozytorium, dlatego notebook zaczyna od przejścia tam.

# %%
import json
import os
import time

import pandas as pd

from coursekit import paths
from coursekit.nb import check
from freshcast import pipeline
from freshcast.config import load_settings

os.chdir(paths.ROOT)
profile = paths.active_profile().name
CONFIG = paths.ROOT / "configs" / f"{'standard' if profile == 'full' else profile}.yaml"
print(f"Konfiguracja: {CONFIG.relative_to(paths.ROOT)}")

# %%
check("14")

# %% [markdown]
# ## Ustawienia
#
# Wczytaj ustawienia i sprawdź, że zmienna środowiskowa wygrywa z plikiem.

# %%
settings = load_settings(CONFIG)
print(settings.model_dump_json(indent=2))

os.environ["FRESHCAST_MODEL__ROUNDS"] = "150"
print("Z nadpisaniem:", load_settings(CONFIG).model.rounds)
del os.environ["FRESHCAST_MODEL__ROUNDS"]

# %% [markdown]
# ## Trening
#
# To samo, co robi `uv run freshcast train --config ...`. Na profilu `standard` trwa kilka sekund do minuty, zależnie od maszyny.

# %%
# >>> SOLUTION 14.4
start = time.perf_counter()
result = pipeline.train(settings)
train_seconds = time.perf_counter() - start
# --- STUB
#| result = ...
#| train_seconds = ...
# <<< SOLUTION
print(f"{train_seconds:.0f} s, model w {result.model_dir}")
result.backtest[["valid_start", "valid_end", "wape_in_stock", "bias_in_stock"]].round({"wape_in_stock": 3, "bias_in_stock": 3})

# %% [markdown]
# Co zostało zapisane obok modelu:

# %%
for item in sorted(result.model_dir.iterdir()):
    print(f"{item.name:>18}  {item.stat().st_size / 1e6:6.2f} MB")
metadata = json.loads((result.model_dir / "metadata.json").read_text(encoding="utf-8"))
{key: metadata[key] for key in ["signature", "rounds", "train_rows", "train_first_day", "train_last_day", "cities", "backtest"]}

# %% [markdown]
# ## Prognoza przyszłego tygodnia
#
# `eval.parquet` to 7 dni po końcu danych treningowych. Prognozujesz je tak, jak w produkcji: model nie widzi sprzedaży z tych dni, bo `forecast` usuwa kolumny wyników, zanim cokolwiek policzy. Wyników prognozy **nie oceniasz**: ten tydzień to zamknięty test capstone'u w module 19.

# %%
# >>> SOLUTION 14.4
forecasts = pipeline.forecast(settings, result.model_dir, paths.FRN_EVAL)
# --- STUB
#| forecasts = ...
# <<< SOLUTION
print(f"{len(forecasts):,} prognoz, {forecasts['dt'].min().date()}..{forecasts['dt'].max().date()}")
forecasts.describe().round(3)

# %% [markdown]
# ## Raport
#
# Odpowiedz krótko.
#
# 1. Ile trwał trening i który krok zajął najwięcej czasu? Odczytaj to z logu (godziny przy kolejnych komunikatach).
# 2. Czego potrzebowałbyś, żeby za trzy miesiące odtworzyć dokładnie ten model? Co z tego jest w `metadata.json`, a czego brakuje?
# 3. Jeśli uruchomiłeś profil `full`: czas, szczyt pamięci i średni WAPE z backtestu. Czym różni się od wyniku na jednym mieście i dlaczego?
#
# *Twoje odpowiedzi:*
