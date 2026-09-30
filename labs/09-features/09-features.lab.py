# %% [markdown]
# # Lab 09: cechy, które model może znać
#
# W labie 08 cechy były gotowe. Teraz piszesz je sam: kalendarz, lagi i okna świadome horyzontu, popyt w dni braków towaru, kodowanie kategorii przez średnią celu. Na koniec łączysz je w rejestr, który sam ustala kolejność liczenia.
#
# Każdą cechę oceniasz eksperymentem, a nie intuicją. Do oceny służy LightGBM z ustalonymi ustawieniami. Traktuj go na razie jak czarną skrzynkę: dostaje cechy, zwraca prognozy. Do środka zajrzysz w module 10.
#
# Dwa eksperymenty w tym labie mają wynik, którego się nie spodziewasz. To jest cel, nie przypadek.
#
# **Czas:** około 7 godzin.
#
# | Zadanie | Co piszesz w `src/freshcast/features/` | Czas |
# |---|---|---|
# | 09.1 | `calendar.py`: dzień tygodnia, kodowanie cykliczne, święta | 45 min |
# | 09.2 | `lags.py`: lagi i okna świadome horyzontu | 45 min |
# | 09.5 | `build.py`: kolejność z grafu zależności, `build_features` | 60 min |
# | 09.3 | `demand.py`: profil godzinowy, pokrycie, korekta popytu | 90 min |
# | 09.4 | `encoding.py`: `TargetEncoder` | 60 min |
# | 09.6 | Eksperymenty i pytania | 90 min |

# %%
# %load_ext autoreload
# %autoreload 2

import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from coursekit import paths
from coursekit.nb import check
from coursekit.plotting import use_course_style
from freshcast.data.prepare import load_processed
from freshcast.data.schema import DATE, OOS_HOURS, SALES_IN_STOCK, SERIES_KEY, TARGET
from freshcast.evaluation.scores import score_forecast
from freshcast.split import last_days_start, split_by_date

use_course_style()
daily = load_processed(paths.PROCESSED_DIR)
CITIES = paths.active_profile().cities or paths.PROFILES["standard"].cities


def quick_model(rows, target, features):
    """LightGBM with fixed settings: a stand-in until module 10."""
    model = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, random_state=0, verbose=-1)
    return model.fit(rows[features], target)


def evaluate(model, rows, features):
    """Score a model on rows, with forecasts below zero raised to zero."""
    forecast = np.clip(model.predict(rows[features]), 0.0, None)
    return score_forecast(rows[TARGET], forecast, rows[OOS_HOURS] == 0)


# %% [markdown]
# ## 09.1 Kalendarz
#
# W `calendar.py` napisz `day_of_week`, `cyclical`, `public_holidays`, `is_public_holiday` i `days_to_next_holiday`. Święta bierzesz z pakietu `holidays` dla Chin (`COUNTRY = "CN"`), bo dane pochodzą z chińskiej sieci sklepów.
#
# Dlaczego kodowanie cykliczne? Dla modelu liniowego niedziela (6) i poniedziałek (0) leżą na przeciwnych końcach skali, choć w tygodniu są sąsiadami. Na okręgu (`sin`, `cos`) leżą obok siebie.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `df[DATE].dt.dayofweek` daje 0 dla poniedziałku. `holidays.country_holidays(COUNTRY, years=...)` zwraca słownik data → nazwa święta.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Dni do najbliższego święta licz na unikalnych datach, nie na wierszach: dat jest 90, wierszy ćwierć miliona. `DatetimeIndex.searchsorted(daty)` zwraca pozycję pierwszego święta nie wcześniejszego niż każda data. Na końcu przypisz wynik z powrotem do wierszy przez `map`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# angle = 2 * np.pi * values / period
# return np.sin(angle), np.cos(angle)
# ```
#
# </details>

# %%
check("09.1")

# %% [markdown]
# Dane mają własną kolumnę `holiday_flag`. Porównaj ją ze świętami z pakietu:

# %%
from freshcast.features import calendar

days = daily.drop_duplicates(DATE)[[DATE, "holiday_flag"]].reset_index(drop=True)
days = days.assign(
    public_holiday=calendar.is_public_holiday(days),
    weekend=calendar.day_of_week(days) >= 5,
)
pd.crosstab(days["holiday_flag"], [days["public_holiday"], days["weekend"]])

# %% [markdown]
# Co oznacza `holiday_flag` w tych danych? Jaką informację dodaje `days_to_holiday`, której flaga nie ma?
#
# *Twoja odpowiedź:*
#
# ## 09.2 Lagi świadome horyzontu
#
# Prognozujesz 7 dni naprzód. Lag 1 dla prognozy na siódmy dzień to sprzedaż szóstego dnia horyzontu: w chwili prognozy nieznana. W `lags.py` napisz `check_horizon`, `lag_feature` i `window_mean_feature`. Obie funkcje cech najpierw sprawdzają, że lag nie jest krótszy niż horyzont (reguła C2), a potem korzystają z `add_lag` i `add_rolling_mean` z modułu 07.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Cała wiedza o czasie siedzi w `check_horizon`. Reszta to wywołanie funkcji z modułu 07 i wybranie jednej kolumny.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Okno świadome horyzontu kończy się `horizon` dni przed wierszem: `add_rolling_mean(df, column, window, lag=horizon)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# if lag < horizon:
#     raise ValueError(f"A lag of {lag} days is not available {horizon} days ahead.")
# ```
#
# </details>

# %%
check("09.2")

# %%
from freshcast.features import lags

try:
    lags.lag_feature(daily, TARGET, 1, horizon=7)
except ValueError as error:
    print("ValueError:", error)

# %% [markdown]
# ## 09.5 Rejestr cech
#
# Cechy zależą od siebie: `dow_sin` potrzebuje `dow`, `same_weekday_mean` potrzebuje czterech lagów. Plik `catalog.py` (gotowy) rejestruje wszystkie cechy kursu razem z listą kolumn, których każda potrzebuje. W `build.py` napisz:
#
# - `resolve_order(names, features, available)`: kolejność liczenia, w której każda cecha idzie po wszystkim, czego potrzebuje. Nieznana nazwa albo cykl zależności to `ValueError`,
# - `build_features(df, names, features)`: liczy cechy w tej kolejności i zwraca nową ramkę.
#
# To jest sortowanie topologiczne grafu. Nie musisz znać nazwy, żeby je napisać.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Zanim policzysz cechę, policz rekurencyjnie wszystko, czego ona wymaga, a nie ma tego ani w ramce, ani na liście już policzonych.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Przejście w głąb (DFS) z dwoma zbiorami: "gotowe" i "w trakcie". Jeśli wchodzisz do cechy, która jest "w trakcie", to znalazłeś cykl.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# order, done, visiting = [], set(available), set()
#
# def visit(name):
#     if name in done:
#         return
#     if name in visiting:
#         raise ValueError(f"Features depend on each other in a cycle through {name!r}.")
#     if name not in features:
#         raise ValueError(f"Unknown feature or column {name!r}.")
#     visiting.add(name)
#     for requirement in features[name].requires:
#         visit(requirement)
#     visiting.discard(name)
#     done.add(name)
#     order.append(name)
# ```
#
# </details>

# %%
check("09.5")

# %%
from freshcast.features import catalog

table = catalog.build_feature_table(daily)
FEATURES = catalog.NUMERIC_FEATURES
print(f"{len(FEATURES)} cech:", FEATURES)
table.to_parquet(paths.PROCESSED_DIR / catalog.FEATURES_FILE, index=False)

# %% [markdown]
# Podział jak w labie 08: test to ostatni tydzień, walidacja tydzień przed nim.

# %%
rest, test = split_by_date(table, last_days_start(table, 7))
train, valid = split_by_date(rest, last_days_start(rest, 7))
in_stock_train = train.loc[train[OOS_HOURS] == 0]
print(f"trening {len(train):,}, w tym bez braków {len(in_stock_train):,}; walidacja {len(valid):,}; test {len(test):,}")

# %% [markdown]
# ## 09.3 Popyt w dni braków towaru
#
# W dzień, w którym produktu zabrakło o 14:00, sprzedaż jest mniejsza niż popyt. Model uczony na takich dniach uczy się, że popyt jest niższy, niż był. Pomysł na korektę: jeśli zwykle 60% sprzedaży dnia przypada na godziny do 14:00, to dzisiejsza sprzedaż to około 60% popytu, więc popyt ≈ sprzedaż / 0.6.
#
# W `demand.py` napisz:
#
# - `hourly_profile(hourly)`: średni udział każdej godziny w sprzedaży dnia, z dni bez braków i z jakąkolwiek sprzedażą,
# - `coverage(hourly, profile)`: dla każdego dnia suma udziałów godzin, w których towar był,
# - `corrected_demand(sales_in_stock, covered, min_coverage=0.2)`: sprzedaż w godzinach z towarem podzielona przez pokrycie, a `NaN`, gdy pokrycie jest za małe, żeby coś z niego wnioskować.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Wszystko to operacje na macierzach (dni, 24): `to_matrix` z modułu 07 i `row_shares` z modułu 05.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Profil: udziały godzin w dniach, które się kwalifikują, uśrednione po dniach. Pokrycie: `np.where(brak_towaru, 0.0, profil)` i suma po godzinach. Profil ma kształt `(24,)`, macierz `(dni, 24)`: broadcasting zrobi resztę.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# enough = covered >= min_coverage
# safe = np.where(enough, covered, 1.0)
# return np.where(enough, sales_in_stock / safe, np.nan)
# ```
#
# </details>

# %%
check("09.3")

# %%
from freshcast.data.hourly import load_hourly, to_matrix
from freshcast.data.schema import HOURLY_SALES, HOURLY_STOCKOUT
from freshcast.features import demand

hourly = load_hourly(paths.FRN_TRAIN, cities=CITIES)
profile = demand.hourly_profile(hourly)
covered = demand.coverage(hourly, profile)

fig, ax = plt.subplots(figsize=(7, 3))
ax.bar(range(24), profile)
ax.set(xlabel="godzina", ylabel="udział w sprzedaży dnia", title="Profil godzinowy dnia bez braków")
plt.show()

# %% [markdown]
# ### Eksperyment 1: symulacja
#
# Czy korekta działa? Sprawdź ją tam, gdzie znasz prawdę: na dniach **bez** braków. Nałóż na każdy taki dzień sztuczny brak od losowej godziny między 10 a 21 do końca dnia. Porównaj z prawdziwą sprzedażą dnia: sprzedaż "ocenzurowaną" (tylko godziny przed brakiem) i skorygowaną.

# %%
# >>> SOLUTION 09.3
sales = to_matrix(hourly[HOURLY_SALES])
out_of_stock = to_matrix(hourly[HOURLY_STOCKOUT]).astype(bool)
full_days = sales[~out_of_stock.any(axis=1) & (sales.sum(axis=1) > 0)]
rng = np.random.default_rng(0)
cut = rng.integers(10, 22, size=len(full_days))
simulated_stockout = np.arange(24)[None, :] >= cut[:, None]
censored = np.where(simulated_stockout, 0.0, full_days).sum(axis=1)
simulated_coverage = np.where(simulated_stockout, 0.0, profile).sum(axis=1)
estimate = demand.corrected_demand(censored, simulated_coverage)
truth = full_days.sum(axis=1)
known = ~np.isnan(estimate)
censored_bias = censored.sum() / truth.sum() - 1
corrected_bias = estimate[known].sum() / truth[known].sum() - 1
# --- STUB
#| censored_bias = ...
#| corrected_bias = ...
# <<< SOLUTION
print(f"Bias sprzedaży ocenzurowanej: {censored_bias:+.1%}, po korekcie: {corrected_bias:+.1%}")

# %% [markdown]
# ### Eksperyment 2: prawdziwe dane
#
# Korekta usuwa obciążenie w symulacji. Teraz trzy sposoby uczenia modelu na prawdziwych danych, każdy oceniony na dniach walidacji bez braków:
#
# 1. cel to sprzedaż, wszystkie dni,
# 2. cel to sprzedaż, tylko dni bez braków,
# 3. cel to popyt skorygowany, wszystkie dni, na których korekta istnieje.

# %%
# >>> SOLUTION 09.3
corrected = pd.Series(demand.corrected_demand(daily[SALES_IN_STOCK].to_numpy(), covered), index=table.index)
train_corrected = train.assign(corrected=corrected).dropna(subset=["corrected"])
targets = {
    "sprzedaż, wszystkie dni": (train, train[TARGET]),
    "sprzedaż, dni bez braków": (in_stock_train, in_stock_train[TARGET]),
    "popyt skorygowany": (train_corrected, train_corrected["corrected"]),
}
target_results = pd.DataFrame(
    {name: evaluate(quick_model(rows, target, FEATURES), valid, FEATURES) for name, (rows, target) in targets.items()}
).T[["wape_in_stock", "bias_in_stock", "wape"]]
# --- STUB
#| target_results = ...
# <<< SOLUTION
target_results.round(3)

# %% [markdown]
# Korekta, która działała w symulacji, na prawdziwych danych zawyża prognozy. Co symulacja założyła o brakach, czego prawdziwe braki nie spełniają? Podpowiedź: w module 07 policzyłeś, kiedy produkty wyprzedają się najczęściej.
#
# *Twoja odpowiedź:*
#
# Od tej pory kurs uczy modele na dniach bez braków. Prostsze rozwiązanie wygrało w pomiarze.

# %% [markdown]
# ## 09.4 Kodowanie średnią celu
#
# `store_id` i `product_id` to liczby, ale nie wielkości: sklep 300 nie jest "większy" od sklepu 200. Jeden ze sposobów, żeby model mógł ich użyć, to **target encoding**: zamień grupę (na przykład seria i dzień tygodnia) na średnią celu w tej grupie.
#
# Napisz `TargetEncoder` w `encoding.py`: `fit(X, y)` zapamiętuje średnią celu w każdej grupie kolumn `columns`, `transform(X)` zwraca ją dla każdego wiersza. Grupa nieznana z `fit` dostaje średnią ogólną. `smoothing` ściąga małe grupy w stronę średniej ogólnej.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `fit` to `groupby(columns)` na celu z `agg(["mean", "count"])`. `transform` to `merge` z wierszami `X` po tych kolumnach, z zachowaniem indeksu `X`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Wygładzona średnia grupy: `(n * średnia_grupy + smoothing * średnia_ogólna) / (n + smoothing)`. Przy `merge` indeks ramki się gubi: zapamiętaj go i ustaw z powrotem. Braki po złączeniu to nieznane grupy: `fillna(średnia_ogólna)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# stats = y.groupby([X[c] for c in self.columns]).agg(["mean", "count"])
# self._overall = float(y.mean())
# smoothed = (stats["count"] * stats["mean"] + self.smoothing * self._overall) / (stats["count"] + self.smoothing)
# self._encoding = smoothed.rename(self.name).reset_index()
# ```
#
# </details>

# %%
check("09.4")

# %% [markdown]
# ### Eksperyment 3: kodowanie serii i dnia tygodnia
#
# Kolega dodaje cechę: średnia sprzedaż serii w danym dniu tygodnia, dopasowaną "na wszystkich danych, które mamy", czyli na treningu i walidacji. Wynik na walidacji się poprawia. Porównaj trzy warianty. Wyjątkowo patrzysz też na test, żeby zobaczyć skutek decyzji. W prawdziwej pracy tej informacji byś nie miał.

# %%
from freshcast.features.encoding import TargetEncoder

GROUP = [*SERIES_KEY, "dow"]
in_stock_rest = rest.loc[rest[OOS_HOURS] == 0]

# >>> SOLUTION 09.4
def encoded(encoder, frame):
    """Add the encoded column as the feature ``te``."""
    return frame.assign(te=encoder.transform(frame))


variants = {"bez kodowania": None, "kodowanie: trening": in_stock_train, "kodowanie: trening + walidacja": in_stock_rest}
encoding_results = {}
for name, encoder_rows in variants.items():
    if encoder_rows is None:
        features, prepare = FEATURES, lambda frame: frame
    else:
        encoder = TargetEncoder(GROUP).fit(encoder_rows, encoder_rows[TARGET])
        features, prepare = [*FEATURES, "te"], (lambda frame, e=encoder: encoded(e, frame))
    model = quick_model(prepare(in_stock_train), in_stock_train[TARGET], features)
    encoding_results[name] = {
        "walidacja": evaluate(model, prepare(valid), features)["wape_in_stock"],
        "test": evaluate(model, prepare(test), features)["wape_in_stock"],
    }
# --- STUB
#| encoding_results = ...
# <<< SOLUTION
pd.DataFrame(encoding_results).T.round(3)

# %% [markdown]
# ## 09.6 Pytania
#
# Bez sprawdzeń. Odpowiedz krótko.
#
# 1. Wariant "trening + walidacja" wygrywa na walidacji i przegrywa na teście. Co dokładnie przeciekło? Która reguła z `docs/standard.md` to opisuje?
# 2. Wariant "trening" jest uczciwy wobec walidacji, a i tak pogarsza wynik względem modelu bez kodowania. Dlaczego? Pomyśl, co zawiera zakodowana wartość wiersza treningowego.
# 3. Symulacja braków pokazała, że korekta działa. Prawdziwe dane pokazały, że zawyża. Czego uczy to o sprawdzaniu metody w symulacji?
# 4. Cechy są czystymi funkcjami zarejestrowanymi z listą wymagań. Co to daje, gdy w module 14 te same cechy trzeba policzyć dla przyszłego tygodnia w pipeline'ie?
#
# *Twoje odpowiedzi:*
