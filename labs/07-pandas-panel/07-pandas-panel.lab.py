# %% [markdown]
# # Lab 07: panel sprzedaży w pandas
#
# Wracasz do FreshRetailNet-50K z labu 05. W labie 05 dane trafiały do tablic NumPy. Teraz pracujesz w pandas i budujesz z tego zbioru trwały plik, na którym stoi reszta kursu. To 90 dni sprzedaży świeżych produktów w 898 sklepach, po jednym wierszu na parę sklep × produkt × dzień.
#
# Na koniec labu masz na dysku plik `data/processed/daily.parquet`. Każdy kolejny moduł, od pierwszego modelu po capstone, zaczyna od wczytania tego pliku. Jeśli coś tu zrobisz byle jak, będzie to wracać przez kolejne sto godzin.
#
# **Czas:** około 7 godzin. Nie rób tego na jedno posiedzenie.
#
# ## Jak pracujesz w tym labie
#
# Kod piszesz w dwóch miejscach:
#
# - **Funkcje do pakietu**: w plikach `src/freshcast/data/*.py`. Każda ma gotową sygnaturę i docstring. Docstring jest po angielsku i jest dokładną specyfikacją: argumenty, wynik, błędy. Opis w notebooku mówi to samo po polsku. Twoje zadanie to ciało funkcji w miejscu `raise NotImplementedError`.
# - **Eksploracja**: w komórkach tego notebooka, tam gdzie widzisz `...`. Wynik zapisujesz do zmiennej o podanej nazwie. Notebook ją potem wypisuje albo sprawdza.
#
# Duże zadania są podzielone na kroki: 07.3a, 07.3b i tak dalej. Krok to jedna funkcja albo jedno pytanie. Opis każdego kroku ma ten sam układ:
#
# - **Cel**: po co to robisz.
# - **Gdzie**: plik i funkcja albo zmienna w notebooku.
# - **Wejście**: co dostajesz, z typem i znaczeniem.
# - **Wynik**: co oddajesz, z typem, kolumnami i kolejnością wierszy.
# - **Skorzystaj z**: funkcje z wcześniejszych kroków, stałe i zmienne, które już masz.
# - **Kroki**: plan w słowach, bez gotowego kodu.
# - **Sprawdzenie**: po czym poznasz, że działa.
#
# Na końcu zadania uruchamiasz komórkę `check("07.x")`. Sprawdzenie działa na małej próbce danych z repozytorium (8 serii po 90 dni) i testuje funkcje w kolejności kroków. Możesz je uruchomić po każdym kroku:
#
# - ✅ wszystkie funkcje zadania działają,
# - ⬜ „jeszcze nie zrobione”: sprawdzenie doszło do funkcji, która wciąż ma `raise NotImplementedError`. Jeśli to funkcja z następnego kroku, Twój krok przeszedł,
# - ❌ komunikat mówi, który warunek nie jest spełniony.
#
# To samo zrobisz z terminala: `uv run course check 07.1` dla jednego zadania, `uv run course check 07` dla całego modułu.
#
# Pod każdym zadaniem są trzy podpowiedzi, od ogólnej do prawie gotowego kodu. Otwieraj je po kolei i dopiero wtedy, gdy naprawdę utkniesz. Jeśli pracujesz z tutorem, wpisz `/hint`.
#
# | Krok | Gdzie | Czas zadania |
# |---|---|---|
# | **07.0** Rozpoznanie pliku | notebook: `scalar_bytes`, `nested_bytes`, `total_gb` | 30 min |
# | **07.1a** Najmniejsze typy całkowite | `data/load.py`: `shrink_integers` | 45 min |
# | 07.1b Wczytanie wybranych kolumn i miast | `data/load.py`: `load_sales` | |
# | 07.1c Ile pamięci zaoszczędziłeś | notebook: `saving` | |
# | **07.2a** Śledztwo: pięć pytań do danych | notebook: `n_duplicated`, `days_distribution`, `n_zero`, `n_above_one`, `zero_days`, `comparison` | 75 min |
# | 07.2b Twój wniosek o zerowym rabacie | notebook: komórka tekstowa | |
# | 07.2c Reguły panelu | `data/validate.py`: `check_panel` | |
# | 07.2d Zero rabatu poza skalą | `data/validate.py`: `clean_discount` | |
# | **07.3a** Wymiar sklepu | `data/dims.py`: `build_store_dim` | 60 min |
# | 07.3b Wymiar produktu | `data/dims.py`: `build_product_dim` | |
# | 07.3c Bezpieczne złączenie | `data/dims.py`: `attach_dim` | |
# | 07.3d Najlepiej sprzedająca się kategoria | notebook: `top_category` | |
# | **07.4a** Wczytanie tablic godzinowych | `data/hourly.py`: `load_hourly` | 75 min |
# | 07.4b Kolumna tablic jako jedna tablica | `data/hourly.py`: `to_matrix` | |
# | 07.4c Cztery liczby na dzień | `data/hourly.py`: `summarise_hours` | |
# | 07.4d Zgodność z surową kolumną | notebook: `n_disagree` | |
# | 07.4e Sprzedaż mimo braku towaru | notebook: `share_rows`, `share_sales` | |
# | **07.5a** Czy panel jest posortowany | `data/panel.py`: `is_sorted_panel` | 60 min |
# | 07.5b Lag w obrębie serii | `data/panel.py`: `add_lag` | |
# | 07.5c Średnia krocząca z przeszłości | `data/panel.py`: `add_rolling_mean` | |
# | 07.5d Profil tygodnia | `data/panel.py`: `dow_profile` | |
# | 07.5e Czy lagi coś mówią | notebook: `corr_lag`, `corr_mean` | |
# | **07.6a** Zbiór przetworzony | `data/prepare.py`: `prepare_daily` | 45 min |
# | 07.6b Zapis | `data/prepare.py`: `save_processed` | |
# | 07.6c Odczyt z kontrolą kontraktu | `data/prepare.py`: `load_processed` | |
# | **07.7** Eksploracja | notebook: cztery odpowiedzi pisemne | 45 min |

# %%
# %load_ext autoreload
# %autoreload 2

import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from coursekit import paths
from coursekit.nb import check
from coursekit.plotting import use_course_style
from freshcast.data.schema import DAILY_COLUMNS, DATE, HIERARCHY, SERIES_KEY, TARGET

use_course_style()
pd.set_option("display.max_columns", 30)

RAW = paths.FRN_TRAIN
PROFILE = paths.active_profile()
CITIES = PROFILE.cities
print(f"Profil danych: {PROFILE.name}, miasta w tym labie: {CITIES}")

# %% [markdown]
# `autoreload` sprawia, że po zapisaniu zmiany w pliku pakietu notebook widzi nową wersję bez restartu kernela.
#
# `CITIES` to filtr miast dla Twojego profilu danych. Profil wybrał `course doctor` na podstawie pamięci komputera. Wszystkie obliczenia w tym labie robisz na tym podzbiorze. W profilu `full` `CITIES` to `None`, czyli wszystkie miasta.
#
# Komórka powyżej daje Ci nazwy, których używasz w całym labie:
#
# | Nazwa | Co to jest |
# |---|---|
# | `RAW` | ścieżka (`Path`) do surowego pliku `data/raw/freshretailnet/train.parquet` |
# | `CITIES` | krotka identyfikatorów miast, na przykład `(3,)` w profilu `standard`; `None` w profilu `full` (wszystkie miasta) |
# | `SERIES_KEY` | `["store_id", "product_id"]`, klucz serii. Seria to jeden produkt w jednym sklepie |
# | `DATE` | `"dt"`, kolumna z datą dnia |
# | `TARGET` | `"sale_amount"`, sprzedaż w danym dniu. Tę liczbę będziesz prognozować od modułu 08 |
# | `HIERARCHY` | cztery kolumny ścieżki produktu w katalogu, od najszerszej grupy (`management_group_id`) do najwęższej kategorii (`third_category_id`) |
# | `DAILY_COLUMNS` | lista kolumn bez tablic godzinowych, które `load_sales` czyta domyślnie |
#
# Funkcje w pakiecie nie widzą zmiennych notebooka (`daily`, `CITIES`, `RAW`). Wszystko, czego potrzebują, dostają przez argumenty, a inne funkcje pakietu importują.
#
# Wszystkie te stałe są w `src/freshcast/data/schema.py`. W plikach pakietu importujesz je stamtąd, na przykład `from freshcast.data.schema import DATE, SERIES_KEY`, zamiast pisać nazwy kolumn w cudzysłowie. Na górze pliku z zadaniem są tylko importy potrzebne sygnaturom funkcji (na przykład `import pandas as pd`, `from pathlib import Path`). Importy dla Twojego rozwiązania dopisujesz sam: każdy krok podaje w „Skorzystaj z” linię, którą dopisać i do którego pliku. Dopisuj nazwy wtedy, gdy ich używasz, bo `ruff` zgłasza import, którego nic nie używa.

# %% [markdown]
# ## 07.0 Rozpoznanie pliku, zanim go wczytasz
#
# Plik `train.parquet` ma około 100 MB. To nic nie mówi o tym, ile zajmie w pamięci. Parquet jest skompresowany i kolumnowy, a pandas trzyma dane rozpakowane.
#
# Parquet pozwala przeczytać metadane bez dotykania danych. Zacznij od tego. Z metadanych weźmiesz liczbę wierszy pliku. Pamięć zmierzysz potem w pandas, na próbce `first`, bo metadane mówią o rozmiarze skompresowanym na dysku.

# %%
info = pq.ParquetFile(RAW)
print(f"Na dysku: {RAW.stat().st_size / 1e6:.0f} MB")
print(f"Wiersze: {info.metadata.num_rows:,}")
print(f"Grupy wierszy: {info.metadata.num_row_groups:,}")
print()
print(info.schema_arrow)

# %% [markdown]
# Dwie kolumny mają typ `list`: `hours_sale` i `hours_stock_status`. Każda komórka to 24 liczby, po jednej na godzinę.
#
# Wczytaj tylko pierwszą grupę wierszy (1000 wierszy) i zobacz, jak to wygląda w pandas.

# %%
first = info.read_row_group(0).to_pandas()
first.head(3).T

# %% [markdown]
# ### Ile pamięci zajęłaby całość?
#
# pandas ma metodę `memory_usage(deep=True)`. Zwraca Series: liczbę bajtów dla każdej kolumny. Dla kolumn zagnieżdżonych podaje za mało: liczy obiekt tablicy (nagłówek), ale nie jej dane.
#
# **Cel:** oszacować, ile pamięci zajęłoby wczytanie całego pliku do pandas, zanim spróbujesz to zrobić.
#
# **Gdzie:** komórka poniżej, zmienne `scalar_bytes`, `nested_bytes`, `total_gb`.
#
# **Wejście:**
#
# - `first`: `pd.DataFrame`, pierwsza grupa wierszy pliku (1000 wierszy, wszystkie kolumny),
# - `nested`: lista dwóch nazw kolumn z tablicami godzinowymi,
# - `n_rows_file`: `int`, liczba wierszy całego pliku.
#
# **Wynik:** trzy liczby (`float`):
#
# - `scalar_bytes`: średnia liczba bajtów na wiersz we wszystkich kolumnach poza dwiema zagnieżdżonymi,
# - `nested_bytes`: bajty na wiersz w dwóch kolumnach zagnieżdżonych razem, nagłówek i dane,
# - `total_gb`: oszacowanie dla wszystkich wierszy pliku, w GB (1 GB to 10⁹ bajtów).
#
# **Skorzystaj z:** `memory_usage(deep=True)` i `.sum()`; `.nbytes` tablicy NumPy (moduł 05) daje rozmiar jej danych w bajtach. Pojedynczą komórkę wyjmiesz przez `.iloc[0]`.
#
# **Kroki:**
#
# 1. `scalar_bytes`: suma `memory_usage(deep=True)` wszystkich kolumn poza dwiema zagnieżdżonymi, podzielona przez liczbę wierszy `first`. Domyślnie wynik zawiera też indeks. Możesz go wliczyć albo pominąć: na tych 1000 wierszach to 132 bajty, czyli ułamek bajta na wiersz.
# 2. `nested_bytes`: nagłówek plus dane, dla obu kolumn zagnieżdżonych razem. Nagłówek zmierz: `memory_usage(deep=True, index=False)` dwóch kolumn zagnieżdżonych, zsumowane i podzielone przez liczbę wierszy `first` (wyjdzie około 120 bajtów na komórkę). Dane to `.nbytes` pierwszej komórki każdej z dwóch kolumn. Każda komórka ma 24 liczby tego samego typu, więc pierwsza wystarczy.
# 3. `total_gb`: bajty jednego wiersza (obie części) razy liczba wierszy pliku, przeliczone na GB.
#
# To oszacowanie samej ramki w pandas, a nie szczytu pamięci procesu podczas wczytywania. O szczycie jest mowa pod sprawdzeniem.
#
# **Sprawdzenie:** komórka z `assert` pod spodem wypisuje „Zgadza się.”. Jeśli nie, komunikat mówi, którą liczbę poprawić.

# %%
nested = ["hours_sale", "hours_stock_status"]
n_rows_file = info.metadata.num_rows

# >>> SOLUTION 07.0
scalar_bytes = first.drop(columns=nested).memory_usage(deep=True).sum() / len(first)
header_bytes = first[nested].memory_usage(deep=True, index=False).sum() / len(first)
data_bytes = sum(first[column].iloc[0].nbytes for column in nested)
nested_bytes = header_bytes + data_bytes
total_gb = (scalar_bytes + nested_bytes) * n_rows_file / 1e9
# --- STUB
#| scalar_bytes = ...
#| nested_bytes = ...
#| total_gb = ...
# <<< SOLUTION

print(f"Kolumny skalarne:    {scalar_bytes:6.0f} bajtów na wiersz")
print(f"Kolumny zagnieżdżone: {nested_bytes:6.0f} bajtów na wiersz")
print(f"Cały plik w pandas:  {total_gb:6.1f} GB")

# %%
assert 100 < scalar_bytes < 200, "Policz średnią na wiersz, bez kolumn zagnieżdżonych."
assert 550 < nested_bytes < 700, "Dwie kolumny, w każdej nagłówek i 24 liczby po 8 bajtów."
assert 2.5 < total_gb < 4.0
print("Zgadza się.")

# %% [markdown]
# Ponad 80% pamięci zjadają dwie kolumny, których do większości zadań nie potrzebujesz.
#
# To i tak zaniżony rachunek. Podczas wczytywania przez chwilę istnieją dwie kopie danych, tabela Arrow i ramka pandas. Zmierzony szczyt przy `pd.read_parquet(RAW)` na całym pliku to 7,5 GB. W WSL na laptopie z 16 GB RAM kończy się to zabiciem procesu.
#
# Wniosek na resztę kursu: **wybieraj kolumny i wiersze przy czytaniu, a nie po nim.**

# %% [markdown]
# ## 07.1 Wczytanie
#
# **Cel:** wczytać z pliku tylko te kolumny i miasta, których potrzebujesz, w małych typach i w kolejności serii i dni. Wynik tej funkcji, ramka `daily`, jest punktem startu wszystkich kolejnych zadań.
#
# **Gdzie:** `src/freshcast/data/load.py`, dwie funkcje: 07.1a `shrink_integers` i 07.1b `load_sales`. Potem 07.1c w notebooku.
#
# Dlaczego sortowanie już tutaj? Plik nie jest posortowany. Lagi i okna kroczące, które policzysz w 07.5, czytają "poprzedni wiersz tej samej serii". Na nieposortowanych danych dają bzdury bez żadnego błędu.
#
# ### 07.1a `shrink_integers`
#
# **Cel:** zmniejszyć pamięć kolumn całkowitych bez zmiany żadnej wartości.
#
# **Gdzie:** `src/freshcast/data/load.py`, funkcja `shrink_integers(df)`.
#
# **Wejście:** `df`: `pd.DataFrame`, dowolna ramka. W tym labie to wiersze sprzedaży prosto z pliku Parquet. Kolumny całkowite (`store_id`, `product_id`, `city_id`, flagi) mają tam typ `int64` albo `int32`.
#
# **Wynik:** nowy `pd.DataFrame` z tymi samymi wierszami, indeksem, wartościami i kolejnością kolumn. Każda kolumna całkowita ma najmniejszy typ całkowity ze znakiem, który mieści jej wartości: `int8`, `int16`, `int32` albo `int64`. Kolumny `float64`, daty i tekst zostają bez zmian. Ramki wejściowej nie zmieniasz.
#
# **Skorzystaj z:**
#
# - `pd.to_numeric(kolumna, downcast="integer")` z wykładu (sekcja „Typy”): zwraca kolumnę w najmniejszym pasującym typie,
# - `df.select_dtypes("integer")`: ramka złożona tylko z kolumn całkowitych; jej `.columns` to ich nazwy,
# - `df.assign(...)` z modułu 06: zwraca nową ramkę z podmienionymi lub dodanymi kolumnami.
#
# Importu nie dopisujesz: `import pandas as pd` jest już na górze `load.py`.
#
# **Kroki:**
#
# 1. Ustal nazwy kolumn całkowitych ramki.
# 2. Dla każdej policz zmniejszoną wersję przez `pd.to_numeric` z `downcast`.
# 3. Zbierz wyniki w słownik: nazwa kolumny → nowa kolumna.
# 4. Zwróć kopię ramki z podmienionymi kolumnami, jednym wywołaniem `assign`.
#
# **Sprawdzenie:** `check("07.1")` testuje najpierw tę funkcję na ramce z trzema kolumnami: liczby 1, 2, 3, liczba 3 000 000 000 i ułamki. Jeśli ten krok działa, a `load_sales` jeszcze nie, zobaczysz ⬜.
#
# ### 07.1b `load_sales`
#
# **Cel:** wczytać dzienną sprzedaż wybranych miast tak, żeby pamięć zależała od rozmiaru wyniku, a nie pliku.
#
# **Gdzie:** `src/freshcast/data/load.py`, funkcja `load_sales(path, cities=..., columns=...)`.
#
# **Wejście:**
#
# - `path`: `Path`, surowy plik Parquet. W notebooku to `RAW`. Jeden wiersz pliku to sprzedaż jednego produktu w jednym sklepie w jednym dniu. Kolumna `dt` jest w pliku tekstem, na przykład `"2024-03-28"`.
# - `cities`: `Sequence[int] | None`, identyfikatory miast (`city_id`) do zostawienia. W notebooku to `CITIES`. `None` znaczy: wszystkie miasta.
# - `columns`: `Sequence[str]`, nazwy kolumn do wczytania, w kolejności, którą chcesz mieć w wyniku. Domyślnie `DAILY_COLUMNS`. Zawsze zawiera `store_id`, `product_id` i `dt`. `city_id` nie musi być na liście: filtr miast działa i bez niej.
#
# **Wynik:** `pd.DataFrame`, jeden wiersz na serię i dzień:
#
# - dokładnie kolumny z `columns`, w tej kolejności,
# - wiersze posortowane po `store_id`, potem `product_id`, potem `dt`,
# - indeks od nowa: 0, 1, ..., n-1,
# - `dt` ma typ `datetime64`, kolumny całkowite są zmniejszone, `float64` zostają.
#
# **Skorzystaj z:**
#
# - `shrink_integers` z kroku 07.1a. Jest w tym samym pliku, więc wywołujesz ją po nazwie.
# - Stałych `CITY`, `DATE`, `SERIES_KEY` z `schema.py`. Na górze `load.py` jest już `from freshcast.data.schema import DAILY_COLUMNS`. Rozszerz tę linię do `from freshcast.data.schema import CITY, DAILY_COLUMNS, DATE, SERIES_KEY`.
# - `pd.read_parquet` z argumentami `columns` i `filters` oraz `pd.to_datetime(..., format="%Y-%m-%d")` z wykładu (sekcja „Czytaj mniej, niż jest w pliku”).
# - `sort_values` i `reset_index(drop=True)` z modułu 06.
#
# **Kroki:**
#
# 1. Zbuduj filtr miast w formie z wykładu: lista warunków `(kolumna, operator, wartość)`. Gdy `cities` to `None`, filtra nie ma (`None`).
# 2. Wczytaj plik: tylko kolumny z `columns`, z tym filtrem.
# 3. Zamień `dt` z tekstu na datę.
# 4. Zmniejsz typy całkowite funkcją z 07.1a.
# 5. Posortuj po kluczu serii i dacie. Ponumeruj wiersze od zera, wyrzucając stary indeks.
#
# **Sprawdzenie:** `check("07.1")` pokazuje ✅. Komórki pod nim wczytują `daily` z prawdziwego pliku i sprawdzają kolumny, indeks, typ daty i miasta.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `pd.read_parquet` przyjmuje argumenty `columns` i `filters`. Oba działają przed wczytaniem danych do pamięci. Do zmniejszania typów służy `pd.to_numeric` z argumentem `downcast`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Filtr zapisujesz jako listę krotek `(kolumna, operator, wartość)`. Operator `"in"` przyjmuje listę wartości. Gdy `cities` to `None`, filtr też ma być `None`.
#
# W `shrink_integers` wybierz kolumny całkowite przez `df.select_dtypes("integer")`, policz dla każdej zmniejszoną wersję i podmień je jednym wywołaniem `df.assign(...)`. `assign` zwraca nową ramkę, więc wejścia nie zmieniasz.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# filters = None if cities is None else [(CITY, "in", list(cities))]
# df = pd.read_parquet(path, columns=list(columns), filters=filters)
# # teraz: data, shrink_integers, sort_values po [*SERIES_KEY, DATE], reset_index(drop=True)
# ```
#
# `assign` z nazwą kolumny trzymaną w zmiennej: `df.assign(**{DATE: ...})`.
#
# </details>

# %%
check("07.1")

# %% [markdown]
# Teraz użyj swojej funkcji na prawdziwych danych. Od tej komórki `daily` to Twoja tabela sprzedaży: jeden wiersz to sprzedaż jednej serii (sklep × produkt) w jednym dniu, kolumny `DAILY_COLUMNS`.

# %%
from freshcast.data.load import load_sales

daily = load_sales(RAW, cities=CITIES)
print(f"{len(daily):,} wierszy, {daily.memory_usage(deep=True).sum() / 1e6:.1f} MB")
daily.dtypes

# %%
# Step 07.1b on the real file: columns, index, date type, cities.
assert list(daily.columns) == DAILY_COLUMNS, "daily ma mieć kolumny DAILY_COLUMNS, w tej kolejności."
assert daily.index.equals(pd.RangeIndex(len(daily))), "Indeks daily ma biec od 0 do n-1."
assert pd.api.types.is_datetime64_any_dtype(daily[DATE]), "dt ma być datą (datetime64)."
assert CITIES is None or set(daily["city_id"]) == set(CITIES), "W daily są wiersze spoza Twoich miast."
print(f"daily: {daily.groupby(SERIES_KEY).ngroups:,} serii, {daily[DATE].nunique()} dni. Zgadza się.")

# %% [markdown]
# ### 07.1c Ile pamięci zaoszczędziłeś
#
# **Cel:** zmierzyć, ile dały małe typy i data zamiast tekstu.
#
# **Gdzie:** komórka poniżej, zmienna `saving`.
#
# **Wejście:** `plain`: te same wiersze i kolumny wczytane bez zmian typów (komórka tworzy ją za Ciebie); `daily`: wynik `load_sales`.
#
# **Wynik:** `saving`: `float` od 0 do 1, ułamek pamięci zaoszczędzony względem `plain`. 0.25 znaczy: `daily` zajmuje o 25% mniej niż `plain`.
#
# **Skorzystaj z:** `memory_usage(deep=True).sum()`, jak w 07.0, tak samo dla obu ramek. Porównujesz cały efekt `load_sales` (data i typy całkowite), a nie rozmiar pliku Parquet.
#
# **Kroki:** policz pamięć obu ramek w bajtach. Oszczędność to 1 minus stosunek pamięci `daily` do pamięci `plain`.
#
# **Sprawdzenie:** wydruk pokazuje procent, a komórka pod nim sprawdza, czy to ułamek od 0 do 1.

# %%
filters = None if CITIES is None else [("city_id", "in", list(CITIES))]
plain = pd.read_parquet(RAW, columns=DAILY_COLUMNS, filters=filters)

# >>> SOLUTION 07.1
before = plain.memory_usage(deep=True).sum()
after = daily.memory_usage(deep=True).sum()
saving = 1 - after / before
# --- STUB
#| saving = ...
# <<< SOLUTION

print(f"Oszczędność: {saving:.0%}")

# %%
assert isinstance(saving, float) and 0 < saving < 1, "saving to ułamek od 0 do 1, na przykład 0.25."
print("Zgadza się.")

# %% [markdown]
# Większość zysku dają kolumny całkowite: identyfikator miasta mieści się w 1 bajcie zamiast 8, flagi w 1 zamiast 4. Data zamiast tekstu oszczędza kolejne 10 bajtów na wiersz i, co ważniejsze, pozwala liczyć na datach: odejmować je, wyciągać dzień tygodnia, sortować chronologicznie.
#
# Kolumn zmiennoprzecinkowych nie ruszamy. `float32` ma około 7 cyfr znaczących, więc sumy i średnie na milionach wierszy zaczynają się rozjeżdżać. Pamięć oszczędzona na floatach nie jest warta błędów, których nikt nie zauważy.

# %% [markdown]
# ## 07.2 Reguły i anomalie
#
# **Cel:** zanim cokolwiek policzysz, sprawdzić, czy dane są tym, za co je bierzesz. Zasada tego kursu: **cicha zła prognoza jest gorsza niż błąd**. Funkcja walidująca ma się wywrócić głośno, z liczbą złych wierszy w komunikacie.
#
# **Gdzie:** najpierw notebook (07.2a śledztwo, 07.2b wniosek), potem `src/freshcast/data/validate.py`: 07.2c `check_panel` i 07.2d `clean_discount`.
#
# ### 07.2a Najpierw śledztwo
#
# Odpowiedz kodem na pięć pytań. To jest eksploracja: liczy się wynik, a nie forma kodu. Każdy wynik zapisujesz do zmiennej o podanej nazwie.
#
# Wszystkie pytania zadajesz ramce `daily` z 07.1: jeden wiersz to sprzedaż jednej serii w jednym dniu. Para (seria, dzień) to trzy kolumny: `[*SERIES_KEY, DATE]`.
#
# **Pytanie 1.** **Gdzie:** `n_duplicated`. **Wynik:** `int`, liczba wierszy, które powtarzają parę (seria, dzień) z wcześniejszego wiersza. Pierwsze wystąpienie pary się nie liczy. **Skorzystaj z:** `df.duplicated(lista_kolumn)` z wykładu (sekcja „Reguły zamiast nadziei”) daje True przy każdym powtórzeniu, a `.sum()` liczy wartości True.

# %%
# Pytanie 1: ile wierszy powtarza parę (seria, dzień)?
# >>> SOLUTION 07.2
n_duplicated = int(daily.duplicated([*SERIES_KEY, DATE]).sum())
# --- STUB
#| n_duplicated = ...
# <<< SOLUTION
print(n_duplicated)

# %% [markdown]
# **Pytanie 2.** **Gdzie:** `days_distribution`. **Wynik:** `pd.Series`: indeks to liczba dni w serii, wartość to liczba serii, które mają tyle dni. Pytanie 1 pokazało, że żadna para (seria, dzień) się nie powtarza, więc liczba wierszy serii to liczba jej dni. **Skorzystaj z:** `groupby(SERIES_KEY).size()` daje liczbę wierszy każdej serii. `value_counts()` na tym wyniku liczy, ile razy występuje każda wartość.

# %%
# Pytanie 2: ile dni ma każda seria? Pokaż rozkład (ile serii ma ile dni).
# >>> SOLUTION 07.2
days_per_series = daily.groupby(SERIES_KEY).size()
days_distribution = days_per_series.value_counts()
# --- STUB
#| days_distribution = ...
# <<< SOLUTION
print(days_distribution)

# %%
# Questions 1 and 2 hold for every data profile: the raw file is a complete panel.
assert n_duplicated == 0, "W tym zbiorze żadna para (seria, dzień) się nie powtarza. Sprawdź listę kolumn klucza."
assert list(days_distribution.index) == [90], "Każda seria ma 90 dni. Sprawdź, po czym grupujesz."
print("Zgadza się.")

# %% [markdown]
# **Pytanie 3.** `discount` to mnożnik ceny: 1.0 to cena regularna, 0.8 to 20% taniej. Zakres, czyli minimum i maksimum, wypisz sam w tej samej komórce: `print(daily["discount"].describe())`. Do zmiennych zapisujesz tylko dwa liczniki. **Gdzie:** `n_zero`, `n_above_one`. **Wynik:** dwa `int`: liczba wierszy z `discount` równym dokładnie 0 i liczba wierszy z `discount` większym niż 1. **Skorzystaj z:** `describe()` pokazuje minimum, maksimum i kwartyle kolumny. Porównanie kolumny z liczbą daje Series True/False, a jej `.sum()` liczy wartości True.

# %%
# Pytanie 3: jaki jest zakres kolumny discount? Ile wierszy ma dokładnie 0,
# a ile więcej niż 1?
# >>> SOLUTION 07.2
print(daily["discount"].describe())
n_zero = int((daily["discount"] == 0).sum())
n_above_one = int((daily["discount"] > 1).sum())
# --- STUB
#| n_zero = ...
#| n_above_one = ...
# <<< SOLUTION
print(f"discount == 0: {n_zero}, discount > 1: {n_above_one}")

# %% [markdown]
# `discount` to mnożnik ceny: 1.0 oznacza cenę regularną, 0.8 oznacza 20% taniej. Dokumentacja zbioru mówi tylko tyle. O wartości 0 milczy.
#
# Zero może znaczyć dwie rzeczy: produkt rozdawany za darmo albo znacznik "nie zapisano". Zbierz dowody, zanim zdecydujesz.

# %% [markdown]
# **Pytanie 4.** **Gdzie:** `zero_days`. **Wynik:** `pd.DataFrame` z kolumnami `store_id`, `product_id`, `zero_days`. Jeden wiersz na serię, tylko serie, które mają choć jeden dzień z `discount == 0`. `zero_days` to liczba takich dni w serii (`int`). **Skorzystaj z:** kolumna pomocnicza True/False dodana przez `assign`, potem `groupby(SERIES_KEY, as_index=False)` z nazwaną agregacją (wykład, sekcja „groupby”). Suma kolumny True/False to liczba wartości True. Na końcu zostaw wiersze z `zero_days > 0`.

# %%
# Pytanie 4: weź serie, które mają choć jeden wiersz z discount == 0.
# Dla każdej policz, w ilu dniach rabat wynosił 0 (kolumna zero_days).
# >>> SOLUTION 07.2
is_zero = daily["discount"] == 0
zero_days = (
    daily.assign(is_zero=is_zero)
    .groupby(SERIES_KEY, as_index=False)
    .agg(zero_days=("is_zero", "sum"))
    .query("zero_days > 0")
)
# --- STUB
#| zero_days = ...
# <<< SOLUTION
print(f"Serie z zerem: {len(zero_days)}")
print(zero_days["zero_days"].value_counts().sort_index())

# %% [markdown]
# **Pytanie 5.** **Gdzie:** `comparison`. **Wynik:** `pd.DataFrame` o dwóch wierszach: dni z `discount == 0` i pozostałe dni tych samych serii. Kolumny: `mean_sales` (średnia `sale_amount`), `rows` (liczba wierszy), `activity_share` (ułamek od 0 do 1 wierszy z `activity_flag == 1`; ta flaga znaczy, że w tym dniu produkt był objęty akcją promocyjną). Etykiety wierszy możesz zostawić jako True/False albo nadać im czytelne nazwy. **Skorzystaj z:** `zero_days[SERIES_KEY]` z pytania 4 jako listy serii. `merge` z jawnym `on`, `how` i `validate` (wykład, sekcja „Fakty, wymiary i merge”) zostawi w `daily` tylko wiersze tych serii. Potem `groupby` po warunku `discount == 0` i nazwane agregacje. Średnia kolumny z zerami i jedynkami to udział jedynek.

# %%
# Pytanie 5: w tych samych seriach porównaj dni z discount == 0 z pozostałymi:
# średnia sprzedaż, liczba wierszy, udział wierszy z activity_flag == 1.
# >>> SOLUTION 07.2
affected = daily.merge(
    zero_days[SERIES_KEY], on=SERIES_KEY, how="inner", validate="many_to_one"
)
comparison = affected.groupby(affected["discount"] == 0).agg(
    mean_sales=(TARGET, "mean"),
    rows=(TARGET, "size"),
    activity_share=("activity_flag", "mean"),
)
comparison.index = comparison.index.map({False: "discount > 0", True: "discount == 0"})
# --- STUB
#| comparison = ...
# <<< SOLUTION
comparison

# %% [markdown]
# ### 07.2b Twój wniosek
#
# To, co widzisz, zależy od profilu danych. W całym zbiorze są dwa wzorce:
#
# - Dwa produkty mają zero prawie we wszystkie dni, w każdym sklepie. Sprzedają się 10-15 razy lepiej niż przeciętny produkt i prawie nigdy nie mają flagi akcji.
# - Sześć innych produktów ma zero w pojedyncze dni, zawsze z `activity_flag == 1`. Sprzedaż jest wtedy około trzy razy wyższa niż w pozostałe dni tych samych serii.
#
# Drugi wzorzec wygląda jak prawdziwe rozdawnictwo w ramach akcji. Pierwszy może być produktem zawsze darmowym albo produktem, dla którego rabatu nikt nie zapisuje. Z danych tego nie rozstrzygniesz.
#
# **Gdzie:** komórka „Twój wniosek” poniżej. **Wynik:** dwa do czterech zdań własnymi słowami: co wiesz na pewno, czego nie wiesz i co w związku z tym zrobisz z wartością 0. **Sprawdzenie:** nie ma automatycznego. Jeśli pracujesz z tutorem, omów z nim swój wniosek.

# %% [markdown]
# *Twój wniosek:*

# %% [markdown]
# ### Decyzja
#
# W tym kursie przyjmujemy taką decyzję. Zero, czymkolwiek jest, nie zachowuje się jak dolny koniec tej samej skali co 0.8 czy 0.6. Gdyby zostało liczbą, model liniowy potraktowałby je jako "rabat dwa razy głębszy niż 0.5" i dopasował do niego całą zależność sprzedaży od ceny. Dlatego zdejmujemy je ze skali: `discount` staje się `NaN`, a osobna kolumna `discount_is_zero` pamięta, gdzie zero było. Żadna informacja nie ginie.
#
# Nie robimy `fillna(1.0)`. "Nie wiem, co znaczy ta wartość" i "rabatu nie było" to dwie różne informacje, a wpisanych po cichu jedynek nikt później nie odróżni od prawdziwych.
#
# W całym zbiorze są też 34 wiersze z rabatem powyżej 1, najwyżej 1.088, w dwóch miastach spoza Twojego profilu. To cena o kilka procent wyższa od regularnej: nieudokumentowana, ale leżąca na tej samej skali. Zostawiamy ją. Sprawdzenie używa próbki, która takie wiersze zawiera. To częsta sytuacja: reguła napisana na podzbiorze spotyka dane, których autor nie widział.
#
# ### 07.2c `check_panel`
#
# **Cel:** zamienić założenia o panelu na kod, który zatrzyma pipeline, zanim złe dane trafią do lagów i modelu. Lagi z 07.5 liczą "7 wierszy wstecz" i są poprawne tylko wtedy, gdy 7 wierszy wstecz to 7 dni wstecz.
#
# **Gdzie:** `src/freshcast/data/validate.py`, funkcja `check_panel(df)`.
#
# **Wejście:** `df`: `pd.DataFrame`, dzienna sprzedaż, jeden wiersz na serię i dzień. W notebooku to `daily` z 07.1. Używasz kolumn `store_id`, `product_id`, `dt` (data) i `sale_amount`. Pozostałe pomijasz.
#
# **Wynik:** nic (`None`). Funkcja niczego nie zwraca i niczego nie zmienia. Gdy reguła jest złamana, rzuca `ValueError` z liczbą w komunikacie. Reguły sprawdzasz w kolejności z docstringa:
#
# 1. brak wartości (NaN) w kluczu serii, dacie albo sprzedaży: liczysz wiersze,
# 2. powtórzona para (seria, dzień): liczysz wiersze po pierwszym wystąpieniu pary, jak w pytaniu 1. Dwa identyczne klucze dają liczbę 1,
# 3. seria bez kompletu dni od najwcześniejszej do najpóźniejszej daty całej ramki, oba końce włącznie: liczysz serie,
# 4. ujemna sprzedaż: liczysz wiersze.
#
# Kolejności wierszy ta funkcja nie sprawdza. Tym zajmie się `is_sorted_panel` w 07.5a.
#
# **Skorzystaj z:**
#
# - pytań 1 i 2 ze śledztwa 07.2a: to prawie reguły 2 i 3,
# - wzorca „policz, sprawdź, rzuć” z wykładu (sekcja „Reguły zamiast nadziei”) i z `check_raw` w labie 06 (06.2),
# - `isna()` z modułu 06; `.any(axis=1)` daje True dla wiersza, w którym choć jedna kolumna ma True,
# - odejmowania dat: różnica dwóch dat to odstęp czasu, a jego `.days` to liczba dni,
# - stałych `SERIES_KEY`, `DATE`, `TARGET` z `schema.py`. W `validate.py` jest tylko `import pandas as pd`. Dopisz pod nim `from freshcast.data.schema import DATE, SERIES_KEY, TARGET`.
#
# **Kroki:**
#
# 1. Dla każdej reguły policz jedną liczbę: ile wierszy (w regule 3: serii) ją łamie. Zamień ją na `int`.
# 2. Jeśli liczba jest większa od zera, rzuć `ValueError` z tą liczbą w komunikacie.
# 3. W regule 3 najpierw ustal, ile dni powinna mieć każda seria (od najwcześniejszej do najpóźniejszej daty ramki), potem porównaj z liczbą wierszy każdej serii. To wystarcza, bo reguła 2 wykluczyła już duplikaty.
#
# **Sprawdzenie:** `check("07.2")` testuje najpierw `check_panel`. Poprawny panel z próbki ma przejść bez błędu. Cztery zepsute wersje mają rzucić `ValueError`: powtórzony wiersz, brak jednego dnia w środku serii, NaN w sprzedaży, ujemna sprzedaż.
#
# ### 07.2d `clean_discount`
#
# **Cel:** zdjąć zero rabatu ze skali liczbowej i nie zgubić informacji, gdzie było.
#
# **Gdzie:** `src/freshcast/data/validate.py`, funkcja `clean_discount(df)`.
#
# **Wejście:** `df`: `pd.DataFrame`, dzienna sprzedaż z kolumną `discount` (`float`, mnożnik ceny: 1.0 to cena regularna, 0.8 to 20% taniej). W notebooku to `daily` po `check_panel`.
#
# **Wynik:** nowy `pd.DataFrame`, te same wiersze, kolejność i indeks:
#
# - `discount`: 0 zamienione na `NaN`, każda inna wartość bez zmian, także powyżej 1,
# - nowa kolumna `discount_is_zero` (`bool`) na końcu: True tam, gdzie było zero, False wszędzie indziej,
# - ramki wejściowej nie zmieniasz,
# - rabat ujemny albo `NaN` w `discount` już na wejściu: `ValueError` z liczbą takich wierszy.
#
# **Skorzystaj z:**
#
# - stałych `DISCOUNT` i `DISCOUNT_IS_ZERO` z `schema.py`. Rozszerz linię importu z 07.2c w `validate.py` do `from freshcast.data.schema import DATE, DISCOUNT, DISCOUNT_IS_ZERO, SERIES_KEY, TARGET`,
# - `Series.mask(warunek)`: zwraca kopię, w której tam, gdzie warunek jest True, stoi `NaN` (wykład, sekcja „Wartość, która nie pasuje do skali”),
# - `df.assign(**{NAZWA: wartości})`: `assign`, gdy nazwa kolumny siedzi w zmiennej (wykład, sekcja „Typy”).
#
# **Kroki:**
#
# 1. Sprawdź wejście: policz wiersze z rabatem ujemnym albo brakującym. Jeśli są, rzuć błąd.
# 2. Zbuduj maskę True/False „rabat równy 0”.
# 3. Zwróć kopię, w której `discount` ma `NaN` pod maską, a sama maska jest nową kolumną.
#
# **Sprawdzenie:** `check("07.2")` pokazuje ✅. W próbce są 3 wiersze z zerem i rabat 1.088, który ma zostać. Komórki pod sprawdzeniem uruchamiają obie funkcje na `daily` i potwierdzają wynik.
#
# Komórka z `daily = clean_discount(daily)` nadpisuje `daily`. Drugie uruchomienie zgłosi `ValueError`, bo w `discount` są już braki (`NaN`). Wtedy uruchom ponownie komórkę z `load_sales` w 07.1b, a dopiero potem tę.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Każda reguła w `check_panel` to jedno pytanie do ramki, na które odpowiedzią jest liczba. Jeśli liczba jest większa od zera, rzucasz wyjątek. Trzy z czterech pytań zadałeś już w śledztwie powyżej.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Kompletność: policz, ile dni powinien mieć panel (od najwcześniejszej do najpóźniejszej daty, włącznie), i porównaj z liczbą wierszy każdej serii. Skoro wcześniej wykluczyłeś duplikaty, seria z właściwą liczbą wierszy nie ma luk.
#
# W `clean_discount` przyda się `Series.mask(warunek)`, który wstawia `NaN` tam, gdzie warunek jest prawdziwy.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# expected_days = (df[DATE].max() - df[DATE].min()).days + 1
# days_per_series = df.groupby(SERIES_KEY, sort=False).size()
# incomplete = int((days_per_series != expected_days).sum())
# if incomplete:
#     raise ValueError(f"{incomplete} series do not cover all {expected_days} days.")
# ```
#
# Pozostałe trzy reguły mają ten sam kształt: policz, sprawdź, rzuć.
#
# </details>

# %%
check("07.2")

# %%
from freshcast.data.validate import check_panel, clean_discount

check_panel(daily)
daily = clean_discount(daily)
print(f"Wiersze z zerowym rabatem: {int(daily['discount_is_zero'].sum())}")

# %%
# Step 07.2d on the real data: the flag and the NaN sit in the same rows.
assert daily["discount_is_zero"].dtype == bool, "discount_is_zero ma być typu bool."
assert int(daily["discount"].isna().sum()) == int(daily["discount_is_zero"].sum()), (
    "NaN w discount mają stać dokładnie tam, gdzie discount_is_zero jest True."
)
assert not (daily["discount"] == 0).any(), "W discount zostały zera."
print("Zgadza się.")

# %% [markdown]
# ## 07.3 Wymiary i złączenia
#
# **Cel:** opisać sklepy i produkty w osobnych tabelach i dołączać je do sprzedaży tak, żeby żaden wiersz sprzedaży nie zginął ani się nie podwoił.
#
# **Gdzie:** `src/freshcast/data/dims.py`: 07.3a `build_store_dim`, 07.3b `build_product_dim`, 07.3c `attach_dim`. Potem 07.3d w notebooku.
#
# Tabela, którą trzymasz w `daily`, to **tabela faktów**: jeden wiersz to jedno zdarzenie (sprzedaż serii w danym dniu). Informacje opisujące sklep albo produkt, które nie zmieniają się z dnia na dzień, trzyma się osobno w **tabelach wymiarów**: jeden wiersz na sklep, jeden wiersz na produkt.
#
# Powody są dwa. Pamięć: hierarchia produktu to cztery kolumny powtórzone w każdym wierszu. I jedno źródło prawdy: jeśli produkt zmieni kategorię, poprawiasz jeden wiersz.
#
# Wymiar dołączasz do faktów przez `merge`. I tu jest pułapka, którą zobaczysz na własne oczy.
#
# Komórka poniżej wczytuje Twoim `load_sales` ramkę `hierarchy`: klucz serii, datę i cztery kolumny `HIERARCHY`. Potrzebujesz jej, bo `daily` tych kolumn nie ma (nie ma ich w `DAILY_COLUMNS`). `hierarchy` będzie wejściem kroku 07.3b. `product_paths` to unikalne ścieżki produktów, a `broken_dim` to ten sam wymiar z trzema produktami wpisanymi dwa razy.

# %%
hierarchy = load_sales(RAW, cities=CITIES, columns=[*SERIES_KEY, DATE, *HIERARCHY])
product_paths = hierarchy[["product_id", *HIERARCHY]].drop_duplicates()

# Ktoś przez pomyłkę wpisał trzy produkty dwa razy.
broken_dim = pd.concat([product_paths, product_paths.head(3)], ignore_index=True)

merged = daily.merge(broken_dim, on="product_id", how="left")
print(f"Wiersze przed: {len(daily):,}")
print(f"Wiersze po:    {len(merged):,}")
print(f"Sprzedaż przed: {daily[TARGET].sum():,.1f}")
print(f"Sprzedaż po:    {merged[TARGET].sum():,.1f}")

# %% [markdown]
# Żadnego błędu, żadnego ostrzeżenia. Trzy zduplikowane klucze w wymiarze podwoiły wszystkie wiersze tych produktów i zawyżyły sprzedaż. W raporcie wyglądałoby to jak dobry miesiąc.
#
# `merge` ma na to argument `validate`. Uruchom komórkę i przeczytaj komunikat.

# %%
try:
    daily.merge(broken_dim, on="product_id", how="left", validate="many_to_one")
except pd.errors.MergeError as error:
    print(f"MergeError: {error}")

# %% [markdown]
# Reguła kursu: **każdy `merge` ma jawne `on`, `how` i `validate`.**
#
# ### 07.3a `build_store_dim`
#
# **Cel:** tabela wymiaru sklepu: w jakim mieście leży, ile produktów sprzedaje i ile średnio sprzedaje jedna jego seria.
#
# **Gdzie:** `src/freshcast/data/dims.py`, funkcja `build_store_dim(df)`.
#
# **Wejście:** `df`: `pd.DataFrame`, dzienna sprzedaż, jeden wiersz na serię i dzień. W notebooku to `daily` po 07.2. Używasz kolumn `store_id`, `city_id`, `product_id`, `sale_amount`.
#
# **Wynik:** nowy `pd.DataFrame`, jeden wiersz na sklep, kolumny w tej kolejności:
#
# - `store_id`,
# - `city_id`: miasto sklepu,
# - `n_products`: liczba różnych produktów w sklepie (`int`),
# - `mean_sales`: średnia `sale_amount` ze wszystkich wierszy sklepu, czyli średnia dzienna sprzedaż jednej jego serii (`float`).
#
# Wiersze posortowane po `store_id`, indeks 0..n-1. `city_id` jest stałą cechą sklepu. `n_products` i `mean_sales` to statystyki policzone na ramce, którą dostajesz: dla innego okresu albo innych miast wyjdą inne. `mean_sales` nie jest średnim dziennym obrotem całego sklepu. Sklep, który występuje w więcej niż jednym mieście: `ValueError` z liczbą takich sklepów.
#
# **Skorzystaj z:**
#
# - `groupby("store_id", as_index=False).agg(...)` z nazwanymi agregacjami. Wykład (sekcja „groupby”) pokazuje prawie ten sam przykład,
# - `nunique`: liczba różnych wartości w grupie,
# - stałych `CITY` i `TARGET` z `schema.py`. W `dims.py` jest tylko `import pandas as pd`. Dopisz pod nim `from freshcast.data.schema import CITY, TARGET`.
#
# **Kroki:**
#
# 1. Sprawdź regułę: policz różne miasta w każdym sklepie. Sklepy z więcej niż jednym miastem to błąd.
# 2. Zwiń ramkę do jednego wiersza na sklep: miasto (skoro jest jedno, wystarczy pierwsze), liczba różnych produktów, średnia sprzedaż.
# 3. Posortuj po `store_id` i ponumeruj wiersze od zera.
#
# **Sprawdzenie:** `check("07.3")` testuje najpierw tę funkcję: kolumny, kolejność sklepów, miasto i liczbę produktów, `mean_sales` sklepu 70, błąd dla sklepu w dwóch miastach.
#
# ### 07.3b `build_product_dim`
#
# **Cel:** tabela wymiaru produktu: jego ścieżka w katalogu i liczba sklepów, które go sprzedają.
#
# **Gdzie:** `src/freshcast/data/dims.py`, funkcja `build_product_dim(df)`.
#
# **Wejście:** `df`: `pd.DataFrame` z kolumnami `product_id`, `store_id` i czterema kolumnami `HIERARCHY` (`management_group_id`, `first_category_id`, `second_category_id`, `third_category_id`). W notebooku to `hierarchy`, nie `daily`.
#
# **Wynik:** nowy `pd.DataFrame`, jeden wiersz na produkt, kolumny w tej kolejności: `product_id`, cztery kolumny hierarchii, `n_stores` (liczba różnych sklepów, `int`). Wiersze posortowane po `product_id`, indeks 0..n-1. Produkt z więcej niż jedną ścieżką w hierarchii: `ValueError`. Liczba w komunikacie to liczba powtórzeń `product_id` wśród unikalnych ścieżek, czyli ścieżek nadmiarowych: produkt z dwiema ścieżkami daje 1, z trzema daje 2.
#
# **Skorzystaj z:**
#
# - `drop_duplicates()` z modułu 06: na kolumnach produkt + hierarchia daje unikalne ścieżki,
# - `duplicated()` na samej kolumnie `product_id`, jak w pytaniu 1 z 07.2a,
# - `groupby` z `nunique`, jak w 07.3a,
# - `merge` z `validate="one_to_one"`: obie części mają po jednym wierszu na produkt,
# - stałej `HIERARCHY` z `schema.py`. Rozszerz linię importu z 07.3a w `dims.py` do `from freshcast.data.schema import CITY, HIERARCHY, TARGET`.
#
# Nie wybieraj jednej ścieżki z grupy (na przykład pierwszej). Produkt pod dwiema ścieżkami ma dać błąd, a nie po cichu jedną z nich.
#
# **Kroki:**
#
# 1. Wyciągnij unikalne ścieżki: produkt i jego cztery kolumny hierarchii.
# 2. Policz powtórzenia `product_id` wśród unikalnych ścieżek (pierwsze wystąpienie się nie liczy). Jeśli są, rzuć błąd z tą liczbą.
# 3. Policz różne sklepy każdego produktu.
# 4. Dołącz te liczby do ścieżek po `product_id`, posortuj i ponumeruj wiersze od zera.
#
# **Sprawdzenie:** `check("07.3")` sprawdza kolejność produktów, `n_stores`, kolumny hierarchii i błąd dla produktu z dwiema ścieżkami.
#
# ### 07.3c `attach_dim`
#
# **Cel:** dołączyć kolumny wymiaru do faktów z gwarancją: ani jednego wiersza więcej, ani jednego mniej.
#
# **Gdzie:** `src/freshcast/data/dims.py`, funkcja `attach_dim(fact, dim, on)`.
#
# **Wejście:**
#
# - `fact`: `pd.DataFrame`, tabela faktów, wiele wierszy na klucz. W notebooku to `daily`.
# - `dim`: `pd.DataFrame`, wymiar, dokładnie jeden wiersz na klucz, na przykład `product_dim` z 07.3b.
# - `on`: `str`, nazwa kolumny klucza, obecna w obu ramkach, na przykład `"product_id"`.
#
# **Wynik:** nowy `pd.DataFrame`: wszystkie kolumny `fact`, za nimi pozostałe kolumny `dim`. Tyle wierszy co `fact`, w tej samej kolejności, indeks 0..n-1, bez kolumn pomocniczych. Błędy:
#
# - klucz powtórzony w `dim`: `pd.errors.MergeError`. Rzuca go sam `merge`, gdy podasz `validate`,
# - klucz z `fact`, którego nie ma w `dim`: `ValueError` z liczbą wierszy faktów bez pary.
#
# **Skorzystaj z:** demonstracji powyżej (`validate`) i wzorca z `indicator=True` z wykładu (sekcja „Fakty, wymiary i merge”). Importu nie dopisujesz: `pd.errors.MergeError` rzuca sam `merge`.
#
# **Kroki:**
#
# 1. Złącz lewostronnie, z `validate` dla relacji wiele do jednego i z `indicator`.
# 2. Policz wiersze, które nie znalazły pary.
# 3. Jeśli są, rzuć `ValueError`. Jeśli nie, usuń kolumnę `_merge` i zwróć wynik.
#
# **Sprawdzenie:** `check("07.3")` pokazuje ✅. Sprawdza też liczbę i kolejność wierszy po złączeniu oraz oba błędy.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Wymiar sklepu to `groupby("store_id")` z kilkoma agregacjami naraz. Składnia nazwanych agregacji: `.agg(nowa_kolumna=("kolumna_źródłowa", "funkcja"))`.
#
# W `attach_dim` duplikaty w wymiarze łapie `validate`. Klucze bez pary musisz wykryć sam: po złączeniu lewostronnym zostają po nich wiersze bez wartości z wymiaru.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Sprawdzenie "sklep leży w jednym mieście": policz `nunique()` miast na sklep i zobacz, czy gdzieś wyszło więcej niż 1.
#
# `merge` ma argument `indicator=True`. Dodaje kolumnę `_merge` z wartościami `both`, `left_only`, `right_only`. Po sprawdzeniu usuń ją.
#
# W wymiarze produktu najpierw wyciągnij unikalne ścieżki hierarchii (`drop_duplicates`). Jeśli po tym `product_id` się powtarza, produkt ma dwie ścieżki.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# merged = fact.merge(dim, on=on, how="left", validate="many_to_one", indicator=True)
# unmatched = int((merged["_merge"] != "both").sum())
# # jeśli unmatched > 0: ValueError z liczbą; inaczej zwróć merged bez kolumny _merge
# ```
#
# </details>

# %%
check("07.3")

# %%
from freshcast.data.dims import attach_dim, build_product_dim, build_store_dim

store_dim = build_store_dim(daily)
product_dim = build_product_dim(hierarchy)
print(f"Sklepy: {len(store_dim)}, produkty: {len(product_dim)}")
store_dim.head()

# %%
# Steps 07.3a and 07.3b on the real data: one row per key, columns in order.
assert list(store_dim.columns) == ["store_id", "city_id", "n_products", "mean_sales"]
assert list(product_dim.columns) == ["product_id", *HIERARCHY, "n_stores"]
assert store_dim["store_id"].is_unique and product_dim["product_id"].is_unique, (
    "Wymiar ma mieć dokładnie jeden wiersz na klucz."
)
print("Zgadza się.")

# %% [markdown]
# ### 07.3d Najlepiej sprzedająca się kategoria
#
# **Cel:** użyć wymiaru do pytania o biznes: która kategoria pierwszego poziomu (`first_category_id`) sprzedaje najwięcej na serię i dzień?
#
# **Gdzie:** komórka poniżej, zmienna `top_category`.
#
# **Wejście:** `daily` (fakty, bez kolumn hierarchii) i `product_dim` z 07.3b.
#
# **Wynik:** `top_category`: `int`, identyfikator `first_category_id` tej kategorii, której wiersze (seria × dzień) mają najwyższą średnią `sale_amount`.
#
# **Skorzystaj z:** `attach_dim` z 07.3c (klucz `"product_id"`), `groupby` ze średnią, `idxmax()` (zwraca etykietę indeksu przy największej wartości, wykład, sekcja „groupby”) i `int(...)`.
#
# **Kroki:**
#
# 1. Dołącz wymiar produktu do `daily`.
# 2. Policz średnią sprzedaż w każdej kategorii pierwszego poziomu.
# 3. Weź etykietę największej średniej i zamień ją na `int`.
#
# **Sprawdzenie:** komórka pod spodem sprawdza typ i to, czy taka kategoria istnieje w `product_dim`.

# %%
# >>> SOLUTION 07.3
with_category = attach_dim(daily, product_dim, on="product_id")
by_category = with_category.groupby("first_category_id")[TARGET].mean()
top_category = int(by_category.idxmax())
# --- STUB
#| top_category = ...
# <<< SOLUTION
print(f"Kategoria {top_category}")

# %%
assert isinstance(top_category, int), "top_category ma być liczbą całkowitą (int)."
assert top_category in set(product_dim["first_category_id"]), "Nie ma takiej kategorii w product_dim."
print("Zgadza się.")

# %% [markdown]
# ## 07.4 Tablice godzinowe
#
# **Cel:** zamienić dwie kolumny z tablicami 24 liczb na cztery liczby na dzień, bez pętli po wierszach.
#
# **Gdzie:** `src/freshcast/data/hourly.py`: 07.4a `load_hourly`, 07.4b `to_matrix`, 07.4c `summarise_hours`. Potem 07.4d i 07.4e w notebooku.
#
# Wracamy do dwóch ciężkich kolumn. `hours_sale` to sprzedaż w każdej z 24 godzin. `hours_stock_status` mówi, czy w danej godzinie towaru brakowało: **1 oznacza brak**, 0 oznacza, że towar był. Pozycja 0 tablicy to godzina 0:00-0:59, pozycja 23 to 23:00-23:59.
#
# Braki towaru są najważniejszą cechą tego zbioru. Kiedy towaru nie ma, sprzedaż wynosi zero bez względu na to, ilu klientów chciało go kupić. Sprzedaż to nie popyt. Model uczony na surowej sprzedaży nauczy się zaniżać. Wrócimy do tego w module 09, a teraz trzeba wyciągnąć z tablic liczby, na których da się pracować.
#
# ### Pętla kontra tablica
#
# Najprostszy sposób to przejść wiersz po wierszu. Poniżej gotowa wersja z pętlą. Uruchom ją i zobacz, ile trwa.

# %%
# Five row groups straight from the file: 5,000 rows, any cities.
sample = info.read_row_groups(
    range(5), columns=[*SERIES_KEY, DATE, "hours_sale", "hours_stock_status"]
).to_pandas()

started = time.perf_counter()
oos_loop = []
for _, row in sample.iterrows():
    count = 0
    for hour in range(6, 22):
        if row["hours_stock_status"][hour] == 1:
            count += 1
    oos_loop.append(count)
loop_seconds = time.perf_counter() - started

per_row = loop_seconds / len(sample)
print(f"Pętla: {loop_seconds:.2f} s na {len(sample):,} wierszy")
print(f"Cały zbiór: około {per_row * n_rows_file / 60:.1f} min")

# %% [markdown]
# Szybsza droga: 24 liczby w każdym wierszu to w sumie prostokąt liczb, czyli tablica NumPy o kształcie `(liczba wierszy, 24)`. Na takiej tablicy "zsumuj godziny 6-22 w każdym wierszu" to jedno wyrażenie, wykonane w skompilowanym kodzie.
#
# ### 07.4a `load_hourly`
#
# **Cel:** wczytać tylko klucz, datę i dwie kolumny godzinowe, dla Twoich miast, w tej samej kolejności wierszy co `daily`.
#
# **Gdzie:** `src/freshcast/data/hourly.py`, funkcja `load_hourly(path, cities=...)`.
#
# **Wejście:** `path` i `cities` znaczą to samo co w `load_sales` (07.1b). W notebooku to `RAW` i `CITIES`.
#
# **Wynik:** `pd.DataFrame`, jeden wiersz na serię i dzień, dokładnie kolumny `HOURLY_COLUMNS`: `store_id`, `product_id`, `dt`, `hours_sale`, `hours_stock_status`. Każda komórka dwóch ostatnich kolumn to tablica NumPy z 24 liczbami (sprzedaż jako `float`, status jako `int`). Wiersze posortowane po `store_id`, `product_id`, `dt`, indeks 0..n-1, `dt` jako `datetime64`. Dzięki temu wiersz `i` odpowiada wierszowi `i` w `daily`. Typów całkowitych nie musisz tu zmniejszać.
#
# **Skorzystaj z:** kroków z `load_sales` (07.1b): filtr miast, wczytanie wybranych kolumn, zamiana daty, sortowanie. Stałe `CITY`, `DATE`, `SERIES_KEY`, `HOURLY_COLUMNS` są w `schema.py`. W `hourly.py` są tylko importy sygnatur (`Sequence`, `Path`, `numpy`, `pandas`). Dopisz pod nimi `from freshcast.data.schema import CITY, DATE, HOURLY_COLUMNS, SERIES_KEY`.
#
# **Kroki:** jak w 07.1b, tylko z listą kolumn `HOURLY_COLUMNS` i bez zmniejszania typów.
#
# **Sprawdzenie:** `check("07.4")` testuje najpierw tę funkcję: kolumny, liczbę wierszy, typ daty, sortowanie i filtr miast.
#
# ### 07.4b `to_matrix`
#
# **Cel:** zamienić kolumnę tablic na jedną dwuwymiarową tablicę, na której liczysz bez pętli.
#
# **Gdzie:** `src/freshcast/data/hourly.py`, funkcja `to_matrix(column)`.
#
# **Wejście:** `column`: `pd.Series`, w której każda komórka to jednowymiarowa tablica NumPy z wartościami godzinowymi, na przykład `hourly["hours_sale"]`.
#
# **Wynik:** `np.ndarray` o kształcie `(len(column), 24)`. Wiersz `i` to komórka `i`, kolumna `h` to godzina od `h`:00. Typ elementów taki jak w tablicach: `float` dla sprzedaży, `int` dla statusu. Wiersz z inną liczbą wartości niż 24: `ValueError` z liczbą takich wierszy.
#
# **Skorzystaj z:** `np.stack` z wykładu (sekcja „Tablice w komórkach”); `Series.map(len)` daje długość każdej komórki; stała `HOURS_PER_DAY` (24) z `schema.py`: dopisz ją do linii importu z 07.4a w `hourly.py`. Lab 05 (05.6a) też miał funkcję `to_matrix`, ale to inna funkcja: miała cztery argumenty i układała długą tabelę w macierz seria × dzień. Nie przenoś jej. Ta przyjmuje jedną Series, niczego nie sortuje, a każda komórka jest już gotowym wierszem macierzy wiersz × godzina.
#
# **Kroki:**
#
# 1. Policz długość każdej komórki. Jeśli któraś nie ma 24 wartości, rzuć błąd z liczbą takich wierszy.
# 2. Zamień kolumnę na listę tablic i sklej ją w jedną tablicę.
#
# **Sprawdzenie:** `check("07.4")` sprawdza kształt wyniku na próbce i błąd dla wiersza z 23 wartościami.
#
# ### 07.4c `summarise_hours`
#
# **Cel:** zredukować 48 liczb na wiersz do czterech, z których korzystają kolejne moduły.
#
# **Gdzie:** `src/freshcast/data/hourly.py`, funkcja `summarise_hours(hourly)`.
#
# **Wejście:** `hourly`: wynik `load_hourly` z 07.4a.
#
# **Wynik:** nowy `pd.DataFrame`: `store_id`, `product_id`, `dt` i cztery kolumny, w tej kolejności:
#
# - `oos_hours` (`int`, od 0 do 16): godziny bez towaru między 6:00 a 22:00, czyli pozycje 6 do 21 tablicy,
# - `oos_hours_total` (`int`, od 0 do 24): godziny bez towaru w całym dniu,
# - `sales_in_stock` (`float`): sprzedaż w godzinach, w których towar był,
# - `sales_while_oos` (`float`): sprzedaż zapisana w godzinach oznaczonych jako brak towaru.
#
# Okno 6:00-22:00 dotyczy tylko `oos_hours`. Trzy pozostałe kolumny liczysz ze wszystkich 24 godzin. Wiersze w kolejności wejścia, z tym samym indeksem. `sales_in_stock + sales_while_oos` daje sprzedaż dnia, `sale_amount`. "oos" to skrót od out of stock (brak towaru).
#
# **Skorzystaj z:**
#
# - `to_matrix` z 07.4b, dla obu kolumn godzinowych,
# - `.astype(bool)`: zamienia status 0/1 na False/True,
# - `OOS_WINDOW` z `schema.py`: gotowy wycinek `slice(6, 22)`, czyli pozycje 6 do 21,
# - `sum(axis=1)` i `np.where` z modułu 05 i z wykładu (sekcja „Tablice w komórkach”),
# - stałych nazw `HOURLY_SALES`, `HOURLY_STOCKOUT`, `OOS_HOURS`, `OOS_HOURS_TOTAL`, `SALES_IN_STOCK`, `SALES_WHILE_OOS` i `OOS_WINDOW` z `schema.py`. Dopisz je do linii importu w `hourly.py`. Po krokach 07.4a-c ta linia to `from freshcast.data.schema import CITY, DATE, HOURLY_COLUMNS, HOURLY_SALES, HOURLY_STOCKOUT, HOURS_PER_DAY, OOS_HOURS, OOS_HOURS_TOTAL, OOS_WINDOW, SALES_IN_STOCK, SALES_WHILE_OOS, SERIES_KEY` (`ruff format` może ją potem rozbić na kilka wierszy w nawiasach).
#
# **Kroki:**
#
# 1. Zrób dwie tablice: sprzedaż i status braku jako wartości logiczne.
# 2. Zacznij wynik od kopii kolumn klucza i daty z `hourly`.
# 3. `oos_hours`: w każdym wierszu policz godziny braku w wycinku `OOS_WINDOW`.
# 4. `oos_hours_total`: to samo dla całego wiersza.
# 5. `sales_in_stock`: wstaw zero tam, gdzie towaru nie było, i zsumuj każdy wiersz.
# 6. `sales_while_oos`: odwrotnie, zero tam, gdzie towar był.
#
# **Sprawdzenie:** `check("07.4")` pokazuje ✅. Porównuje `oos_hours` z surową kolumną `stock_hour6_22_cnt` i sprawdza, czy obie sumy sprzedaży dają `sale_amount`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `np.stack` skleja listę tablic o tym samym kształcie w jedną tablicę o wymiar większą. Po zamianie statusu na typ logiczny (`.astype(bool)`) suma po osi 1 liczy godziny braku.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Sprzedaż w godzinach z towarem: chcesz zsumować w każdym wierszu tylko te godziny, w których status to "jest towar". `np.where(warunek, a, b)` wybiera element po elemencie. Wstaw zero tam, gdzie towaru nie było, i zsumuj po osi 1.
#
# Wycinek kolumn tablicy dwuwymiarowej: `matrix[:, OOS_WINDOW]`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# sales = to_matrix(hourly[HOURLY_SALES])
# out_of_stock = to_matrix(hourly[HOURLY_STOCKOUT]).astype(bool)
#
# summary = hourly[[*SERIES_KEY, DATE]].copy()
# summary[OOS_HOURS] = out_of_stock[:, OOS_WINDOW].sum(axis=1)
# # pozostałe trzy kolumny analogicznie
# ```
#
# </details>

# %%
check("07.4")

# %%
from freshcast.data.hourly import load_hourly, summarise_hours, to_matrix

hourly = load_hourly(RAW, cities=CITIES)

started = time.perf_counter()
summary = summarise_hours(hourly)
vector_seconds = time.perf_counter() - started
print(f"Tablica: {vector_seconds:.2f} s na {len(hourly):,} wierszy")
print(f"Pętla na tylu wierszach: około {per_row * len(hourly):.0f} s")
summary.head()

# %%
# Step 07.4c on the real data: one summary row per row of daily, sales split adds up.
assert len(hourly) == len(daily), "hourly ma mieć tyle wierszy co daily: te same miasta, ten sam panel."
assert list(summary.columns) == [
    *SERIES_KEY, DATE, "oos_hours", "oos_hours_total", "sales_in_stock", "sales_while_oos"
]
assert np.allclose(summary["sales_in_stock"] + summary["sales_while_oos"], daily[TARGET]), (
    "sales_in_stock + sales_while_oos ma dawać sale_amount z daily."
)
print("Zgadza się.")

# %% [markdown]
# ### 07.4d Zgodność z surową kolumną
#
# Surowe dane mają kolumnę `stock_hour6_22_cnt`: liczbę godzin bez towaru między 6:00 a 22:00, policzoną przez autorów zbioru. Twoje `oos_hours` powinno dawać to samo.
#
# **Gdzie:** `n_disagree`. **Wynik:** `int`, liczba wierszy, w których `summary["oos_hours"]` różni się od `daily["stock_hour6_22_cnt"]`. Oczekiwane 0: komórka ma `assert`. **Skorzystaj z:** obie ramki są posortowane tak samo (07.1b i 07.4a), więc porównujesz je pozycja po pozycji. `.to_numpy()` zamienia kolumnę w tablicę bez indeksu; porównanie `!=` daje tablicę True/False.

# %%
# >>> SOLUTION 07.4
raw_count = daily["stock_hour6_22_cnt"].to_numpy()
n_disagree = int((summary["oos_hours"].to_numpy() != raw_count).sum())
# --- STUB
#| n_disagree = ...
# <<< SOLUTION
print(f"Różnice: {n_disagree}")
assert n_disagree == 0

# %% [markdown]
# ### 07.4e Sprzedaż mimo braku towaru
#
# **Gdzie:** `share_rows`, `share_sales`. **Wynik:** dwa `float` od 0 do 1:
#
# - `share_rows`: ułamek wierszy `summary`, w których `sales_while_oos > 0`,
# - `share_sales`: suma `sales_while_oos` podzielona przez całą sprzedaż, czyli przez sumę `sales_in_stock` plus sumę `sales_while_oos`.
#
# Wydruk pokazuje je jako procenty. **Skorzystaj z:** średnia kolumny True/False to ułamek wartości True.

# %%
# >>> SOLUTION 07.4
share_rows = float((summary["sales_while_oos"] > 0).mean())
total_sales = summary["sales_in_stock"].sum() + summary["sales_while_oos"].sum()
share_sales = float(summary["sales_while_oos"].sum() / total_sales)
# --- STUB
#| share_rows = ...
#| share_sales = ...
# <<< SOLUTION
print(f"Wiersze ze sprzedażą mimo braku towaru: {share_rows:.1%}")
print(f"Udział w całej sprzedaży: {share_sales:.1%}")

# %%
assert 0 <= share_rows <= 1 and 0 <= share_sales <= 1, "Oba wyniki to ułamki od 0 do 1."
print("Zgadza się.")

# %% [markdown]
# Sprzedaż bez towaru jest fizycznie niemożliwa, więc coś w danych jest niedokładne: status godzinowy albo moment zaksięgowania sprzedaży. Tego nie naprawisz. Możesz to zmierzyć, zapisać i pamiętać, że flaga braku towaru jest przybliżeniem.
#
# Na koniec zobacz, o której godzinie towaru brakuje najczęściej.

# %%
oos_by_hour = to_matrix(hourly["hours_stock_status"]).mean(axis=0)

fig, ax = plt.subplots()
ax.bar(range(24), oos_by_hour, width=0.7)
ax.set_title("Udział serii bez towaru według godziny")
ax.set_xlabel("Godzina")
ax.set_xticks(range(0, 24, 2))
ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
plt.show()

# %% [markdown]
# ## 07.5 Obliczenia wewnątrz serii
#
# **Cel:** liczyć cechy z przeszłości tej samej serii (lag, średnia krocząca) i typowy kształt tygodnia tak, żeby żadna wartość nie przeciekła z innej serii ani z dnia, który model ma przewidzieć.
#
# **Gdzie:** `src/freshcast/data/panel.py`: 07.5a `is_sorted_panel`, 07.5b `add_lag`, 07.5c `add_rolling_mean`, 07.5d `dow_profile`. Potem 07.5e w notebooku.
#
# Panel to wiele szeregów czasowych ułożonych jeden pod drugim. Prawie każde obliczenie na panelu ma sens tylko **wewnątrz jednej serii**: sprzedaż sprzed tygodnia tego samego produktu w tym samym sklepie, średnia z ostatnich 7 dni tej samej serii.
#
# Zobacz, co się dzieje, gdy o tym zapomnisz.

# %%
demo = daily[[*SERIES_KEY, DATE, TARGET]].copy()
demo["wrong_lag_1"] = demo[TARGET].shift(1)

boundary = demo.index[demo[DATE] == demo[DATE].min()][1]
demo.loc[boundary - 2 : boundary + 1]

# %% [markdown]
# Pierwszy dzień drugiej serii dostał jako "wczorajszą sprzedaż" ostatni dzień zupełnie innego produktu. Błędu nie było.
#
# Poprawnie robi się to przez `groupby`. Są tu dwie różne operacje i warto je rozróżniać:
#
# - `groupby(...).agg(...)` **zwija**: zwraca jeden wiersz na grupę.
# - `groupby(...).transform(...)` i `groupby(...).shift(...)` **zachowują kształt**: zwracają jedną wartość na każdy wiersz wejścia, policzoną w obrębie jego grupy.
#
# ### Granica czasu
#
# Druga pułapka jest subtelniejsza. Średnia krocząca z 7 dni liczona przez `rolling(7).mean()` obejmuje **dzień bieżący**. Jeśli użyjesz jej jako cechy do przewidywania sprzedaży w tym dniu, model dostaje w cesze kawałek odpowiedzi. To się nazywa leakage (przeciek) i zajmiemy się nim porządnie w module 08. Tutaj obowiązuje prosta reguła: **okno kończy się najpóźniej wczoraj.**
#
# Lag przez `shift` zakłada, że kolejne wiersze serii to kolejne dni. Kompletność gwarantuje `check_panel` z 07.2c, kolejność sprawdza `is_sorted_panel` z 07.5a.
#
# Wszystkie funkcje poniżej dostają w notebooku `daily` po 07.2: kompletny panel posortowany przez `load_sales`.
#
# ### 07.5a `is_sorted_panel`
#
# **Cel:** jedna funkcja, która odpowiada, czy na ramce wolno liczyć lagi. Używają jej 07.5b i 07.5c.
#
# **Gdzie:** `src/freshcast/data/panel.py`, funkcja `is_sorted_panel(df)`.
#
# **Wejście:** `df`: `pd.DataFrame` z kolumnami `store_id`, `product_id`, `dt`.
#
# **Wynik:** `bool`, zwykłe Pythonowe `True` albo `False` (nie Series i nie `np.bool_`; sprawdzenie porównuje wynik przez `is True`). `True`, gdy wiersze od góry do dołu są ułożone rosnąco po `store_id`, potem `product_id`, potem `dt`. Powtórzony wiersz nie psuje porządku: duplikaty łapie `check_panel`. Ramki nie zmieniasz.
#
# **Skorzystaj z:** `sort_values` z `kind="stable"` (sortowanie stabilne: równe wiersze zostają w dotychczasowej kolejności) i porównania indeksów przed sortowaniem i po nim; `bool(...)` zamienia wynik na zwykłe `True`/`False`. W `panel.py` jest tylko `import pandas as pd`. Dopisz pod nim `from freshcast.data.schema import DATE, SERIES_KEY`.
#
# **Kroki:**
#
# 1. Weź kolumny klucza i daty.
# 2. Posortuj ich kopię.
# 3. Jeśli sortowanie nie przestawiło żadnego wiersza (etykiety indeksu są w tej samej kolejności), ramka była posortowana.
#
# **Sprawdzenie:** `check("07.5")` testuje najpierw tę funkcję na dwóch małych seriach: posortowanych i przetasowanych.
#
# ### 07.5b `add_lag`
#
# **Cel:** cecha „wartość sprzed `lag` dni w tej samej serii”, na przykład sprzedaż sprzed tygodnia.
#
# **Gdzie:** `src/freshcast/data/panel.py`, funkcja `add_lag(df, column, lag)`.
#
# **Wejście:**
#
# - `df`: `pd.DataFrame`, kompletny panel posortowany po serii i dacie. W notebooku to `daily`.
# - `column`: `str`, nazwa kolumny, z której bierzesz wartości, na przykład `TARGET`.
# - `lag`: `int`, o ile dni wstecz, co najmniej 1.
#
# **Wynik:** nowy `pd.DataFrame`: wszystkie kolumny `df` i na końcu nowa kolumna `{column}_lag_{lag}`, na przykład `sale_amount_lag_7`. Te same wiersze, kolejność i indeks. Pierwsze `lag` dni każdej serii mają `NaN`: wcześniejszej wartości nie ma, a wartość z innej serii nie może jej zastąpić. Ramki wejściowej nie zmieniasz. `lag` mniejszy od 1 albo nieposortowana ramka: `ValueError`.
#
# **Skorzystaj z:**
#
# - `is_sorted_panel` z 07.5a (ten sam plik),
# - `groupby(SERIES_KEY)[column].shift(lag)` z wykładu (sekcja „Czas w panelu: shift i rolling”),
# - `df.assign(**{nazwa: wartości})` i f-stringa do zbudowania nazwy kolumny.
#
# Nowego importu nie dopisujesz: `SERIES_KEY` masz z 07.5a.
#
# **Kroki:**
#
# 1. Sprawdź argumenty: za mały `lag` albo nieposortowana ramka to błąd. Nie sortuj ramki w funkcji, żeby błąd ominąć: umowa wymaga `ValueError`.
# 2. Przesuń kolumnę o `lag` wierszy w obrębie każdej serii.
# 3. Zwróć kopię ramki z nową kolumną.
#
# **Sprawdzenie:** `check("07.5")` liczy lag 2 na dwóch seriach `[1..5]` i `[10..50]` i oczekuje `[NaN, NaN, 1, 2, 3]` oraz `[NaN, NaN, 10, 20, 30]`.
#
# ### 07.5c `add_rolling_mean`
#
# **Cel:** cecha „średnia z ostatnich `window` dni tej samej serii”, policzona wyłącznie z przeszłości.
#
# **Gdzie:** `src/freshcast/data/panel.py`, funkcja `add_rolling_mean(df, column, window, lag=1)`.
#
# **Wejście:**
#
# - `df`, `column`: jak w 07.5b,
# - `window`: `int`, liczba dni w oknie, co najmniej 1,
# - `lag`: `int`, ile dni przed wierszem kończy się okno, co najmniej 1. Domyślne 1 znaczy: okno kończy się wczoraj.
#
# **Wynik:** nowy `pd.DataFrame`: wszystkie kolumny `df` i na końcu kolumna `{column}_mean_{window}_lag_{lag}`, na przykład `sale_amount_mean_7_lag_1`. Dla wiersza z dnia t okno obejmuje dni od t − lag − window + 1 do t − lag. Wiersze, które nie mają w swojej serii `window` pełnych dni przeszłości, mają `NaN`. Te same wiersze, kolejność i indeks, wejście bez zmian. `window` albo `lag` mniejsze od 1 albo nieposortowana ramka: `ValueError`.
#
# **Skorzystaj z:** `is_sorted_panel` z 07.5a, przesunięcia z 07.5b i wzorca „najpierw przesuń, potem licz okno” z wykładu (sekcja „Czas w panelu: shift i rolling”, pułapka druga). `reset_index(level=..., drop=True)` usuwa wybrane poziomy indeksu. Nowego importu nie dopisujesz.
#
# **Kroki:**
#
# 1. Sprawdź argumenty i sortowanie, jak w 07.5b.
# 2. Przesuń kolumnę o `lag` w obrębie serii. To ustawia koniec okna w przeszłości.
# 3. Na przesuniętych wartościach policz średnią kroczącą z `window` wierszy, znowu w obrębie serii. Przesunięta Series nie pamięta podziału na serie: `groupby` trzeba podać jeszcze raz.
# 4. Wynik ma indeks z dodatkowymi poziomami (klucze serii). Usuń je, żeby indeks pasował do ramki.
# 5. Zwróć kopię ramki z nową kolumną.
#
# **Sprawdzenie:** `check("07.5")` liczy okno 2 dni na tych samych dwóch seriach. Jeśli trzeci wynik to 2.5 zamiast 1.5, okno obejmuje bieżący dzień.
#
# ### 07.5d `dow_profile`
#
# **Cel:** typowy kształt tygodnia: o ile w każdy dzień tygodnia sprzedaż jest wyższa albo niższa od zwykłej. "dow" to skrót od day of week (dzień tygodnia). Wynik to jedna krótka Series z siedmioma liczbami dla wszystkich serii razem, a nie nowa kolumna w ramce ani profil osobno dla każdej serii.
#
# **Gdzie:** `src/freshcast/data/panel.py`, funkcja `dow_profile(df)`.
#
# **Wejście:** `df`: `pd.DataFrame`, dzienna sprzedaż z kluczem serii, `dt` (data) i `sale_amount`. W notebooku to `daily`.
#
# **Wynik:** `pd.Series` z 7 liczbami `float`, indeks od 0 (poniedziałek) do 6 (niedziela), nazwa `dow_profile`. 1.2 znaczy: sprzedaż o 20% wyższa od średniej serii. Seria ze średnią sprzedażą równą 0: `ValueError` z liczbą wierszy takich serii, bo dzielenie przez 0 nie ma sensu.
#
# **Skorzystaj z:** `groupby(...).transform("mean")` z wykładu (sekcja „groupby”, przykład z `relative_sales`), `.dt.dayofweek` (dzień tygodnia z daty, 0 to poniedziałek) i `rename`. Potrzebujesz `TARGET`: rozszerz linię importu w `panel.py` do `from freshcast.data.schema import DATE, SERIES_KEY, TARGET`.
#
# **Kroki:**
#
# 1. Do każdego wiersza dopisz średnią sprzedaż jego serii (wartość na wiersz, nie na serię).
# 2. Jeśli któraś średnia to 0, rzuć błąd.
# 3. Podziel sprzedaż przez średnią serii. Teraz duża i mała seria ważą tyle samo.
# 4. Policz średnią tych względnych wartości dla każdego dnia tygodnia, po wszystkich seriach.
# 5. Nadaj wynikowi nazwę `dow_profile`.
#
# **Sprawdzenie:** `check("07.5")` pokazuje ✅. Dla serii z podwójną sprzedażą w weekend i serii płaskiej, dziesięć razy większej, profil to 0.889 w dni robocze i 1.278 w weekend.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `df.groupby(SERIES_KEY)[column].shift(lag)` przesuwa wartości w obrębie każdej serii i zwraca Series o tej samej długości co ramka.
#
# W `add_rolling_mean` zrób dwa kroki: najpierw przesuń (to załatwia granicę czasu), potem policz średnią kroczącą z przesuniętych wartości, znowu w obrębie serii.
#
# W `dow_profile` potrzebujesz średniej każdej serii rozpisanej na wszystkie jej wiersze. To robi `transform("mean")`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `is_sorted_panel`: posortuj kopię kluczy i porównaj indeks przed i po. Jeśli sortowanie niczego nie przestawiło, ramka była posortowana.
#
# Średnia krocząca w grupach: `seria.groupby(klucze).rolling(window).mean()` zwraca Series z indeksem wielopoziomowym (klucze grupy plus oryginalny indeks). Poziomy kluczy trzeba usunąć, żeby wynik dało się przypisać z powrotem do ramki.
#
# Przesunięta Series nie ma już kolumn z kluczami, więc grupujesz po kolumnach z ramki: `past.groupby([df[k] for k in SERIES_KEY])`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# past = df.groupby(SERIES_KEY, sort=False)[column].shift(lag)
# mean = (
#     past.groupby([df[key] for key in SERIES_KEY], sort=False)
#     .rolling(window)
#     .mean()
#     .reset_index(level=SERIES_KEY, drop=True)
# )
# ```
#
# Dzień tygodnia z daty: `df[DATE].dt.dayofweek` (0 to poniedziałek).
#
# </details>

# %%
check("07.5")

# %%
from freshcast.data.panel import add_lag, add_rolling_mean, dow_profile

panel = add_lag(daily, TARGET, 7)
panel = add_rolling_mean(panel, TARGET, window=7)
panel[[*SERIES_KEY, DATE, TARGET, "sale_amount_lag_7", "sale_amount_mean_7_lag_1"]].iloc[5:12]

# %%
# Steps 07.5b and 07.5c on the real data: NaN only in the first 7 days of each series.
n_series = daily.groupby(SERIES_KEY).ngroups
assert int(panel["sale_amount_lag_7"].isna().sum()) == 7 * n_series, (
    "Lag 7 ma dać NaN dokładnie w pierwszych 7 dniach każdej serii."
)
assert int(panel["sale_amount_mean_7_lag_1"].isna().sum()) == 7 * n_series, (
    "Okno 7 dni kończące się wczoraj ma dać NaN dokładnie w pierwszych 7 dniach każdej serii."
)
print("Zgadza się.")

# %% [markdown]
# ### 07.5e Czy lagi coś mówią
#
# Czy te dwie kolumny coś mówią o sprzedaży? Policz korelację każdej z nich z `sale_amount`.
#
# **Gdzie:** `corr_lag`, `corr_mean`. **Wynik:** dwa `float` od -1 do 1: korelacja `sale_amount` z `sale_amount_lag_7` i z `sale_amount_mean_7_lag_1` w ramce `panel`. 1 znaczy: kolumny rosną i maleją razem, 0: brak związku liniowego. **Skorzystaj z:** `Series.corr(inna_series)` (wykład, sekcja „Czas w panelu: shift i rolling”). Wiersze z `NaN` w którejkolwiek kolumnie pomija sama, więc braków na początku serii nie wypełniaj. Wysoka korelacja mówi, że cecha niesie informację, a nie że jest przyczyną sprzedaży.

# %%
# >>> SOLUTION 07.5
corr_lag = float(panel[TARGET].corr(panel["sale_amount_lag_7"]))
corr_mean = float(panel[TARGET].corr(panel["sale_amount_mean_7_lag_1"]))
# --- STUB
#| corr_lag = ...
#| corr_mean = ...
# <<< SOLUTION
print(f"Korelacja ze sprzedażą sprzed tygodnia:      {corr_lag:.2f}")
print(f"Korelacja ze średnią z poprzednich 7 dni:    {corr_mean:.2f}")

# %%
assert -1 <= corr_lag <= 1 and -1 <= corr_mean <= 1, "Korelacja to liczba od -1 do 1."
print("Zgadza się.")

# %% [markdown]
# Średnia z tygodnia koreluje mocniej niż pojedynczy dzień sprzed tygodnia. Pojedynczy dzień niesie dużo szumu, średnia go wygładza. Z takich obserwacji powstają cechy modelu, którymi zajmiesz się w module 09.

# %%
profile = dow_profile(daily)

fig, ax = plt.subplots()
ax.bar(["pon", "wt", "śr", "czw", "pt", "sob", "niedz"], profile.to_numpy(), width=0.6)
ax.axhline(1.0, color="#898781", linewidth=1)
ax.set_title("Sprzedaż względem średniej serii według dnia tygodnia")
ax.set_ylim(0, profile.max() * 1.15)
plt.show()

# %%
# Step 07.5d on the real data: seven weekdays, Monday first.
assert list(profile.index) == list(range(7)), "Indeks profilu to dni tygodnia 0..6."
assert profile.name == "dow_profile", "Series ma mieć nazwę dow_profile."
print("Zgadza się.")

# %% [markdown]
# ## 07.6 Zbiór przetworzony
#
# **Cel:** złożyć z gotowych klocków jedną funkcję, która z surowego pliku robi zbiór gotowy do modelowania, i dwie funkcje do jego zapisu i odczytu. Od `load_processed` zaczyna każdy następny moduł.
#
# **Gdzie:** `src/freshcast/data/prepare.py`: 07.6a `prepare_daily`, 07.6b `save_processed`, 07.6c `load_processed`.
#
# `PROCESSED_COLUMNS` to **kontrakt**. Kod, który ten plik zapisuje, i kod, który go czyta, mogą powstać w odstępie tygodni. Jeśli ktoś doda kolumnę po jednej stronie, a plik na dysku zostanie stary, chcesz dostać czytelny błąd przy wczytaniu, a nie `KeyError` trzy moduły dalej.
#
# Zwróć uwagę na nazwę: surowa kolumna `stock_hour6_22_cnt` nie wchodzi do zbioru przetworzonego. Zastępuje ją Twoje `oos_hours`. Zanim wyrzucisz surową kolumnę, porównaj ją z własną i rzuć błąd, jeśli się różnią.
#
# ### 07.6a `prepare_daily`
#
# **Cel:** jedno wywołanie od surowego pliku do zbioru, który spełnia kontrakt.
#
# **Gdzie:** `src/freshcast/data/prepare.py`, funkcja `prepare_daily(raw_path, cities=...)`.
#
# **Wejście:** `raw_path`: `Path`, surowy plik (w notebooku `RAW`); `cities`: identyfikatory miast albo `None`, jak w `load_sales` (w notebooku `CITIES`).
#
# **Wynik:** `pd.DataFrame`, jeden wiersz na serię i dzień, dokładnie kolumny `PROCESSED_COLUMNS`, w tej kolejności: `store_id`, `product_id`, `city_id`, `dt`, `sale_amount`, `discount`, `discount_is_zero`, `holiday_flag`, `activity_flag`, `precpt`, `avg_temperature`, `avg_humidity`, `avg_wind_level`, `oos_hours`, `oos_hours_total`, `sales_in_stock`, `sales_while_oos`. Wiersze posortowane po serii i dacie, indeks 0..n-1. `ValueError`, gdy dane łamią regułę panelu, rabat jest ujemny albo brakuje go, albo `stock_hour6_22_cnt` różni się od `oos_hours`.
#
# **Skorzystaj z:** funkcji, które już masz. W `prepare.py` są tylko importy sygnatur (`Sequence`, `Path`, `pandas`) i stała `DAILY_FILE`. Dopisz na górze pliku:
#
# ```python
# from freshcast.data.hourly import load_hourly, summarise_hours
# from freshcast.data.load import load_sales
# from freshcast.data.schema import DATE, OOS_HOURS, PROCESSED_COLUMNS, RAW_OOS_HOURS, SERIES_KEY
# from freshcast.data.validate import check_panel, clean_discount
# ```
#
# Te linie dają Ci:
#
# - `load_sales` (07.1b),
# - `check_panel` i `clean_discount` (07.2c, 07.2d),
# - `load_hourly` i `summarise_hours` (07.4a, 07.4c),
# - stałe `RAW_OOS_HOURS` (`"stock_hour6_22_cnt"`), `OOS_HOURS`, `PROCESSED_COLUMNS`, `SERIES_KEY`, `DATE`.
#
# `attach_dim` z 07.3c tu nie pasuje: łączy po jednej kolumnie i zakłada wiele wierszy faktów na klucz. Tu klucz to trzy kolumny `[*SERIES_KEY, DATE]`, a relacja jest jeden do jednego, więc `merge` piszesz sam, z jawnym `on`, `how` i `validate`.
#
# `prepare_daily` musi działać sama, w nowym procesie, bez zmiennych tego notebooka (`daily`, `summary`). Oba odczyty, dzienny i godzinowy, robisz z tego samego `raw_path` i z tymi samymi `cities`.
#
# **Kroki:**
#
# 1. Wczytaj dzienną sprzedaż.
# 2. Sprawdź reguły panelu.
# 3. Wyczyść rabat.
# 4. Wczytaj tablice godzinowe i zrób z nich podsumowanie.
# 5. Dołącz podsumowanie do sprzedaży po serii i dacie, jeden do jednego.
# 6. Policz wiersze, w których surowa liczba godzin braku różni się od `oos_hours`. Jeśli są, rzuć błąd.
# 7. Wybierz kolumny listą `PROCESSED_COLUMNS`. To ustawia ich kolejność i wyrzuca surową kolumnę.
#
# **Sprawdzenie:** `check("07.6")` uruchamia `prepare_daily` na próbce. Korzysta przy tym z Twoich funkcji z 07.1, 07.2 i 07.4, więc te zadania muszą już przechodzić.
#
# ### 07.6b `save_processed`
#
# **Cel:** zapisać zbiór na dysk tylko wtedy, gdy spełnia kontrakt.
#
# **Gdzie:** `src/freshcast/data/prepare.py`, funkcja `save_processed(daily, directory)`.
#
# **Wejście:** `daily`: `pd.DataFrame`, zbiór z 07.6a; `directory`: `Path`, katalog docelowy (w notebooku `paths.PROCESSED_DIR`, czyli `data/processed`).
#
# **Wynik:** `Path` zapisanego pliku: `directory / "daily.parquet"` (stała `DAILY_FILE` w `prepare.py`). Plik bez indeksu. Brakujący katalog tworzysz, istniejący plik nadpisujesz. Kolumny inne niż `PROCESSED_COLUMNS` (nazwy albo kolejność): `ValueError` i nic nie zapisujesz.
#
# **Skorzystaj z:** `PROCESSED_COLUMNS` z linii importu dopisanej w 07.6a (nic nowego nie dopisujesz); `save_daily` z labu 06 (06.7b) to ten sam wzorzec; `Path.mkdir(parents=True, exist_ok=True)`; `to_parquet(path, index=False)`.
#
# **Kroki:**
#
# 1. Porównaj listę kolumn ramki z `PROCESSED_COLUMNS`. Jeśli się różni, rzuć błąd.
# 2. Utwórz katalog.
# 3. Zapisz plik i zwróć jego ścieżkę.
#
# **Sprawdzenie:** `check("07.6")` zapisuje zbiór do katalogu tymczasowego i sprawdza, że plik istnieje i że ramka bez jednej kolumny daje `ValueError`.
#
# ### 07.6c `load_processed`
#
# **Cel:** wczytać zbiór i od razu wiedzieć, czy plik na dysku pasuje do obecnego kontraktu.
#
# **Gdzie:** `src/freshcast/data/prepare.py`, funkcja `load_processed(directory)`.
#
# **Wejście:** `directory`: `Path`, ten sam katalog, który dostało `save_processed`.
#
# **Wynik:** `pd.DataFrame` z pliku `directory / "daily.parquet"`, z kolumnami `PROCESSED_COLUMNS` w tej kolejności. Brak pliku: `FileNotFoundError`. Kolumny inne niż kontrakt: `ValueError`.
#
# **Skorzystaj z:** `PROCESSED_COLUMNS` i `DAILY_FILE`, które już masz w `prepare.py` po 07.6a; `load_daily` z labu 06 (06.7b); `Path.is_file()`; `pd.read_parquet`.
#
# **Kroki:**
#
# 1. Zbuduj ścieżkę pliku. Jeśli go nie ma, rzuć `FileNotFoundError`.
# 2. Wczytaj plik.
# 3. Porównaj kolumny z `PROCESSED_COLUMNS`. Jeśli się różnią, rzuć `ValueError`. Inaczej zwróć ramkę.
#
# **Sprawdzenie:** `check("07.6")` pokazuje ✅. Zbiór po zapisie i odczycie ma być identyczny z oryginałem.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `prepare_daily` to pięć wywołań funkcji, które już masz, plus jedno złączenie. Podsumowanie godzin ma dokładnie jeden wiersz na wiersz faktów, więc jaki `validate` tu pasuje?
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Klucz złączenia to seria i data: `[*SERIES_KEY, DATE]`. Na końcu wybierz kolumny listą `PROCESSED_COLUMNS`. To jednocześnie ustawia kolejność i wyrzuca surową kolumnę.
#
# Katalog tworzysz przez `directory.mkdir(parents=True, exist_ok=True)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# daily = daily.merge(
#     summary, on=[*SERIES_KEY, DATE], how="left", validate="one_to_one"
# )
# ```
#
# Porównanie listy kolumn: `list(daily.columns) != PROCESSED_COLUMNS`.
#
# </details>

# %%
check("07.6")

# %% [markdown]
# Zbuduj zbiór dla swojego profilu i zapisz go. Od tej chwili kolejne moduły zaczynają od `load_processed`.

# %%
from freshcast.data.prepare import load_processed, prepare_daily, save_processed

processed = prepare_daily(RAW, cities=CITIES)
path = save_processed(processed, paths.PROCESSED_DIR)
store_dim.to_parquet(paths.PROCESSED_DIR / "store_dim.parquet", index=False)
product_dim.to_parquet(paths.PROCESSED_DIR / "product_dim.parquet", index=False)

print(f"{path.relative_to(paths.ROOT)}: {path.stat().st_size / 1e6:.1f} MB")
load_processed(paths.PROCESSED_DIR).info()

# %%
# Step 07.6a on the real data: the contract and one row per row of daily.
from freshcast.data.schema import PROCESSED_COLUMNS

assert list(processed.columns) == PROCESSED_COLUMNS, "processed ma mieć kolumny PROCESSED_COLUMNS."
assert len(processed) == len(daily), "processed ma mieć tyle wierszy co daily."
print("Zgadza się.")

# %% [markdown]
# ## 07.7 Eksploracja
#
# **Cel:** obejrzeć czysty zbiór, zanim zaczniesz cokolwiek przewidywać. Ta część nie ma sprawdzeń.
#
# **Gdzie:** komórki „Twoja odpowiedź” pod wykresami.
#
# **Wejście:** `data`: zbiór wczytany Twoim `load_processed` (07.6c). Trzy wykresy są gotowe.
#
# **Wynik:** odpowiedzi na cztery pytania, każda w jednym, dwóch zdaniach.
#
# **Skorzystaj z:** wykresów i tego, co wiesz o brakach towaru z 07.4. Jeśli pracujesz z tutorem, omów z nim swoje odpowiedzi.

# %%
data = load_processed(paths.PROCESSED_DIR)
by_day = data.groupby(DATE).agg(
    sales=(TARGET, "mean"), temperature=("avg_temperature", "mean")
)

fig, (top, bottom) = plt.subplots(2, 1, sharex=True, figsize=(8, 5))
top.plot(by_day.index, by_day["sales"], color="#c3c2b7", linewidth=1)
top.plot(by_day.index, by_day["sales"].rolling(7).mean())
top.set_title("Średnia sprzedaż na serię: dziennie i średnia z 7 dni")
bottom.plot(by_day.index, by_day["temperature"], color="#eb6834")
bottom.set_title("Średnia temperatura (°C)")
fig.tight_layout()
plt.show()

# %% [markdown]
# **Pytanie 1.** Opisz trend średniej z 7 dni w Twoim profilu, oddzielnie od wahań z dnia na dzień. W profilach `small` i `standard` jest ona na końcu okresu wyższa niż na początku. Jeśli u Ciebie sprzedaż rośnie, podaj dwa różne wyjaśnienia tego wzrostu. Czy z tych danych da się rozstrzygnąć, które jest prawdziwe?

# %% [markdown]
# *Twoja odpowiedź:*

# %%
bins = [0, 0.5, 0.7, 0.8, 0.9, 0.999, 1.0]
labels = ["do 0.5", "0.5-0.7", "0.7-0.8", "0.8-0.9", "0.9-1.0", "bez rabatu"]
series_mean = data.groupby(SERIES_KEY)[TARGET].transform("mean")
relative = (data[TARGET] / series_mean).rename("relative")
by_discount = relative.groupby(pd.cut(data["discount"], bins=bins, labels=labels)).mean()

fig, ax = plt.subplots()
ax.bar(by_discount.index.astype(str), by_discount.to_numpy(), width=0.6)
ax.axhline(1.0, color="#898781", linewidth=1)
ax.set_title("Sprzedaż względem średniej serii według mnożnika ceny")
ax.set_xlabel("discount (mnożnik ceny)")
plt.show()

# %% [markdown]
# **Pytanie 2.** Wykres pokazuje sprzedaż podzieloną przez średnią serii, a nie surową sprzedaż. Dlaczego? Co pokazałby wykres surowej sprzedaży, gdyby drogie w utrzymaniu, wolno rotujące produkty były przeceniane częściej?

# %% [markdown]
# *Twoja odpowiedź:*

# %%
by_oos = data.groupby("oos_hours").agg(sales=(TARGET, "mean"), rows=(TARGET, "size"))

fig, ax = plt.subplots()
ax.plot(by_oos.index, by_oos["sales"], marker="o", markersize=5)
ax.set_title("Średnia sprzedaż według liczby godzin bez towaru (6:00-22:00)")
ax.set_xlabel("Godziny bez towaru")
ax.set_ylim(0, None)
plt.show()

print(f"Wiersze bez żadnej godziny braku: {by_oos.loc[0, 'rows'] / len(data):.0%}")

# %% [markdown]
# **Pytanie 3.** Sprawdź na wykresie, czy dni z jedną do trzech godzin bez towaru mają wyższą średnią sprzedaż niż dni bez żadnego braku. W profilach `small` i `standard` tak jest. Jeśli u Ciebie też, wyjaśnij dlaczego. Pomyśl, co jest tu przyczyną, a co skutkiem.
#
# **Pytanie 4.** Wyobraź sobie model, który uczy się przewidywać `sale_amount` na wszystkich wierszach z historii sprzedaży serii i nie ma żadnej informacji, która odróżnia brak towaru od słabego popytu. Co przewidzi dla dnia, w którym towar będzie dostępny cały czas, jeśli w danych treningowych ta seria miała długie braki w co drugim dniu? W którą stronę będzie się mylił?

# %% [markdown]
# *Twoja odpowiedź:*

# %% [markdown]
# ## Koniec labu
#
# Uruchom wszystkie sprawdzenia modułu jeszcze raz, z terminala:
#
# ```bash
# uv run course check 07
# uv run ruff check src
# uv run mypy
# ```
#
# Potem commit na osobnej gałęzi i pull request we własnym forku.
#
# Co zbudowałeś:
#
# - wczytywanie, które nie zależy od rozmiaru pliku, tylko od rozmiaru wyniku,
# - reguły, które wywracają pipeline, zanim zrobią to złe dane,
# - złączenia, które nie potrafią po cichu zgubić ani pomnożyć wierszy,
# - lagi i okna liczone wewnątrz serii, zawsze z przeszłości,
# - zbiór z kontraktem, od którego zaczyna każdy następny moduł.
#
# W module 08 zbudujesz na tym zbiorze pierwszy model i zobaczysz, jak łatwo oszukać samego siebie przy jego ocenie.
