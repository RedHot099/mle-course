# %% [markdown]
# # Lab 07: panel sprzedaży w pandas
#
# W tym labie pierwszy raz dotykasz zbioru, na którym zbudujesz resztę kursu: FreshRetailNet-50K. To 90 dni sprzedaży świeżych produktów w 898 sklepach, po jednym wierszu na parę sklep × produkt × dzień.
#
# Na koniec labu masz na dysku plik `data/processed/daily.parquet`. Każdy kolejny moduł, od pierwszego modelu po capstone, zaczyna od wczytania tego pliku. Jeśli coś tu zrobisz byle jak, będzie to wracać przez kolejne sto godzin.
#
# **Czas:** około 7 godzin. Nie rób tego na jedno posiedzenie.
#
# ## Jak pracujesz w tym labie
#
# Kod piszesz w dwóch miejscach:
#
# - **Funkcje do pakietu**: w plikach `src/freshcast/data/*.py`. Każda ma gotową sygnaturę i docstring, który jest specyfikacją. Twoje zadanie to ciało funkcji w miejscu `raise NotImplementedError`.
# - **Eksploracja**: w komórkach tego notebooka, tam gdzie widzisz `...`.
#
# Po każdym zadaniu uruchamiasz komórkę `check("07.x")`. Sprawdzenie działa na małej próbce danych z repozytorium i mówi, co jest nie tak. To samo zrobisz z terminala: `uv run course check 07`.
#
# Pod każdym zadaniem są trzy podpowiedzi, od ogólnej do prawie gotowego kodu. Otwieraj je po kolei i dopiero wtedy, gdy naprawdę utkniesz. Jeśli pracujesz z tutorem, wpisz `/hint`.
#
# | Zadanie | Plik | Czas |
# |---|---|---|
# | 07.0 Rozpoznanie pliku | notebook | 30 min |
# | 07.1 Wczytanie | `data/load.py` | 45 min |
# | 07.2 Reguły i anomalie | `data/validate.py` | 75 min |
# | 07.3 Wymiary i złączenia | `data/dims.py` | 60 min |
# | 07.4 Tablice godzinowe | `data/hourly.py` | 75 min |
# | 07.5 Obliczenia w serii | `data/panel.py` | 60 min |
# | 07.6 Zbiór przetworzony | `data/prepare.py` | 45 min |
# | 07.7 Eksploracja | notebook | 45 min |

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
print(f"Profil danych: {PROFILE.name} ({PROFILE.series} serii)")

# %% [markdown]
# `autoreload` sprawia, że po zapisaniu zmiany w pliku pakietu notebook widzi nową wersję bez restartu kernela.
#
# `CITIES` to filtr miast dla Twojego profilu danych. Profil wybrał `course doctor` na podstawie pamięci komputera. Wszystkie obliczenia w tym labie robisz na tym podzbiorze.

# %% [markdown]
# ## 07.0 Rozpoznanie pliku, zanim go wczytasz
#
# Plik `train.parquet` ma około 100 MB. To nic nie mówi o tym, ile zajmie w pamięci. Parquet jest skompresowany i kolumnowy, a pandas trzyma dane rozpakowane.
#
# Parquet pozwala przeczytać metadane bez dotykania danych. Zacznij od tego.

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
# pandas ma metodę `memory_usage(deep=True)`. Dla kolumn zagnieżdżonych podaje ona za mało: liczy obiekt tablicy (nagłówek), ale nie jej dane.
#
# Policz to uczciwie dla jednego wiersza:
#
# 1. `scalar_bytes`: suma `memory_usage(deep=True)` wszystkich kolumn poza dwiema zagnieżdżonymi, podzielona przez liczbę wierszy.
# 2. `nested_bytes`: dla jednej komórki zagnieżdżonej to nagłówek obiektu (120 bajtów według pandas) plus dane tablicy (`.nbytes`). Kolumny są dwie.
# 3. `total_gb`: oszacowanie dla wszystkich wierszy pliku, w GB.

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
# **Plik:** `src/freshcast/data/load.py`
#
# Napisz dwie funkcje:
#
# - `shrink_integers(df)`: zwraca kopię, w której każda kolumna całkowita ma najmniejszy typ mieszczący jej wartości.
# - `load_sales(path, cities=..., columns=...)`: czyta tylko wskazane kolumny i miasta, zamienia `dt` na datę, zmniejsza typy, sortuje po serii i dacie.
#
# Dokładna specyfikacja jest w docstringach.
#
# Dlaczego sortowanie już tutaj? Plik nie jest posortowany. Lagi i okna kroczące, które policzysz w 07.5, czytają "poprzedni wiersz tej samej serii". Na nieposortowanych danych dają bzdury bez żadnego błędu.
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
# Teraz użyj swojej funkcji na prawdziwych danych.

# %%
from freshcast.data.load import load_sales

daily = load_sales(RAW, cities=CITIES)
print(f"{len(daily):,} wierszy, {daily.memory_usage(deep=True).sum() / 1e6:.1f} MB")
daily.dtypes

# %% [markdown]
# Porównaj z tym, co dałoby wczytanie tych samych wierszy bez zmniejszania typów. W zmiennej `saving` policz, jaki ułamek pamięci zaoszczędziłeś (liczba między 0 a 1).

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

# %% [markdown]
# Większość zysku dają kolumny całkowite: identyfikator miasta mieści się w 1 bajcie zamiast 8, flagi w 1 zamiast 4. Data zamiast tekstu oszczędza kolejne 10 bajtów na wiersz i, co ważniejsze, pozwala liczyć na datach: odejmować je, wyciągać dzień tygodnia, sortować chronologicznie.
#
# Kolumn zmiennoprzecinkowych nie ruszamy. `float32` ma około 7 cyfr znaczących, więc sumy i średnie na milionach wierszy zaczynają się rozjeżdżać. Pamięć oszczędzona na floatach nie jest warta błędów, których nikt nie zauważy.

# %% [markdown]
# ## 07.2 Reguły i anomalie
#
# **Plik:** `src/freshcast/data/validate.py`
#
# Zanim cokolwiek policzysz, sprawdź, czy dane są tym, za co je bierzesz. Zasada tego kursu: **cicha zła prognoza jest gorsza niż błąd**. Funkcja walidująca ma się wywrócić głośno, z liczbą złych wierszy w komunikacie.
#
# ### Najpierw śledztwo
#
# Odpowiedz kodem na cztery pytania. To jest eksploracja: nie ma jednej dobrej formy odpowiedzi, liczy się wynik.

# %%
# Pytanie 1: ile wierszy powtarza parę (seria, dzień)?
# >>> SOLUTION 07.2
n_duplicated = int(daily.duplicated([*SERIES_KEY, DATE]).sum())
# --- STUB
#| n_duplicated = ...
# <<< SOLUTION
print(n_duplicated)

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
# To, co widzisz, zależy od profilu danych. W całym zbiorze są dwa wzorce:
#
# - Dwa produkty mają zero prawie we wszystkie dni, w każdym sklepie. Sprzedają się 10-15 razy lepiej niż przeciętny produkt i prawie nigdy nie mają flagi akcji.
# - Sześć innych produktów ma zero w pojedyncze dni, zawsze z `activity_flag == 1`. Sprzedaż jest wtedy około trzy razy wyższa niż w pozostałe dni tych samych serii.
#
# Drugi wzorzec wygląda jak prawdziwe rozdawnictwo w ramach akcji. Pierwszy może być produktem zawsze darmowym albo produktem, dla którego rabatu nikt nie zapisuje. Z danych tego nie rozstrzygniesz.
#
# Zapisz w komórce poniżej własnymi słowami: co wiesz na pewno, czego nie wiesz i co w związku z tym zrobisz z tą wartością.

# %% [markdown]
# *Twój wniosek:*

# %% [markdown]
# ### Decyzja i funkcje
#
# W tym kursie przyjmujemy taką decyzję. Zero, czymkolwiek jest, nie zachowuje się jak dolny koniec tej samej skali co 0.8 czy 0.6. Gdyby zostało liczbą, model liniowy potraktowałby je jako "rabat dwa razy głębszy niż 0.5" i dopasował do niego całą zależność sprzedaży od ceny. Dlatego zdejmujemy je ze skali: `discount` staje się `NaN`, a osobna kolumna `discount_is_zero` pamięta, gdzie zero było. Żadna informacja nie ginie.
#
# Nie robimy `fillna(1.0)`. "Nie wiem, co znaczy ta wartość" i "rabatu nie było" to dwie różne informacje, a wpisanych po cichu jedynek nikt później nie odróżni od prawdziwych.
#
# - `check_panel(df)`: cztery reguły z docstringa. Każda złamana reguła to `ValueError` z liczbą w komunikacie.
# - `clean_discount(df)`: zero zamienia na `NaN` i dodaje kolumnę `discount_is_zero`. Pozostałych wartości nie rusza. Rabat ujemny albo brak na wejściu to błąd.
#
# W całym zbiorze są też 34 wiersze z rabatem powyżej 1, najwyżej 1.088, w dwóch miastach spoza Twojego profilu. To cena o kilka procent wyższa od regularnej: nieudokumentowana, ale leżąca na tej samej skali. Zostawiamy ją. Sprawdzenie używa próbki, która takie wiersze zawiera. To częsta sytuacja: reguła napisana na podzbiorze spotyka dane, których autor nie widział.
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

# %% [markdown]
# ## 07.3 Wymiary i złączenia
#
# **Plik:** `src/freshcast/data/dims.py`
#
# Tabela, którą trzymasz w `daily`, to **tabela faktów**: jeden wiersz to jedno zdarzenie (sprzedaż serii w danym dniu). Informacje opisujące sklep albo produkt, które nie zmieniają się z dnia na dzień, trzyma się osobno w **tabelach wymiarów**: jeden wiersz na sklep, jeden wiersz na produkt.
#
# Powody są dwa. Pamięć: hierarchia produktu to cztery kolumny powtórzone w każdym wierszu. I jedno źródło prawdy: jeśli produkt zmieni kategorię, poprawiasz jeden wiersz.
#
# Wymiar dołączasz do faktów przez `merge`. I tu jest pułapka, którą zobaczysz na własne oczy.

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
# ### Funkcje
#
# - `build_store_dim(df)`: jeden wiersz na sklep z miastem, liczbą produktów i średnią sprzedażą.
# - `build_product_dim(df)`: jeden wiersz na produkt z hierarchią i liczbą sklepów.
# - `attach_dim(fact, dim, on)`: dołącza wymiar tak, żeby liczba i kolejność wierszy faktów się nie zmieniła. Zduplikowany klucz w wymiarze i klucz faktów bez pary w wymiarze to błędy.
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

# %% [markdown]
# Użyj wymiaru produktu, żeby odpowiedzieć na pytanie: która kategoria pierwszego poziomu (`first_category_id`) ma najwyższą średnią dzienną sprzedaż na serię? Zapisz jej identyfikator w `top_category`.

# %%
# >>> SOLUTION 07.3
with_category = attach_dim(daily, product_dim, on="product_id")
by_category = with_category.groupby("first_category_id")[TARGET].mean()
top_category = int(by_category.idxmax())
# --- STUB
#| top_category = ...
# <<< SOLUTION
print(f"Kategoria {top_category}")

# %% [markdown]
# ## 07.4 Tablice godzinowe
#
# **Plik:** `src/freshcast/data/hourly.py`
#
# Wracamy do dwóch ciężkich kolumn. `hours_sale` to sprzedaż w każdej z 24 godzin. `hours_stock_status` mówi, czy w danej godzinie towaru brakowało: **1 oznacza brak**.
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
# ### Funkcje
#
# - `load_hourly(path, cities=...)`: klucz, data i dwie kolumny godzinowe, posortowane jak w `load_sales`.
# - `to_matrix(column)`: z kolumny tablic robi jedną tablicę `(n, 24)`. Wiersz o innej długości niż 24 to błąd.
# - `summarise_hours(hourly)`: cztery liczby na wiersz, opisane w docstringu.
#
# Godziny 6:00-22:00 to pozycje 6 do 21 tablicy. W `schema.py` jest gotowy wycinek `OOS_WINDOW`.
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

# %% [markdown]
# ### Dwa pytania do danych
#
# Surowe dane mają kolumnę `stock_hour6_22_cnt`. Twoje `oos_hours` powinno dawać to samo. Skoro oba zbiory są posortowane tak samo, porównasz je pozycja po pozycji. W `n_disagree` policz wiersze, w których się różnią.

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
# Drugie pytanie: w ilu procentach wierszy zanotowano sprzedaż w godzinie oznaczonej jako brak towaru (`sales_while_oos > 0`)? I jaki to ułamek całej sprzedaży?

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
# **Plik:** `src/freshcast/data/panel.py`
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
# ### Funkcje
#
# - `is_sorted_panel(df)`: czy wiersze są ułożone po serii i dacie.
# - `add_lag(df, column, lag)`: wartość sprzed `lag` dni w tej samej serii.
# - `add_rolling_mean(df, column, window, lag=1)`: średnia z okna `window` dni, które kończy się `lag` dni przed wierszem.
# - `dow_profile(df)`: typowy kształt tygodnia, czyli względna sprzedaż według dnia tygodnia.
#
# Lag przez `shift` zakłada, że kolejne wiersze serii to kolejne dni. Gwarantuje to `check_panel` z zadania 07.2.
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

# %% [markdown]
# Czy te dwie kolumny coś mówią o sprzedaży? Policz korelację każdej z nich z `sale_amount`. Wynik zapisz w `corr_lag` i `corr_mean`.

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

# %% [markdown]
# ## 07.6 Zbiór przetworzony
#
# **Plik:** `src/freshcast/data/prepare.py`
#
# Masz wszystkie klocki. Teraz złóż z nich jedną funkcję, która z surowego pliku robi zbiór gotowy do modelowania, i dwie funkcje do zapisu i odczytu.
#
# - `prepare_daily(raw_path, cities=...)`: wczytaj, sprawdź panel, wyczyść rabat, dołącz podsumowanie godzin. Wynik ma dokładnie kolumny `PROCESSED_COLUMNS` z `schema.py`.
# - `save_processed(daily, directory)`: zapisuje `daily.parquet`.
# - `load_processed(directory)`: czyta i sprawdza, czy kolumny zgadzają się z kontraktem.
#
# `PROCESSED_COLUMNS` to **kontrakt**. Kod, który ten plik zapisuje, i kod, który go czyta, mogą powstać w odstępie tygodni. Jeśli ktoś doda kolumnę po jednej stronie, a plik na dysku zostanie stary, chcesz dostać czytelny błąd przy wczytaniu, a nie `KeyError` trzy moduły dalej.
#
# Zwróć uwagę na nazwę: surowa kolumna `stock_hour6_22_cnt` nie wchodzi do zbioru przetworzonego. Zastępuje ją Twoje `oos_hours`. Zanim wyrzucisz surową kolumnę, porównaj ją z własną i rzuć błąd, jeśli się różnią.
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

# %% [markdown]
# ## 07.7 Eksploracja
#
# Ta część nie ma sprawdzeń. Masz czysty zbiór, więc obejrzyj go, zanim zaczniesz cokolwiek przewidywać. Trzy wykresy są gotowe. Pod każdym są pytania. Odpowiedz na nie pisemnie w komórce pod wykresem: jedno, dwa zdania. Jeśli pracujesz z tutorem, omów z nim swoje odpowiedzi.

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
# **Pytanie 1.** Sprzedaż rośnie przez całe 90 dni. Podaj dwa różne wyjaśnienia tego wzrostu. Czy z tych danych da się rozstrzygnąć, które jest prawdziwe?

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
# **Pytanie 3.** Krzywa nie spada od razu. Dni z dwiema albo trzema godzinami bez towaru mają wyższą sprzedaż niż dni bez żadnego braku. Dlaczego? Pomyśl, co jest tu przyczyną, a co skutkiem.
#
# **Pytanie 4.** Wyobraź sobie model, który uczy się przewidywać `sale_amount` na wszystkich wierszach. Co przewidzi dla dnia, w którym towar będzie dostępny cały czas, jeśli w danych treningowych ta seria miała długie braki w co drugim dniu? W którą stronę będzie się mylił?

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
