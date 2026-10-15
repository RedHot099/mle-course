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
# **Jak pracujesz.** Zadania 08.1-08.5 piszesz w pakiecie `src/freshcast/`, w plikach podanych w tabeli. Docstring każdej funkcji to dokładna specyfikacja: tekst w notebooku opisuje to samo po polsku. Po zapisaniu pliku uruchom komórkę `check(...)`; `%autoreload` wczyta Twoją zmianę bez restartu notebooka. Zadania 08.6 i 08.7 piszesz w komórkach tego notebooka, w miejscu `...`.
#
# | Zadanie | Krok | Gdzie | Czas |
# |---|---|---|---|
# | 08.1 | 08.1a `last_days_start` | `src/freshcast/split.py` | 30 min |
# | | 08.1b `split_by_date` | `src/freshcast/split.py` | |
# | | 08.1c podział panelu | notebook: `rest`, `test`, `train`, `valid` | |
# | 08.2 | 08.2a `PerSeriesForecaster.fit` | `src/freshcast/models/panel.py` | 60 min |
# | | 08.2b `PerSeriesForecaster.predict` | `src/freshcast/models/panel.py` | |
# | 08.3 | 08.3a `predict_linear` | `src/freshcast/models/gradient.py` | 90 min |
# | | 08.3b `mse` | `src/freshcast/models/gradient.py` | |
# | | 08.3c `mse_gradient` | `src/freshcast/models/gradient.py` | |
# | | 08.3d `fit_linear_gd` | `src/freshcast/models/gradient.py` | |
# | 08.4 | 08.4a `LinearForecaster._checked` | `src/freshcast/models/panel.py` | 45 min |
# | | 08.4b `LinearForecaster.fit` | `src/freshcast/models/panel.py` | |
# | | 08.4c `LinearForecaster.predict` | `src/freshcast/models/panel.py` | |
# | 08.5 | `score_forecast` | `src/freshcast/evaluation/scores.py` | 20 min |
# | 08.6 | 08.6a model "wszystkie kolumny" | notebook: `everything`, `greedy`, `greedy_scores` | 45 min |
# | | 08.6b dobre cechy plus `oos_hours` | notebook: `with_oos_scores` | |
# | 08.7 | 08.7a wybór `alpha` | notebook: `by_alpha`, `best_alpha` | 45 min |
# | | 08.7b test | notebook: `results` | |
#
# **Co bierzesz z wcześniejszych labów.** Lab 08 nie wczytuje surowych danych. Pracuje na:
#
# - pliku `data/processed/daily.parquet` z zadania 07.6, który czyta `load_processed` (krok 07.6c) z `freshcast.data.prepare`,
# - funkcjach `add_lag` (krok 07.5b) i `add_rolling_mean` (krok 07.5c) z `freshcast.data.panel`, które budują cechy,
# - nazwach kolumn z `freshcast.data.schema` (plik dany): `DATE` to `"dt"`, `TARGET` to `"sale_amount"`, `SERIES_KEY` to `["store_id", "product_id"]`, `OOS_HOURS` to `"oos_hours"`, `OUTCOME_COLUMNS` to kolumny znane dopiero po zakończeniu dnia,
# - `SeasonalNaiveForecaster` z zadania 04.1 (`freshcast.models.local`): prognoza "tak samo jak tydzień temu",
# - metrykach `wape`, `mae`, `bias` z zadań 05.2 i 05.3 (`freshcast.metrics`), z argumentem `mask`.
#
# Jeśli któregoś z tych zadań nie masz, `uv run course catchup 08` wpisze kod referencyjny modułów 00-07 do Twojego pakietu.

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
# Komórka poniżej wczytuje zbiór przetworzony z labu 07 funkcją `load_processed(paths.PROCESSED_DIR)` do zmiennej `daily`. Jeśli pliku `data/processed/daily.parquet` jeszcze nie ma, najpierw go buduje: `prepare_daily` czyta surowy plik FreshRetailNet dla miast z Twojego profilu, a `save_processed` zapisuje wynik. To kroki 07.6a, 07.6b i 07.6c. Po `uv run course catchup 08` zadziała to także bez robienia labu 07.
#
# `daily` to `pd.DataFrame`. Jeden wiersz to sprzedaż jednego produktu w jednym sklepie jednego dnia. Wiersze są posortowane po serii (`store_id`, `product_id`) i dacie, a każda seria ma każdy dzień od 2024-03-28 do 2024-06-25. Kolumny to dokładnie `PROCESSED_COLUMNS` z `freshcast.data.schema`. W tym labie potrzebujesz z nich: `dt` (data), `sale_amount` (sprzedaż, cel prognozy), `discount` i `discount_is_zero` (rabat, moduł 07), `holiday_flag`, `activity_flag` (święto, promocja) i `oos_hours` (liczba godzin bez towaru tego dnia).

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
# Rabat ma braki tam, gdzie w danych było zero (moduł 07). Model liniowy nie przyjmie braku, więc wypełniasz go wartością 1.0, czyli "bez rabatu", i zostawiasz obok flagę `discount_is_zero`. Model dostaje obie informacje i sam zdecyduje, ile są warte. To nie odwołuje decyzji z labu 07 (krok 07.2b): zapisany `daily.parquet` się nie zmienia, `discount` dalej ma braki. `discount_filled` to osobna kolumna tylko dla modelu, który wymaga kompletu liczb, a 1.0 w niej to umowne wypełnienie, które flaga `discount_is_zero` pozwala odróżnić od prawdziwej ceny bez rabatu.
#
# Komórka poniżej jest gotowa. Buduje dwie rzeczy, z których korzysta reszta labu:
#
# - `FEATURES`: lista nazw 8 kolumn-cech (`list[str]`). Każdy model liniowy w tym labie dostaje dokładnie te kolumny.
# - `panel`: `daily` z pięcioma nowymi kolumnami. Cztery dodają Twoje funkcje z kroków 07.5b i 07.5c: `add_lag` tworzy `sale_amount_lag_7` i `sale_amount_lag_14`, `add_rolling_mean` tworzy `sale_amount_mean_7_lag_7` i `sale_amount_mean_28_lag_7`. Piąta, `discount_filled`, to rabat z brakami zamienionymi na 1.0. `discount_is_zero` zmienia typ z `bool` na `int` (0 albo 1). Wiersze, kolejność i indeks są te same co w `daily`.
#
# Na początku każdej serii nowe kolumny mają `NaN`: nie ma jeszcze tylu dni historii. Tabela pokazuje to w kolumnie `count`.

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
# **Cel.** Model ocenia się na dniach, których nie widział przy uczeniu. W prognozie te dni leżą zawsze w przyszłości, więc podział też idzie po czasie (reguła C3): trening to najstarsze dni, walidacja to tydzień po nim, test to ostatni tydzień danych. Dwie funkcje z tego zadania dzielą tak panel, a w następnych modułach także inne ramki.
#
# ### 08.1a `last_days_start`
#
# **Gdzie.** `src/freshcast/split.py`, funkcja `last_days_start(df, days)`.
#
# **Wejście.**
#
# - `df`: `pd.DataFrame`; ramka z kolumną daty `dt` (stała `DATE`, typ `datetime64`), na przykład `panel`. Ta sama data powtarza się w wielu wierszach, raz na serię, a wiersze mogą być w dowolnej kolejności. Funkcja patrzy tylko na `dt`.
# - `days`: `int`; długość okresu na końcu danych, w dniach. Co najmniej 1 i mniej niż liczba dni w danych.
#
# **Wynik.** `pd.Timestamp`: pierwszy dzień ostatnich `days` dni. Dla danych z dni 2024-04-01..2024-04-10 i `days=3` to 2024-04-08 (ostatnie trzy dni to 04-08, 04-09, 04-10). Gdy `days` jest mniejsze od 1 albo obejmuje wszystkie dni danych, funkcja zgłasza `ValueError`.
#
# **Skorzystaj z.** Stałej `DATE` (nazwa kolumny daty, `"dt"`). W pliku `split.py` jej jeszcze nie ma: dopisz na górze, pod `import pandas as pd`, linię `from freshcast.data.schema import DATE`. Z tego importu korzysta też 08.1b.
#
# **Kroki.**
#
# 1. Znajdź najwcześniejszą i najpóźniejszą datę w kolumnie dat (`min()`, `max()`).
# 2. Policz, ile dni kalendarzowych obejmują dane, licząc oba końce. Różnica dwóch dat to `pd.Timedelta`, a jej atrybut `.days` to liczba całkowita.
# 3. Gdy `days` jest poza zakresem z punktu **Wejście**, zgłoś `ValueError` z komunikatem, który podaje `days` i dozwolony zakres.
# 4. Cofnij się od ostatniej daty o `days - 1` dni. Datę przesuwa dodanie albo odjęcie `pd.Timedelta(days=...)`.
#
# ### 08.1b `split_by_date`
#
# **Gdzie.** `src/freshcast/split.py`, funkcja `split_by_date(df, cutoff)`.
#
# **Wejście.**
#
# - `df`: `pd.DataFrame` z kolumną `dt`, jak w 08.1a. Pozostałe kolumny przechodzą do wyniku bez zmian.
# - `cutoff`: `pd.Timestamp`; pierwszy dzień drugiej części. Zwykle to wynik `last_days_start`.
#
# **Wynik.** Krotka dwóch ramek `(before, after)`. `before` to wiersze z datą wcześniejszą niż `cutoff`, `after` to wiersze z datą `cutoff` i późniejszą. Obie mają wszystkie kolumny `df`, jego kolejność wierszy i jego indeks: bez sortowania i bez `reset_index`. Razem mają tyle wierszy co `df`. Gdy któraś część wyszłaby pusta, funkcja zgłasza `ValueError`.
#
# **Skorzystaj z.** Stałej `DATE` zaimportowanej w 08.1a. Maski logicznej z modułu 06: porównanie kolumny z datą daje `Series` z `True` i `False`, `.loc[maska]` wybiera wiersze, a `~maska` odwraca maskę.
#
# **Kroki.**
#
# 1. Zbuduj maskę "data przed `cutoff`".
# 2. Gdy maska jest cała `True` (`.all()`) albo nie ma w niej ani jednego `True` (`.any()`), zgłoś `ValueError` z datą `cutoff` w komunikacie.
# 3. Zwróć wiersze z maską i wiersze z odwróconą maską.
#
# **Sprawdzenie (08.1a i 08.1b).** `check("08.1")` poniżej wypisuje ✅. Sprawdza obie funkcje na dwóch seriach po 10 dni w losowej kolejności wierszy, z błędnymi `days` i `cutoff`.
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

# %% [markdown]
# ### 08.1c Podział panelu
#
# **Gdzie.** Komórka poniżej, w miejscu `...`. Tworzysz cztery zmienne: `rest`, `test`, `train`, `valid`.
#
# **Wejście.** `panel` z sekcji "Cechy znane tydzień wcześniej".
#
# **Wynik.** Cztery `pd.DataFrame` z kolumnami i indeksem `panel`:
#
# - `test`: ostatnie 7 dni danych (2024-06-19..2024-06-25),
# - `rest`: wszystkie wiersze przed testem,
# - `valid`: ostatnie 7 dni z `rest` (2024-06-12..2024-06-18),
# - `train`: reszta `rest`, do 2024-06-11.
#
# **Skorzystaj z.** `last_days_start` i `split_by_date`, każdej dwa razy: najpierw na `panel` (odcinasz test), potem na `rest` (odcinasz walidację).
#
# **Sprawdzenie.** Komórka drukuje liczbę wierszy i zakres dat każdej części. Komórka pod nią sprawdza kolejność części i ich długość w dniach.

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

# %%
assert train[DATE].max() < valid[DATE].min() and valid[DATE].max() < test[DATE].min(), "Części mają iść po sobie: trening, walidacja, test."
assert valid[DATE].nunique() == 7 and test[DATE].nunique() == 7, "Walidacja i test mają po 7 dni."
assert len(train) + len(valid) + len(test) == len(panel), "Każdy wiersz panelu ma trafić do dokładnie jednej części."

# %% [markdown]
# ## 08.2 Baseline na całym panelu
#
# **Cel.** Prognozy lokalne z modułu 04 widzą jedną serię: `fit(history)` dostaje listę liczb, `predict(horizon)` zwraca listę `horizon` prognoz. Modele od tego labu widzą cały panel naraz: `fit(X, y)` dostaje wiersze panelu i ich sprzedaż, `predict(X)` zwraca jedną prognozę na wiersz. Żeby baseline z modułu 04 dało się porównać z każdym modelem na tych samych wierszach (reguła C6), potrzebny jest adapter: obiekt o interfejsie panelowym, który w środku uruchamia osobny model lokalny dla każdej serii.
#
# **Gdzie.** `src/freshcast/models/panel.py`, klasa `PerSeriesForecaster`. `__init__` jest gotowy: zapamiętuje `make_local` w `self._make_local` i tworzy pusty słownik `self._histories`. Piszesz `fit` (08.2a) i `predict` (08.2b).
#
# **Skorzystaj z.** `SERIES_KEY` i `DATE`. W pliku `models/panel.py` ich nie ma: dopisz na górze, obok `from freshcast.models.local import LocalForecaster`, linię `from freshcast.data.schema import DATE, SERIES_KEY`. `np` (NumPy) jest już zaimportowany. Dalej `groupby` po kilku kolumnach z modułu 07. `make_local` to funkcja bez argumentów, która przy każdym wywołaniu zwraca nowy model lokalny z modułu 04, na przykład `lambda: SeasonalNaiveForecaster(season=7)`.
#
# ### 08.2a `fit(X, y)`
#
# **Wejście.**
#
# - `X`: `pd.DataFrame`; wiersze treningowe panelu, na przykład `train`. Używasz tylko kolumn `store_id`, `product_id`, `dt`. Wiersze mogą być w dowolnej kolejności.
# - `y`: `pd.Series`; sprzedaż (`sale_amount`) tych samych wierszy, w tej samej kolejności, na przykład `train[TARGET]`.
#
# **Wynik.** Zwracasz `self`. Po `fit` w `self._histories` jest słownik: klucz to krotka `(store_id, product_id)`, wartość to lista sprzedaży tej serii (`list[float]`), od najstarszego dnia.
#
# **Kroki.**
#
# 1. Weź z `X` kolumny klucza serii i daty, a sprzedaż z `y` dołącz jako nową kolumnę. `y` łączysz z `X` po pozycji: wartość na pozycji `i` należy do `i`-tego wiersza `X`. `y.to_numpy()` odcina indeks, więc pandas niczego nie dopasuje po etykietach. Od tej chwili sprzedaż jest kolumną tej samej ramki, więc sortowanie przestawia ją razem z wierszem.
# 2. Posortuj wiersze po serii, potem po dacie.
# 3. Pogrupuj po `SERIES_KEY`. Klucz grupy przy dwóch kolumnach to krotka. Dla każdej grupy zapisz w słowniku listę jej sprzedaży (`tolist()`).
#
# ### 08.2b `predict(X)`
#
# **Wejście.** `X`: `pd.DataFrame`; wiersze do prognozy, na przykład `valid`, w dowolnej kolejności. Używasz kolumn `store_id`, `product_id`, `dt`. Wiersze każdej serii to kolejne dni zaraz po jej historii z `fit`.
#
# **Wynik.** Tablica NumPy (`np.ndarray`, `float64`) o długości `len(X)`. Element na pozycji `i` to prognoza dla `i`-tego wiersza `X`. Liczy się pozycja, nie etykieta indeksu: `valid` ma indeks odziedziczony po `panel`, nie 0, 1, 2, .... Seria, której nie było w `fit`, to `ValueError`.
#
# **Kroki.**
#
# 1. Weź z `X` kolumny klucza i daty i ponumeruj wiersze od zera (`reset_index(drop=True)`). Teraz etykieta wiersza to jego pozycja.
# 2. Przygotuj pustą tablicę na wynik, o długości `X`.
# 3. Dla każdej serii w `X`: sprawdź, czy jest w `self._histories`; posortuj jej wiersze po dacie; zrób świeży model `self._make_local()`, naucz go na historii serii i poproś o tyle kroków, ile seria ma wierszy; wpisz prognozy w pozycje tych wierszy, najwcześniejszy dzień dostaje pierwszy krok.
#
# **Sprawdzenie.** `check("08.2")` wypisuje ✅. Sprawdzenie używa zastępczego modelu lokalnego (ostatnia wartość plus numer kroku), więc nie zależy od Twojego kodu z modułu 04. Wiersze `X` przychodzą w losowej kolejności.
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

# %% [markdown]
# Komórka poniżej jest gotowa. Uczy baseline sezonowy na `train` i prognozuje 7 dni walidacji. Powstają trzy zmienne, których użyjesz dalej:
#
# - `baseline`: Twój `PerSeriesForecaster` z `SeasonalNaiveForecaster(season=7)` z zadania 04.1,
# - `baseline_valid`: tablica prognoz, jedna na wiersz `valid`,
# - `valid_in_stock`: `pd.Series` z `True` tam, gdzie dzień walidacji nie miał ani jednej godziny bez towaru (`oos_hours == 0`).
#
# WAPE liczy `metrics.wape` z zadania 05.3: raz na wszystkich wierszach, raz z maską `valid_in_stock`.

# %%
from freshcast import metrics
from freshcast.models.local import SeasonalNaiveForecaster
from freshcast.models.panel import PerSeriesForecaster

baseline = PerSeriesForecaster(lambda: SeasonalNaiveForecaster(season=7))
baseline.fit(train, train[TARGET])
baseline_valid = baseline.predict(valid)
valid_in_stock = valid[OOS_HOURS] == 0
print(f"Baseline, walidacja: WAPE {metrics.wape(valid[TARGET], baseline_valid):.3f}, bez braków {metrics.wape(valid[TARGET], baseline_valid, valid_in_stock):.3f}")

# %%
assert baseline_valid.shape == (len(valid),), "Jedna prognoza na wiersz walidacji."
assert not np.isnan(baseline_valid).any(), "Prognoza baseline'u nie może mieć NaN."

# %% [markdown]
# ## 08.3 Regresja liniowa od zera
#
# **Cel.** Model liniowy przewiduje `X @ w + b`. Uczenie to szukanie `w` i `b`, dla których średni kwadrat błędu (MSE) jest najmniejszy. Gradient descent robi to krokami: liczy, w którą stronę MSE rośnie najszybciej (gradient), i przesuwa parametry trochę w przeciwną stronę. Piszesz go sam, żeby "model się uczy" znaczyło konkretną pętlę. W 08.4 tę samą robotę zrobi scikit-learn.
#
# **Gdzie.** `src/freshcast/models/gradient.py`, cztery funkcje w kolejności 08.3a-08.3d. Każda następna korzysta z poprzednich.
#
# **Oznaczenia.** Wszystko tu to tablice NumPy z liczbami `float`. `X` ma kształt `(n, k)`: `n` wierszy panelu, `k` cech. W notebooku `k` to 8, liczba kolumn w `FEATURES`. `y` i każda prognoza mają kształt `(n,)`: jedna sprzedaż na wiersz. `w` (`weights`) ma kształt `(k,)`: jedna waga na cechę. `b` (`intercept`) to jedna liczba. Operator `@` i `.T` objaśnia wykład 08, sekcja "Gradient descent". To inne `X` niż w 08.2: tam ramka panelu z kluczem i datą, tu tablica samych liczb-cech.
#
# **Skorzystaj z.** Wzorów z wykładu 08 i z docstringów. Funkcje nie używają pandas ani niczego z labu 07. Importów nie dopisujesz: `import numpy as np` jest już na górze `gradient.py`.
#
# ### 08.3a `predict_linear(X, weights, intercept)`
#
# **Wejście.** `X` `(n, k)`, `weights` `(k,)`, `intercept` `float`.
#
# **Wynik.** Tablica `(n,)`: prognoza dla każdego wiersza, czyli suma "cecha razy waga" plus `intercept`.
#
# ### 08.3b `mse(actual, predicted)`
#
# **Wejście.** Dwie tablice `(n,)`: prawdziwe wartości i prognozy dla tych samych wierszy.
#
# **Wynik.** `float`: średnia z kwadratów różnic. Funkcje NumPy zwracają typ `np.float64`; zamień go na zwykły `float()`.
#
# ### 08.3c `mse_gradient(X, y, weights, intercept)`
#
# **Wejście.** `X` `(n, k)`, `y` `(n,)`, obecne `weights` `(k,)` i `intercept` `float`.
#
# **Wynik.** Krotka: gradient po wagach, tablica `(k,)`, i gradient po wyrazie wolnym, `float`. Wzory są w docstringu.
#
# **Kroki.** Policz błąd `predict_linear(...) - y` raz i użyj go w obu wzorach.
#
# ### 08.3d `fit_linear_gd(X, y, *, learning_rate, steps)`
#
# **Wejście.** `X` `(n, k)` (najlepiej po standaryzacji), `y` `(n,)`, `learning_rate` (`float` większy od 0, długość kroku), `steps` (`int`, co najmniej 1, liczba kroków). Gwiazdka w sygnaturze znaczy, że dwa ostatnie argumenty podajesz z nazwą: `learning_rate=0.1, steps=500`.
#
# **Wynik.** Krotka `(weights, intercept, losses)`: wagi `(k,)`, wyraz wolny `float` i lista `steps` liczb, gdzie `losses[i]` to MSE przed krokiem `i`. Błędne argumenty i strata, która przestała być skończona, to `ValueError`.
#
# **Kroki.**
#
# 1. Sprawdź `learning_rate` i `steps`; złe wartości to `ValueError`.
# 2. Zacznij od zerowych wag (`np.zeros`, tyle, ile `X` ma kolumn) i zerowego wyrazu wolnego.
# 3. W każdym kroku: policz MSE obecnego modelu; jeśli nie jest skończone (`np.isfinite`), zgłoś `ValueError`; dopisz je do `losses`; policz gradient; odejmij od parametrów `learning_rate` razy gradient.
#
# **Sprawdzenie (08.3a-08.3d).** `check("08.3")` wypisuje ✅. Gradient porównuje z przybliżeniem liczonym z samej straty, a uczenie z wagami, z których wygenerowano dane bez szumu.
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
# Komórki do końca tej sekcji są gotowe: uruchamiasz je i czytasz wynik.
#
# Ucz na wierszach treningu, które mają wszystkie cechy (pierwsze 34 dni każdej serii nie mają średniej z 28 dni sprzed tygodnia). Komórka tworzy:
#
# - `fit_rows`: wiersze `train` bez `NaN` w kolumnach `FEATURES` (`pd.DataFrame`); na nich uczą się wszystkie modele liniowe aż do 08.7,
# - `X`: cechy tych wierszy jako tablica NumPy `(n, 8)`, `y`: ich sprzedaż `(n,)`,
# - `X_scaled`: `X` po standaryzacji średnią i odchyleniem **z treningu** (reguła C4).
#
# Potem porównuje trzy długości kroku uczenia:

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
# Co się stanie przy kroku 1.5? Uruchom i przeczytaj komunikat. `ValueError` zgłasza Twoje sprawdzenie `np.isfinite` z 08.3d: każdy krok przeskakuje dno coraz dalej, aż strata przestaje być skończoną liczbą. Sama wartość 1.5 nie jest zakazana; bezpieczny krok zależy od danych i od ich skali.

# %%
try:
    gradient.fit_linear_gd(X_scaled, y, learning_rate=1.5, steps=200)
except ValueError as error:
    print("ValueError:", error)

# %% [markdown]
# Twój model i `LinearRegression` ze scikit-learn szukają tego samego minimum MSE. scikit-learn liczy je dokładnie, Twoja pętla zbliża się do niego krokami. Na profilu `standard` po 500 krokach wagi zgadzają się do trzeciego miejsca po przecinku. Na profilu `small` 500 kroków nie wystarcza, żeby dojść do samego dna: wagi niektórych cech różnią się w drugim miejscu po przecinku, a MSE obu modeli jest prawie takie samo.

# %%
from sklearn.linear_model import LinearRegression

weights, intercept, _ = gradient.fit_linear_gd(X_scaled, y, learning_rate=0.1, steps=500)
reference = LinearRegression().fit(X_scaled, y)
pd.DataFrame({"gradient descent": weights, "scikit-learn": reference.coef_}, index=FEATURES).round(3)

# %%
gd_loss = gradient.mse(y, gradient.predict_linear(X_scaled, weights, intercept))
sklearn_loss = gradient.mse(y, reference.predict(X_scaled))
print(f"MSE: gradient descent {gd_loss:.4f}, scikit-learn {sklearn_loss:.4f}")
assert gd_loss <= 1.01 * sklearn_loss, "Gradient descent nie doszedł blisko minimum straty."

# %% [markdown]
# ## 08.4 `LinearForecaster`
#
# **Cel.** Ten sam model w wersji, której używa reszta kursu: `StandardScaler` i `Ridge` ze scikit-learn w jednym `Pipeline`, pod interfejsem panelowym `fit(X, y)` / `predict(X)` z 08.2. Skaler dopasowuje się w `fit`, więc widzi tylko wiersze treningu (reguła C4). Model nie zgaduje brakujących cech i nie prognozuje ujemnej sprzedaży. Postać prognozy jest ta sama co w 08.3, ale `Ridge` dodaje karę za duże wagi, więc jego wagi nie muszą być identyczne z wagami z 08.3.
#
# **Gdzie.** `src/freshcast/models/panel.py`, klasa `LinearForecaster`. Gotowe są `__init__` (zapamiętuje `self.features`, listę nazw kolumn, i `self.alpha`, siłę kary; `self._pipeline` to `None` aż do `fit`) i `coefficients`, która czyta wagi z `self._pipeline`. Piszesz `_checked` (08.4a), `fit` (08.4b) i `predict` (08.4c).
#
# **Skorzystaj z.** `make_pipeline`, `StandardScaler` i `Ridge` ze scikit-learn. W `models/panel.py` jest tylko `from sklearn.pipeline import Pipeline` (typ atrybutu `self._pipeline`). Zmień tę linię na `from sklearn.pipeline import Pipeline, make_pipeline` i dopisz pod nią `from sklearn.linear_model import Ridge` oraz `from sklearn.preprocessing import StandardScaler`. Jak ich używać, pokazuje wykład 08, sekcja "Pipeline w scikit-learn". `np.clip(tablica, 0.0, None)` zamienia każdą wartość poniżej 0 na 0, a resztę zostawia.
#
# ### 08.4a `_checked(X)`: metoda pomocnicza
#
# **Wejście.** `X`: `pd.DataFrame`; wiersze panelu, w których są wszystkie kolumny z `self.features`. Inne kolumny mogą mieć `NaN`, to nie błąd.
#
# **Wynik.** `pd.DataFrame` z samymi kolumnami `self.features`, w tej kolejności, z tymi samymi wierszami. Gdy któraś z tych kolumn ma `NaN` w choć jednym wierszu, `ValueError` z liczbą takich wierszy w komunikacie. Metoda niczego nie usuwa (ani kolumn, ani wierszy) i niczego nie wypełnia. Wiersze bez kompletu cech odfiltrowuje kod, który woła model, jak przy `fit_rows` niżej.
#
# **Kroki.** Wybierz kolumny z listy. Policz wiersze, w których któraś z nich ma `NaN` (`isna()`, potem `any(axis=1)` i `sum()`). Jeśli jest ich więcej niż zero, zgłoś błąd.
#
# ### 08.4b `fit(X, y)`
#
# **Wejście.** `X`: wiersze treningu, na przykład `fit_rows`; `y`: ich sprzedaż, `fit_rows[TARGET]`.
#
# **Wynik.** `self`. Po `fit` w `self._pipeline` jest dopasowany `Pipeline`: skaler, potem `Ridge(alpha=self.alpha)`.
#
# **Kroki.** Zbuduj nowy pipeline (w `fit`, nie w `__init__`: każde `fit` zaczyna od zera) i dopasuj go do kolumn z `_checked(X)` i do `y`.
#
# ### 08.4c `predict(X)`
#
# **Wejście.** `X`: wiersze do prognozy, na przykład `valid`, z kompletem cech.
#
# **Wynik.** `np.ndarray` (`float64`) o długości `len(X)`, w kolejności `X`, bez wartości ujemnych. `predict` przed `fit` to `RuntimeError`.
#
# **Kroki.** Gdy `self._pipeline` to `None`, zgłoś `RuntimeError`. Inaczej prognozuj na `_checked(X)` i podnieś ujemne wartości do zera.
#
# **Sprawdzenie (08.4a-08.4c).** `check("08.4")` wypisuje ✅. Sprawdza `predict` przed `fit`, odtworzenie celu na danych bez szumu, obcinanie do zera, `NaN` w cechach przy `fit` i przy `predict` oraz to, że `NaN` w innej kolumnie nie jest błędem.
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
# **Cel.** Każdy model od teraz oceniasz tak samo: WAPE, MAE i bias na wszystkich wierszach, a WAPE i bias także na dniach bez braków towaru. Sprzedaż w dniu z brakiem towaru jest ograniczona przez zapas, więc o trafności prognozy popytu mówi mniej. Jedna funkcja oceny daje tabele, które da się porównać między modułami.
#
# **Gdzie.** `src/freshcast/evaluation/scores.py`, funkcja `score_forecast(actual, predicted, in_stock)`.
#
# **Wejście.**
#
# - `actual`: prawdziwa sprzedaż dzienna, jedna wartość na wiersz (tablica NumPy albo `pd.Series`, np. `valid[TARGET]`),
# - `predicted`: prognozy dla tych samych wierszy, w tej samej kolejności (np. `baseline_valid`),
# - `in_stock`: wartości logiczne tej samej długości, `True` dla dnia bez braku towaru (np. `valid_in_stock`). Funkcja dostaje gotową maskę i nie wybiera definicji. W tym labie maska to `oos_hours == 0`: brak żadnej godziny bez towaru między 06:00 a 22:00, bo tylko te godziny liczy `oos_hours` (krok 07.4c). Nie używaj tu `oos_hours_total`.
#
# **Wynik.** `dict[str, float]` z pięcioma kluczami, w tej kolejności: `"wape"`, `"mae"`, `"bias"` (wszystkie wiersze), `"wape_in_stock"`, `"bias_in_stock"` (tylko wiersze z `in_stock`). WAPE i bias to ułamki (0.25 to 25%), MAE jest w sztukach sprzedaży.
#
# **Skorzystaj z.** `metrics.wape`, `metrics.mae` i `metrics.bias` z zadań 05.2 i 05.3; w pliku `evaluation/scores.py` jest tylko import `ArrayLike`, więc dopisz na górze linię `from freshcast import metrics`. Wersje "bez braków" to te same funkcje z trzecim argumentem `mask`. Niczego nie liczysz od nowa.
#
# **Sprawdzenie.** `check("08.5")` wypisuje ✅. Sprawdza klucze, ich kolejność i wartości na czterech wierszach.

# %%
check("08.5")

# %% [markdown]
# Komórka poniżej jest gotowa. Uczy Twój `LinearForecaster` na `fit_rows` z `alpha=1.0` (zmienna `linear`) i zbiera wyniki obu modeli na walidacji w ramce `scores`: wiersze `"baseline"` i `"liniowy"`, kolumny to klucze `score_forecast`. Z tego samego wzoru (słownik słowników, potem `.T`) skorzystasz w 08.7b.

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
# **Cel.** Kolega proponuje: "po co wybierać cechy, daj modelowi wszystko, co jest w tabeli, Ridge sam wybierze". Sprawdzasz to i uczysz się rozpoznawać wynik, który jest zbyt dobry, żeby był prawdziwy. Tego zadania nie sprawdza `check`: wynik oceniasz sam, pod komórką jest tylko `assert` na kształt odpowiedzi.
#
# ### 08.6a Model "wszystkie kolumny"
#
# **Gdzie.** Komórka poniżej, w miejscu `...`. Tworzysz `everything`, `greedy` i `greedy_scores`.
#
# **Wejście.** `panel` (wszystkie kolumny), `train`, `valid`, `valid_in_stock`.
#
# **Wynik.**
#
# - `everything`: `list[str]`, nazwy wszystkich kolumn liczbowych `panel` poza trzema rodzajami: celem `TARGET` (to go prognozujesz), surowym `"discount"` (ma `NaN`, a jego wypełniona wersja `discount_filled` jest na liście) i identyfikatorami, czyli kolumnami z nazwą kończącą się na `_id` (`store_id`, `product_id`, `city_id` to numery, a nie wielkości). Wszystkie kolumny z `FEATURES` są na tej liście.
# - `greedy`: `LinearForecaster(everything, alpha=1.0)` nauczony na wierszach `train`, które nie mają `NaN` w żadnej kolumnie z `everything`; cel to sprzedaż tych samych wierszy.
# - `greedy_scores`: `dict` z `score_forecast` dla prognozy `greedy` na `valid`, z maską `valid_in_stock`.
#
# **Skorzystaj z.** `LinearForecaster` (08.4) i `score_forecast` (08.5). Kolumny liczbowe wybiera `panel.select_dtypes("number").columns`. Wiersze bez braków w wybranych kolumnach daje `dropna(subset=...)`, jak przy `fit_rows`. Koniec nazwy sprawdza metoda napisu `endswith`.
#
# **Sprawdzenie.** Komórka drukuje listę i wyniki; komórka z `assert` pod nią sprawdza skład listy.

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

# %%
assert TARGET not in everything and "discount" not in everything, "Cel i surowy rabat nie są cechami."
assert not any(name.endswith("_id") for name in everything), "Identyfikatory nie są cechami."
assert set(FEATURES) <= set(everything), "Lista ma zawierać wszystkie kolumny z FEATURES."
assert list(greedy_scores) == list(scores.columns), "greedy_scores to wynik score_forecast."

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
# ### 08.6b Dobre cechy plus godziny bez towaru
#
# Jest też wersja subtelniejsza. Do dobrych cech dokładasz tylko liczbę godzin bez towaru z tego samego dnia i porównujesz oba WAPE z modelem bez niej.
#
# **Gdzie.** Komórka poniżej, w miejscu `...`. Tworzysz `with_oos_scores`.
#
# **Wejście.** `fit_rows`, `valid`, `valid_in_stock`; lista cech to `FEATURES` plus `OOS_HOURS` (`"oos_hours"`, kolumna z labu 07).
#
# **Wynik.** `with_oos_scores`: `dict` z `score_forecast` dla `LinearForecaster` z tą listą cech i `alpha=1.0`, nauczonego na `fit_rows` i ocenionego na `valid`.
#
# **Skorzystaj z.** Tego samego wzoru co `linear` w komórce pod 08.5; zmienia się tylko lista cech.
#
# **Sprawdzenie.** Tabela pod komórką zestawia WAPE modelu `"liniowy"` z `scores` z Twoim wynikiem.

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
# **Cel.** `alpha` to siła kary w Ridge: im większa, tym bliżej zera są wagi. To hiperparametr: wybierasz go na walidacji, nigdy na teście (reguła C5). Gdy decyzja zapadnie, jeden raz oceniasz oba modele na teście. Tego zadania nie sprawdza `check`; pod komórkami są `assert` na kształt wyników.
#
# ### 08.7a Wybór `alpha`
#
# **Gdzie.** Komórka poniżej, w miejscu `...`. Tworzysz `by_alpha` i `best_alpha`.
#
# **Wejście.** `fit_rows`, `valid`, `valid_in_stock`, `FEATURES`. Wartości `alpha` do porównania: 0.01, 1, 100, 1 000, 10 000 i 100 000.
#
# **Wynik.**
#
# - `by_alpha`: `dict[float, float]`; klucz to `alpha`, wartość to `"wape_in_stock"` na walidacji dla `LinearForecaster(FEATURES, alpha=...)` nauczonego na `fit_rows`. Sześć wpisów.
# - `best_alpha`: `float`, ta wartość `alpha`, dla której WAPE w `by_alpha` jest najmniejszy.
#
# **Skorzystaj z.** `LinearForecaster` i `score_forecast`, jak w komórce pod 08.5. Klucz z najmniejszą wartością daje `min(słownik, key=słownik.get)`. Przy remisie `min` zwraca pierwszy taki klucz, czyli mniejszą `alpha` z listy, i tę zasadę przyjmujesz. Test zostaje nietknięty.

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

# %%
assert sorted(by_alpha) == [0.01, 1.0, 100.0, 1_000.0, 10_000.0, 100_000.0], "by_alpha ma mieć sześć wartości alpha z treści zadania."
assert by_alpha[best_alpha] == min(by_alpha.values()), "best_alpha ma dawać najmniejszy WAPE na walidacji."

# %% [markdown]
# ### 08.7b Test
#
# Decyzje zapadły. Teraz, jeden raz, test: oba modele uczysz na treningu i walidacji razem i prognozujesz ostatni tydzień.
#
# **Gdzie.** Komórka poniżej, w miejscu `...`. Tworzysz `results`.
#
# **Wejście.** `rest` (trening i walidacja razem, z 08.1c), `test`, `best_alpha`, `FEATURES`.
#
# **Wynik.** `results`: `pd.DataFrame` z dwoma wierszami o etykietach `"baseline sezonowy"` i `"Ridge"`, w tej kolejności, i kolumnami `score_forecast` (`wape`, `mae`, `bias`, `wape_in_stock`, `bias_in_stock`), ocenionymi na `test` z maską "dzień testu bez godzin bez towaru".
#
# **Skorzystaj z.**
#
# - baseline: `PerSeriesForecaster(lambda: SeasonalNaiveForecaster(season=7))`, nauczony na wszystkich wierszach `rest` i ich sprzedaży,
# - Ridge: `LinearForecaster(FEATURES, alpha=best_alpha)`, nauczony na wierszach `rest` z kompletem cech (`dropna(subset=FEATURES)`, jak `fit_rows`),
# - maska: jak `valid_in_stock`, tylko na `test`,
# - ramka: jak `scores` w komórce pod 08.5.
#
# **Sprawdzenie.** Komórka pokazuje tabelę; komórka z `assert` pod nią sprawdza wiersze i kolumny.

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

# %%
assert list(results.index) == ["baseline sezonowy", "Ridge"], "results ma wiersze 'baseline sezonowy' i 'Ridge', w tej kolejności."
assert list(results.columns) == ["wape", "mae", "bias", "wape_in_stock", "bias_in_stock"], "Kolumny results to klucze score_forecast."

# %% [markdown]
# ## Pytania
#
# Bez sprawdzeń. Odpowiedz krótko.
#
# 1. Dlaczego walidacja i test leżą po treningu, a nie są losowymi wierszami z całego okresu? Co by się stało z wynikiem przy losowym podziale?
# 2. Jak bardzo `alpha` zmienia wynik w `by_alpha` na Twoim profilu danych? Od czego zależy, ile regularyzacja ma tu do roboty? Kiedy miałaby dużo?
# 3. Spójrz na tabelę z 08.6b (walidacja). Jak zmienił się WAPE na wszystkich dniach, a jak na dniach bez braków, po dodaniu `oos_hours`? Wyjaśnij oba kierunki.
# 4. Porównaj w `results` Ridge z baseline'em i odczytaj znak `bias_in_stock` Ridge'a. Jeśli jest ujemny, co to znaczy dla sklepu i skąd może się brać?
#
# Twoje liczby zależą od profilu danych. Wynik inny niż u kolegi nie dowodzi błędu w kodzie: opisz to, co widzisz u siebie.
#
# *Twoje odpowiedzi:*
