# %% [markdown]
# # Lab 05: NumPy na prawdziwym panelu sprzedaży
#
# Od tego labu pracujesz na FreshRetailNet: dzienna sprzedaż świeżych produktów w sklepach jednego miasta, 90 dni. Każdy wiersz pliku to jedna seria (sklep i produkt) w jednym dniu, z 24 godzinowymi wartościami sprzedaży i liczbą godzin, w których produktu brakowało na półce.
#
# W tym labie nie używasz jeszcze pandas. Czytasz kolumny prosto do tablic NumPy i liczysz na całych tablicach naraz: układasz dane w macierz, prognozujesz wszystkie serie jednym wyrażeniem i oceniasz prognozy metrykami, które napiszesz w pakiecie. Te metryki ocenią każdy model do końca kursu.
#
# **Czas:** około 5 godzin.
#
# Zadania idą w kolejności notebooka. Duże zadania mają kroki (a, b): pierwszy krok to funkcja, drugi to jej użycie na prawdziwych danych w notebooku.
#
# | Zadanie | Gdzie | Czas |
# |---|---|---|
# | 05.6a | funkcja `to_matrix` w notebooku | 35 min |
# | 05.6b | zmienne `series`, `sales`, `stockouts` w notebooku | 10 min |
# | 05.1 | `prepare` w `src/freshcast/metrics.py` | 35 min |
# | 05.2 | `mae`, `rmse` w `src/freshcast/metrics.py` | 15 min |
# | 05.3a | `wape`, `bias` w `src/freshcast/metrics.py` | 25 min |
# | 05.7 | funkcja `seasonal_naive` w notebooku | 30 min |
# | 05.3b | zmienne `forecasts`, `in_stock` w notebooku | 15 min |
# | 05.4a | `row_shares` w `src/freshcast/numeric.py` | 20 min |
# | 05.4b | zmienne `profiles`, `no_profile`, `mean_profile` w notebooku | 10 min |
# | 05.5 | testy w `tests/test_metrics.py` | 60 min |
# | 05.8 | eksploracja: trzy pytania | 30 min |
#
# Jak pracujesz:
#
# - Zadania w notebooku piszesz w komórce z `...` albo z `raise NotImplementedError`. Sprawdzenie przekazuje Twoją funkcję do `check`: `check("05.6", to_matrix)`, nazwa funkcji bez nawiasów.
# - Zadania w pakiecie piszesz w pliku w edytorze, w miejscu `raise NotImplementedError("Zadanie 05.x")`. Zmienne i importy notebooka nie istnieją w plikach pakietu: czego potrzebujesz w pliku, importujesz na jego górze. Komórka `check("05.x")` w notebooku albo `uv run course check 05.x` w terminalu sprawdza to, co jest zapisane w pliku.
# - Docstring funkcji to dokładna umowa: co przyjmuje, co zwraca, kiedy zgłasza błąd. Tekst w notebooku mówi to samo prostszymi słowami.

# %%
# %load_ext autoreload
# %autoreload 2

import time

import numpy as np
import pyarrow.parquet as pq

from coursekit import paths
from coursekit.nb import check

# The full profile is for modules 14 and 19; labs work on one city.
CITIES = paths.active_profile().cities or paths.PROFILES["standard"].cities
print("Miasta:", CITIES)

# %% [markdown]
# `autoreload` sprawia, że notebook widzi zmiany, które zapisujesz w plikach pakietu, bez restartu kernela.
#
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
# Po tej komórce masz tablice, z których korzysta cały lab. Wszystkie jednowymiarowe mają tę samą długość: jeden element na wiersz pliku, czyli na jedną serię w jednym dniu, w kolejności pliku.
#
# | Zmienna | Kształt i typ | Co znaczy |
# |---|---|---|
# | `ids` | `(wiersze,)`, `int64` | identyfikator serii: `store_id * 1000 + product_id` |
# | `day` | `(wiersze,)`, `int64` | numer dnia od 0 do 89; 0 to pierwsza data w `dates` |
# | `dates` | `(90,)`, napisy (`object`) | daty w kolejności numerów dni |
# | `sale` | `(wiersze,)`, `float64` | sprzedaż serii w tym dniu (`sale_amount`) |
# | `stockout_hours` | `(wiersze,)`, `int32` | ile godzin między 6:00 a 22:00 produktu brakowało na półce, od 0 do 16 |
# | `hours` | `(wiersze, 24)`, `float64` | sprzedaż w każdej z 24 godzin tego dnia |
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
# Dane są "długie": jeden wiersz na serię i dzień, w przypadkowej kolejności. Do liczenia po seriach wygodniejsza jest macierz: wiersz to seria, kolumna to dzień. Z taką macierzą prognoza dla wszystkich serii (05.7) i ocena tygodnia testowego (05.3b) to po jednym wyrażeniu.
#
# ### 05.6a Funkcja `to_matrix`
#
# **Cel:** zamienić trzy równoległe tablice (seria, dzień, wartość) w macierz (serie, dni), bez pętli po wierszach.
#
# **Gdzie:** funkcja `to_matrix` w komórce kodu pod podpowiedziami. Zastępujesz linię `raise NotImplementedError("Zadanie 05.6")`. Nazwy i kolejności argumentów nie zmieniasz.
#
# **Wejście:**
#
# - `ids`: `np.ndarray` liczb całkowitych, kształt `(wiersze,)`. Identyfikator serii każdego wiersza. W labie przekażesz `ids`.
# - `days`: `np.ndarray` liczb całkowitych, kształt `(wiersze,)`. Numer dnia każdego wiersza, od 0 do `n_days - 1`. W labie `day`.
# - `values`: `np.ndarray`, kształt `(wiersze,)`. Wartość, którą chcesz ułożyć w macierz. W labie najpierw `sale`, potem `stockout_hours`.
# - `n_days`: `int`. Ile dni ma każda seria. W labie `len(dates)`, czyli 90.
#
# Wiersz numer `k` trzech tablic opisuje jedno zdarzenie: seria `ids[k]` w dniu `days[k]` miała wartość `values[k]`.
#
# **Wynik:** krotka `(series, matrix)`:
#
# - `series`: `np.ndarray` jednowymiarowa, każdy identyfikator serii raz, rosnąco,
# - `matrix`: `np.ndarray` o kształcie `(len(series), n_days)` i typie jak `values`. `matrix[i, d]` to wartość serii `series[i]` w dniu `d`.
#
# Tablice wejściowe zostają bez zmian. `ValueError`, gdy trzy tablice mają różne długości albo gdy któraś seria nie ma każdego dnia od 0 do `n_days - 1` dokładnie raz (brakuje dnia albo dzień jest dwa razy).
#
# **Skorzystaj z:** sortowania i powtarzania tablic z wykładu (sekcja "Sortowanie i powtarzanie"): `np.lexsort`, `np.unique`, `np.arange`, `np.tile`, `np.array_equal`, `reshape`.
#
# **Kroki:**
#
# 1. Porównaj długości trzech tablic. Jeśli się różnią, zgłoś `ValueError` z tymi długościami w komunikacie.
# 2. Wyznacz kolejność wierszy: najpierw według serii, w obrębie serii według dnia. `np.lexsort` przyjmuje krotkę kluczy, sortuje według ostatniego klucza, a remisy rozstrzyga poprzednim. Zwraca numery wierszy w nowej kolejności, nie same wartości.
# 3. Wyznacz listę serii. `np.unique` zwraca każdą wartość raz, rosnąco. Jej długość to liczba wierszy macierzy.
# 4. Sprawdź dni. W poprawnych danych po posortowaniu dni każdej serii idą 0, 1, ..., `n_days - 1`, seria po serii. Zbuduj taki oczekiwany ciąg (`np.arange` daje jeden blok, `np.tile` powtarza go dla każdej serii) i porównaj z posortowanymi dniami przez `np.array_equal`. Różnica oznacza brak albo powtórzenie dnia: `ValueError`. Samo liczenie wierszy na serię tego nie wykryje, bo seria z podwójnym dniem i brakującym dniem ma poprawną liczbę wierszy.
# 5. Ułóż wartości w posortowanej kolejności i zmień ich kształt przez `reshape` na `(liczba serii, n_days)`. Indeksowanie tablicą numerów wierszy daje kopię, więc `values` się nie zmieni.
#
# **Sprawdzenie:** komórka z `check("05.6", to_matrix)` przekazuje do sprawdzenia samą funkcję (bez nawiasów). Sprawdzenie woła ją na małym przykładzie: dwie serie, trzy dni, wiersze pomieszane, oraz na danych z brakującym i z podwójnym dniem. Zaliczone zadanie wypisuje `✅ 05.6`.
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
    """Arrange a long table into a (series, day) matrix.

    Row ``k`` of the three input arrays says: series ``ids[k]`` had the value
    ``values[k]`` on day ``days[k]``. The rows come in any order.

    Args:
        ids: 1-D integer array, the series id of every row.
        days: 1-D integer array of the same length, the day number of every
            row, from 0 to ``n_days - 1``.
        values: 1-D array of the same length, the value of every row.
        n_days: Number of days every series must have.

    Returns:
        A pair ``(series, matrix)``. ``series`` holds every distinct id once,
        in ascending order. ``matrix`` has the shape
        ``(len(series), n_days)`` and the dtype of ``values``;
        ``matrix[i, d]`` is the value of series ``series[i]`` on day ``d``.
        The inputs are not changed.

    Raises:
        ValueError: The three arrays differ in length, or a series does not
            have each day from 0 to ``n_days - 1`` exactly once.
    """
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

# %% [markdown]
# ### 05.6b Macierze sprzedaży i braków
#
# **Cel:** mieć sprzedaż i godziny braków wszystkich serii jako dwie macierze o tych samych wierszach i kolumnach. Na nich pracują 05.7 i 05.3b.
#
# **Gdzie:** komórka pod tym tekstem. Zastępujesz `...` w dwóch liniach, nazwy zmiennych zostają.
#
# **Wejście:** tablice z sekcji "Dane jako tablice": `ids`, `day`, `sale`, `stockout_hours`, `dates`.
#
# **Wynik:**
#
# - `series`: `np.ndarray` identyfikatorów serii, rosnąco,
# - `sales`: `np.ndarray` o kształcie `(liczba serii, 90)`, `float64`: sprzedaż serii w każdym dniu,
# - `stockouts`: `np.ndarray` o tym samym kształcie: liczba godzin bez towaru na półce, od 0 do 16.
#
# Wiersz `i` obu macierzy to ta sama seria `series[i]`. `_` w drugiej linii to zmienna, której nie używasz: identyfikatory serii wyjdą te same co w pierwszej.
#
# **Skorzystaj z:** `to_matrix` z 05.6a, dwa wywołania.
#
# **Sprawdzenie:** komórka wypisuje kształty obu macierzy, a następna sprawdza je asercjami i wypisuje `Zgadza się.`

# %%
# >>> SOLUTION 05.6
series, sales = to_matrix(ids, day, sale, len(dates))
_, stockouts = to_matrix(ids, day, stockout_hours, len(dates))
# --- STUB
#| series, sales = ...
#| _, stockouts = ...
# <<< SOLUTION
print(sales.shape, stockouts.shape)

# %%
assert sales.shape == (len(series), len(dates)), "sales ma mieć kształt (liczba serii, liczba dni)."
assert stockouts.shape == sales.shape, "stockouts ma mieć ten sam kształt co sales."
assert bool((np.diff(series) > 0).all()), "series ma być rosnąca, każda seria raz."
assert np.isclose(sales.sum(), sale.sum()), "Suma macierzy różni się od sumy sale: zgubiłeś albo zdublowałeś wiersze."
print("Zgadza się.")

# %% [markdown]
# ## 05.1-05.3 Metryki w pakiecie
#
# Otwórz `src/freshcast/metrics.py`. Plik ma pięć funkcji. Cztery metryki (`mae`, `rmse`, `wape`, `bias`) oceniają prognozę jedną liczbą. Każda z nich na początku woła `prepare`, które sprawdza wejścia i stosuje maskę. Dzięki temu reguły walidacji są w jednym miejscu. Wzory metryk są w wykładzie, w sekcji "Metryki błędu prognozy".
#
# W labie metryki dostaną dwie macierze `(liczba serii, 7)`: rzeczywistą sprzedaż tygodnia testowego i prognozę, a czasem maskę dni bez braków. Od modułu 08 dostaną kolumny ramek pandas. Dlatego przyjmują wszystko, co da się zamienić na tablicę.
#
# ### 05.1 `prepare`
#
# **Cel:** jedna funkcja, która zamienia wejścia metryki na dwie płaskie tablice liczb i odrzuca złe dane, zanim jakakolwiek metryka coś policzy.
#
# **Gdzie:** `src/freshcast/metrics.py`, funkcja `prepare`. Zastępujesz `raise NotImplementedError("Zadanie 05.1")`.
#
# **Wejście:**
#
# - `actual`: `ArrayLike`, czyli lista liczb, tablica 1-D albo 2-D. Wartości rzeczywiste, na przykład sprzedaż w tygodniu testowym.
# - `predicted`: `ArrayLike` o tym samym kształcie. Prognozy tych samych wartości, element w element.
# - `mask`: `ArrayLike` wartości logicznych o tym samym kształcie albo `None`. `True` znaczy "ten element bierze udział w ocenie". W labie to `in_stock`: dni bez braków towaru. `None` znaczy "wszystkie".
#
# **Wynik:** krotka dwóch tablic `np.ndarray` typu `float64`, jednowymiarowych, tej samej długości: najpierw `actual`, potem `predicted`. Zostają tylko elementy z `True` w masce, w tej samej kolejności. Maska ma jeden element na każdą ocenianą wartość: dla macierzy (serie, dni) wybiera pojedyncze komórki, a nie całe serie.
#
# `ValueError`, gdy:
#
# - `actual` i `predicted` mają po spłaszczeniu różną długość,
# - maska ma po spłaszczeniu inną długość niż dane,
# - po zastosowaniu maski nie zostaje żaden element,
# - wśród elementów, które zostały, jest `NaN`. `NaN` w elemencie odrzuconym przez maskę nie jest błędem.
#
# **Skorzystaj z:** `np.asarray(x, dtype=...)` (zamienia listę albo tablicę na tablicę danego typu), `.ravel()` (spłaszcza do 1-D), maski z wykładu (sekcja "Maski i np.where"), `np.isnan` (sekcja "NaN i typy liczbowe").
#
# **Kroki:**
#
# 1. Zamień `actual` i `predicted` na płaskie tablice `float64`.
# 2. Porównaj ich kształty po spłaszczeniu, czyli liczbę elementów. Różne: `ValueError`. Sprawdzenie nie odróżni macierzy (2, 3) od (3, 2), więc pilnujesz sam, żeby prognoza miała ten sam układ co dane.
# 3. Jeśli jest maska, zamień ją na płaską tablicę `bool`, porównaj jej kształt z danymi i wybierz nią elementy z obu tablic.
# 4. Sprawdź, czy coś zostało.
# 5. Policz `NaN` w tym, co zostało. Kolejność kroków 3 i 5 ma znaczenie: braki sprawdzasz dopiero po masce.
#
# **Sprawdzenie:** `check("05.1")` w komórce pod 05.3a albo `uv run course check 05.1` w terminalu. Sprawdzenie woła `prepare` na krótkich listach, z maską i bez, oraz na każdym przypadku błędu z listy.
#
# ### 05.2 `mae` i `rmse`
#
# **Cel:** dwie metryki w sztukach: średni rozmiar pomyłki (MAE) i wersja, w której duże pomyłki ważą więcej (RMSE).
#
# **Gdzie:** `src/freshcast/metrics.py`, funkcje `mae` i `rmse`.
#
# **Wejście:** `actual`, `predicted`, `mask`, tak samo jak w `prepare`.
#
# **Wynik:** `float`, zwykła liczba Pythona (nie `np.float64`), w jednostkach danych, czyli w sztukach sprzedaży. Błędy jak w `prepare`.
#
# **Skorzystaj z:** `prepare` z 05.1, w tym samym pliku, wołasz je bezpośrednio. Wzory z tabeli w wykładzie. `np.abs`, `np.square`, `np.sqrt`, `.mean()`.
#
# **Kroki:**
#
# 1. Wywołaj `prepare` i odbierz dwie tablice.
# 2. Policz różnice element po elemencie, potem wzór metryki.
# 3. Zamień wynik na `float` przed `return`.
#
# **Sprawdzenie:** `check("05.2")` albo `uv run course check 05.2`. Dla błędów `[0, 0, 0, 4]` MAE wynosi 1.0, a RMSE 2.0.
#
# ### 05.3a `wape` i `bias`
#
# **Cel:** dwie metryki, którymi kurs wybiera modele. WAPE mówi, jaka część całej sprzedaży to pomyłka. Bias mówi, czy prognoza jest w sumie za wysoka (dodatni) czy za niska (ujemny).
#
# **Gdzie:** `src/freshcast/metrics.py`, funkcje `wape` i `bias`.
#
# **Wejście:** `actual`, `predicted`, `mask`, tak samo jak w `prepare`.
#
# **Wynik:** `float`, ułamek bez jednostki: WAPE 0.3 to pomyłki równe 30% sprzedaży, bias -0.1 to prognoza o 10% za niska. Mianownik WAPE to suma wartości bezwzględnych danych rzeczywistych, mianownik biasu to ich zwykła suma. Dla sprzedaży, która nie bywa ujemna, to ta sama liczba, ale wzory są różne. Gdy mianownik wynosi zero, `ValueError`. Pozostałe błędy jak w `prepare`.
#
# **Skorzystaj z:** `prepare` z 05.1, wzory z tabeli w wykładzie.
#
# **Kroki:**
#
# 1. Wywołaj `prepare`.
# 2. Policz mianownik: dla WAPE sumę wartości bezwzględnych danych rzeczywistych, dla biasu ich zwykłą sumę. Zero: `ValueError`.
# 3. WAPE: suma pomyłek bezwzględnych przez mianownik. Bias: suma prognoz minus suma wartości rzeczywistych, przez mianownik. Znak ma znaczenie: za wysoka prognoza daje bias dodatni.
#
# **Sprawdzenie:** `check("05.3")` albo `uv run course check 05.3`. Dla `actual = [0, 10, 10]` i `predicted = [1, 8, 13]` WAPE wynosi 0.3, a bias 0.1.
#
# Podpowiedzi poniżej dotyczą wszystkich trzech zadań: 1 i 2 funkcji `prepare`, 3 metryki `wape`.
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
# **Cel:** prognoza sezonowa ("to, co tydzień wcześniej") dla wszystkich serii jednym wyrażeniem zamiast pętli po seriach. W labie 04 `SeasonalNaiveForecaster` prognozuje jedną serię. Na macierzy ta sama prognoza to jedno wyrażenie dla wszystkich serii.
#
# **Gdzie:** funkcja `seasonal_naive` w komórce kodu pod podpowiedziami. Zastępujesz `raise NotImplementedError("Zadanie 05.7")`.
#
# **Wejście:**
#
# - `history`: `np.ndarray` o kształcie `(liczba serii, liczba dni historii)`. Wiersz to jedna seria, kolumny to kolejne dni, ostatnia kolumna to ostatni dzień przed prognozą. W labie to `sales` bez ostatnich 7 dni.
# - `horizon`: `int`, ile dni do przodu prognozujesz, co najmniej 1.
# - `season`: `int`, długość sezonu w dniach, co najmniej 1, domyślnie 7 (tydzień). Wartości mniejszej od 1 funkcja nie musi sprawdzać.
#
# **Wynik:** `np.ndarray` o kształcie `(liczba serii, horizon)`. Kolumna `h` prognozy to wartość z pozycji `h % season` ostatniego sezonu historii. Przykład: historia jednej serii `[0, 1, 2, 3, 4, 5]`, sezon 3, horyzont 4. Ostatni sezon to `[3, 4, 5]`, prognoza to `[3, 4, 5, 3]`. `ValueError`, gdy `horizon` jest mniejszy od 1 albo historia ma mniej kolumn niż `season`.
#
# **Skorzystaj z:** wycinków 2-D z wykładu (`history[:, ...]` bierze kolumny wszystkich wierszy naraz), indeksowania listą albo tablicą numerów kolumn, `np.arange` i reszty z dzielenia `%`. `SeasonalNaiveForecaster` z labu 04 (`from freshcast.models.local import SeasonalNaiveForecaster`) daje wzorcowe wyniki: komórka pod sprawdzeniem porówna z nim Twoją funkcję.
#
# **Kroki:**
#
# 1. Sprawdź `horizon` i liczbę kolumn historii (`history.shape[1]`). Złe: `ValueError`.
# 2. Wytnij ostatnie `season` kolumn wszystkich wierszy.
# 3. Wybierz z nich kolumny w kolejności `0, 1, ..., season - 1, 0, 1, ...`, aż będzie ich `horizon`. Taki ciąg numerów daje reszta z dzielenia przez `season`.
#
# **Sprawdzenie:** `check("05.7", seasonal_naive)` przekazuje samą funkcję. Sprawdzenie używa przykładu z punktu **Wynik** (dla dwóch serii) i obu przypadków błędu. Komórka pod nim wypisuje `Te same prognozy: True`, gdy wynik zgadza się z klasą z labu 04 na wszystkich seriach.
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
    """Repeat the last ``season`` columns of every row for ``horizon`` steps.

    The array version of ``SeasonalNaiveForecaster`` from module 04: the
    forecast for step ``h`` (0-based) is column ``h % season`` of the last
    season of the row.

    Args:
        history: 2-D array, one row per series, one column per day in time
            order; the last column is the last day before the forecast.
        horizon: Number of steps to forecast, at least 1.
        season: Length of the season in columns, at least 1; smaller values
            are not checked.

    Returns:
        An array of shape ``(history.shape[0], horizon)``.

    Raises:
        ValueError: ``horizon`` is below 1, or ``history`` has fewer than
            ``season`` columns.
    """
    # >>> SOLUTION 05.7
    if horizon < 1:
        raise ValueError(f"horizon must be at least 1, got {horizon}.")
    if history.shape[1] < season:
        raise ValueError(f"History of {history.shape[1]} columns is shorter than {season}.")
    return history[:, -season:][:, np.arange(horizon) % season]
    # <<< SOLUTION


check("05.7", seasonal_naive)

# %% [markdown]
# Porównaj czas z klasą z labu 04, która prognozuje serię po serii w pętli. Komórka dzieli `sales` na historię i ostatni tydzień: `history` to wszystkie dni oprócz ostatnich 7, `actual` to ostatnie 7 dni, oba z wierszami jak w `series`.

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
# ## 05.3b Ocena ostatniego tygodnia
#
# Ostatnie 7 dni to okres testowy. Porównasz na nim trzy proste prognozy:
#
# - sezonowa: to, co tydzień wcześniej,
# - naiwna: ostatni dzień historii na każdy dzień tygodnia,
# - średnia z ostatnich 7 dni historii na każdy dzień tygodnia.
#
# Dzień, w którym produktu przez część dnia brakowało na półce, pokazuje sprzedaż mniejszą niż popyt. Oceniasz więc dwa razy: na wszystkich dniach i tylko na dniach bez braków (`stockouts == 0`), podając maskę do metryk.
#
# **Cel:** przygotować prognozy i maskę, które gotowa pętla pod spodem oceni metrykami z 05.3a.
#
# **Gdzie:** komórka pod tym tekstem, zmienne `forecasts` i `in_stock`. Pętlę `for` pod nimi zostawiasz bez zmian.
#
# **Wejście:** `history` (`(liczba serii, 83)`, sprzedaż przed tygodniem testowym), `actual` (`(liczba serii, 7)`, sprzedaż w tygodniu testowym), `vectorised` (prognoza sezonowa z poprzedniej komórki), `stockouts` z 05.6b, `HORIZON` (7).
#
# **Wynik:**
#
# - `forecasts`: słownik (`dict`) z trzema kluczami, dokładnie `"sezonowa"`, `"naiwna"` i `"średnia 7 dni"`. Każda wartość to `np.ndarray` o kształcie `actual`: prognoza dla każdej serii i każdego dnia tygodnia testowego.
# - `in_stock`: `np.ndarray` typu `bool` o kształcie `actual`. `True` tam, gdzie seria w tym dniu tygodnia testowego nie miała ani godziny braku.
#
# **Skorzystaj z:** `vectorised` jako prognozy sezonowej. Z wykładu: wycinek `[:, -1:]` (ostatnia kolumna, ale dalej 2-D), `mean(axis=1, keepdims=True)` (sekcje "Osie" i "Broadcasting"). `np.repeat(a, k, axis=1)` powtarza kolumny tablicy `k` razy.
#
# **Kroki:**
#
# 1. Prognoza naiwna: weź ostatnią kolumnę historii jako tablicę `(liczba serii, 1)` i powtórz ją 7 razy w poziomie.
# 2. Średnia 7 dni: policz średnią ostatnich 7 kolumn historii dla każdego wiersza, zostaw wymiar kolumny i powtórz 7 razy.
# 3. Złóż słownik z trzema prognozami.
# 4. Maska: weź ostatnie 7 kolumn `stockouts` i porównaj z zerem.
#
# **Sprawdzenie:** komórka wypisuje udział dni bez braków i trzy wiersze z WAPE i biasem. Następna komórka sprawdza kształty i typy asercjami.

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

# %%
assert set(forecasts) == {"sezonowa", "naiwna", "średnia 7 dni"}, "forecasts ma mieć trzy klucze z zadania."
for name, forecast in forecasts.items():
    assert forecast.shape == actual.shape, f"Prognoza {name!r} ma kształt {forecast.shape}, a powinna {actual.shape}."
assert in_stock.dtype == bool and in_stock.shape == actual.shape, "in_stock ma być maską bool o kształcie actual."
print("Zgadza się.")

# %% [markdown]
# ## 05.4 Profil godzinowy
#
# Wiersz `hours` to sprzedaż w 24 godzinach jednego dnia. Żeby porównać kształt dnia między seriami o różnej skali, dzielisz każdy wiersz przez jego sumę: wtedy wartości to udziały godzin w sprzedaży dnia.
#
# ### 05.4a `row_shares`
#
# **Cel:** funkcja, która zamienia wiersze liczb na udziały w sumie wiersza. Tu: sprzedaż w godzinach na udział godziny w sprzedaży dnia.
#
# **Gdzie:** `src/freshcast/numeric.py`, funkcja `row_shares`. Zastępujesz `raise NotImplementedError("Zadanie 05.4")`.
#
# **Wejście:** `matrix`: `np.ndarray` dwuwymiarowa liczb nieujemnych, typ `float64`. W labie `hours`: wiersz to jeden dzień jednej serii, kolumna to godzina od 0 do 23.
#
# **Wynik:** nowa `np.ndarray` o tym samym kształcie. Każdy wiersz podzielony przez własną sumę, więc sumuje się do 1. Wiersz samych zer nie ma profilu i ma dać same `NaN`, a nie zera ani nieskończoności. Wejście zostaje bez zmian. `ValueError`, gdy tablica nie jest dwuwymiarowa (`ndim`) albo ma wartość ujemną.
#
# **Skorzystaj z:** `sum(axis=1, keepdims=True)` i reguły broadcastingu z wykładu (sekcja "Broadcasting"), `np.where` (sekcja "Maski i np.where"), `np.nan`.
#
# **Kroki:**
#
# 1. Sprawdź liczbę wymiarów i wartości ujemne. Złe: `ValueError`.
# 2. Policz sumy wierszy tak, żeby miały kształt `(wiersze, 1)`, a nie `(wiersze,)`.
# 3. Zamień zerowe sumy na `NaN`, zanim podzielisz. Dzielenie przez `NaN` daje `NaN` bez ostrzeżenia.
# 4. Podziel macierz przez sumy.
#
# **Sprawdzenie:** `check("05.4")` albo `uv run course check 05.4`. Wiersz `[1, 1, 2]` ma dać `[0.25, 0.25, 0.5]`, wiersz `[0, 0, 0]` same `NaN`.
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

# %% [markdown]
# ### 05.4b Średni profil dnia
#
# **Cel:** zobaczyć, o której godzinie sklepy sprzedają najwięcej, i ile dni w ogóle nie ma profilu.
#
# **Gdzie:** komórka pod tym tekstem, zmienne `profiles`, `no_profile`, `mean_profile`.
#
# **Wejście:** `hours` z sekcji "Dane jako tablice", `(wiersze, 24)`.
#
# **Wynik:**
#
# - `profiles`: `np.ndarray` `(wiersze, 24)`, udziały godzin w sprzedaży dnia. Dzień bez sprzedaży to wiersz `NaN`.
# - `no_profile`: `np.ndarray` typu `bool`, kształt `(wiersze,)`. `True` dla dnia bez sprzedaży, czyli bez profilu.
# - `mean_profile`: `np.ndarray` `(24,)`, średni udział każdej godziny, liczony tylko z dni, które mają profil. Każdy taki dzień waży tyle samo, niezależnie od tego, ile sprzedał. To nie jest udział godziny w sumie całej sprzedaży. Sumuje się do 1.
#
# **Skorzystaj z:** `row_shares` z 05.4a (import jest w komórce), `np.isnan` na jednej kolumnie `profiles` (wiersz bez profilu ma `NaN` w każdej kolumnie), `np.nanmean` z `axis` (sekcje "Osie" i "NaN i typy liczbowe").
#
# **Sprawdzenie:** komórka wypisuje udział dni bez profilu, średni profil i godzinę szczytu. Następna komórka sprawdza wynik asercjami.

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

# %%
assert profiles.shape == hours.shape, "profiles ma mieć kształt hours."
assert no_profile.dtype == bool and no_profile.shape == (len(hours),), "no_profile ma być maską bool, jedna wartość na wiersz hours."
assert np.array_equal(no_profile, hours.sum(axis=1) == 0), "no_profile ma być True dokładnie dla dni bez sprzedaży."
assert mean_profile.shape == (24,) and np.isclose(mean_profile.sum(), 1.0), "mean_profile ma mieć 24 udziały, które sumują się do 1."
print("Zgadza się.")

# %% [markdown]
# ## 05.5 Testy metryk
#
# **Cel:** testy, które złapią błąd w metrykach, zanim zły wynik trafi do porównania modeli. Mechanizm znasz z labu 04 (04.2).
#
# **Gdzie:** `tests/test_metrics.py`, pod gotowym testem `test_mae_is_the_mean_absolute_difference`, w miejscu komentarza `# Your tests go here.`
#
# **Wejście:** metryki z 05.2 i 05.3a. Na górze pliku jest import tylko `mae`: dopisz do niego metryki, których używasz (`from freshcast.metrics import bias, mae, rmse, wape`). Alias `Metric` przyda się w adnotacji testu z `@pytest.mark.parametrize`, który dostaje metrykę jako argument.
#
# **Wynik:** plik ma razem co najmniej sześć testów, licząc gotowy test MAE, i wszystkie przechodzą na Twoich metrykach. Każdy przypadek parametryzacji liczy się jako osobny test. Do wykrycia siedmiu błędów zwykle potrzeba więcej. Razem mają wykryć siedem celowo zepsutych wersji metryk:
#
# - `mae` zwraca to samo co `rmse`,
# - `rmse` nie wyciąga pierwiastka,
# - `wape` liczy średnią z błędów procentowych poszczególnych wierszy,
# - `bias` ma odwrócony znak,
# - metryki ignorują argument `mask`,
# - `NaN` w danych jest po cichu liczony jako zero,
# - przy różnej długości wejść metryki obcinają dłuższe wejście zamiast zgłosić błąd.
#
# **Skorzystaj z:** wzoru gotowego testu (małe dane widoczne w teście, wynik policzony w głowie), `pytest.approx` do porównania liczb, `pytest.raises(ValueError, match=...)` do błędów, `@pytest.mark.parametrize` (lab 04).
#
# **Kroki:**
#
# 1. Dla każdego zepsutego zachowania z listy wymyśl dane, na których poprawna i zepsuta metryka dają różny wynik.
# 2. Policz oczekiwany wynik na kartce i zapisz go w asercji.
# 3. Uruchom testy komórką poniżej. Wszystkie mają przejść.
#
# **Sprawdzenie:** `check("05.5")` albo `uv run course check 05.5`. Sprawdzenie liczy testy, uruchamia je na Twoim kodzie, a potem na każdej zepsutej wersji. Wypisuje błędy, których Twoje testy nie wykryły.
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
# Bez sprawdzeń. Odpowiedz jednym, dwoma zdaniami pod pytaniami, w miejscu *Twoje odpowiedzi*.
#
# **Skorzystaj z:** wydruku komórki 05.3b (WAPE na wszystkich dniach i bez braków, bias) i wydruku 05.4b (udział dni bez profilu).
#
# 1. Porównaj w wydruku 05.3b WAPE na wszystkich dniach i bez braków dla każdej prognozy. Co widzisz? Zaproponuj wyjaśnienie. To obserwacja z tych danych, a nie własność wzoru WAPE.
# 2. Która prognoza wygrała w Twoim tygodniu testowym? Czy to wystarczy, żeby wybrać ją jako baseline na resztę kursu? Czego brakuje?
# 3. Co by wyszło z `profiles.mean(axis=0)` zamiast `np.nanmean`? Dlaczego?
#
# *Twoje odpowiedzi:*
