# %% [markdown]
# # Lab 05: NumPy na prawdziwym panelu sprzedaży
#
# Od tego labu pracujesz na FreshRetailNet: dzienna sprzedaż świeżych produktów w sklepach jednego miasta, 90 dni. Każdy wiersz pliku to jedna seria (sklep i produkt) w jednym dniu, z 24 godzinowymi wartościami sprzedaży i stanu magazynu.
#
# W tym labie nie używasz jeszcze pandas. Czytasz kolumny prosto do tablic NumPy i liczysz na całych tablicach naraz: układasz dane w macierz, prognozujesz wszystkie serie jednym wyrażeniem i oceniasz prognozy metrykami, które napiszesz w pakiecie. Te metryki ocenią każdy model do końca kursu.
#
# **Czas:** około 5 godzin.
#
# | Zadanie | Gdzie | Czas |
# |---|---|---|
# | 05.6 | `to_matrix` w notebooku | 45 min |
# | 05.1-05.3 | `prepare`, `mae`, `rmse`, `wape`, `bias` w `src/freshcast/metrics.py` | 75 min |
# | 05.7 | `seasonal_naive` w notebooku | 30 min |
# | 05.4 | `row_shares` w `src/freshcast/numeric.py` | 30 min |
# | 05.5 | Testy w `tests/test_metrics.py` | 60 min |
# | 05.8 | Eksploracja | 30 min |

# %%
import time

import numpy as np
import pyarrow.parquet as pq

from coursekit import paths
from coursekit.nb import check

# The full profile is for modules 14 and 19; labs work on one city.
CITIES = paths.active_profile().cities or paths.PROFILES["standard"].cities
print("Miasta:", CITIES)

# %% [markdown]
# ## Dane jako tablice
#
# `pyarrow` czyta plik Parquet kolumna po kolumnie. `filters` wybiera wiersze jeszcze przy czytaniu, więc reszta pliku nie trafia do pamięci. Kod wczytania jest gotowy: przeczytaj go, zanim uruchomisz.

# %%
COLUMNS = ["store_id", "product_id", "dt", "sale_amount", "stock_hour6_22_cnt", "hours_sale"]
table = pq.read_table(paths.FRN_TRAIN, columns=COLUMNS, filters=[("city_id", "in", list(CITIES))])

store = table.column("store_id").to_numpy()
product = table.column("product_id").to_numpy()
sale = table.column("sale_amount").to_numpy()
stockout_hours = table.column("stock_hour6_22_cnt").to_numpy()
# Each cell of hours_sale is a list of 24 numbers; np.stack makes one (rows, 24) array.
hours = np.stack(table.column("hours_sale").to_numpy(zero_copy_only=False))

# A series is one product in one store. Products are numbered below 1000.
ids = store * 1000 + product
dates, day = np.unique(table.column("dt").to_numpy(zero_copy_only=False), return_inverse=True)

for name, array in [("ids", ids), ("day", day), ("sale", sale), ("hours", hours)]:
    print(f"{name:>6}: shape {array.shape}, dtype {array.dtype}, {array.nbytes / 1e6:.1f} MB")
print(f"Dni: {dates[0]} .. {dates[-1]} ({len(dates)})")

# %% [markdown]
# `np.unique(..., return_inverse=True)` zwraca posortowane unikalne daty i dla każdego wiersza numer jego daty na tej liście. Tekst zamienił się w liczby 0-89, na których da się liczyć.
#
# ### Pułapka: równość liczb zmiennoprzecinkowych
#
# `sale_amount` to suma sprzedaży z 24 godzin. Sprawdź to:

# %%
exact = (hours.sum(axis=1) == sale).mean()
close = np.isclose(hours.sum(axis=1), sale).mean()
print(f"Równe dokładnie: {exact:.1%}, równe z tolerancją: {close:.1%}")

# %% [markdown]
# Co czwarty wiersz "nie zgadza się" na piętnastym miejscu po przecinku. Suma 24 liczb zmiennoprzecinkowych zależy od kolejności dodawania, a plik liczył ją inaczej niż NumPy. Liczby zmiennoprzecinkowe porównujesz z tolerancją: `np.isclose`, `np.allclose`, w testach `pytest.approx`.

# %% [markdown]
# ## 05.6 Z długiej tabeli do macierzy
#
# Dane są "długie": jeden wiersz na serię i dzień, w przypadkowej kolejności. Do liczenia po seriach wygodniejsza jest macierz: wiersz to seria, kolumna to dzień.
#
# Napisz `to_matrix(ids, days, values, n_days)`, która zwraca parę:
#
# - posortowane rosnąco identyfikatory serii,
# - macierz `(liczba serii, n_days)`, w której `matrix[i, d]` to wartość serii `i` w dniu `d`.
#
# Jeśli któraś seria nie ma każdego dnia dokładnie raz albo tablice mają różne długości, `ValueError`. Bez pętli po wierszach.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Gdy posortujesz wiersze po serii, a w serii po dniu, wartości leżą w kolejności wiersz po wierszu macierzy. Wtedy wystarczy `reshape`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `np.lexsort((days, ids))` zwraca kolejność sortowania po `ids`, a przy remisie po `days` (ostatni klucz jest najważniejszy). `np.unique(..., return_counts=True)` powie, ile wierszy ma każda seria. Poprawne dni po sortowaniu to `0, 1, ..., n_days - 1` powtórzone dla każdej serii: `np.tile(np.arange(n_days), liczba_serii)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# order = np.lexsort((days, ids))
# series, counts = np.unique(ids[order], return_counts=True)
# if not np.array_equal(days[order], np.tile(np.arange(n_days), len(series))):
#     raise ValueError(...)
# return series, values[order].reshape(len(series), n_days)
# ```
#
# </details>

# %%
def to_matrix(ids, days, values, n_days):
    """Arrange a long table into a (series, day) matrix; see the task for the rules."""
    # >>> SOLUTION 05.6
    if not len(ids) == len(days) == len(values):
        raise ValueError(f"Lengths differ: {len(ids)}, {len(days)}, {len(values)}.")
    order = np.lexsort((days, ids))
    series = np.unique(ids[order])
    expected_days = np.tile(np.arange(n_days), len(series))
    if not np.array_equal(days[order], expected_days):
        raise ValueError(f"Some series do not have each of the {n_days} days exactly once.")
    return series, values[order].reshape(len(series), n_days)
    # <<< SOLUTION


check("05.6", to_matrix)

# %%
# >>> SOLUTION 05.6
series, sales = to_matrix(ids, day, sale, len(dates))
_, stockouts = to_matrix(ids, day, stockout_hours, len(dates))
# --- STUB
#| series, sales = ...
#| _, stockouts = ...
# <<< SOLUTION
print(sales.shape, stockouts.shape)

# %% [markdown]
# ## 05.1-05.3 Metryki w pakiecie
#
# Otwórz `src/freshcast/metrics.py`. Każda z czterech metryk najpierw woła `prepare`, które sprawdza wejścia i stosuje maskę. Napisz po kolei:
#
# - **05.1** `prepare`: zamienia wejścia na płaskie tablice `float64`, sprawdza kształty, stosuje maskę, zgłasza `ValueError` przy różnych kształtach, braku wartości po maskowaniu i przy `NaN`,
# - **05.2** `mae` i `rmse`,
# - **05.3** `wape` i `bias`: obie dzielą przez sumę wartości rzeczywistych, więc gdy ta suma wynosi zero, `ValueError`.
#
# Docstringi w pliku mówią dokładnie, co każda funkcja ma robić. Wzory są w wykładzie.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `np.asarray(x, dtype=np.float64).ravel()` robi płaską tablicę z listy, tablicy 2-D albo kolumny. Maskę zamieniasz na tablicę `bool` i indeksujesz nią obie tablice.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Kolejność sprawdzeń w `prepare` ma znaczenie: najpierw kształty, potem maska, potem pustość, na końcu `NaN`, ale tylko w wierszach, które zostały. `NaN` w wierszu wyciętym przez maskę nie przeszkadza. `np.isnan(a).sum()` liczy braki.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# a, p = prepare(actual, predicted, mask)
# total = float(np.abs(a).sum())
# if total == 0:
#     raise ValueError(...)
# return float(np.abs(a - p).sum() / total)
# ```
#
# </details>

# %%
check("05.1")
check("05.2")
check("05.3")

# %% [markdown]
# ## 05.7 Prognoza dla wszystkich serii naraz
#
# W labie 04 `SeasonalNaiveForecaster` prognozuje jedną serię. Na macierzy ta sama prognoza to jedno wyrażenie dla wszystkich serii.
#
# Napisz `seasonal_naive(history, horizon, season=7)`: dla każdego wiersza macierzy `history` zwraca `horizon` kolejnych wartości, powtarzając ostatnie `season` kolumn, tak jak klasa z labu 04. Wynik ma kształt `(liczba wierszy, horizon)`. Horyzont mniejszy od 1 albo historia krótsza niż sezon to `ValueError`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Ostatni sezon wszystkich serii to jeden wycinek: `history[:, -season:]`. Zostaje go powtórzyć w poziomie i obciąć do `horizon` kolumn.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `np.tile(a, (1, k))` powtarza kolumny `k` razy. Ile razy trzeba, żeby było co najmniej `horizon` kolumn? Alternatywa: tablica indeksów kolumn `np.arange(horizon) % season` użyta do indeksowania ostatniego sezonu.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# last_season = history[:, -season:]
# return last_season[:, np.arange(horizon) % season]
# ```
#
# </details>

# %%
def seasonal_naive(history, horizon, season=7):
    """Repeat the last `season` columns of every row for `horizon` steps."""
    # >>> SOLUTION 05.7
    if horizon < 1:
        raise ValueError(f"horizon must be at least 1, got {horizon}.")
    if history.shape[1] < season:
        raise ValueError(f"History of {history.shape[1]} columns is shorter than {season}.")
    return history[:, -season:][:, np.arange(horizon) % season]
    # <<< SOLUTION


check("05.7", seasonal_naive)

# %% [markdown]
# Porównaj czas z klasą z labu 04, która prognozuje serię po serii w pętli:

# %%
from freshcast.models.local import SeasonalNaiveForecaster

HORIZON = 7
history, actual = sales[:, :-HORIZON], sales[:, -HORIZON:]

start = time.perf_counter()
looped = np.array([SeasonalNaiveForecaster(7).fit(row).predict(HORIZON) for row in history])
loop_seconds = time.perf_counter() - start

start = time.perf_counter()
vectorised = seasonal_naive(history, HORIZON)
vector_seconds = time.perf_counter() - start

print(f"Pętla: {loop_seconds * 1000:.1f} ms, tablica: {vector_seconds * 1000:.3f} ms")
print("Te same prognozy:", np.array_equal(looped, vectorised))

# %% [markdown]
# ## Ocena ostatniego tygodnia
#
# Ostatnie 7 dni to okres testowy. Trzy proste prognozy:
#
# - sezonowa: to, co tydzień wcześniej,
# - naiwna: ostatni dzień historii na każdy dzień tygodnia,
# - średnia z ostatnich 7 dni.
#
# Dzień, w którym produktu przez część dnia brakowało na półce, pokazuje sprzedaż mniejszą niż popyt. Oceniasz więc dwa razy: na wszystkich dniach i tylko na dniach bez braków (`stockouts == 0`), podając maskę do metryk.

# %%
from freshcast import metrics

# >>> SOLUTION 05.3
forecasts = {
    "sezonowa": vectorised,
    "naiwna": np.repeat(history[:, -1:], HORIZON, axis=1),
    "średnia 7 dni": np.repeat(history[:, -7:].mean(axis=1, keepdims=True), HORIZON, axis=1),
}
in_stock = stockouts[:, -HORIZON:] == 0
# --- STUB
#| forecasts = ...
#| in_stock = ...
# <<< SOLUTION
print(f"Dni bez braków w tygodniu testowym: {in_stock.mean():.1%}")
for name, forecast in forecasts.items():
    print(
        f"{name:>14}: WAPE {metrics.wape(actual, forecast):.3f} wszystkie dni, "
        f"{metrics.wape(actual, forecast, in_stock):.3f} bez braków; "
        f"bias {metrics.bias(actual, forecast, in_stock):+.3f}"
    )

# %% [markdown]
# ## 05.4 Profil godzinowy
#
# Wiersz `hours` to sprzedaż w 24 godzinach jednego dnia. Żeby porównać kształt dnia między seriami o różnej skali, dzielisz każdy wiersz przez jego sumę: wtedy wartości to udziały godzin w sprzedaży dnia.
#
# Napisz `row_shares` w `src/freshcast/numeric.py` według docstringu. Wiersz samych zer nie ma profilu i ma dać `NaN`, a nie zera ani nieskończoności.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Sumy wierszy to `matrix.sum(axis=1)`. Żeby podzielić przez nie macierz, potrzebujesz kształtu `(n, 1)`, a nie `(n,)`: wtedy broadcasting dopasuje kolumnę sum do każdej kolumny macierzy.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `keepdims=True` zostawia wymiar sumy. Zanim podzielisz, zamień zerowe sumy na `np.nan` przez `np.where`. Wtedy dzielenie da `NaN` zamiast ostrzeżenia i `inf`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# totals = matrix.sum(axis=1, keepdims=True)
# safe_totals = np.where(totals == 0, np.nan, totals)
# return matrix / safe_totals
# ```
#
# </details>

# %%
check("05.4")

# %%
from freshcast.numeric import row_shares

# >>> SOLUTION 05.4
profiles = row_shares(hours)
no_profile = np.isnan(profiles[:, 0])
mean_profile = np.nanmean(profiles, axis=0)
# --- STUB
#| profiles = ...
#| no_profile = ...
#| mean_profile = ...
# <<< SOLUTION
print(f"Dni bez sprzedaży (bez profilu): {no_profile.mean():.1%}")
print("Średni udział godzin:", np.round(mean_profile, 3))
print("Godzina szczytu:", int(np.argmax(mean_profile)))

# %% [markdown]
# ## 05.5 Testy metryk
#
# Jak w labie 04: w `tests/test_metrics.py` jest jeden test na wzór. Dopisz co najmniej sześć. Sprawdzenie podmieni metryki na siedem zepsutych wersji i powie, których Twoje testy nie wykryły.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Każdy błąd na liście wymaga danych, na których zepsuta metryka da inny wynik niż poprawna. Na przykład MAE i RMSE są równe, gdy wszystkie błędy mają ten sam rozmiar.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Średnia z procentów po wierszach różni się od WAPE, gdy wiersze mają różną skalę. Znak biasu sprawdzisz prognozą wyraźnie za wysoką. Maskę sprawdzisz danymi, w których wycięty wiersz zmieniłby wynik. `NaN` i różne kształty to `pytest.raises(ValueError, match=...)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# def test_wape_is_total_miss_over_total_actual() -> None:
#     actual = np.array([1.0, 100.0])
#     predicted = np.array([2.0, 100.0])
#
#     assert wape(actual, predicted) == pytest.approx(1.0 / 101.0)
# ```
#
# </details>

# %%
# !cd ../.. && uv run pytest tests/test_metrics.py -q

# %%
check("05.5")

# %% [markdown]
# ## 05.8 Eksploracja
#
# Bez sprawdzeń. Odpowiedz jednym, dwoma zdaniami.
#
# 1. Dlaczego każda prognoza ma mniejszy WAPE na dniach bez braków niż na wszystkich dniach?
# 2. Średnia z 7 dni wygrała z prognozą sezonową w tym jednym tygodniu. Czy to wystarczy, żeby wybrać ją jako baseline na resztę kursu? Czego brakuje?
# 3. Co by wyszło z `profiles.mean(axis=0)` zamiast `np.nanmean`? Dlaczego?
#
# *Twoje odpowiedzi:*
