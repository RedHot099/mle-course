# %% [markdown]
# # Lab 06: czyszczenie sprzedaży sklepu internetowego
#
# UCI Online Retail II to dwa lata faktur brytyjskiego sklepu z upominkami: milion linii, każda z towarem, ilością, ceną i klientem. Plik jest prawdziwy, więc brudny w prawdziwy sposób: anulowania, odpisy magazynowe, próbki za darmo, opłaty pocztowe udające towary, klienci bez identyfikatora, arkusze, które na siebie zachodzą.
#
# Z tego pliku zbudujesz tabelę dziennej sprzedaży towarów: jeden wiersz na towar i dzień, z liczbą sprzedanych sztuk, zwróconych sztuk i przychodem. W module 17 wróci ona jako wejście cudzego kodu, który będziesz naprawiać.
#
# Każda decyzja w tym labie jest twierdzeniem o danych. Zanim coś usuniesz albo wypełnisz, policz, czego to dotyczy, i zapisz liczbę w docstringu. Docstringi w pakiecie już mają te liczby: nie wierz im, sprawdź je na pliku.
#
# **Czas:** około 6 godzin.
#
# Całość to łańcuch kroków. Każdy krok to funkcja, która dostaje ramkę z poprzedniego kroku i zwraca nową:
#
# skoroszyt `.xlsx` → `read_sheets` → cache Parquet → `load_raw` → `check_raw` → `add_flags` → `drop_sheet_overlap` → `product_lines` → `daily_totals` → `check_daily` → plik `online_retail_daily.parquet`
#
# Wszystkie funkcje piszesz w pakiecie, w katalogu `src/freshcast/warmup/`. Duże zadania mają kroki z literą (06.1a, 06.1b, ...): każdy krok to jedna funkcja albo jedna komórka notebooka.
#
# | Zadanie | Plik w `src/freshcast/warmup/` | Funkcja albo zmienna | Czas |
# |---|---|---|---|
# | 06.1a | `online_retail.py` | `read_sheets` | 35 min |
# | 06.1b | `online_retail.py` | `build_cache` | 10 min |
# | 06.1c | `online_retail.py` | `load_raw` | 15 min |
# | 06.2a | `online_retail.py` | `check_raw`, reguły 1-4 | 20 min |
# | 06.2b | `online_retail.py` | `check_raw`, reguły 5-8 | 25 min |
# | 06.3 | `lines.py` | `add_flags` | 40 min |
# | 06.4a | `lines.py` | `drop_sheet_overlap` | 35 min |
# | 06.4b | `lines.py` | `flag_repeat_lines` | 10 min |
# | 06.4c | notebook | `all_duplicates`, `deduplicated`, `copies`, `repeats` | 15 min |
# | 06.5 | `lines.py` | `product_lines` | 45 min |
# | 06.6a | `daily.py` | `daily_totals` | 15 min |
# | 06.6b | `daily.py` | `check_daily` | 25 min |
# | 06.7a | `daily.py` | `build_daily` | 15 min |
# | 06.7b | `daily.py` | `save_daily`, `load_daily` | 15 min |
# | 06.8 | notebook | eksploracja: pięć pytań | 40 min |
#
# Jak pracujesz:
#
# - Funkcje piszesz w edytorze, w miejscu `raise NotImplementedError("Zadanie 06.x")`. Nazw i argumentów nie zmieniasz. Stałe (nazwy kolumn, wzorce) są gotowe na górze `online_retail.py`.
# - W `lines.py` i `daily.py` stałe i funkcje z innych modułów importujesz sam, na górze pliku, na przykład `from freshcast.warmup.online_retail import CANCELLATION_PREFIX`. Importy notebooka nie działają w plikach pakietu.
# - Docstring funkcji to dokładna umowa: co przyjmuje, co zwraca, kiedy zgłasza błąd. Tekst w notebooku mówi to samo prostszymi słowami.
# - `check("06.x")` w notebooku albo `uv run course check 06.x` w terminalu sprawdza zadanie na małej próbce prawdziwego pliku, więc trwa sekundy. Kroki z tą samą liczbą (06.1a, 06.1b, 06.1c) sprawdza jedno `check("06.1")`.
# - Pierwsza komórka włącza `autoreload`: notebook widzi zmiany zapisane w pakiecie bez restartu kernela.

# %%
# %load_ext autoreload
# %autoreload 2

import time

import pandas as pd

from coursekit import paths
from coursekit.nb import check
from freshcast.warmup import daily, lines, online_retail

XLSX = paths.ONLINE_RETAIL
CACHE = paths.ONLINE_RETAIL_CACHE
print(XLSX.name, f"{XLSX.stat().st_size / 1e6:.0f} MB")

# %% [markdown]
# `XLSX` to ścieżka (`Path`) do skoroszytu `data/raw/online_retail/online_retail_II.xlsx`, a `CACHE` to ścieżka pliku Parquet, który zbudujesz w 06.1b: `data/raw/online_retail/online_retail_II.parquet`. Moduły pakietu są zaimportowane jako `online_retail`, `lines` i `daily`, więc w notebooku piszesz na przykład `lines.add_flags(raw)`.
#
# ## Plik tak, jak przychodzi
#
# Najpierw wczytaj skoroszyt bez żadnych ustawień, tak jak robi to większość tutoriali. To potrwa do około półtorej minuty. Zapamiętaj ten czas: porównasz go z odczytem z Parquet w komórce pod sprawdzeniem 06.1. Nigdzie go nie wpisujesz.

# %%
start = time.perf_counter()
sheets = pd.read_excel(XLSX, sheet_name=None)
print(f"{time.perf_counter() - start:.0f} s, arkusze: {list(sheets)}")
naive = pd.concat(sheets.values(), ignore_index=True)
naive.info()

# %% [markdown]
# `object` przy numerze faktury i kodzie towaru to sygnał ostrzegawczy. Sprawdź, co naprawdę jest w tych kolumnach:

# %%
for column in ["Invoice", "StockCode"]:
    print(column, naive[column].map(type).value_counts().to_dict())

starts_with_c = naive["Invoice"].str.startswith("C")
print("startswith('C'):", starts_with_c.value_counts(dropna=False).to_dict())

# %% [markdown]
# Liczby i napisy w jednej kolumnie. `.str.startswith("C")` na komórce z liczbą nie rzuca błędu, tylko zwraca `NaN`, więc o 98% faktur ta operacja nic nie mówi. Taki błąd nie zatrzyma programu, tylko po cichu da zły wynik.
#
# Zapis do Parquet jest bardziej wymagający niż pandas:

# %%
try:
    naive.to_parquet(paths.PROCESSED_DIR / "naive.parquet", index=False)
except Exception as error:  # noqa: BLE001 - the error is what we want to see
    print(type(error).__name__, str(error)[:200])

# %% [markdown]
# ## 06.1 Wczytanie z typami i cache
#
# Otwórz `src/freshcast/warmup/online_retail.py`. Stałe na górze pliku są gotowe: nazwy kolumn (`SHEET_HEADERS`, `SHEET`, `RAW_COLUMNS`), wzorce, kontrakt tabeli wynikowej. Używasz ich w funkcjach bezpośrednio, bez importu, bo są w tym samym pliku.
#
# ### 06.1a `read_sheets`
#
# **Cel:** wczytać skoroszyt raz, z jawnymi typami, tak żeby żadna kolumna nie mieszała liczb z tekstem i żeby ten sam towar miał jeden kod.
#
# **Gdzie:** `online_retail.py`, funkcja `read_sheets`.
#
# **Wejście:** `path`: `Path`, ścieżka do skoroszytu `.xlsx`. W notebooku `XLSX`. Co jest w skoroszycie:
#
# - dwa arkusze, "Year 2009-2010" i "Year 2010-2011", z tymi samymi ośmioma nagłówkami,
# - jeden wiersz to jedna linia faktury, czyli jeden towar na jednej fakturze.
#
# **Wynik:** `pd.DataFrame` z kolumnami `RAW_COLUMNS`, w tej kolejności, z indeksem 0..n-1. Najpierw wiersze pierwszego arkusza, potem drugiego, w kolejności pliku.
#
# | Kolumna | Typ | Co znaczy |
# |---|---|---|
# | `invoice` | `str` | numer faktury: sześć cyfr, z literą `C` dla anulowania, `A` dla korekty |
# | `stock_code` | `str` | kod towaru, bez odstępów na brzegach, wielkimi literami |
# | `description` | `str` | opis towaru. Brak zostaje brakiem, a nie napisem `"nan"` |
# | `quantity` | liczba całkowita | ilość sztuk, ujemna na anulowaniach |
# | `invoice_date` | `datetime64` | data i godzina faktury |
# | `price` | `float64` | cena jednej sztuki w funtach |
# | `customer_id` | `Int64` | numer klienta, liczba całkowita z brakami |
# | `country` | `str` | kraj klienta |
# | `sheet` | `str` | nazwa arkusza, z którego pochodzi wiersz |
#
# `ValueError`, gdy któremuś arkuszowi brakuje nagłówka z `SHEET_HEADERS`.
#
# **Skorzystaj z:**
#
# - `SHEET_HEADERS` z góry pliku. Przypisuje nagłówkowi w skoroszycie nazwę kolumny.
# - `SHEET` z góry pliku. To nazwa kolumny `"sheet"`.
# - `RAW_COLUMNS` z góry pliku. Wyznacza kolejność kolumn wyniku.
# - `dtype` w `pd.read_excel` i typ `"Int64"` z wykładu, sekcja "Typy". Razem ustawiają typy już przy czytaniu.
# - `sheet_name=None` z wykładu, sekcja "Narzędzia, których użyjesz w labie". Wczytuje wszystkie arkusze naraz.
# - `rename` z tej samej sekcji. Zmienia nazwy kolumn według `SHEET_HEADERS`.
# - `pd.concat` z tej samej sekcji. Skleja arkusze jeden pod drugim.
# - `.str.strip()` i `.str.upper()` z tej samej sekcji. Razem porządkują `stock_code`.
#
# **Kroki:**
#
# 1. Wczytaj wszystkie arkusze naraz i podaj `dtype` jako słownik nagłówek → typ. Klucze to nagłówki ze skoroszytu (`"Invoice"`, `"Customer ID"`), bo typy działają przy czytaniu, przed zmianą nazw. Numer faktury, kod, opis i kraj dostają typ tekstowy, a klient typ `"Int64"`. Data, ilość i cena wczytują się dobrze same. Typ tekstowy podany przy czytaniu zostawia pustą komórkę jako brak. Liczbę z komórki ten typ zamienia na napis bez `.0` (`489434` → `"489434"`). Po wczytaniu sprawdź `isna().sum()` dla kolumny `Description`. Wynik ma się zgadzać z liczbą z docstringu.
# 2. Przejdź po słowniku arkuszy. Dla każdego arkusza sprawdź, czy ma wszystkie nagłówki z `SHEET_HEADERS`. Jeśli brakuje nagłówka, zgłoś `ValueError` z nazwą arkusza i brakującymi nagłówkami.
# 3. Zmień nazwy kolumn według `SHEET_HEADERS`. Dodaj kolumnę `sheet` z nazwą arkusza.
# 4. Sklej arkusze jeden pod drugim, z nowym indeksem.
# 5. W `stock_code` usuń odstępy na brzegach i zamień litery na wielkie. Potem ustaw kolumny w kolejności `RAW_COLUMNS`.
#
# ### 06.1b `build_cache`
#
# **Cel:** zapisać wynik `read_sheets` raz do Parquet, żeby każde następne wczytanie trwało ułamek sekundy zamiast minuty.
#
# **Gdzie:** `online_retail.py`, funkcja `build_cache`.
#
# **Wejście:**
#
# - `xlsx`: `Path` do skoroszytu. W notebooku `XLSX`.
# - `cache`: `Path` pliku Parquet do zapisania. W notebooku `CACHE`.
#
# **Wynik:** funkcja zwraca `cache`. Po wywołaniu:
#
# - plik istnieje i zawiera tabelę z `read_sheets`, bez indeksu,
# - brakujące katalogi już istnieją,
# - wcześniejszy plik pod tą ścieżką jest nadpisany.
#
# Błędy jak w `read_sheets`.
#
# **Skorzystaj z:**
#
# - `read_sheets` z 06.1a. Daje tabelę do zapisania.
# - `to_parquet(..., index=False)` z wykładu, sekcja "Zapis i odczyt Parquet". Zapisuje tabelę bez indeksu.
# - `mkdir(parents=True, exist_ok=True)` z tej samej sekcji. Tworzy brakujące katalogi.
#
# ### 06.1c `load_raw`
#
# **Cel:** wczytać cache i od razu wykryć plik zapisany przez starszą wersję kodu.
#
# **Gdzie:** `online_retail.py`, funkcja `load_raw`.
#
# **Wejście:** `cache`: `Path` pliku Parquet zapisanego przez `build_cache`.
#
# **Wynik:** `pd.DataFrame` taka sama jak z `read_sheets`: te same kolumny, typy i kolejność.
#
# Błędy:
#
# - `FileNotFoundError`, gdy pliku nie ma,
# - `ValueError`, gdy lista kolumn pliku, razem z kolejnością, różni się od `RAW_COLUMNS`.
#
# **Skorzystaj z:**
#
# - `Path.is_file()`. Sprawdza, czy plik istnieje.
# - `pd.read_parquet`. Wczytuje cache.
# - `RAW_COLUMNS` z góry pliku. Z tą listą porównujesz kolumny pliku.
#
# **Sprawdzenie 06.1a-06.1c:** `check("06.1")` albo `uv run course check 06.1`. Sprawdzenie kolejno:
#
# - czyta małą próbkę skoroszytu: 40 wierszy w dwóch arkuszach, z tymi samymi typami komórek,
# - sprawdza kolumny, typy i kody towarów,
# - zapisuje i czyta cache w katalogu tymczasowym.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `pd.read_excel` ma parametr `dtype`, słownik kolumna → typ. Numer faktury i kod towaru to napisy (`str`). Identyfikator klienta ma braki, więc zwykły `int64` go nie pomieści: pandas ma na to typ `"Int64"` z wielką literą.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `sheet_name=None` zwraca słownik arkuszy. Przejdź po nim, dodaj każdemu kolumnę z nazwą arkusza, połącz przez `pd.concat(..., ignore_index=True)`. Kod towaru porządkujesz przez `.str.strip().str.upper()`. Sprawdź, czy każdy arkusz ma wszystkie nagłówki, zanim zmienisz nazwy kolumn.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# sheets = pd.read_excel(path, sheet_name=None, dtype={"Invoice": str, "StockCode": str, "Description": str})
# frames = []
# for name, sheet in sheets.items():
#     missing = set(SHEET_HEADERS) - set(sheet.columns)
#     ...
#     frames.append(sheet.rename(columns=SHEET_HEADERS).assign(**{SHEET: name}))
# raw = pd.concat(frames, ignore_index=True)
# ```
#
# Słownik `dtype` w pierwszej linii jest niepełny: dopisz do niego pozostałe typy z kroku 1, czyli tekst dla kraju i `"Int64"` dla klienta.
#
# </details>

# %%
check("06.1")

# %% [markdown]
# Zbuduj cache raz i porównaj czasy. Od tej komórki `raw` to surowa tabela z typami: jeden wiersz to jedna linia faktury. Z niej korzystają wszystkie dalsze zadania.

# %%
if not CACHE.is_file():
    online_retail.build_cache(XLSX, CACHE)

start = time.perf_counter()
raw = online_retail.load_raw(CACHE)
print(f"Parquet: {time.perf_counter() - start:.2f} s, {len(raw):,} wierszy, {CACHE.stat().st_size / 1e6:.1f} MB")
raw.dtypes

# %% [markdown]
# ## 06.2 Reguły surowej tabeli
#
# Każdy dalszy krok zakłada coś o danych: że numer faktury ma sześć cyfr, że ujemna ilość ma powód, że faktura ma najwyżej jednego klienta. Założenie, którego nikt nie sprawdza, pęknie po cichu przy następnej wersji pliku.
#
# **Cel:** jedna funkcja, która sprawdza osiem założeń o surowej tabeli i zatrzymuje przetwarzanie przy pierwszym złamanym, z komunikatem, który mówi, co się zmieniło.
#
# **Gdzie:** `online_retail.py`, funkcja `check_raw`. Piszesz ją w dwóch krokach, ale to jedna funkcja i jedno sprawdzenie.
#
# **Wejście:** `raw`: `pd.DataFrame`, surowa tabela z `load_raw`, z kolumnami `RAW_COLUMNS`.
#
# **Wynik:** funkcja niczego nie zwraca (`None`), gdy wszystkie reguły są spełnione. Przy pierwszej złamanej regule, w kolejności z docstringu, zgłasza `ValueError`. Komunikat błędu:
#
# - mówi, która reguła jest złamana,
# - przy regule 1 wymienia kolumny,
# - przy regułach 2-7 podaje liczbę wierszy, które łamią regułę,
# - przy regule 8 podaje liczbę faktur.
#
# Liczbę wierszy albo faktur podajesz jako liczbę w tekście. Możesz dodać przykład pierwszego złego wiersza. Sprawdzasz dokładnie osiem reguł z docstringu. Anulowanie z dodatnią ilością i faktura bez klienta są dozwolone.
#
# **Skorzystaj z:**
#
# - `RAW_COLUMNS` z góry pliku. Reguła 1 porównuje z tą listą kolumny `raw`.
# - `REQUIRED_COLUMNS` z góry pliku. Kolumny, w których reguła 2 szuka braków.
# - `INVOICE_PATTERN` z góry pliku. Wzorzec numeru faktury dla reguły 3.
# - `CANCELLATION_PREFIX` z góry pliku. Prefiks anulowania dla reguły 6.
# - `ADJUSTMENT_PREFIX` z góry pliku. Prefiks korekty dla reguły 7.
# - `isna` i `any(axis=1)` z wykładu, sekcja "Braki". Razem znajdują wiersze z brakiem.
# - wzoru maski i komunikatu z wykładu, sekcja "Założenie to kod, który zgłasza błąd".
# - `.str.fullmatch` z tej samej sekcji. Sprawdza, czy cały numer faktury pasuje do wzorca.
# - `groupby(...).nunique()` z wykładu, sekcja "Narzędzia, których użyjesz w labie". Liczy różne wartości w obrębie faktury.
#
# ### 06.2a Reguły 1-4: kolumny, braki, formaty
#
# **Kroki:**
#
# 1. Reguła 1: sprawdź, czy lista kolumn `raw` jest równa `RAW_COLUMNS`.
# 2. Reguła 2: policz wiersze (nie komórki) z brakiem w którejś z `REQUIRED_COLUMNS`.
# 3. Reguła 3: policz wiersze, w których numer faktury nie pasuje w całości do `INVOICE_PATTERN`. Liczysz wiersze, nie różne numery: trzy wiersze tej samej złej faktury to 3. Tylko reguła 8 liczy faktury.
# 4. Reguła 4: policz kody towarów, które różnią się od siebie samych po usunięciu odstępów i zamianie na wielkie litery.
#
# Każda reguła to maska złych wierszy, jej suma i jeden `if` z `raise`.
#
# ### 06.2b Reguły 5-8: ilości, ceny, faktury
#
# **Kroki:**
#
# 1. Reguła 5: policz wiersze z ilością równą 0.
# 2. Reguła 6: policz wiersze z ujemną ilością, która nie jest dozwolona. Ujemna ilość jest dozwolona, gdy faktura to anulowanie (`C`) albo gdy cena wynosi 0. Zły wiersz ma więc trzy cechy naraz: ilość ujemna, faktura nie zaczyna się od `C`, cena różna od 0. Na prawdziwym `raw` ta reguła ma dać 0 wierszy. Jeśli daje tysiące, pomyliłeś się w łączeniu trzech warunków. Każdy warunek weź w nawias, a `~` postaw przed warunkiem, który odwracasz.
# 3. Reguła 7: policz wiersze, w których cena jest ujemna, a faktura nie zaczyna się od `A`.
# 4. Reguła 8: policz faktury, które mają więcej niż jednego klienta albo więcej niż jeden kraj. Liczysz faktury, nie wiersze. Grupuj po `invoice` i licz różne wartości w grupie.
#
# **Sprawdzenie 06.2a i 06.2b:** `check("06.2")` albo `uv run course check 06.2`. Sprawdzenie podaje dwa rodzaje danych:
#
# - próbkę prawdziwych danych, na której wszystkie reguły są spełnione,
# - małe ramki, z których każda łamie jedną regułę w trzech wierszach. Komunikat ma wtedy zawierać liczbę 3.
#
# Ta sama komórka uruchamia `check_raw(raw)` na całym pliku. Brak wydruku i brak błędu znaczy, że reguły są spełnione.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Jedna reguła to maska wierszy, które ją łamią, i jeden `if`. Komunikat mówi, która reguła, ile wierszy i jak wygląda pierwszy z nich.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Wzorzec sprawdzasz przez `.str.fullmatch`, nie `.str.match`: `match` kotwiczy tylko początek, więc przepuści siedem cyfr. Regułę "jedna faktura, jeden klient" sprawdza `groupby("invoice")["customer_id"].nunique()`. Zanim uwierzysz regule o ujemnych ilościach, uruchom ją na prawdziwym pliku.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# bad = ~raw["invoice"].str.fullmatch(INVOICE_PATTERN)
# if bad.any():
#     example = raw.loc[bad, "invoice"].iloc[0]
#     raise ValueError(f"{int(bad.sum())} invoice numbers do not match {INVOICE_PATTERN}, e.g. {example!r}")
# ```
#
# </details>

# %%
check("06.2")
online_retail.check_raw(raw)

# %% [markdown]
# ## 06.3 Flagi zamiast usuwania
#
# **Cel:** opisać każdą linię czterema flagami (prawda albo fałsz), nic nie usuwając. O tym, co zrobić z oflagowanymi liniami, zdecydujesz w 06.5. Do tego czasu możesz te linie policzyć i obejrzeć.
#
# **Gdzie:** `src/freshcast/warmup/lines.py`, funkcja `add_flags`.
#
# **Wejście:** `raw`: `pd.DataFrame`, surowa tabela z `load_raw` (w notebooku `raw`).
#
# **Wynik:** nowa `pd.DataFrame`. `raw` zostaje bez zmian. Nowa tabela ma:
#
# - wszystkie kolumny `raw`, a za nimi cztery kolumny typu `bool`, w kolejności `FLAG_COLUMNS`,
# - te same wiersze, w tej samej kolejności, z tym samym indeksem.
#
# | Flaga | `True`, gdy |
# |---|---|
# | `is_cancellation` | numer faktury zaczyna się od `C` (anulowanie) |
# | `is_non_product` | kod towaru nie pasuje w całości do `PRODUCT_CODE_PATTERN` (pięć cyfr i najwyżej dwie litery): opłata pocztowa, korekta, rabat |
# | `is_missing_customer` | brak `customer_id` |
# | `is_bad_price` | cena wynosi 0 albo mniej |
#
# **Skorzystaj z:**
#
# - `CANCELLATION_PREFIX` z `online_retail.py`. Rozpoznaje anulowanie po numerze faktury.
# - `PRODUCT_CODE_PATTERN` z `online_retail.py`. Wzorzec kodu dla flagi `is_non_product`.
# - `assign` z wykładu, sekcja ".loc, assign i łańcuchy". Dodaje cztery flagi w nowej tabeli.
# - `.str.startswith`, `.str.fullmatch`, `isna` i `~` (zaprzeczenie maski) z wykładu. Razem budują maski flag.
#
# Obie stałe dopisz w `lines.py` do importu z `freshcast.warmup.online_retail` na górze pliku. Flaga `is_non_product` to umowny podział według wzorca kodu, nie pewność, że linia nie dotyczy żadnego towaru.
#
# **Kroki:**
#
# 1. Dla każdej flagi zbuduj maskę z tabeli powyżej.
# 2. Zwróć `raw.assign(...)` z czterema maskami. Nie przypisuj do `raw[...]`, bo takie przypisanie zmieniłoby tabelę wołającego.
#
# **Sprawdzenie:** `check("06.3")` albo `uv run course check 06.3`. Sprawdzenie podaje 11 ręcznie napisanych linii i porównuje ich flagi z oczekiwanymi. Wśród tych linii są między innymi kody `POST`, `DCGS0058`, `85123ABC`, `8512`, `79323LP`.
#
# Komórka pod sprawdzeniem tworzy `flagged` na całym pliku i wypisuje liczbę `True` w każdej fladze. Porównaj te liczby z liczbami w docstringu `add_flags`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Każda flaga to jedna maska z docstringu. Nową tabelę robisz przez `raw.assign(...)`, bez przypisywania do `raw[...]`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Anulowanie rozpoznajesz po prefiksie faktury, nie po znaku ilości. Nie-towar to kod, który nie pasuje do `PRODUCT_CODE_PATTERN` w całości. Zła cena to cena nie większa od zera.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# return raw.assign(
#     is_cancellation=raw["invoice"].str.startswith(CANCELLATION_PREFIX),
#     is_non_product=~raw["stock_code"].str.fullmatch(PRODUCT_CODE_PATTERN),
#     ...
# )
# ```
#
# </details>

# %%
check("06.3")

# %%
flagged = lines.add_flags(raw)
flagged[online_retail.FLAG_COLUMNS].sum()

# %% [markdown]
# Anulowanie po prefiksie czy po znaku ilości? Porównaj:

# %%
negative = flagged["quantity"] < 0
pd.crosstab(negative, flagged["is_cancellation"], rownames=["ilość < 0"], colnames=["faktura C"])

# %% [markdown]
# Ujemne linie spoza faktur C to nie zwroty. Obejrzyj kilka:

# %%
flagged.loc[negative & ~flagged["is_cancellation"], ["invoice", "stock_code", "description", "quantity", "price", "customer_id"]].sample(8, random_state=0)

# %% [markdown]
# ## 06.4 Duplikaty: kopie i powtórzenia
#
# `drop_duplicates()` na całej tabeli (bez kolumny `sheet`) usuwa 34 335 wierszy. To dwa różne zjawiska:
#
# - **kopie z eksportu**: faktury z 1-9 grudnia 2010 są w obu arkuszach. Kopię usuwasz bez wahania,
# - **powtórzone linie w źródle**: ta sama linia dwa razy na jednej fakturze. Nie wiesz, czy to błąd, czy dwa zamówienia tego samego. Tych nie usuwasz, tylko je oznaczasz.
#
# ### 06.4a `drop_sheet_overlap`
#
# **Cel:** usunąć drugą kopię faktur, które eksport zapisał w obu arkuszach, żeby dziewięć dni sprzedaży nie liczyło się dwa razy.
#
# **Gdzie:** `lines.py`, funkcja `drop_sheet_overlap`.
#
# **Wejście:** `raw`: `pd.DataFrame` z kolumnami `invoice`, `sheet` i `quantity`, z flagami albo bez. W notebooku `flagged` z 06.3.
#
# **Wynik:** nowa `pd.DataFrame` z tymi samymi kolumnami, bez wierszy późniejszych kopii. Wiersze stoją w pierwotnej kolejności, z indeksem 0..n-1. Które wiersze zostają:
#
# - Z faktury, która jest w kilku arkuszach, zostaje kopia z arkusza pierwszego według nazwy (`"Year 2009-2010"` przed `"Year 2010-2011"`). Ta kopia zostaje także wtedy, gdy jej wiersze stoją w tabeli później.
# - Tabela bez takich faktur wraca z wszystkimi wierszami.
#
# `ValueError`, gdy kopie jednej faktury różnią się:
#
# - liczbą linii,
# - sumą ilości.
#
# Takie wiersze nie są wtedy kopiami. Komunikat podaje, ile jest takich faktur.
#
# **Skorzystaj z:**
#
# - `groupby(...)["sheet"].nunique()` i `transform` z wykładu, sekcja "Narzędzia, których użyjesz w labie". Razem dają każdemu wierszowi wynik policzony dla jego faktury.
# - `.loc[maska]`. Zostawia wiersze, które nie są późniejszą kopią.
# - `reset_index(drop=True)` z wykładu, sekcja "Series i DataFrame". Nadaje nowy indeks.
#
# **Kroki:**
#
# 1. Dla każdego wiersza ustal, w ilu arkuszach jest jego faktura. Jeśli arkuszy jest więcej niż jeden, wiersz należy do wspólnej faktury.
# 2. Dla każdego wiersza ustal pierwszy według nazwy arkusz jego faktury. Wiersz wspólnej faktury z innego arkusza to późniejsza kopia.
# 3. Sprawdź, że kopie są kopiami. Dla każdej wspólnej faktury i każdego arkusza policz linie i sumę ilości. W obrębie faktury te liczby muszą być takie same we wszystkich arkuszach. Policz faktury, w których liczby się różnią, i zgłoś `ValueError`.
# 4. Zostaw wiersze, które nie są późniejszą kopią. Potem nadaj nowy indeks.
#
# ### 06.4b `flag_repeat_lines`
#
# **Cel:** oznaczyć linie, które powtarzają wcześniejszą linię co do wszystkiego, bez ich usuwania. Dzięki fladze każdy może zmierzyć, co zmieniłoby ich usunięcie.
#
# **Gdzie:** `lines.py`, funkcja `flag_repeat_lines`.
#
# **Wejście:** `raw`: `pd.DataFrame`, surowa tabela z flagami albo bez. W notebooku `deduplicated` z 06.4c.
#
# **Wynik:** nowa `pd.DataFrame` z kolumnami `raw` i za nimi kolumną `is_repeat_line` (`bool`). Te same wiersze, kolejność i indeks. Wartości `is_repeat_line`:
#
# - `True` dla każdego wiersza, który ma te same wartości we wszystkich ośmiu `LINE_COLUMNS` co któryś wcześniejszy wiersz,
# - `False` dla pierwszego wystąpienia.
#
# Kolumna `sheet` nie jest porównywana. Brak w tej samej kolumnie liczy się jako równy brakowi.
#
# **Skorzystaj z:**
#
# - `LINE_COLUMNS`, zdefiniowane na górze `lines.py`. Osiem kolumn linii, bez `sheet`.
# - `REPEAT_FLAG` z `online_retail.py`. To nazwa kolumny `"is_repeat_line"`. Zaimportuj stałą albo wpisz nazwę wprost.
# - `duplicated` z `subset` i `keep` z wykładu, sekcja "Duplikaty". Oznacza wiersze powtórzone.
#
# **Sprawdzenie 06.4a i 06.4b:** `check("06.4")` albo `uv run course check 06.4`. Sprawdzenie buduje dwa arkusze po kilka linii. Faktura 500001 jest w obu arkuszach, a w każdym arkuszu jest też linia powtórzona. Z 10 wierszy `drop_sheet_overlap` ma zostawić 7.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Kopia z eksportu to faktura, która występuje w dwóch arkuszach. `groupby("invoice")["sheet"].nunique()` powie, które to są.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Z faktur w obu arkuszach zostaw linie z jednego: z pierwszego według nazwy. Zanim uznasz je za kopie, sprawdź w notebooku, że linie w obu arkuszach są identyczne. Do `flag_repeat_lines` służy `duplicated(subset=..., keep="first")`, bez kolumny `sheet` w `subset`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# by_invoice = raw.groupby("invoice")["sheet"]
# shared = by_invoice.transform("nunique") > 1
# later = shared & (raw["sheet"] != by_invoice.transform("min"))
# return raw.loc[~later].reset_index(drop=True)
# ```
#
# </details>

# %%
check("06.4")

# %% [markdown]
# ### 06.4c Ile czego usunąłeś
#
# **Cel:** rozdzielić 34 335 identycznych wierszy na kopie z eksportu i powtórzenia w źródle, liczbami.
#
# **Gdzie:** komórka pod tym tekstem, cztery zmienne w miejscu `...`.
#
# **Wejście:** `raw` (06.1), `flagged` (06.3).
#
# **Wynik:**
#
# - `all_duplicates`: `int`, ile wierszy `raw` powtarza wcześniejszy wiersz we wszystkich kolumnach oprócz `sheet`. Tyle usunęłoby `drop_duplicates()` na kolumnach linii.
# - `deduplicated`: `pd.DataFrame`, `flagged` bez kopii z eksportu. Ma kolumny `flagged`, razem z flagami. Używasz jej w 06.5 i 06.8.
# - `copies`: `int`, ile wierszy usunęło `drop_sheet_overlap`.
# - `repeats`: `int`, ile wierszy `deduplicated` oznaczyłoby `flag_repeat_lines` jako powtórzone (`True` w `is_repeat_line`). Flagę liczysz na boku, w osobnym wyniku. Sama `deduplicated` zostaje z kolumnami `flagged`, bez `is_repeat_line`.
#
# **Skorzystaj z:**
#
# - `lines.drop_sheet_overlap` z 06.4a. Usuwa kopie z eksportu.
# - `lines.flag_repeat_lines` z 06.4b. Oznacza powtórzenia w źródle.
# - `lines.LINE_COLUMNS` i `duplicated(subset=...)`. Razem znajdują identyczne wiersze `raw`.
# - `online_retail.REPEAT_FLAG`. To nazwa kolumny z flagą powtórzenia.
# - `len`. Liczy wiersze.
#
# Liczby zamieniasz na zwykły `int` przez `int(...)`.
#
# **Sprawdzenie:** komórka wypisuje trzy liczby, a następna sprawdza asercjami, że kopie i powtórzenia razem dają wszystkie identyczne wiersze.

# %%
# >>> SOLUTION 06.4
all_duplicates = int(raw.duplicated(subset=online_retail.RAW_COLUMNS[:-1]).sum())
deduplicated = lines.drop_sheet_overlap(flagged)
copies = len(flagged) - len(deduplicated)
repeats = int(lines.flag_repeat_lines(deduplicated)[online_retail.REPEAT_FLAG].sum())
# --- STUB
#| all_duplicates = ...
#| deduplicated = ...
#| copies = ...
#| repeats = ...
# <<< SOLUTION
print(f"Identyczne wiersze (bez kolumny sheet): {all_duplicates:,}")
print(f"Kopie z nakładania się arkuszy: {copies:,}")
print(f"Linie oznaczone jako powtórzone (każde wystąpienie po pierwszym): {repeats:,}")

# %%
assert all(isinstance(n, int) for n in (all_duplicates, copies, repeats)), "Trzy liczby mają być typu int."
assert list(deduplicated.columns) == list(flagged.columns), "deduplicated ma mieć kolumny flagged, razem z flagami."
assert all_duplicates == copies + repeats, "Kopie i powtórzenia razem mają dać wszystkie identyczne wiersze."
print("Zgadza się.")

# %% [markdown]
# ## 06.5 Linie towarowe
#
# **Cel:** zostawić tylko linie, które mówią coś o popycie na towar: sprzedaż i zwroty. Każdą zamienić na trzy miary: sprzedane sztuki, zwrócone sztuki, przychód.
#
# **Gdzie:** `lines.py`, funkcja `product_lines`.
#
# **Wejście:** `flagged`: `pd.DataFrame` z `add_flags`, po `drop_sheet_overlap`. W notebooku `deduplicated` z 06.4c. Funkcja czyta kolumny `stock_code`, `invoice_date`, `quantity`, `price` i flagi `is_cancellation`, `is_non_product`, `is_bad_price`.
#
# **Wynik:** nowa `pd.DataFrame`, jeden wiersz na zachowaną linię, w pierwotnej kolejności, z indeksem 0..n-1, z kolumnami w tej kolejności:
#
# | Kolumna | Typ | Linia sprzedaży | Linia zwrotu |
# |---|---|---|---|
# | `stock_code` | `str` | kod towaru | kod towaru |
# | `date` | `datetime64` | dzień faktury o północy | dzień faktury o północy |
# | `units_sold` | liczba całkowita | ilość | 0 |
# | `units_returned` | liczba całkowita | 0 | minus ilość, czyli liczba dodatnia |
# | `revenue` | `float64` | ilość razy cena, w funtach | 0.0 |
#
# Zostaje linia, która jest towarem i jest jednym z dwóch rodzajów:
#
# - sprzedażą: nie jest anulowaniem i ma cenę powyżej 0,
# - zwrotem: jest anulowaniem.
#
# Reszta odpada: nietowary, wydania za darmo i odpisy magazynowe. Ujemna ilość poza fakturą C to odpis, a nie zwrot. Gdy odpadną wszystkie linie, wynik ma te kolumny i zero wierszy.
#
# `ValueError`, gdy:
#
# - zachowana linia sprzedaży ma ilość 0 albo mniej,
# - zachowany zwrot ma ilość 0 albo więcej.
#
# Komunikat podaje, ile jest takich linii.
#
# **Skorzystaj z:**
#
# - flag z 06.3. Z nich budujesz maskę linii, które zostają.
# - `.loc[maska]`, `&`, `|` i `~` z wykładu, sekcja ".loc, assign i łańcuchy". Razem wybierają linie, które zostają.
# - `.dt.normalize()` z wykładu, sekcja "Narzędzia, których użyjesz w labie". Daje dzień faktury o północy.
# - `Series.where` z tej samej sekcji. Wstawia ilość albo 0 zależnie od rodzaju linii.
# - `reset_index(drop=True)`. Nadaje nowy indeks.
#
# **Kroki:**
#
# 1. Zbuduj maskę linii, które zostają, z trzech flag.
# 2. Wybierz te linie.
# 3. Wśród nich policz sprzedaże z ilością nie większą od 0 i zwroty z ilością nie mniejszą od 0. Jeśli którakolwiek liczba jest większa od 0, zgłoś `ValueError`. Sprawdzasz dopiero po wyborze linii. W pliku jest anulowanie z dodatnią ilością na kodzie `M`, czyli na nietowarze, i to anulowanie ma odpaść.
# 4. Zbuduj pięć kolumn według tabeli. Każda miara to ilość albo ilość razy cena tam, gdzie linia jest danego rodzaju, a 0 gdzie indziej.
# 5. Zwróć tylko te pięć kolumn, w tej kolejności, z nowym indeksem.
#
# **Sprawdzenie:** `check("06.5")` albo `uv run course check 06.5`. Z 7 ręcznie napisanych linii mają zostać 3: sprzedaż, zwrot i sprzedaż bez klienta. Komórka pod sprawdzeniem porównuje zwroty z faktur C z wynikiem, który dałoby liczenie każdej ujemnej ilości jako zwrotu.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Najpierw maska linii, które zostają, potem `.loc[maska]`, potem `assign` nowych kolumn i wybór końcowych kolumn.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Zostaje linia, która jest towarem i albo jest anulowaniem, albo ma dobrą cenę. Sprzedaż to ilość na liniach nie-anulowanych, zwrot to minus ilość na anulowanych: `np.where` albo `Series.where`. Datę dnia z datą i godziną daje `.dt.normalize()`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# is_kept = ~flagged["is_non_product"] & (flagged["is_cancellation"] | ~flagged["is_bad_price"])
# kept = flagged.loc[is_kept]
# is_return = kept["is_cancellation"]
# result = kept.assign(
#     date=kept["invoice_date"].dt.normalize(),
#     units_sold=kept["quantity"].where(~is_return, 0),
#     ...
# )
# ```
#
# </details>

# %%
check("06.5")

# %%
products = lines.product_lines(deduplicated)
naive_returns = int(-deduplicated.loc[~deduplicated["is_non_product"] & (deduplicated["quantity"] < 0), "quantity"].sum())
print(f"Zwroty z faktur C: {products['units_returned'].sum():,} szt.")
print(f"Gdyby każda ujemna ilość była zwrotem: {naive_returns:,} szt.")

# %% [markdown]
# ## 06.6 Suma dzienna i kontrakt
#
# Otwórz `src/freshcast/warmup/daily.py`. Kontrakt tabeli dziennej, czyli umowa o jej kolumnach, typach i kluczu, jest opisany w docstringu na górze `online_retail.py` i w stałej `DAILY_COLUMNS`.
#
# ### 06.6a `daily_totals`
#
# **Cel:** zsumować linie do jednego wiersza na towar i dzień, tak żeby żadna sztuka nie zginęła po drodze.
#
# **Gdzie:** `daily.py`, funkcja `daily_totals`.
#
# **Wejście:** `lines`: `pd.DataFrame` z `product_lines`, z kolumnami `DAILY_COLUMNS`. Ten sam towar i dzień może mieć wiele linii. W notebooku `products` z 06.5.
#
# **Wynik:** nowa `pd.DataFrame` z kolumnami `DAILY_COLUMNS`. Tabela ma:
#
# - jeden wiersz na parę (`stock_code`, `date`), która występuje w `lines`,
# - wiersze posortowane po `stock_code`, potem po `date`, z indeksem 0..n-1,
# - miary, które są sumami i zachowują typ: sztuki całkowite, przychód zmiennoprzecinkowy.
#
# Linia z brakiem w `stock_code` albo `date` nie znika. Tworzy własny wiersz z brakiem w kluczu, żeby `check_daily` mogło ten wiersz odrzucić.
#
# **Skorzystaj z:**
#
# - `PRODUCT_KEY` z `online_retail.py`, czyli `["stock_code", "date"]`. Klucz grupowania.
# - `MEASURE_COLUMNS` z `online_retail.py`, czyli trzy miary. Kolumny do zsumowania.
# - `groupby` z `dropna=False` z wykładu, sekcja "Uzgodnienie po groupby". Grupuje linie i nie gubi wierszy z brakiem w kluczu.
# - `as_index=False`. Zostawia klucz jako zwykłe kolumny.
#
# `daily.py` nie ma importów stałych. Dopisz je na górze pliku. `groupby` domyślnie sortuje grupy po kluczu.
#
# ### 06.6b `check_daily`
#
# **Cel:** sprawdzić kontrakt tabeli dziennej w jednym miejscu, żeby każdy, kto ją zapisuje albo czyta, sprawdzał to samo.
#
# **Gdzie:** `daily.py`, funkcja `check_daily`.
#
# **Wejście:** `daily`: `pd.DataFrame`, kandydat na tabelę dzienną.
#
# **Wynik:** `None`, gdy kontrakt jest spełniony. Inaczej `ValueError` przy pierwszej złamanej regule z docstringu. Reguły idą w tej kolejności:
#
# 1. kolumny,
# 2. typy,
# 3. braki,
# 4. ujemne miary,
# 5. godzina w dacie,
# 6. powtórzony klucz,
# 7. sortowanie,
# 8. wiersz bez sprzedaży i bez zwrotu.
#
# Komunikat podaje liczbę złych wierszy, oprócz reguł 1, 2 i 7.
#
# **Skorzystaj z:**
#
# - `_wrong_dtypes(daily)`, gotowej funkcji pomocniczej nad `check_daily`. Zwraca listę kolumn o złym typie. Przyjmuje każdą szerokość liczby całkowitej i zmiennoprzecinkowej, na przykład `int32`. Tabela z `daily_totals` i tak ma `int64` i `float64`.
# - `DAILY_COLUMNS`, `MEASURE_COLUMNS` i `PRODUCT_KEY`. Razem opisują kontrakt tabeli dziennej.
# - wzoru reguł z `check_raw` z 06.2.
# - `isna().any(axis=1)` z wykładu i labu. Znajduje wiersze z brakiem.
# - `.dt.normalize()` z wykładu i labu. Ucina godzinę z daty.
# - `duplicated(subset=...)` z wykładu i labu. Znajduje powtórzony klucz.
# - `sort_values` z wykładu i labu. Daje kolejność, z którą porównujesz tabelę.
#
# **Kroki:**
#
# 1. Reguły 1 i 2: sprawdź listę kolumn, potem typy przez `_wrong_dtypes`.
# 2. Reguły 3-6: dla każdej reguły zbuduj maskę złych wierszy, policz jej sumę i użyj `raise`. Data "bez godziny" to data równa sobie po `.dt.normalize()`.
# 3. Reguła 7: weź kolumny klucza i porównaj je z tymi samymi kolumnami po `sort_values`. Kolumny różnią się, gdy choć jeden wiersz stoi nie na swoim miejscu. Ten błąd nie ma liczby w komunikacie.
# 4. Reguła 8: policz wiersze, w których suma sprzedanych i zwróconych sztuk wynosi 0 albo mniej.
#
# **Sprawdzenie 06.6a i 06.6b:** `check("06.6")` albo `uv run course check 06.6`. Sprawdzenie ma dwie części:
#
# - Z 6 linii mają powstać 4 wiersze.
# - Sprawdzenie psuje poprawną tabelę na jedenaście sposobów i oczekuje `ValueError` przy każdym.
#
# Komórki pod sprawdzeniem liczą tabelę na całym pliku i uzgadniają sumy przed `groupby` i po nim.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `groupby(klucz, as_index=False)[miary].sum()`. Przeczytaj w docstringu, co ma się stać z linią, której klucz jest pusty.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Domyślnie `groupby` po cichu pomija wiersze z brakującym kluczem. `dropna=False` je zostawia, żeby `check_daily` mógł je odrzucić. W `check_daily` każda reguła to maska i `ValueError` z liczbą, jak w `check_raw`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# return lines.groupby(PRODUCT_KEY, as_index=False, dropna=False)[MEASURE_COLUMNS].sum()
# ```
#
# </details>

# %%
check("06.6")

# %% [markdown]
# Po `groupby` zawsze uzgadniasz sumy: czy nic nie zginęło po drodze?

# %%
table = daily.daily_totals(products)
daily.check_daily(table)
print(f"{len(table):,} wierszy towar-dzień, {table['stock_code'].nunique():,} towarów")
print(table[online_retail.MEASURE_COLUMNS].sum().round(2).to_dict())
print(products[online_retail.MEASURE_COLUMNS].sum().round(2).to_dict())

# %%
difference = table[online_retail.MEASURE_COLUMNS].sum() - products[online_retail.MEASURE_COLUMNS].sum()
assert (difference.abs() < 0.01).all(), f"Sumy przed i po groupby się różnią: {difference.to_dict()}"
print("Zgadza się.")

# %% [markdown]
# ## 06.7 Całość w jednym łańcuchu
#
# ### 06.7a `build_daily`
#
# **Cel:** jedna funkcja, która z cache buduje gotową tabelę dzienną. Każdy następny moduł woła ją albo czyta jej wynik.
#
# **Gdzie:** `daily.py`, funkcja `build_daily`.
#
# **Wejście:** `cache`: `Path` pliku Parquet z `build_cache`. W notebooku `CACHE`.
#
# **Wynik:** `pd.DataFrame` spełniająca `check_daily`.
#
# Błędy:
#
# - `FileNotFoundError`, gdy cache nie istnieje,
# - `ValueError`, gdy surowe dane łamią regułę,
# - `ValueError`, gdy wynik łamie kontrakt.
#
# **Skorzystaj z:**
#
# - `load_raw` z 06.1c, z `online_retail.py`. Wczytuje cache.
# - `check_raw` z 06.2, z `online_retail.py`. Sprawdza reguły surowej tabeli.
# - `add_flags`, `drop_sheet_overlap` i `product_lines` z 06.3-06.5, z `lines.py`. Kolejne kroki łańcucha.
# - `daily_totals` z 06.6a, z tego pliku. Ostatni krok łańcucha.
# - `check_daily` z 06.6b, z tego pliku. Sprawdza kontrakt wyniku.
# - `pipe` z wykładu, sekcja ".loc, assign i łańcuchy". Łączy kroki w łańcuch.
#
# Importy z `online_retail.py` i `lines.py` dopisujesz na górze `daily.py`.
#
# **Kroki:**
#
# 1. Wczytaj cache i sprawdź reguły surowej tabeli.
# 2. Zbuduj łańcuch `pipe`: flagi, usunięcie kopii, linie towarowe, sumy dzienne. `flag_repeat_lines` nie wchodzi do łańcucha, bo powtórzenia zostają w danych.
# 3. Sprawdź kontrakt i zwróć tabelę.
#
# ### 06.7b `save_daily` i `load_daily`
#
# **Cel:** zapis i odczyt tabeli dziennej z kontrolą kontraktu po obu stronach, żeby zły plik nie trafił na dysk ani z dysku do modelu.
#
# **Gdzie:** `daily.py`, funkcje `save_daily` i `load_daily`.
#
# **Wejście:**
#
# - `save_daily(daily, path)`: tabela dzienna i `Path` pliku Parquet.
# - `load_daily(path)`: `Path` pliku zapisanego przez `save_daily`.
#
# W notebooku ścieżka to `paths.ONLINE_RETAIL_DAILY`, czyli `data/processed/online_retail_daily.parquet`.
#
# **Wynik:** `save_daily` robi kolejno trzy rzeczy:
#
# - sprawdza kontrakt. Zła tabela daje `ValueError` i żaden plik nie powstaje,
# - tworzy brakujące katalogi,
# - zapisuje tabelę bez indeksu i zwraca `path`.
#
# `load_daily` zwraca tabelę równą zapisanej. `load_daily` zgłasza:
#
# - `FileNotFoundError`, gdy pliku nie ma,
# - `ValueError`, gdy plik łamie kontrakt.
#
# **Skorzystaj z:**
#
# - `check_daily` z 06.6b. Sprawdza kontrakt przed zapisem i po odczycie.
# - `to_parquet(..., index=False)` z wykładu, sekcja "Zapis i odczyt Parquet". Zapisuje tabelę bez indeksu.
# - `pd.read_parquet` z tej samej sekcji. Czyta plik.
# - `mkdir` z tej samej sekcji. Tworzy brakujące katalogi.
# - `is_file` z tej samej sekcji. Sprawdza, czy plik istnieje.
# - `build_cache` i `load_raw` z 06.1b i 06.1c. To wzór zapisu i odczytu.
#
# **Sprawdzenie 06.7a i 06.7b:** `check("06.7")` albo `uv run course check 06.7`. Sprawdzenie kolejno:
#
# - buduje tabelę z próbki cache, czyli z 1263 wierszy linii faktur,
# - porównuje liczby wierszy, towarów i sztuk ze zmierzonymi,
# - zapisuje i czyta plik w katalogu tymczasowym.
#
# Komórka pod sprawdzeniem buduje tabelę z całego pliku i zapisuje ją. Gdy odczyt daje tę samą tabelę, komórka wypisuje `True` ze ścieżką.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `df.pipe(f)` to `f(df)`, ale w łańcuchu czyta się od góry do dołu. `check_raw` niczego nie zwraca, więc stoi przed łańcuchem, nie w nim.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `save_daily` najpierw sprawdza, potem zapisuje, żeby na dysku nie został zły plik. `load_daily` sprawdza po odczycie: plik mógł zapisać ktoś z inną wersją kodu.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# raw = load_raw(cache)
# check_raw(raw)
# result = raw.pipe(add_flags).pipe(drop_sheet_overlap).pipe(product_lines).pipe(daily_totals)
# check_daily(result)
# return result
# ```
#
# </details>

# %%
check("06.7")

# %%
built = daily.build_daily(CACHE)
daily.save_daily(built, paths.ONLINE_RETAIL_DAILY)
print(daily.load_daily(paths.ONLINE_RETAIL_DAILY).equals(built), paths.ONLINE_RETAIL_DAILY.relative_to(paths.ROOT))

# %% [markdown]
# ## 06.8 Eksploracja
#
# Bez sprawdzeń. Przy pytaniach 1-4 policz coś w komórce pod pytaniem. Potem odpowiedz dwoma albo trzema zdaniami, z liczbami, w miejscu *Twoja odpowiedź*. Korzystasz ze zmiennych z wcześniejszych zadań: `deduplicated` (06.4c), `built` (06.7).
#
# **1. Czy powtórzona linia to błąd?** Porównaj powtórzone linie z resztą: jaki mają udział w sztukach i przychodzie? Czy są w obu kopiach nakładających się faktur?
#
# - **Gdzie:** komórka pod pytaniem. Zmienne `sale_lines`, `units` i `revenue` utwórz pod tymi nazwami. Użyjesz ich w pytaniu 2.
# - **Wynik:** wydruk dwóch udziałów, każdy jako ułamek 0-1 wypisany w procentach. Liczysz udział linii z `is_repeat_line` (tylko wystąpienia po pierwszym) w sztukach i w przychodzie wszystkich linii sprzedaży `deduplicated`. Po drodze tworzysz trzy zmienne:
#
#   - `sale_lines`: `pd.DataFrame`, linie sprzedaży towarów (nie anulowanie, towar, cena powyżej 0) z kolumną `is_repeat_line`,
#   - `units`: `pd.Series`, `quantity` tych linii,
#   - `revenue`: `pd.Series`, ilość razy cena.
#
# - **Skorzystaj z:**
#
#   - `lines.flag_repeat_lines(deduplicated)`. Dodaje kolumnę `is_repeat_line`.
#   - flag z 06.3. Wybierają linie sprzedaży towarów.
#   - `online_retail.REPEAT_FLAG`. To nazwa kolumny z flagą powtórzenia.
#   - masek w `.loc`.
#
#   Udział to suma po maskowanych wierszach przez sumę wszystkich. Do drugiej części pytania wystarczy docstring `flag_repeat_lines`.

# %%
# >>> SOLUTION 06.8
repeated = lines.flag_repeat_lines(deduplicated)
sale_lines = repeated.loc[~repeated["is_cancellation"] & ~repeated["is_non_product"] & ~repeated["is_bad_price"]]
units = sale_lines["quantity"]
revenue = units * sale_lines["price"]
is_repeat = sale_lines[online_retail.REPEAT_FLAG]
print(f"Udział powtórzeń: {units[is_repeat].sum() / units.sum():.2%} sztuk, {revenue[is_repeat].sum() / revenue.sum():.2%} przychodu")
# --- STUB
#| ...
# <<< SOLUTION

# %% [markdown]
# *Twoja odpowiedź:*
#
# **2. Kim są klienci bez identyfikatora?** Porównaj linie sprzedaży z klientem i bez: udział w liniach, sztukach i przychodzie, mediana ilości i ceny, kraj.
#
# - **Gdzie:** zmienna `summary` w komórce pod pytaniem. Linię `summary.round(3)` pod nią zostawiasz.
# - **Wynik:** `pd.DataFrame` z dwoma wierszami, "z klientem" i "bez klienta". Kolumny:
#
#   - `linie`, `sztuki`, `przychód`: udziały 0-1, w każdej kolumnie sumują się do 1,
#   - `mediana ilości`,
#   - `mediana ceny`, w funtach,
#   - `UK`: udział linii z krajem `"United Kingdom"`, 0-1.
#
# - **Skorzystaj z:**
#
#   - `sale_lines`, `units` i `revenue` z pytania 1.
#   - `is_missing_customer`, flagi z 06.3. Dzieli linie na dwie grupy.
#   - `groupby(maska)`. Grupuje serię według maski. Grupy to `False` i `True`.
#   - `pd.DataFrame({nazwa: seria, ...})`. Składa serie o tym samym indeksie w kolumny.
#   - `rename(index={False: "z klientem", True: "bez klienta"})`. Nazywa wiersze.

# %%
# >>> SOLUTION 06.8
missing = sale_lines["is_missing_customer"]
summary = pd.DataFrame(
    {
        "linie": sale_lines.groupby(missing).size() / len(sale_lines),
        "sztuki": units.groupby(missing).sum() / units.sum(),
        "przychód": revenue.groupby(missing).sum() / revenue.sum(),
        "mediana ilości": units.groupby(missing).median(),
        "mediana ceny": sale_lines["price"].groupby(missing).median(),
        "UK": (sale_lines["country"] == "United Kingdom").groupby(missing).mean(),
    }
).rename(index={False: "z klientem", True: "bez klienta"})
# --- STUB
#| summary = ...
# <<< SOLUTION
summary.round(3)

# %% [markdown]
# *Twoja odpowiedź:*
#
# **3. Co znaczy brakujący dzień?** Ile z 739 dni kalendarzowych ma jakąkolwiek linię? Które dni tygodnia i które okresy roku są puste? Czy brak wiersza w tabeli dziennej to zerowy popyt?
#
# - **Gdzie:** komórka pod pytaniem.
# - **Wynik:** wydruk trzech rzeczy:
#
#   - liczba dni, które mają choć jeden wiersz w `built` (sprzedaż albo zwrot towaru), na tle wszystkich dni kalendarza od pierwszej do ostatniej daty,
#   - liczba pustych dni według dnia tygodnia,
#   - lista pustych dni w grudniu i styczniu, bez sobót. Soboty widać już w liczbie według dnia tygodnia. Z listy wystarczy pierwszych 20.
#
# - **Skorzystaj z:**
#
#   - `date`, kolumny `built` z 06.7.
#   - `pd.date_range(start, end, freq="D")`. Daje wszystkie dni kalendarza między dwiema datami.
#   - `pd.DatetimeIndex(...)`. Robi indeks dat z kolumny unikalnych dat.
#   - `a.difference(b)`. Zwraca daty z `a`, których nie ma w `b`.
#   - `.day_name()`. Daje nazwę dnia tygodnia.
#   - `.value_counts()`. Liczy wystąpienia.

# %%
# >>> SOLUTION 06.8
trading_days = pd.DatetimeIndex(built["date"].unique())
calendar = pd.date_range(built["date"].min(), built["date"].max(), freq="D")
empty = calendar.difference(trading_days)
print(f"Dni z liniami: {len(trading_days)} z {len(calendar)}")
print("Puste dni według dnia tygodnia:", empty.day_name().value_counts().to_dict())
print("Puste dni w grudniu i styczniu:", [str(d.date()) for d in empty if d.month in (12, 1) and d.day_name() != "Saturday"][:20])
# --- STUB
#| ...
# <<< SOLUTION

# %% [markdown]
# *Twoja odpowiedź:*
#
# **4. Co robią z danymi dwie największe sprzedaże?** Znajdź dwie linie z największą ilością i sprawdź, co stało się z nimi chwilę później.
#
# - **Gdzie:** komórka pod pytaniem.
# - **Wynik:** wydruk dla każdej z dwóch linii: kod towaru, ilość, data i godzina, a obok pierwsza późniejsza linia anulowania tego samego towaru (numer faktury, ilość, czas).
# - **Skorzystaj z:**
#
#   - `deduplicated` z 06.4c.
#   - `nlargest(2, "quantity")`. Zwraca dwa wiersze z największą ilością.
#   - `itertuples()`. Przechodzi po wierszach jak po krotkach z polami o nazwach kolumn.
#   - maski. Wybiera anulowania tego samego towaru: ten sam `stock_code`, `is_cancellation`, `invoice_date` nie wcześniejsza niż sprzedaż.
#
#   `deduplicated` ma kolejność pliku, a plik idzie chronologicznie. Pierwszy wiersz spełniający maskę to więc najwcześniejsze takie anulowanie. Przy równym czasie bierzesz anulowanie, które stoi wyżej.

# %%
# >>> SOLUTION 06.8
biggest = deduplicated.nlargest(2, "quantity")[["invoice", "stock_code", "quantity", "invoice_date"]]
for row in biggest.itertuples():
    later = deduplicated.loc[(deduplicated["stock_code"] == row.stock_code) & deduplicated["is_cancellation"] & (deduplicated["invoice_date"] >= row.invoice_date), ["invoice", "quantity", "invoice_date"]]
    print(f"{row.stock_code}: {row.quantity:,} szt. o {row.invoice_date}; potem: {later.head(1).to_dict('records')}")
# --- STUB
#| ...
# <<< SOLUTION

# %% [markdown]
# *Twoja odpowiedź:*
#
# **5. Czego nie wyczyściłeś i dlaczego?** Wymień co najmniej dwie rzeczy, które zostały w danych, i powiedz, co musiałoby się zmienić, żeby trzeba było się nimi zająć. Bez komórki z kodem. Oprzyj się na docstringach i liczbach z pytań 1-4.
#
# *Twoja odpowiedź:*
