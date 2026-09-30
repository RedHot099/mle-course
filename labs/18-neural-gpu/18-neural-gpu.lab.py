# %% [markdown]
# # Lab 18: GRU na GPU obok LightGBM
#
# Tickety są w `README.md` tego katalogu. Ten notebook sprawdza sprzęt, pokazuje, co sieć dostaje na wejściu, uczy ją, mierzy czas na GPU i CPU i stawia GRU w tym samym backteście co LightGBM. Na końcu to samo w Lightning.

# %%
import time
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from coursekit import paths
from coursekit.nb import check
from coursekit.plotting import use_course_style
from freshcast.data.prepare import load_processed
from freshcast.data.schema import DATE, OOS_HOURS, TARGET
from freshcast.evaluation.backtest import backtest
from freshcast.evaluation.scores import score_forecast
from freshcast.features import catalog
from freshcast.models.gbm import LightGBMForecaster
from freshcast.models.neural import FUTURE_CHANNELS, PAST_CHANNELS, GRUForecaster
from freshcast.neural.device import pick_device
from freshcast.split import rolling_origin_folds

import logging

warnings.filterwarnings("ignore", message=".*does not have many workers.*")
warnings.filterwarnings("ignore", message=".*LeafSpec.*")
logging.getLogger("lightning.pytorch").setLevel(logging.WARNING)
use_course_style()
device = pick_device()
print("PyTorch", torch.__version__, "| urządzenie:", device, "|", torch.cuda.get_device_name(0) if device.type == "cuda" else "bez GPU")

# %%
check("18")

# %% [markdown]
# ## Co sieć dostaje na wejściu
#
# Panel jako tablica `(serie, dni, kanały)`, a z niej okna: 28 dni historii i 7 dni prognozy.

# %%
from freshcast.neural.windows import WindowDataset, WindowSpec, panel_cube

daily = load_processed(paths.PROCESSED_DIR)
table = catalog.build_feature_table(daily)  # the channels include features such as dow_sin
channels = list(dict.fromkeys(PAST_CHANNELS + FUTURE_CHANNELS))
cube = panel_cube(table, channels)
print("tablica:", cube.data.shape, "| kanały historii:", PAST_CHANNELS, "| kanały przyszłości:", FUTURE_CHANNELS)

spec = WindowSpec(28, 7, PAST_CHANNELS, FUTURE_CHANNELS)
windows = [(series, 0) for series in range(4)]
batch = WindowDataset(cube, spec, windows).__getitems__(list(range(len(windows))))
{name: tuple(tensor.shape) for name, tensor in batch.items()}

# %% [markdown]
# ## Sieć
#
# Ile parametrów ma GRU z embeddingami sklepów i produktów?

# %%
from freshcast.neural.gru import GRUForecastNet

net = GRUForecastNet(len(PAST_CHANNELS), len(FUTURE_CHANNELS), 7, n_stores=cube.keys["store_id"].nunique(), n_products=cube.keys["product_id"].nunique())
print(net)
print(f"Parametry: {sum(p.numel() for p in net.parameters()):,}")

# %% [markdown]
# ## Uczenie na ostatnim foldzie
#
# `GRUForecaster` uczy się na wszystkim przed tygodniem walidacji i prognozuje ten tydzień. Log pokazuje stratę treningową i walidacyjną w każdej epoce i czas epoki.

# %%
folds = rolling_origin_folds(table[DATE].max(), n_folds=4, horizon=7)
history, week = folds[-1].split(table)

# >>> SOLUTION 18.6
start = time.perf_counter()
gru = GRUForecaster().fit(history, history[TARGET])
gpu_seconds = time.perf_counter() - start
week_scores = score_forecast(week[TARGET], gru.predict(week), week[OOS_HOURS] == 0)
# --- STUB
#| gru = ...
#| week_scores = ...
# <<< SOLUTION
log = gru.log
print(f"{gpu_seconds:.1f} s, najlepsza epoka {log.best_epoch + 1} z {len(log.train_loss)}, epoka średnio {np.mean(log.seconds):.2f} s")
print({name: round(value, 3) for name, value in week_scores.items()})

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(range(1, len(log.train_loss) + 1), log.train_loss, label="trening")
ax.plot(range(1, len(log.valid_loss) + 1), log.valid_loss, label="walidacja")
ax.axvline(log.best_epoch + 1, linestyle=":", label="zachowana epoka")
ax.set(xlabel="epoka", ylabel="MAE na dniach bez braków (skala serii)", title="Uczenie GRU")
ax.legend()
plt.show()

# %% [markdown]
# ## GPU kontra CPU
#
# Ta sama sieć, jedna epoka na CPU.

# %%
if device.type == "cuda":
    start = time.perf_counter()
    on_cpu = GRUForecaster(epochs=1, prefer_gpu=False).fit(history, history[TARGET])
    print(f"Epoka na CPU: {np.mean(on_cpu.log.seconds):.1f} s, na GPU: {np.mean(log.seconds):.2f} s")
else:
    print("Brak GPU: cały lab liczy się na CPU.")

# %% [markdown]
# ## Ten sam backtest co LightGBM
#
# LightGBM uczy się na dniach bez braków (moduł 09). GRU dostaje wszystkie dni jako wejście, a dni z brakami wyłącza ze straty. Oceniane są te same tygodnie, tą samą funkcją.

# %%
FEATURES = [*catalog.NUMERIC_FEATURES, *catalog.CATEGORICAL_FEATURES]
fit_mask = (table[OOS_HOURS] == 0) & table["sale_amount_lag_28"].notna()

# >>> SOLUTION 18.6
results = {}
start = time.perf_counter()
results["LightGBM"] = backtest(lambda: LightGBMForecaster(FEATURES, catalog.CATEGORICAL_FEATURES), table, folds, fit_mask=fit_mask)
lightgbm_seconds = time.perf_counter() - start
start = time.perf_counter()
results["GRU"] = backtest(GRUForecaster, table, folds)
gru_seconds = time.perf_counter() - start
comparison = pd.DataFrame(
    {
        name: {
            **{f"fold {i}": value for i, value in enumerate(result["wape_in_stock"], start=1)},
            "średnio": result["wape_in_stock"].mean(),
            "bias": result["bias_in_stock"].mean(),
        }
        for name, result in results.items()
    }
).T.assign(sekundy=[lightgbm_seconds, gru_seconds])
# --- STUB
#| comparison = ...
# <<< SOLUTION
comparison.round(3)

# %% [markdown]
# ## To samo w Lightning
#
# Te same okna i ta sama sieć, ale pętlę, urządzenie, mixed precision, early stopping i zapis najlepszej epoki robi Lightning. Okna budujesz tak jak `GRUForecaster`: trening kończy się tydzień przed końcem historii, walidacja to okna, które na ten tydzień prognozują.

# %%
from freshcast.neural.lightning import WindowModule, fit_with_lightning

scaled_cube = gru._cube(history)  # the forecaster's own scaling of the channels
days = scaled_cube.data.shape[1]
last_start = days - spec.past - spec.horizon
series = range(scaled_cube.data.shape[0])
train_windows = WindowDataset(scaled_cube, spec, [(s, t) for s in series for t in range(last_start - 7 - spec.horizon + 2)])
valid_windows = WindowDataset(scaled_cube, spec, [(s, t) for s in series for t in range(last_start - 6, last_start + 1)])
codes = tuple(torch.tensor(pd.factorize(scaled_cube.keys[key])[0]) for key in ["store_id", "product_id"])
network = GRUForecastNet(len(PAST_CHANNELS), len(FUTURE_CHANNELS), 7, int(codes[0].max()) + 1, int(codes[1].max()) + 1)

# >>> SOLUTION 18.7
start = time.perf_counter()
module, lightning_loss = fit_with_lightning(WindowModule(network, codes), train_windows, valid_windows, checkpoint_dir=paths.DATA_DIR / "checkpoints")
lightning_seconds = time.perf_counter() - start
# --- STUB
#| module, lightning_loss = ...
# <<< SOLUTION
print(f"Lightning: najlepsza strata walidacyjna {lightning_loss:.4f}, {lightning_seconds:.1f} s. Własna pętla: {min(log.valid_loss):.4f}")

# %% [markdown]
# ## Profil `full` (nieobowiązkowy)
#
# Ustaw `RUN_FULL = True`, jeśli masz kartę z co najmniej 8 GB pamięci i 16 GB RAM. Przygotowanie danych i dwa backtesty trwają kilkanaście minut.

# %%
RUN_FULL = False
if RUN_FULL:
    from freshcast import pipeline

    full_daily = pipeline.prepare_in_chunks(paths.FRN_TRAIN, None)
    full_table = catalog.build_feature_table(full_daily)
    full_folds = rolling_origin_folds(full_table[DATE].max(), n_folds=4, horizon=7)
    full_mask = (full_table[OOS_HOURS] == 0) & full_table["sale_amount_lag_28"].notna()
    for name, make, mask in [
        ("LightGBM", lambda: LightGBMForecaster(FEATURES, catalog.CATEGORICAL_FEATURES), full_mask),
        ("GRU", GRUForecaster, None),
    ]:
        result = backtest(make, full_table, full_folds, fit_mask=mask)
        print(name, round(result["wape_in_stock"].mean(), 4))

# %% [markdown]
# ## Pytania
#
# Bez sprawdzeń. Odpowiedz krótko, z liczbami z tego notebooka.
#
# 1. Ile razy GPU przyspieszyło epokę? Co by się stało z czasem przy 50 000 seriach zamiast 2 648?
# 2. GRU i LightGBM: który wygrał na tym profilu, o ile i czy ta różnica jest większa od rozrzutu między foldami?
# 3. GRU uczy się na wszystkich dniach, a LightGBM tylko na dniach bez braków. Jak GRU radzi sobie z dniami braków, skoro ich nie wyrzuca?
# 4. Co dał Ci Lightning, a co zabrał? Kiedy wolałbyś własną pętlę?
#
# *Twoje odpowiedzi:*
