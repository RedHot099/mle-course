# %% [markdown]
# # Lab 08: pierwszy model i uczciwy test
#
# Masz czysty panel z labu 07. W tym labie powstaje pierwszy model, który uczy się na wszystkich seriach naraz, i pierwszy test, któremu można wierzyć. Kolejność jest ważniejsza niż model:
#
# 1. podział po czasie: trening, walidacja, test,
# 2. baseline, który każdy model musi pobić,
# 3. model liniowy: najpierw od zera w NumPy, żeby zobaczyć, co znaczy "uczenie", potem w scikit-learn,
# 4. pułapka: model z wynikiem zbyt dobrym, żeby był prawdziwy,
# 5. decyzje na walidacji, jeden rzut oka na test na końcu.
#
# **Czas:** około 7 godzin.
#
# | Zadanie | Co | Czas |
# |---|---|---|
# | 08.1 | `last_days_start`, `split_by_date` w `split.py` | 30 min |
# | 08.2 | `PerSeriesForecaster` w `models/panel.py` | 60 min |
# | 08.3 | Regresja liniowa z gradient descent w `models/gradient.py` | 90 min |
# | 08.4 | `LinearForecaster` w `models/panel.py` | 45 min |
# | 08.5 | `score_forecast` w `evaluation/scores.py` | 20 min |
# | 08.6 | Pułapka: wszystkie kolumny | 45 min |
# | 08.7 | `alpha`, test, tabela wyników | 45 min |

# %%
# %load_ext autoreload
# %autoreload 2

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from coursekit import paths
from coursekit.nb import check
from coursekit.plotting import use_course_style
from freshcast.data.panel import add_lag, add_rolling_mean
from freshcast.data.prepare import load_processed, prepare_daily, save_processed
from freshcast.data.schema import DATE, OOS_HOURS, OUTCOME_COLUMNS, TARGET

use_course_style()

# %% [markdown]
# ## Dane z labu 07
#
# Jeśli nie masz jeszcze `data/processed/daily.parquet`, komórka zbuduje go kodem z modułu 07 (po `uv run course catchup 08` także bez robienia labu 07).

# %%
if not (paths.PROCESSED_DIR / "daily.parquet").is_file():
    cities = paths.active_profile().cities or paths.PROFILES["standard"].cities
    save_processed(prepare_daily(paths.FRN_TRAIN, cities=cities), paths.PROCESSED_DIR)

daily = load_processed(paths.PROCESSED_DIR)
print(daily.shape, daily[DATE].min().date(), daily[DATE].max().date())

# %% [markdown]
# ## Cechy znane tydzień wcześniej
#
# Prognozujesz 7 dni naprzód. Prognozę na przyszłą środę robisz dziś, więc sprzedaży z wtorku przed tą środą jeszcze nie znasz. Każda cecha musi być znana w chwili prognozy: lag co najmniej 7 dni, okno, które kończy się 7 dni wcześniej (reguła C2). Szczegóły w module 09. Tu cechy są gotowe:
#
# - sprzedaż 7 i 14 dni wcześniej,
# - średnia z 7 i z 28 dni, kończąca się 7 dni wcześniej,
# - rabat i flagi promocji oraz święta, które sklep zna z góry.
#
# Rabat ma braki tam, gdzie w danych było zero (moduł 07). Model liniowy nie przyjmie braku, więc wypełniasz go wartością 1.0, czyli "bez rabatu", i zostawiasz obok flagę `discount_is_zero`. Model dostaje obie informacje i sam zdecyduje, ile są warte.

# %%
FEATURES = [
    "sale_amount_lag_7",
    "sale_amount_lag_14",
    "sale_amount_mean_7_lag_7",
    "sale_amount_mean_28_lag_7",
    "discount_filled",
    "discount_is_zero",
    "holiday_flag",
    "activity_flag",
]

panel = (
    daily.pipe(add_lag, TARGET, 7)
    .pipe(add_lag, TARGET, 14)
    .pipe(add_rolling_mean, TARGET, 7, lag=7)
    .pipe(add_rolling_mean, TARGET, 28, lag=7)
    .assign(
        discount_filled=lambda frame: frame["discount"].fillna(1.0),
        discount_is_zero=lambda frame: frame["discount_is_zero"].astype(int),
    )
)
panel[FEATURES].describe().T[["count", "mean", "min", "max"]]

# %% [markdown]
# ## 08.1 Podział po czasie
#
# W `src/freshcast/split.py` napisz:
#
# - `last_days_start(df, days)`: pierwsza data ostatnich `days` dni ramki,
# - `split_by_date(df, cutoff)`: wiersze przed datą i od niej, bez mieszania, z zachowanym indeksem.
#
# Test to ostatni tydzień. Walidacja to tydzień przed nim. Reszta to trening.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Różnica dwóch dat to `Timedelta`; `pd.Timedelta(days=6)` przesuwa datę o 6 dni. Ostatnie 7 dni zaczyna się 6 dni przed ostatnią datą.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `split_by_date` to jedna maska `df[DATE] < cutoff` i dwa `.loc`. Sprawdź, czy któraś część nie wyszłaby pusta: taki podział to prawie zawsze pomyłka w dacie.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# is_before = df[DATE] < cutoff
# if is_before.all() or not is_before.any():
#     raise ValueError(...)
# return df.loc[is_before], df.loc[~is_before]
# ```
#
# </details>

# %%
check("08.1")

# %%
from freshcast.split import last_days_start, split_by_date

# >>> SOLUTION 08.1
rest, test = split_by_date(panel, last_days_start(panel, 7))
train, valid = split_by_date(rest, last_days_start(rest, 7))
# --- STUB
#| rest, test = ...
#| train, valid = ...
# <<< SOLUTION
for name, part in [("trening", train), ("walidacja", valid), ("test", test)]:
    print(f"{name:>10}: {len(part):>7,} wierszy, {part[DATE].min().date()} .. {part[DATE].max().date()}")

# %% [markdown]
# ## 08.2 Baseline na całym panelu
#
# Prognozy lokalne z modułu 04 widzą jedną serię. Żeby porównywać je z modelami panelowymi, potrzebny jest adapter o tym samym interfejsie co każdy model od teraz: `fit(X, y)` i `predict(X)`, gdzie `X` to wiersze panelu.
#
# Napisz `PerSeriesForecaster` w `src/freshcast/models/panel.py`. `fit` zapamiętuje historię każdej serii, `predict` dla każdej serii w `X` robi świeży model lokalny, uczy go na historii i prognozuje tyle dni, ile ta seria ma wierszy w `X`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Historia serii to jej wartości `y` posortowane po dacie. Słownik: klucz serii (krotka `store_id, product_id`) → lista wartości.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# W `predict` wynik musi mieć kolejność wierszy `X`. Zrób pustą tablicę na wynik, a dla każdej serii wpisz prognozy w pozycje jej wierszy, posortowanych po dacie: najwcześniejszy dzień dostaje pierwszy krok prognozy.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# rows = X[[*SERIES_KEY, DATE]].reset_index(drop=True)
# forecast = np.empty(len(rows))
# for key, group in rows.groupby(SERIES_KEY, sort=False):
#     positions = group.sort_values(DATE).index.to_numpy()
#     local = self._make_local().fit(self._histories[key])
#     forecast[positions] = local.predict(len(positions))
# ```
#
# </details>

# %%
check("08.2")

# %%
from freshcast import metrics
from freshcast.models.local import SeasonalNaiveForecaster
from freshcast.models.panel import PerSeriesForecaster

baseline = PerSeriesForecaster(lambda: SeasonalNaiveForecaster(season=7))
baseline.fit(train, train[TARGET])
baseline_valid = baseline.predict(valid)
valid_in_stock = valid[OOS_HOURS] == 0
print(f"Baseline, walidacja: WAPE {metrics.wape(valid[TARGET], baseline_valid):.3f}, bez braków {metrics.wape(valid[TARGET], baseline_valid, valid_in_stock):.3f}")

# %% [markdown]
# ## 08.3 Regresja liniowa od zera
#
# Model liniowy przewiduje `X @ w + b`. Uczenie to szukanie `w` i `b`, dla których średni kwadrat błędu (MSE) jest najmniejszy. Gradient descent robi to krokami: liczy, w którą stronę MSE rośnie najszybciej (gradient), i przesuwa parametry trochę w przeciwną stronę.
#
# W `src/freshcast/models/gradient.py` napisz `predict_linear`, `mse`, `mse_gradient` i `fit_linear_gd`. Wzory są w wykładzie i w docstringach.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Błąd to `r = X @ w + b - y`. MSE to `mean(r ** 2)`. Pochodna MSE po `w` to `2 / n * X.T @ r`, po `b` to `2 * mean(r)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `fit_linear_gd` zaczyna od zer, w każdym kroku zapisuje stratę, liczy gradient i odejmuje `learning_rate * gradient`. Jeśli strata przestanie być skończona (`np.isfinite`), krok był za duży: zgłoś `ValueError`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# weights, intercept, losses = np.zeros(X.shape[1]), 0.0, []
# for _ in range(steps):
#     loss = mse(y, predict_linear(X, weights, intercept))
#     if not np.isfinite(loss):
#         raise ValueError(...)
#     losses.append(loss)
#     grad_w, grad_b = mse_gradient(X, y, weights, intercept)
#     weights = weights - learning_rate * grad_w
#     intercept = intercept - learning_rate * grad_b
# ```
#
# </details>

# %%
check("08.3")

# %% [markdown]
# Ucz na wierszach treningu, które mają wszystkie cechy (pierwsze 34 dni każdej serii nie mają średniej z 28 dni sprzed tygodnia). Cechy standaryzujesz średnią i odchyleniem **z treningu** (reguła C4). Porównaj kilka kroków uczenia:

# %%
from freshcast.models import gradient

fit_rows = train.dropna(subset=FEATURES)
print(f"Wiersze treningu z kompletem cech: {len(fit_rows):,} z {len(train):,}")
X = fit_rows[FEATURES].to_numpy(dtype=float)
mean, std = X.mean(axis=0), X.std(axis=0)
X_scaled = (X - mean) / std
y = fit_rows[TARGET].to_numpy()

fig, ax = plt.subplots(figsize=(7, 3.5))
for learning_rate in [0.003, 0.03, 0.3]:
    _, _, losses = gradient.fit_linear_gd(X_scaled, y, learning_rate=learning_rate, steps=200)
    ax.plot(losses, label=f"krok {learning_rate}")
ax.set(xlabel="krok uczenia", ylabel="MSE", yscale="log", title="Strata w trakcie uczenia")
ax.legend()
plt.show()

# %% [markdown]
# Co się stanie przy kroku 1.5? Uruchom i przeczytaj komunikat.

# %%
try:
    gradient.fit_linear_gd(X_scaled, y, learning_rate=1.5, steps=200)
except ValueError as error:
    print("ValueError:", error)

# %% [markdown]
# Twój model i scikit-learn powinny dojść do tych samych wag:

# %%
from sklearn.linear_model import LinearRegression

weights, intercept, _ = gradient.fit_linear_gd(X_scaled, y, learning_rate=0.1, steps=500)
reference = LinearRegression().fit(X_scaled, y)
pd.DataFrame({"gradient descent": weights, "scikit-learn": reference.coef_}, index=FEATURES).round(3)

# %% [markdown]
# ## 08.4 `LinearForecaster`
#
# Teraz ten sam model w wersji produkcyjnej: `StandardScaler` i `Ridge` w jednym `Pipeline`, pod interfejsem `fit(X, y)` / `predict(X)`. Napisz `LinearForecaster` w `src/freshcast/models/panel.py` według docstringu: odrzuca cechy z brakami, prognozę ujemną podnosi do zera.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `make_pipeline(StandardScaler(), Ridge(alpha=...))` to jeden obiekt z `fit` i `predict`. Skaler dopasowuje się w `fit`, więc widzi tylko dane treningowe.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Wspólne sprawdzenie cech (wybór kolumn, brak `NaN`) napisz raz, jako metodę pomocniczą, i wołaj w `fit` i w `predict`. Ujemne prognozy obcina `np.clip(..., 0.0, None)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# def fit(self, X, y):
#     self._pipeline = make_pipeline(StandardScaler(), Ridge(alpha=self.alpha))
#     self._pipeline.fit(self._checked(X), y)
#     return self
# ```
#
# </details>

# %%
check("08.4")

# %% [markdown]
# ## 08.5 Jedna funkcja oceny
#
# Każdy model od teraz oceniasz tak samo: WAPE, MAE i bias na wszystkich wierszach, a WAPE i bias także na dniach bez braków towaru. Napisz `score_forecast` w `src/freshcast/evaluation/scores.py`, używając metryk z modułu 05.

# %%
check("08.5")

# %%
from freshcast.evaluation.scores import score_forecast
from freshcast.models.panel import LinearForecaster

linear = LinearForecaster(FEATURES, alpha=1.0).fit(fit_rows, fit_rows[TARGET])
scores = pd.DataFrame(
    {
        "baseline": score_forecast(valid[TARGET], baseline_valid, valid_in_stock),
        "liniowy": score_forecast(valid[TARGET], linear.predict(valid), valid_in_stock),
    }
).T
scores.round(3)

# %% [markdown]
# ## 08.6 Pułapka: wszystkie kolumny
#
# Kolega proponuje: "po co wybierać cechy, daj modelowi wszystko, co jest w tabeli, Ridge sam wybierze". Sprawdź to.

# %%
# >>> SOLUTION 08.6
numeric = panel.select_dtypes("number").columns
everything = [c for c in numeric if c not in (TARGET, "discount") and not c.endswith("_id")]
greedy_rows = train.dropna(subset=everything)
greedy = LinearForecaster(everything, alpha=1.0).fit(greedy_rows, greedy_rows[TARGET])
greedy_scores = score_forecast(valid[TARGET], greedy.predict(valid), valid_in_stock)
# --- STUB
#| everything = ...
#| greedy = ...
#| greedy_scores = ...
# <<< SOLUTION
print(everything)
print({name: round(value, 4) for name, value in greedy_scores.items()})

# %% [markdown]
# WAPE bliski zera przy prognozie sprzedaży świeżych produktów na tydzień naprzód nie jest sukcesem, tylko objawem. Znajdź przyczynę: które cechy mają największe wagi?

# %%
greedy.coefficients().abs().sort_values(ascending=False).head(6).round(3)

# %% [markdown]
# Porównaj te kolumny z listą `OUTCOME_COLUMNS` w `src/freshcast/data/schema.py`.

# %%
print(OUTCOME_COLUMNS)

# %% [markdown]
# **Twoja reguła.** Zapisz jednym zdaniem regułę, która zapobiegłaby tej pomyłce, i sprawdź, którą regułę z `docs/standard.md` łamie model "wszystkie kolumny".
#
# *Twoja odpowiedź:*
#
# Jest też wersja subtelniejsza. Dodaj do dobrych cech tylko liczbę godzin bez towaru z tego samego dnia i porównaj oba WAPE z modelem bez niej:

# %%
# >>> SOLUTION 08.6
with_oos = LinearForecaster([*FEATURES, OOS_HOURS], alpha=1.0).fit(fit_rows, fit_rows[TARGET])
with_oos_scores = score_forecast(valid[TARGET], with_oos.predict(valid), valid_in_stock)
# --- STUB
#| with_oos_scores = ...
# <<< SOLUTION
pd.DataFrame({"bez oos_hours": scores.loc["liniowy"], "z oos_hours": with_oos_scores}).T[["wape", "wape_in_stock"]].round(3)

# %% [markdown]
# ## 08.7 Decyzje na walidacji, test na końcu
#
# `alpha` to siła kary w Ridge: im większa, tym bliżej zera są wagi. Wybierasz ją na walidacji, nigdy na teście (reguła C5).

# %%
# >>> SOLUTION 08.7
alphas = [0.01, 1.0, 100.0, 1_000.0, 10_000.0, 100_000.0]
by_alpha = {
    alpha: score_forecast(valid[TARGET], LinearForecaster(FEATURES, alpha=alpha).fit(fit_rows, fit_rows[TARGET]).predict(valid), valid_in_stock)["wape_in_stock"]
    for alpha in alphas
}
best_alpha = min(by_alpha, key=by_alpha.get)
# --- STUB
#| by_alpha = ...
#| best_alpha = ...
# <<< SOLUTION
print({alpha: round(value, 4) for alpha, value in by_alpha.items()}, "najlepsze:", best_alpha)

# %% [markdown]
# Decyzje zapadły. Teraz, jeden raz, test: oba modele uczysz na treningu i walidacji razem i prognozujesz ostatni tydzień.

# %%
# >>> SOLUTION 08.7
final_rows = rest.dropna(subset=FEATURES)
final_baseline = PerSeriesForecaster(lambda: SeasonalNaiveForecaster(season=7)).fit(rest, rest[TARGET])
final_linear = LinearForecaster(FEATURES, alpha=best_alpha).fit(final_rows, final_rows[TARGET])
test_in_stock = test[OOS_HOURS] == 0
results = pd.DataFrame(
    {
        "baseline sezonowy": score_forecast(test[TARGET], final_baseline.predict(test), test_in_stock),
        "Ridge": score_forecast(test[TARGET], final_linear.predict(test), test_in_stock),
    }
).T
# --- STUB
#| results = ...
# <<< SOLUTION
results.round(3)

# %% [markdown]
# ## Pytania
#
# Bez sprawdzeń. Odpowiedz krótko.
#
# 1. Dlaczego walidacja i test leżą po treningu, a nie są losowymi wierszami z całego okresu? Co by się stało z wynikiem przy losowym podziale?
# 2. `alpha` prawie nie zmienia wyniku. Dlaczego regularyzacja ma tu mało do roboty? Kiedy miałaby dużo?
# 3. Model z `oos_hours` ma lepszy WAPE na wszystkich dniach i gorszy na dniach bez braków. Jak to wyjaśnisz?
# 4. Ridge jest lepszy od baseline'u, ale bias na dniach bez braków jest ujemny. Co to znaczy dla sklepu i skąd może się brać?
#
# *Twoje odpowiedzi:*
