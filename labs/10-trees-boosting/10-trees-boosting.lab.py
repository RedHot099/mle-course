# %% [markdown]
# # Lab 10: drzewa, boosting i prognoza na tydzień
#
# W labie 09 LightGBM był czarną skrzynką. Teraz zaglądasz do środka: najpierw napiszesz jeden podział drzewa w NumPy, potem porównasz pojedyncze drzewo, las losowy, kNN i boosting na tych samych danych, a na koniec zbudujesz `LightGBMForecaster`, który zostanie z Tobą do końca kursu.
#
# Ostatnie zadanie to prawdziwa prognoza: model dostaje historię do wczoraj i ma przewidzieć cały przyszły tydzień, dzień po dniu albo jednym przebiegiem.
#
# **Czas:** około 7 godzin.
#
# | Zadanie | Co | Czas |
# |---|---|---|
# | 10.1 | `sum_of_squares`, `best_split` w `models/tree.py` | 60 min |
# | 10.5 | Drzewo, las, kNN i boosting na tych samych danych | 45 min |
# | 10.2 | `LightGBMForecaster` w `models/gbm.py` | 75 min |
# | 10.6 | Kategorie, funkcje celu, ograniczenie monotoniczne | 45 min |
# | 10.3 | `importance`, `contributions` | 45 min |
# | 10.4 | `stack_future`, `forecast_direct`, `forecast_recursive` w `forecast.py` | 75 min |

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
from freshcast.data.prepare import load_processed
from freshcast.data.schema import DATE, OOS_HOURS, OUTCOME_COLUMNS, TARGET
from freshcast.evaluation.scores import score_forecast
from freshcast.features import catalog
from freshcast.split import last_days_start, split_by_date

use_course_style()
daily = load_processed(paths.PROCESSED_DIR)
table = catalog.build_feature_table(daily)
NUMERIC = catalog.NUMERIC_FEATURES
IDS = catalog.CATEGORICAL_FEATURES

rest, test = split_by_date(table, last_days_start(table, 7))
train, valid = split_by_date(rest, last_days_start(rest, 7))
# Module 09: models learn from days without a stockout.
fit_rows = train.loc[train[OOS_HOURS] == 0]
valid_in_stock = valid.loc[valid[OOS_HOURS] == 0]


def scores(rows, forecast):
    """In-stock WAPE and bias, the two numbers every comparison reports."""
    result = score_forecast(rows[TARGET], forecast, rows[OOS_HOURS] == 0)
    return {"wape_in_stock": result["wape_in_stock"], "bias_in_stock": result["bias_in_stock"]}


print(f"trening bez braków: {len(fit_rows):,} wierszy, walidacja: {len(valid):,}")

# %% [markdown]
# ## 10.1 Jeden podział drzewa
#
# Drzewo regresyjne zadaje pytania typu "czy cecha ≤ próg?" i w każdym liściu przewiduje średnią celu. Próg wybiera tak, żeby błąd po podziale był jak najmniejszy. Błąd grupy to suma kwadratów odległości od jej średniej.
#
# W `src/freshcast/models/tree.py` napisz `sum_of_squares(values)` i `best_split(feature, target)`. Kandydaci na próg to środki między kolejnymi różnymi wartościami cechy.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Posortuj wiersze po cesze. Podział "pierwsze k wierszy w lewo, reszta w prawo" to jeden kandydat, ale tylko tam, gdzie wartość cechy się zmienia.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Pętla po kandydatach z `sum_of_squares` na obu stronach działa, ale jest kwadratowa. Szybciej: sumy kumulatywne celu i jego kwadratów (`np.cumsum`). Suma kwadratów odchyleń grupy to `sum(y²) - sum(y)² / n`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# order = np.argsort(feature, kind="stable")
# x, y = feature[order], target[order]
# n = len(y)
# left_sum, left_sq = np.cumsum(y)[:-1], np.cumsum(y**2)[:-1]
# left_n = np.arange(1, n)
# # right side: totals minus left side
# ...
# valid = x[1:] != x[:-1]   # a threshold only where the value changes
# ```
#
# </details>

# %%
check("10.1")

# %% [markdown]
# Twój podział na prawdziwej cesze, porównany z drzewem o głębokości 1 z scikit-learn:

# %%
from sklearn.tree import DecisionTreeRegressor

from freshcast.models.tree import best_split

known = fit_rows.dropna(subset=["same_weekday_mean"])
x, y = known["same_weekday_mean"].to_numpy(), known[TARGET].to_numpy()
start = time.perf_counter()
threshold, gain = best_split(x, y)
print(f"best_split: próg {threshold:.4f}, zysk {gain:,.0f}, {time.perf_counter() - start:.3f} s")
stump = DecisionTreeRegressor(max_depth=1).fit(x[:, None], y)
print(f"scikit-learn: próg {stump.tree_.threshold[0]:.4f}")

# %% [markdown]
# ## 10.5 Cztery rodziny modeli
#
# Porównaj na walidacji, na tych samych cechach:
#
# - drzewo o głębokości 6 i o głębokości 20,
# - las losowy: 100 drzew, każde na losowej próbce wierszy, `min_samples_leaf=20`,
# - kNN: prognoza to średnia 50 najbliższych wierszy treningu (cechy standaryzowane),
# - LightGBM z ustawieniami z labu 09.
#
# Dla każdego modelu zapisz WAPE na treningu i na walidacji. Modele z scikit-learn nie przyjmują `NaN`, więc uczysz je na wierszach z kompletem cech.

# %%
import lightgbm as lgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

complete = fit_rows.dropna(subset=NUMERIC)

# >>> SOLUTION 10.5
models = {
    "drzewo, głębokość 6": DecisionTreeRegressor(max_depth=6, random_state=0),
    "drzewo, głębokość 20": DecisionTreeRegressor(max_depth=20, random_state=0),
    "las losowy": RandomForestRegressor(n_estimators=100, min_samples_leaf=20, n_jobs=-1, random_state=0),
    "kNN, k = 50": make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=50)),
    "LightGBM": lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, random_state=0, verbose=-1),
}
family_results = {}
for name, model in models.items():
    start = time.perf_counter()
    model.fit(complete[NUMERIC], complete[TARGET])
    seconds = time.perf_counter() - start
    family_results[name] = {
        "trening": scores(complete, model.predict(complete[NUMERIC]))["wape_in_stock"],
        "walidacja": scores(valid, np.clip(model.predict(valid[NUMERIC]), 0, None))["wape_in_stock"],
        "sekundy": seconds,
    }
# --- STUB
#| family_results = ...
# <<< SOLUTION
pd.DataFrame(family_results).T.round(3)

# %% [markdown]
# Drzewo o głębokości 20 ma najlepszy wynik na treningu i najgorszy na walidacji. Jak nazywa się to zjawisko i co w lesie losowym i w boostingu mu przeciwdziała?
#
# *Twoja odpowiedź:*

# %% [markdown]
# ## 10.2 `LightGBMForecaster`
#
# Opakuj LightGBM w interfejs `PanelForecaster`. W `src/freshcast/models/gbm.py` napisz według docstringów:
#
# - `_matrix(X)`: kolumny cech, a kategorie zakodowane tak samo jak w treningu. Bez tego ten sam sklep mógłby dostać inny kod przy prognozie,
# - `fit(X, y, valid=None, patience=50)`: trening, z ograniczeniami monotonicznymi, a z `valid` z **early stopping**: trening kończy się, gdy błąd na walidacji przestaje spadać,
# - `rounds_used` i `predict`: prognoza z najlepszą liczbą drzew, nieujemna.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `pd.Categorical(values, categories=...)` koduje kategorie według podanej listy, a nieznane zamienia na brak. Listę kategorii każdej kolumny zapamiętujesz w `fit`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `lgb.train(params, lgb.Dataset(...), num_boost_round=..., valid_sets=[...], callbacks=[lgb.early_stopping(patience, verbose=False)])`. Ograniczenia monotoniczne to lista `monotone_constraints` w parametrach, jedna liczba na cechę, w kolejności cech.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# self._categories = {c: pd.Index(X[c].unique()).sort_values() for c in self.categorical}
# params = dict(self.params)
# if self.monotone:
#     params["monotone_constraints"] = [self.monotone.get(name, 0) for name in self.features]
# train = lgb.Dataset(self._matrix(X), label=y.to_numpy())
# ```
#
# </details>

# %%
check("10.2")

# %% [markdown]
# ## 10.6 Trzy decyzje o modelu
#
# **Identyfikatory jako kategorie.** Czy model zyskuje, gdy wie, który to sklep i produkt?

# %%
from freshcast.models.gbm import LightGBMForecaster

stop_on = (valid_in_stock, valid_in_stock[TARGET])

# >>> SOLUTION 10.6
without_ids = LightGBMForecaster(NUMERIC, rounds=2000).fit(fit_rows, fit_rows[TARGET], valid=stop_on)
with_ids = LightGBMForecaster([*NUMERIC, *IDS], categorical=IDS, rounds=2000).fit(fit_rows, fit_rows[TARGET], valid=stop_on)
id_results = pd.DataFrame(
    {
        "bez identyfikatorów": {**scores(valid, without_ids.predict(valid)), "drzewa": without_ids.rounds_used},
        "z identyfikatorami": {**scores(valid, with_ids.predict(valid)), "drzewa": with_ids.rounds_used},
    }
).T
# --- STUB
#| id_results = ...
# <<< SOLUTION
id_results.round(3)

# %% [markdown]
# Early stopping wybrał liczbę drzew na walidacji, więc wynik walidacji jest odrobinę zbyt optymistyczny. To jedna z decyzji, które ocenisz uczciwie dopiero na teście albo w backteście z modułu 11.
#
# **Funkcja celu.** Sprzedaż to liczby nieujemne, często małe, z długim ogonem. Porównaj domyślną regresję (L2) z celami `poisson` i `tweedie`, które zakładają taki rozkład.

# %%
# >>> SOLUTION 10.6
objective_results = {}
for objective in ["regression", "poisson", "tweedie"]:
    model = LightGBMForecaster([*NUMERIC, *IDS], categorical=IDS, params={"objective": objective}, rounds=2000)
    model.fit(fit_rows, fit_rows[TARGET], valid=stop_on)
    objective_results[objective] = {**scores(valid, model.predict(valid)), "drzewa": model.rounds_used}
# --- STUB
#| objective_results = ...
# <<< SOLUTION
pd.DataFrame(objective_results).T.round(3)

# %% [markdown]
# **Ograniczenie monotoniczne.** `discount_filled` to mnożnik ceny: 0.8 znaczy 20% taniej. Niższa cena nie powinna obniżać prognozy. Drzewa nie wiedzą tego same i na małych grupach potrafią nauczyć się odwrotności. Wymuś, żeby prognoza nie rosła, gdy mnożnik rośnie (`-1`), i sprawdź, ile to kosztuje.

# %%
# >>> SOLUTION 10.6
monotone = LightGBMForecaster([*NUMERIC, *IDS], categorical=IDS, monotone={"discount_filled": -1}, rounds=2000)
monotone.fit(fit_rows, fit_rows[TARGET], valid=stop_on)
monotone_scores = scores(valid, monotone.predict(valid))
# --- STUB
#| monotone = ...
#| monotone_scores = ...
# <<< SOLUTION
print({name: round(value, 3) for name, value in monotone_scores.items()})

# %% [markdown]
# Sprawdź, czy ograniczenie działa: weź jeden wiersz walidacji, zmieniaj tylko mnożnik ceny i patrz na prognozę obu modeli.

# %%
row = valid_in_stock.iloc[[0]]
multipliers = np.linspace(0.5, 1.0, 11)
probe = pd.concat([row.assign(discount_filled=m, promo_depth=1 - m) for m in multipliers], ignore_index=True)
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(multipliers, with_ids.predict(probe), label="bez ograniczenia")
ax.plot(multipliers, monotone.predict(probe), label="monotoniczny")
ax.set(xlabel="mnożnik ceny (1.0 = bez rabatu)", ylabel="prognoza", title="Prognoza jednego wiersza przy różnych cenach")
ax.legend()
plt.show()

# %% [markdown]
# ## 10.3 Co model wykorzystał
#
# Napisz `importance()` (udział każdej cechy w łącznym zysku podziałów) i `contributions(X)` (wartości SHAP: rozkład każdej prognozy na wkłady cech). LightGBM liczy oba, trzeba je tylko dobrze opisać.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `booster.feature_importance(importance_type="gain")` i `booster.predict(..., pred_contrib=True)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `pred_contrib=True` zwraca macierz z jedną kolumną na cechę i ostatnią kolumną z wartością bazową. Nazwij kolumny i daj ramce indeks `X`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# values = self.booster.predict(self._matrix(X), num_iteration=self.rounds_used, pred_contrib=True)
# return pd.DataFrame(values, index=X.index, columns=[*self.features, "baseline"])
# ```
#
# </details>

# %%
check("10.3")

# %%
importance = with_ids.importance()
fig, ax = plt.subplots(figsize=(7, 4))
importance.head(12).iloc[::-1].plot.barh(ax=ax)
ax.set(xlabel="udział w zysku podziałów", title="Ważność cech")
plt.show()

# %% [markdown]
# Ważność mówi, czego model używał w całym zbiorze. SHAP mówi, dlaczego jedna konkretna prognoza jest taka, jaka jest. Rozłóż największą prognozę walidacji:

# %%
contributions = with_ids.contributions(valid_in_stock)
top = with_ids.predict(valid_in_stock).argmax()
one = contributions.iloc[top]
print(f"Prognoza {with_ids.predict(valid_in_stock)[top]:.2f}, suma wkładów {one.sum():.2f}, wartość bazowa {one['baseline']:.2f}")
one.drop("baseline").sort_values(key=np.abs, ascending=False).head(8).round(3)

# %% [markdown]
# ## 10.4 Prognoza przyszłego tygodnia
#
# Do tej pory model przewidywał wiersze, które miały wszystkie cechy policzone z prawdziwej historii. Prawdziwa prognoza wygląda inaczej: masz historię do wczoraj i listę dni do przewidzenia, z cechami znanymi z góry (rabat, flagi, pogoda), ale bez sprzedaży i braków.
#
# W `src/freshcast/forecast.py` napisz:
#
# - `stack_future(history, future)`: przyszłe dni pod historią, z wyzerowanymi (`NaN`) kolumnami znanymi dopiero po fakcie, nawet jeśli wywołujący je podał,
# - `forecast_direct(model, history, future, build)`: buduje cechy raz i prognozuje wszystkie dni naraz. Działa, gdy żaden lag nie jest krótszy niż horyzont,
# - `forecast_recursive(...)`: dzień po dniu. Prognoza dnia wraca do panelu jako jego sprzedaż, więc następny dzień może użyć lagu 1.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Wszystkie trzy funkcje pracują na jednym panelu: historia plus przyszłość. Cechy zawsze liczy ta sama funkcja `build`, co w treningu.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# W wersji rekurencyjnej pętla idzie po przyszłych datach: zbuduj cechy całego panelu, przewidź dzisiejsze wiersze, wpisz prognozy do kolumny celu. Na końcu zwróć prognozy w kolejności wierszy `future`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# panel = stack_future(history, future)
# is_future = panel[DATE] > history[DATE].max()
# for day in sorted(panel.loc[is_future, DATE].unique()):
#     today = panel[DATE] == day
#     features = build(panel)
#     panel.loc[today, TARGET] = model.predict(features.loc[today])
# ```
#
# </details>

# %%
check("10.4")

# %% [markdown]
# Test: historia kończy się tydzień przed końcem danych, a przyszłość to ostatni tydzień bez kolumn wynikowych. Dwa modele: bezpośredni na cechach z labu 09 i rekurencyjny, który dostaje też lagi 1-3 i okna kończące się wczoraj. Oba uczysz na całej historii, z liczbą drzew wybraną wcześniej na walidacji.

# %%
from freshcast import forecast

history, actual_week = split_by_date(daily, last_days_start(daily, 7))
future = actual_week.drop(columns=OUTCOME_COLUMNS)
RECURSIVE = [*NUMERIC, *catalog.SHORT_FEATURES, *IDS]

# >>> SOLUTION 10.4
direct_rows = catalog.build_feature_table(history).query(f"{OOS_HOURS} == 0")
recursive_rows = catalog.build_recursive_table(history).query(f"{OOS_HOURS} == 0")
direct_model = LightGBMForecaster([*NUMERIC, *IDS], categorical=IDS, rounds=with_ids.rounds_used).fit(direct_rows, direct_rows[TARGET])
recursive_model = LightGBMForecaster(RECURSIVE, categorical=IDS, rounds=with_ids.rounds_used).fit(recursive_rows, recursive_rows[TARGET])
start = time.perf_counter()
direct_forecast = forecast.forecast_direct(direct_model, history, future, catalog.build_feature_table)
direct_seconds = time.perf_counter() - start
start = time.perf_counter()
recursive_forecast = forecast.forecast_recursive(recursive_model, history, future, catalog.build_recursive_table)
recursive_seconds = time.perf_counter() - start
week_results = pd.DataFrame(
    {
        "bezpośrednia": {**scores(actual_week, direct_forecast), "sekundy": direct_seconds},
        "rekurencyjna": {**scores(actual_week, recursive_forecast), "sekundy": recursive_seconds},
    }
).T
# --- STUB
#| week_results = ...
# <<< SOLUTION
week_results.round(3)

# %% [markdown]
# Czy błąd prognozy rekurencyjnej rośnie z każdym dniem horyzontu? Policz WAPE bez braków osobno dla każdego dnia tygodnia testowego.

# %%
# >>> SOLUTION 10.4
horizon_day = (actual_week[DATE] - actual_week[DATE].min()).dt.days + 1
in_stock_week = actual_week[OOS_HOURS] == 0
by_day = pd.DataFrame(
    {
        name: (actual_week[TARGET] - forecast_).abs().where(in_stock_week).groupby(horizon_day).sum()
        / actual_week[TARGET].where(in_stock_week).groupby(horizon_day).sum()
        for name, forecast_ in [("bezpośrednia", direct_forecast), ("rekurencyjna", recursive_forecast)]
    }
)
# --- STUB
#| by_day = ...
# <<< SOLUTION
by_day.round(3)

# %% [markdown]
# ## Pytania
#
# Bez sprawdzeń. Odpowiedz krótko.
#
# 1. Identyfikatory sklepu i produktu mają największą ważność. Czy to znaczy, że model "rozumie" sklepy? Co się stanie z nowym produktem, którego nie było w treningu?
# 2. Ograniczenie monotoniczne prawie nie zmieniło WAPE. Po co więc je stosować?
# 3. Ważność cechy liczona zyskiem podziałów mówi, czego model używał. Czego nie mówi? Podaj przykład, w którym cecha ma dużą ważność, a jej usunięcie niemal nic nie zmienia.
# 4. Prognoza rekurencyjna używa lagu 1, a mimo to nie jest wyraźnie lepsza od bezpośredniej. Dlaczego lag 1 daje mniej, niż można by się spodziewać, gdy od drugiego dnia jest prognozą?
#
# *Twoje odpowiedzi:*
