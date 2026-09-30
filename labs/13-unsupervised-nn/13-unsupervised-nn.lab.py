# %% [markdown]
# # Lab 13: segmenty serii i pierwsza sieć neuronowa
#
# Dwie nowe rodziny metod. Pierwsza nie ma celu: k-means i PCA szukają struktury w samych danych. Opiszesz każdą serię sześcioma liczbami, podzielisz serie na segmenty i sprawdzisz uczciwie, czy segment pomaga modelowi prognozy. Uczciwie znaczy: z kontrolą, czyli losowymi etykietami, i z segmentami liczonymi tylko z przeszłości.
#
# Druga rodzina to sieć neuronowa. Napiszesz perceptron wielowarstwowy (MLP) w PyTorch i pętlę treningową od zera, a potem postawisz go obok LightGBM w tym samym backteście. Wynik będzie gorszy i ważne jest, żebyś umiał powiedzieć dlaczego.
#
# **Czas:** około 7 godzin.
#
# | Zadanie | Co piszesz | Czas |
# |---|---|---|
# | 13.1 | `series_profile` w `segments.py` | 40 min |
# | 13.2 | `standardise`, `fit_segments` | 40 min |
# | 13.3 | `inertia_by_k`, `silhouette_by_k` | 30 min |
# | 13.4 | `hour_profiles`, `project_2d` | 50 min |
# | 13.8 | Czy segment pomaga: eksperyment z kontrolą | 40 min |
# | 13.5 | `TabularMLP` w `models/mlp.py` | 30 min |
# | 13.6 | `train_mlp` | 60 min |
# | 13.7 | `MLPForecaster` | 40 min |
# | 13.9 | MLP obok LightGBM i pytania | 50 min |

# %%
# %load_ext autoreload
# %autoreload 2

import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from coursekit import paths
from coursekit.nb import check
from coursekit.plotting import use_course_style
from freshcast import segments
from freshcast.data.prepare import load_processed
from freshcast.data.schema import DATE, OOS_HOURS, SERIES_KEY
from freshcast.evaluation.backtest import backtest
from freshcast.features import catalog
from freshcast.models.gbm import LightGBMForecaster
from freshcast.split import rolling_origin_folds

use_course_style()
daily = load_processed(paths.PROCESSED_DIR)
CITIES = paths.active_profile().cities or paths.PROFILES["standard"].cities
print(f"{daily.groupby(SERIES_KEY).ngroups:,} serii")

# %% [markdown]
# ## 13.1 Profil serii
#
# Każdą serię opisz sześcioma liczbami jej zachowania (`PROFILE_FEATURES`): poziom sprzedaży w logarytmie, zmienność, wzrost w weekend, udział dni z rabatem, częstość braków i udział dni bez sprzedaży. Definicje są w docstringu `series_profile`. Każda liczba liczy się z wierszy jednej serii.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Najpierw kolumny pomocnicze na poziomie dnia (czy weekend, czy rabat, czy zero sprzedaży), potem jeden `groupby(SERIES_KEY).agg(...)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Weekend to `dt.dayofweek >= 5`, nie `holiday_flag`. Rabat z brakiem (`NaN`) liczy się jako brak rabatu: `NaN < 1` daje `False`, ale sprawdź, czy tego chcesz. Odchylenie z `ddof=0`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# days = daily.assign(
#     weekend_sales=daily[TARGET].where(daily[DATE].dt.dayofweek >= FIRST_WEEKEND_DAY),
#     discounted=daily[DISCOUNT].lt(1.0),
#     zero=daily[TARGET].eq(0),
# )
# grouped = days.groupby(SERIES_KEY)
# mean = grouped[TARGET].mean()
# ...
# ```
#
# </details>

# %%
check("13.1")

# %%
profile = segments.series_profile(daily)
profile.describe().T[["mean", "50%", "min", "max"]].round(3)

# %% [markdown]
# ## 13.2 Skalowanie i k-means
#
# k-means mierzy odległości, więc kolumna o największej skali decyduje o wszystkim. Napisz `standardise(features)` (skaler i przeskalowana tablica; stała kolumna to błąd) i `fit_segments(profile, k, seed)`: skalowanie, k-means z ziarnem i `N_INIT` startami, wynik jako `Segmentation`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `StandardScaler().fit_transform`, potem `KMeans(n_clusters=k, n_init=N_INIT, random_state=seed)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Etykiety zwracasz jako `Series` o nazwie `segment` z indeksem profilu, żeby dało się je dołączyć do panelu po kluczu serii.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# scaled, scaler = standardise(profile[PROFILE_FEATURES])
# kmeans = KMeans(n_clusters=k, n_init=N_INIT, random_state=seed).fit(scaled)
# labels = pd.Series(kmeans.labels_, index=profile.index, name=SEGMENT)
# return Segmentation(labels, scaler, kmeans)
# ```
#
# </details>

# %%
check("13.2")

# %% [markdown]
# ## 13.3 Ile segmentów
#
# Algorytm dzieli dane na tyle grup, ile mu każesz. Liczbę `k` trzeba uzasadnić. Napisz `inertia_by_k` (suma kwadratów odległości od najbliższego środka) i `silhouette_by_k` (jak dobrze punkty pasują do swojego segmentu w porównaniu z najbliższym obcym: od −1 do 1).

# %%
check("13.3")

# %%
scaled, _ = segments.standardise(profile[segments.PROFILE_FEATURES])
ks = range(2, 11)
inertia = segments.inertia_by_k(scaled, [1, *ks])
silhouette = segments.silhouette_by_k(scaled, ks)

fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
axes[0].plot(inertia.index, inertia.to_numpy(), marker="o")
axes[0].set(xlabel="k", ylabel="inertia", title="Inercja")
axes[1].plot(silhouette.index, silhouette.to_numpy(), marker="o")
axes[1].set(xlabel="k", ylabel="silhouette", title="Silhouette")
plt.show()
print(silhouette.round(3).to_dict())

# %% [markdown]
# Czy te serie tworzą naturalne grupy? Jakie `k` wybierzesz i dlaczego? Uwaga: "łokieć" na wykresie inercji trzeba zobaczyć, a nie założyć.
#
# *Twoja odpowiedź:*
#
# Segmenty dla `k = 6`, opisane średnimi profilu. Numery segmentów to tylko nazwy.

# %%
K = 6
segmentation = segments.fit_segments(profile, K, seed=0)
profile.join(segmentation.labels).groupby(segments.SEGMENT).agg(
    series=("cv", "size"), **{name: (name, "mean") for name in segments.PROFILE_FEATURES}
).round(2)

# %% [markdown]
# ## 13.4 Profile godzinowe i PCA
#
# Drugi opis serii: udział każdej z 24 godzin w jej sprzedaży. 24 liczby to za dużo, żeby je obejrzeć. PCA znajduje dwa kierunki, wzdłuż których serie różnią się najbardziej, i rzutuje na nie każdą serię.
#
# Napisz `hour_profiles(hourly)` (sumy po dniach, potem udziały) i `project_2d(matrix)` (centrowanie, SVD, dwie pierwsze składowe i ich udział w wariancji).
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Dla PCA wystarczy `np.linalg.svd` na wycentrowanej macierzy. Kolumny `V` to kierunki, a kwadraty wartości osobliwych mówią, ile wariancji niesie każdy.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `centred = matrix - matrix.mean(axis=0)`, `u, s, vt = np.linalg.svd(centred, full_matrices=False)`. Współrzędne to `centred @ vt[:2].T`, udziały to `s[:2]**2 / (s**2).sum()`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# sales = to_matrix(hourly[HOURLY_SALES])
# totals = pd.DataFrame(sales, columns=HOUR_COLUMNS).groupby([hourly[c] for c in SERIES_KEY]).sum()
# shares = totals.div(totals.sum(axis=1), axis=0)
# ```
#
# </details>

# %%
check("13.4")

# %%
from freshcast.data.hourly import load_hourly

hours = segments.hour_profiles(load_hourly(paths.FRN_TRAIN, cities=CITIES))
coordinates, explained = segments.project_2d(hours.to_numpy())
centred = hours.to_numpy() - hours.to_numpy().mean(axis=0)
first_direction = np.linalg.svd(centred, full_matrices=False)[2][0]

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
axes[0].scatter(coordinates[:, 0], coordinates[:, 1], s=4, alpha=0.4)
axes[0].set(xlabel=f"składowa 1 ({explained[0]:.0%})", ylabel=f"składowa 2 ({explained[1]:.0%})", title="Serie w dwóch wymiarach")
axes[1].bar(range(24), first_direction)
axes[1].set(xlabel="godzina", ylabel="waga", title="Składowa 1: co ją tworzy")
plt.show()

# %% [markdown]
# Co opisuje pierwsza składowa? Ile wariancji zostaje poza obrazkiem?
#
# *Twoja odpowiedź:*

# %% [markdown]
# ## 13.8 Czy segment pomaga prognozie
#
# Pomysł: dodać segment serii jako cechę kategoryczną LightGBM. Żeby wynik coś znaczył, potrzebujesz trzech porównań w tym samym backteście:
#
# - model bez segmentu,
# - model z segmentem liczonym **uczciwie**: w każdym foldzie tylko z dni przed walidacją (`SegmentedForecaster`, kod gotowy w `segments.py`),
# - **kontrola**: model z losowymi etykietami o tej samej liczbie poziomów. Kolumna szumu też potrafi przesunąć wynik o ułamek; zysk segmentu musi być od tego większy.
#
# Robisz to w dwóch wersjach: z identyfikatorami sklepu i produktu wśród cech i bez nich.

# %%
table = catalog.build_feature_table(daily)
folds = rolling_origin_folds(table[DATE].max(), n_folds=4, horizon=7)
fit_mask = (table[OOS_HOURS] == 0) & table["sale_amount_lag_28"].notna()
NUMERIC = catalog.NUMERIC_FEATURES
IDS = catalog.CATEGORICAL_FEATURES
series_keys = profile.index.to_frame(index=False)


def with_random_segment(frame, seed):
    """Attach a segment column drawn at random, the same for all days of a series."""
    draws = series_keys.assign(**{segments.SEGMENT: np.random.default_rng(seed).integers(0, K, len(series_keys))})
    return frame.merge(draws, on=SERIES_KEY, how="left", validate="many_to_one").set_index(frame.index)


# >>> SOLUTION 13.8
segment_results = {}
for label, features, categorical in [("z identyfikatorami", [*NUMERIC, *IDS], IDS), ("tylko liczby", NUMERIC, [])]:
    def score(make, frame=table):
        return backtest(make, frame, folds, fit_mask=fit_mask)["wape_in_stock"].mean()

    row = {"bez segmentu": score(lambda: LightGBMForecaster(features, categorical))}
    row["segment uczciwy"] = score(lambda: segments.SegmentedForecaster(daily, features, categorical, K))
    for seed in range(3):
        noisy = with_random_segment(table, seed)
        row[f"losowy {seed}"] = score(lambda: LightGBMForecaster([*features, segments.SEGMENT], [*categorical, segments.SEGMENT]), noisy)
    segment_results[label] = row
# --- STUB
#| segment_results = ...
# <<< SOLUTION
pd.DataFrame(segment_results).round(4)

# %% [markdown]
# Czy segment pomógł? Odpowiedz osobno dla obu wersji, porównując z kontrolą.
#
# *Twoja odpowiedź:*

# %% [markdown]
# ## 13.5 Sieć: `TabularMLP`
#
# Perceptron wielowarstwowy to warstwy liniowe przedzielone nieliniowością (ReLU). W `models/mlp.py` napisz `TabularMLP(n_inputs, hidden)`: dla `hidden=(64, 32)` to `Linear(n, 64) → ReLU → Linear(64, 32) → ReLU → Linear(32, 1)`, a `forward` zwraca jedną liczbę na wiersz, kształt `(n,)`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Klasa dziedziczy po `nn.Module` i na początku `__init__` woła `super().__init__()`. Warstwy trzymasz w `nn.Sequential`, nie w zwykłej liście: tylko wtedy PyTorch widzi ich parametry.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Po ostatniej warstwie liniowej nie ma ReLU: prognoza musi móc wyjść poniżej zera w trakcie uczenia. Wynik `(n, 1)` spłaszczasz przez `squeeze(-1)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# layers, width = [], n_inputs
# for units in hidden:
#     layers += [nn.Linear(width, units), nn.ReLU()]
#     width = units
# layers.append(nn.Linear(width, 1))
# self.net = nn.Sequential(*layers)
# ```
#
# </details>

# %%
check("13.5")

# %% [markdown]
# ## 13.6 Pętla treningowa
#
# Napisz `train_mlp`: epoka po epoce, w każdej wszystkie wiersze treningu w losowej kolejności, w mini-batchach. Na każdym batchu pięć kroków: prognoza, strata, `zero_grad`, `backward`, `step`. Po epoce strata na walidacji. Zatrzymanie, gdy walidacja nie poprawia się przez `patience` epok. Zwracasz model z wagami **najlepszej** epoki i historię strat.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `TensorDataset` i `DataLoader(..., batch_size=..., shuffle=True)` robią batche. `torch.optim.Adam(model.parameters(), lr=...)` i `nn.MSELoss()`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Najlepsze wagi zapamiętujesz jako **kopię**: `copy.deepcopy(model.state_dict())`. Sam `state_dict()` to odwołania do żywych tensorów, które zmienią się w następnym kroku. Walidację licz w `model.eval()` i `torch.no_grad()`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# for epoch in range(epochs):
#     model.train()
#     for xb, yb in loader:
#         optimiser.zero_grad()
#         loss = loss_fn(model(xb), yb)
#         loss.backward()
#         optimiser.step()
#     model.eval()
#     with torch.no_grad():
#         valid_loss = loss_fn(model(X_valid_t), y_valid_t).item()
#     if valid_loss < best_loss:
#         best_loss, best_state, waited = valid_loss, copy.deepcopy(model.state_dict()), 0
#     else:
#         waited += 1
#         if waited >= patience:
#             break
# model.load_state_dict(best_state)
# ```
#
# </details>

# %%
check("13.6")

# %% [markdown]
# ## 13.7 `MLPForecaster`
#
# Sieć jako model panelowy: skalowanie statystykami treningu, brakujące wartości zastąpione średnią i oflagowane osobnym wejściem, ostatnie `valid_days` dni treningu odłożone do zatrzymania. Szczegóły w docstringu.

# %%
check("13.7")

# %% [markdown]
# ## 13.9 MLP obok LightGBM
#
# Ten sam backtest, te same wiersze treningu, te same liczbowe cechy. Sieć z trzema ziarnami, bo jedno ziarno to jedna próbka.

# %%
from freshcast.models.mlp import MLPForecaster

# >>> SOLUTION 13.9
start = time.perf_counter()
mlp_runs = {seed: backtest(lambda seed=seed: MLPForecaster(NUMERIC, seed=seed), table, folds, fit_mask=fit_mask) for seed in range(3)}
mlp_seconds = time.perf_counter() - start
comparison = pd.Series(
    {
        "LightGBM, z identyfikatorami": segment_results["z identyfikatorami"]["bez segmentu"],
        "LightGBM, tylko liczby": segment_results["tylko liczby"]["bez segmentu"],
        **{f"MLP, ziarno {seed}": result["wape_in_stock"].mean() for seed, result in mlp_runs.items()},
    },
    name="wape_in_stock",
)
# --- STUB
#| comparison = ...
# <<< SOLUTION
print(f"MLP: {mlp_seconds:.0f} s na trzy backtesty")
comparison.round(4)

# %% [markdown]
# Jak wyglądało uczenie? Jedna sieć na ostatnim foldzie, krzywe strat:

# %%
fold_train, _ = folds[-1].split(table)
fold_train = fold_train.loc[fit_mask.loc[fold_train.index]]
network = MLPForecaster(NUMERIC, seed=0).fit(fold_train, fold_train["sale_amount"])
history = network.history_
fig, ax = plt.subplots(figsize=(7, 3.5))
epochs = np.arange(1, len(history) + 1)
ax.plot(epochs, history["train_loss"], label="trening")
ax.plot(epochs, history["valid_loss"], label="walidacja (ostatni tydzień treningu)")
ax.axvline(int(history["valid_loss"].to_numpy().argmin()) + 1, linestyle=":", label="zachowana epoka")
ax.set(xlabel="epoka", ylabel="MSE", title="Uczenie MLP")
ax.legend()
plt.show()

# %% [markdown]
# Jedna z przyczyn przewagi drzew: sieć ekstrapoluje. Porównaj temperaturę tygodni walidacji z zakresem temperatur treningu:

# %%
for number, fold in enumerate(folds, start=1):
    fold_train, fold_valid = fold.split(table)
    hotter = (fold_valid["avg_temperature"] > fold_train["avg_temperature"].max()).mean()
    print(f"fold {number}: średnia temperatura walidacji {fold_valid['avg_temperature'].mean():.1f}, treningu {fold_train['avg_temperature'].mean():.1f}, cieplej niż cokolwiek w treningu: {hotter:.0%} wierszy")

# %% [markdown]
# ## Pytania
#
# Bez sprawdzeń. Odpowiedz krótko, z liczbami z tego notebooka.
#
# 1. Czy segment pomógł? Odpowiedz osobno dla modelu z identyfikatorami i bez nich, z odniesieniem do losowych etykiet.
# 2. Dlaczego segmenty trzeba liczyć w każdym foldzie tylko z dni przed walidacją? Co dokładnie by przeciekło?
# 3. Co pokazuje pierwsza składowa profili godzinowych i czego ten obrazek nie mówi?
# 4. Czy serie tworzą naturalne grupy? Na podstawie czego tak twierdzisz?
# 5. Dlaczego LightGBM wygrywa z MLP na tych danych? Podaj przyczyny z dowodami z labu, nie ogólnik.
# 6. Co spróbowałbyś w sieci następnie i którą przyczynę z pytania 5 to adresuje?
#
# *Twoje odpowiedzi:*
