# %% [markdown]
# # Lab 06: czyszczenie sprzedaży sklepu internetowego
#
# UCI Online Retail II to dwa lata faktur brytyjskiego sklepu z upominkami: milion linii, każda z towarem, ilością, ceną i klientem. Plik jest prawdziwy, więc brudny w prawdziwy sposób: anulowania, odpisy magazynowe, próbki za darmo, opłaty pocztowe udające towary, klienci bez identyfikatora, arkusze, które na siebie zachodzą.
#
# Z tego pliku zbudujesz tabelę dziennej sprzedaży towarów. W module 17 wróci ona jako wejście cudzego kodu, który będziesz naprawiać.
#
# Każda decyzja w tym labie jest twierdzeniem o danych. Zanim coś usuniesz albo wypełnisz, policz, czego to dotyczy, i zapisz liczbę w docstringu. Docstringi w pakiecie już mają te liczby: nie wierz im, sprawdź je na pliku.
#
# **Czas:** około 6 godzin.
#
# | Zadanie | Co piszesz w `src/freshcast/warmup/` | Czas |
# |---|---|---|
# | 06.1 | `read_sheets`, `build_cache`, `load_raw` | 60 min |
# | 06.2 | `check_raw` | 45 min |
# | 06.3 | `add_flags` | 40 min |
# | 06.4 | `drop_sheet_overlap`, `flag_repeat_lines` | 60 min |
# | 06.5 | `product_lines` | 45 min |
# | 06.6 | `daily_totals`, `check_daily` | 40 min |
# | 06.7 | `build_daily`, `save_daily`, `load_daily` | 30 min |
# | 06.8 | Eksploracja: pięć pytań | 40 min |

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
# ## Plik tak, jak przychodzi
#
# Najpierw wczytaj skoroszyt bez żadnych ustawień, tak jak robi to większość tutoriali. To potrwa około pół minuty: zanotuj ile.

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
# Otwórz `src/freshcast/warmup/online_retail.py`. Stałe na górze pliku są gotowe: nazwy kolumn, wzorce, kontrakt tabeli wynikowej. Napisz:
#
# - `read_sheets(path)`: oba arkusze w jednej tabeli, z typami podanymi w docstringu, nazwami kolumn z `SHEET_HEADERS`, kolumną `sheet` i uporządkowanym kodem towaru,
# - `build_cache(xlsx, cache)`: czyta skoroszyt raz i zapisuje Parquet,
# - `load_raw(cache)`: czyta cache i sprawdza, że ma dokładnie `RAW_COLUMNS`.
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
# </details>

# %%
check("06.1")

# %% [markdown]
# Zbuduj cache raz i porównaj czasy.

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
# Każdy dalszy krok zakłada coś o danych: że faktura ma sześć cyfr, że anulowanie ma ujemną ilość, że jedna faktura ma jednego klienta. Założenie, którego nikt nie sprawdza, pęknie po cichu przy następnej wersji pliku.
#
# Napisz `check_raw(raw)`, który sprawdza reguły z docstringu, po kolei, i przy pierwszej złamanej zgłasza `ValueError` z liczbą wierszy, które ją łamią, i przykładem.
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
# Napisz `add_flags(raw)` w `src/freshcast/warmup/lines.py`: cztery kolumny logiczne opisujące każdą linię (anulowanie, nie-towar, brak klienta, zła cena). Nic nie usuwasz. Co zrobić z oflagowanymi liniami, zdecydujesz w 06.5, a do tego czasu możesz je policzyć i obejrzeć.
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
# `drop_duplicates()` na całej tabeli usuwa 34 335 wierszy. To dwa różne zjawiska:
#
# - **kopie z eksportu**: faktury z 1-9 grudnia 2010 są w obu arkuszach. Kopię usuwasz bez wahania,
# - **powtórzone linie w źródle**: ta sama linia dwa razy na jednej fakturze. Nie wiesz, czy to błąd, czy dwa zamówienia tego samego. Tych nie usuwasz, tylko je oznaczasz.
#
# Napisz `drop_sheet_overlap` (usuwa drugą kopię faktur, które są w obu arkuszach) i `flag_repeat_lines` (dodaje kolumnę `is_repeat_line`, nic nie usuwa).
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
# Z faktur w obu arkuszach zostaw linie z jednego, na przykład z pierwszego. Zanim uznasz je za kopie, sprawdź w notebooku, że linie w obu arkuszach są identyczne. Do `flag_repeat_lines` służy `duplicated(subset=..., keep=False)`, bez kolumny `sheet` w `subset`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# sheets_per_invoice = raw.groupby("invoice")["sheet"].nunique()
# overlap = sheets_per_invoice.index[sheets_per_invoice > 1]
# second = raw["invoice"].isin(overlap) & (raw["sheet"] != raw["sheet"].iloc[0])
# return raw.loc[~second].reset_index(drop=True)
# ```
#
# </details>

# %%
check("06.4")

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
print(f"Linie oznaczone jako powtórzone (obie z pary): {repeats:,}")

# %% [markdown]
# ## 06.5 Linie towarowe
#
# Napisz `product_lines(flagged)`: zostają linie sprzedaży towarów z dodatnią ceną i linie zwrotów (anulowania towarów). Wynik ma kolumny `stock_code`, `date`, `units_sold`, `units_returned`, `revenue`, opisane w docstringu.
#
# Zwróć uwagę, co **nie** jest zwrotem: ujemna ilość poza fakturą C to odpis magazynowy.
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
# Napisz `daily_totals(lines)` w `src/freshcast/warmup/daily.py`: jeden wiersz na towar i dzień, z sumami trzech miar. Potem `check_daily(daily)`: sprawdza kontrakt z docstringu modułu `online_retail` (kolumny, typy, klucz bez braków i powtórzeń, kolejność, miary nieujemne, w każdym wierszu sprzedaż albo zwrot).
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

# %% [markdown]
# ## 06.7 Całość w jednym łańcuchu
#
# Napisz `build_daily(cache)`: wczytanie, reguły, flagi, usunięcie kopii, linie towarowe, sumy, kontrakt. Jeden czytelny łańcuch z `pipe`. Potem `save_daily` i `load_daily`: zapis i odczyt z kontrolą kontraktu po obu stronach.
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
# Bez sprawdzeń. Przy każdym pytaniu policz coś w komórce pod spodem i odpowiedz dwoma, trzema zdaniami, z liczbami.
#
# **1. Czy powtórzona linia to błąd?** Porównaj powtórzone linie z resztą: jaki mają udział w sztukach i przychodzie? Czy są w obu kopiach nakładających się faktur?

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
# **5. Czego nie wyczyściłeś i dlaczego?** Wymień co najmniej dwie rzeczy, które zostały w danych, i powiedz, co musiałoby się zmienić, żeby trzeba było się nimi zająć.
#
# *Twoja odpowiedź:*
