# %% [markdown]
# # Lab 01: popyt na części samochodowe w czystym Pythonie
#
# Zbiór Monash Car Parts to miesięczna sprzedaż 2 674 części samochodowych od stycznia 1998 do marca 2002. Większość części sprzedaje się rzadko: w trzech na cztery miesiące sprzedaż wynosi zero. Taki popyt nazywa się **przerywanym** (intermittent) i jest jednym z najtrudniejszych do prognozowania.
#
# W tym labie nie używasz pandas ani NumPy. Czytasz plik linia po linii, rozbierasz tekst na liczby i liczysz statystyki listami, słownikami i comprehensions. To, co tu napiszesz ręcznie, w module 06 zrobi za Ciebie jedna linia pandas. Warto raz zobaczyć, co ta linia robi.
#
# **Czas:** około 6 godzin.
#
# ## Jak pracujesz
#
# Każde zadanie to funkcja w komórce tego notebooka. Nazwa funkcji, jej argumenty i docstring (opis po angielsku w potrójnym cudzysłowie pod `def`) są gotowe. Docstring to dokładna umowa: mówi, co funkcja dostaje, co zwraca i kiedy zgłasza błąd. Opis po polsku nad komórką mówi to samo prostszymi słowami. Ty piszesz ciało funkcji w miejscu `raise NotImplementedError`.
#
# Pod funkcją jest komórka `check("01.x", nazwa_funkcji)`. Sprawdza Twoją funkcję na małych, wymyślonych danych. Zadanie jest zrobione, gdy wypisze ✅. Przy ❌ komunikat mówi, dla jakich danych wynik się nie zgadza.
#
# Funkcje budują jedna na drugiej: 01.2 używa 01.1, 01.3 używa 01.2, a 01.5 i 01.6 dostają wynik 01.4. Rób zadania po kolei i uruchamiaj komórki od góry.
#
# Pod każdym zadaniem są trzy podpowiedzi. Otwieraj je po kolei. Jeśli pracujesz z tutorem, wpisz `/hint 01.3`.
#
# | Zadanie | Gdzie piszesz | Czas |
# |---|---|---|
# | 01.1 | funkcja `parse_value` | 30 min |
# | 01.2 | funkcja `parse_series_line` | 45 min |
# | 01.3a | funkcja `read_series` | 45 min |
# | 01.3b | zmienne `series` i `lengths` | 15 min |
# | 01.4a | funkcja `demand_stats` | 40 min |
# | 01.4b | zmienne `stats`, `missing_share`, `zero_share` | 20 min |
# | 01.5 | funkcja `top_series` | 45 min |
# | 01.6 | funkcja `save_summary` | 30 min |
# | 01.7 | Eksploracja: zmienne `regular`, `intermittent` i dwie odpowiedzi tekstem | 45 min |

# %% [markdown]
# Pierwsza komórka przygotowuje to, czego użyjesz w całym labie:
#
# - `PATH`: ścieżka do pliku z danymi (obiekt `Path` z modułu `pathlib`, wykład 01, sekcja "Pliki i `with`"). Plik pobrało polecenie `uv run course data`.
# - `paths`: miejsca na dysku, których używa kurs. W 01.6 zapiszesz wynik do `paths.PROCESSED_DIR`.
# - `check`: funkcja, która uruchamia sprawdzenie zadania.
# - `json`: moduł do zapisu danych w formacie JSON, potrzebny w 01.6.

# %%
import json
from pathlib import Path

from coursekit import paths
from coursekit.nb import check

PATH = paths.CAR_PARTS
print(PATH.name, f"{PATH.stat().st_size / 1000:.0f} kB")

# %% [markdown]
# ## Jak wygląda plik
#
# Zanim cokolwiek napiszesz, obejrzyj plik. Wypisz pierwsze 12 linii. Plik otwierasz przez `with`, więc zamknie się sam.

# %%
with PATH.open(encoding="utf-8") as handle:
    for number, line in enumerate(handle):
        if number == 12:
            break
        print(line.rstrip()[:90])

# %% [markdown]
# Format `.tsf` ma trzy części:
#
# - linie zaczynające się od `#`: komentarze,
# - linie zaczynające się od `@`: nagłówek, opis kolumn,
# - po linii `@data`: jedna seria na linię, w postaci `nazwa:data startu:wartości oddzielone przecinkami`.
#
# Jedna seria to sprzedaż jednej części, miesiąc po miesiącu. Pierwsza wartość to miesiąc z daty startu, każda następna to kolejny miesiąc. Znak zapytania oznacza miesiąc, dla którego nie ma pomiaru. To coś innego niż zero: zero znaczy "pomiar był i nic się nie sprzedało".

# %% [markdown]
# ## 01.1 Jedna wartość
#
# **Cel:** Każda wartość w pliku to tekst: `"0"`, `"2"` albo `"?"`. Żeby liczyć sumy i średnie, potrzebujesz liczb, a brak pomiaru musi zostać brakiem, a nie zerem. Ta funkcja zamienia jeden kawałek tekstu na liczbę albo na `None`.
#
# **Gdzie:** Funkcja `parse_value` w komórce poniżej. Piszesz jej ciało w miejscu `raise NotImplementedError`.
#
# **Wejście:** `text`: napis (`str`), jedna wartość wycięta z linii danych, na przykład `"3"`, `" 12 "`, `"2.5"` albo `"?"`. Dookoła mogą być spacje.
#
# **Wynik:** Liczba zmiennoprzecinkowa (`float`), także dla tekstu z liczbą całkowitą: `"3"` daje `3.0`. Dla `"?"` wynik to `None`.
#
# Funkcja zgłasza `ValueError` z komunikatem, który pokazuje ten tekst, gdy:
#
# - tekst nie jest liczbą, na przykład `"abc"`,
# - tekst to liczba ujemna, na przykład `"-1"`. Popyt nie bywa ujemny.
#
# **Skorzystaj z:**
#
# - `MISSING` z tej samej komórki, nad funkcją. To znak braku, `"?"`.
# - wykładu 01, sekcja "Wyjątki". Pokazuje prawie tę samą funkcję, ale bez usuwania spacji i bez sprawdzenia znaku.
#
# **Kroki:**
#
# 1. Usuń spacje z obu końców tekstu. Robi to metoda napisu `strip()`.
# 2. Jeśli tekst to `MISSING`, zwróć `None`.
# 3. Zamień tekst na liczbę funkcją `float()`. Gdy tekst nie jest liczbą, `float()` sam zgłasza `ValueError`. Złap go i zgłoś własny `ValueError`, którego komunikat pokazuje tekst.
# 4. Jeśli liczba jest mniejsza od zera, zgłoś `ValueError`. W przeciwnym razie ją zwróć.
#
# **Sprawdzenie:** Komórka `check("01.1", parse_value)` pod funkcją wypisuje ✅. Sprawdza `"0"`, `"3"`, `" 12 "`, `"?"`, `"2.5"`, `"abc"` i `"-1"`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `float("3")` zamienia tekst na liczbę, a dla tekstu, który liczbą nie jest, rzuca `ValueError`. Spacje usuwa `text.strip()`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Najpierw przypadek szczególny: `"?"`. Potem `try` z `float(...)` i `except ValueError`, w którym rzucasz własny `ValueError` z lepszym komunikatem. Na końcu sprawdzenie znaku.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# text = text.strip()
# if text == MISSING:
#     return None
# try:
#     value = float(text)
# except ValueError as error:
#     raise ValueError(f"Not a number: {text!r}") from error
# # teraz: ujemna wartość to też ValueError
# ```
#
# </details>

# %%
MISSING = "?"


def parse_value(text):
    """Turn one value of a .tsf series into a float, or None for a missing month.

    Args:
        text: One value cut out of a data line, a string such as "3", " 12 ",
            "2.5" or "?". Spaces around it are allowed.

    Returns:
        The demand of one month as a float ("3" gives 3.0), or None when the
        text is "?" (MISSING), which marks a month without a measurement.

    Raises:
        ValueError: The text is not a number, or the number is negative.
            The message shows the text.
    """
    # >>> SOLUTION 01.1
    text = text.strip()
    if text == MISSING:
        return None
    try:
        value = float(text)
    except ValueError as error:
        raise ValueError(f"Not a number: {text!r}") from error
    if value < 0:
        raise ValueError(f"Demand cannot be negative: {text!r}")
    return value
    # <<< SOLUTION


check("01.1", parse_value)

# %% [markdown]
# ## 01.2 Jedna linia serii
#
# **Cel:** Jedna linia pliku po `@data` to cała historia jednej części. Ta funkcja rozbiera taką linię na trzy pola, z którymi da się dalej pracować: nazwę serii, datę startu i listę miesięcznych wartości.
#
# **Gdzie:** Funkcja `parse_series_line` w komórce poniżej.
#
# **Wejście:** `line`: napis (`str`), jedna linia danych w postaci `nazwa:data startu:wartości`, na przykład
#
# ```
# T7:1998-01-01 00-00-00:0,2,?,1
# ```
#
# Na końcu linii może stać znak nowej linii `\n`, tak jak przy czytaniu pliku.
#
# **Wynik:** Krotka (`tuple`) trzech pól, w tej kolejności:
#
# 1. nazwa serii, napis: `"T7"`,
# 2. data startu, napis z samą datą, bez godziny: `"1998-01-01"`,
# 3. lista wartości (`list`), każda przepuszczona przez `parse_value`: `[0.0, 2.0, None, 1.0]`.
#
# Dla linii z przykładu wynik to `("T7", "1998-01-01", [0.0, 2.0, None, 1.0])`. Linia, która nie ma dwóch dwukropków, to `ValueError`.
#
# Dlaczego krotka, a nie lista? Te trzy pola mają stałe, różne znaczenia. Krotka mówi czytelnikowi: "to jest jeden rekord, nie ciąg podobnych rzeczy".
#
# **Skorzystaj z:**
#
# - `parse_value` z 01.1, dla każdej wartości z listy. Funkcja jest w komórce wyżej, więc wołasz ją bez importu.
#
# Nie pisz drugiego parsera liczb. Błędów z `parse_value`, na przykład o ujemnej wartości, nie łapiesz. Przepuszczasz je dalej.
#
# **Kroki:**
#
# 1. Usuń białe znaki z końców linii metodą `strip()`. Potem podziel linię metodą `split(":", 2)`. Liczba 2 znaczy "podziel najwyżej dwa razy", więc wyjdą najwyżej trzy części.
# 2. Jeśli części nie są dokładnie trzy, zgłoś `ValueError`.
# 3. Z drugiej części weź tekst przed spacją. To data bez godziny.
# 4. Trzecią część podziel po przecinku. Każdy kawałek zamień przez `parse_value`. Pasuje tu list comprehension.
# 5. Zwróć krotkę trzech pól.
#
# **Sprawdzenie:** `check("01.2", parse_series_line)` wypisuje ✅. Sprawdza linię z przykładu, zakończoną `\n`, i linię `"T7 0,1,2"` bez dwukropków.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `text.split(":", 2)` dzieli tekst najwyżej dwa razy, więc trzecia część zostaje w całości, nawet jeśli ma w sobie dwukropki. Data i godzina oddzielone są spacją.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Po podziale sprawdź, czy są trzy części. Datę bierzesz z drugiej części przed spacją. Wartości to trzecia część podzielona przecinkiem, a każdy kawałek przechodzi przez `parse_value`. List comprehension zrobi to w jednej linii.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# parts = line.strip().split(":", 2)
# if len(parts) != 3:
#     raise ValueError(...)
# name, start, values = parts
# return name, start.split(" ")[0], [...]
# ```
#
# </details>

# %%
def parse_series_line(line):
    """Split one data line into (name, start date, list of values).

    Args:
        line: One line after "@data", a string such as
            "T7:1998-01-01 00-00-00:0,2,?,1". A trailing newline is allowed.

    Returns:
        A tuple of three fields: the series name ("T7"), the start date
        without the time ("1998-01-01") and the list of monthly values, each
        turned by parse_value into a float or None ([0.0, 2.0, None, 1.0]).

    Raises:
        ValueError: The line does not have the form name:start:values, or a
            value is not a valid demand (see parse_value).
    """
    # >>> SOLUTION 01.2
    parts = line.strip().split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"Expected name:start:values, got {line.strip()[:40]!r}")
    name, start, values = parts
    return name, start.split(" ")[0], [parse_value(text) for text in values.split(",")]
    # <<< SOLUTION


check("01.2", parse_series_line)

# %% [markdown]
# ## 01.3 Cały plik, seria po serii
#
# Zadanie ma dwa kroki: 01.3a to funkcja `read_series`, 01.3b to wczytanie wszystkich serii do słownika.
#
# ### 01.3a Generator `read_series`
#
# **Cel:** Masz funkcję na jedną linię. Teraz potrzebujesz wszystkich serii z pliku, z pominięciem komentarzy i nagłówka. Zamiast budować od razu wielką listę, piszesz generator. Generator oddaje serie po jednej, gdy pętla o nie prosi. Opisuje go wykład 01, sekcja "Iteracja i generatory".
#
# Generator nie trzyma w pamięci całego pliku. Ten plik jest mały, ale ten sam wzorzec przeczyta plik z milionem serii.
#
# **Gdzie:** Funkcja `read_series` w komórce poniżej.
#
# **Wejście:** `path`: położenie pliku `.tsf`, obiekt `Path` (jak `PATH`) albo napis ze ścieżką.
#
# **Wynik:** Generator, który oddaje (`yield`) serie z pliku:
#
# - każdy element to krotka z 01.2, `(nazwa, data startu, lista wartości)`,
# - serie wychodzą w kolejności z pliku,
# - komentarze, czyli linie od `#`, są pominięte,
# - nagłówek, czyli linie od `@` przed `@data` razem z samą linią `@data`, jest pominięty,
# - puste linie są pominięte.
#
# **Skorzystaj z:**
#
# - `parse_series_line` z 01.2. Wołasz ją dla każdej linii danych.
# - `with` i `encoding="utf-8"` z komórki "Jak wygląda plik" powyżej. Tak otwierasz plik.
#
# **Kroki:**
#
# 1. Utwórz zmienną, która pamięta, czy jesteś już za linią `@data`. Na początku `False`.
# 2. Otwórz plik przez `with` i przejdź pętlą `for` po jego liniach.
# 3. Każdą linię oczyść `strip()`. Pustą linię i linię zaczynającą się od `#` pomiń (`continue`).
# 4. Jeśli jesteś już za `@data`, oddaj `yield` wynik `parse_series_line`. Jeśli nie, a linia to `@data`, przestaw zmienną z kroku 1 na `True`.
#
# **Sprawdzenie:** `check("01.3", read_series)` wypisuje ✅. Sprawdzenie 01.3 dotyczy kroku 01.3a. Sprawdza, że funkcja jest generatorem i że z małego pliku z trzema seriami (A, B, C), komentarzami, nagłówkiem i pustą linią oddaje tylko te trzy serie.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `with path.open(encoding="utf-8") as handle:` i pętla `for line in handle:`. W środku pętli `yield`, zamiast dopisywania do listy.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Potrzebujesz zmiennej, która pamięta, czy jesteś już za `@data`. Na początku `False`, a gdy trafisz na linię `@data`, ustawiasz `True`. Pusta linia i linia zaczynająca się od `#` to `continue`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# in_data = False
# with Path(path).open(encoding="utf-8") as handle:
#     for line in handle:
#         line = line.strip()
#         if not line or line.startswith("#"):
#             continue
#         if in_data:
#             yield ...
#         elif line == "@data":
#             in_data = True
# ```
#
# </details>

# %%
def read_series(path):
    """Yield (name, start, values) for every series of a .tsf file.

    Args:
        path: Location of the .tsf file, a pathlib.Path or a string.

    Yields:
        One tuple per data line, in file order, as returned by
        parse_series_line: (name, start date, list of float or None).
        Comments (#), header lines (@) up to and including "@data", and
        blank lines are skipped.

    Raises:
        ValueError: A data line cannot be parsed (see parse_series_line).
    """
    # >>> SOLUTION 01.3
    in_data = False
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if in_data:
                yield parse_series_line(line)
            elif line.lower() == "@data":
                in_data = True
    # <<< SOLUTION


check("01.3", read_series)

# %% [markdown]
# ### 01.3b Wszystkie serie w słowniku
#
# **Gdzie:** Zmienne `series` i `lengths` w komórce poniżej, w miejscu `...`.
#
# **Wynik:**
#
# - `series`: słownik (`dict`). Klucz to nazwa serii (napis, np. `"T1"`), wartość to lista miesięcznych wartości tej serii (liczby i `None`). Datę startu pomijasz.
# - `lengths`: zbiór (`set`) długości tych list, czyli liczb całkowitych. Zbiór zostawia każdą długość raz, więc od razu widać, czy wszystkie serie są równie długie.
#
# **Skorzystaj z:**
#
# - `read_series(PATH)` z 01.3a. Oddaje wszystkie serie z pliku.
# - dict comprehension, który z każdej krotki bierze nazwę i wartości. Buduje `series`.
# - set comprehension po `series.values()`. Buduje `lengths`.
#
# Generator przejdziesz tylko raz. Dlatego zapisujesz serie do słownika. Ze słownika skorzystasz w 01.4b i dalej.
#
# **Sprawdzenie:** Wypisana liczba serii zgadza się z liczbą części ze wstępu labu. Komórka z `assert` pod spodem nie zgłasza błędu.

# %%
# >>> SOLUTION 01.3
series = {name: values for name, _start, values in read_series(PATH)}
lengths = {len(values) for values in series.values()}
# --- STUB
#| series = ...
#| lengths = ...
# <<< SOLUTION
print(f"Serie: {len(series)}, długości: {lengths}")

# %%
assert isinstance(series, dict), "series ma być słownikiem: nazwa serii -> lista wartości."
assert isinstance(lengths, set), "lengths ma być zbiorem długości list."
assert len(series) == 2674, "W pliku jest 2 674 serii. Czy pomijasz nagłówek i puste linie?"

# %% [markdown]
# ## 01.4 Statystyki serii
#
# Zadanie ma dwa kroki: 01.4a to funkcja `demand_stats` dla jednej serii, 01.4b to statystyki wszystkich serii i dwa udziały dla całego zbioru.
#
# ### 01.4a Funkcja `demand_stats`
#
# **Cel:** Żeby powiedzieć, jak sprzedaje się jedna część, liczysz dla jej serii kilka liczb: ile miesięcy znasz, ile brakuje, ile sprzedano razem i jak rzadko ktoś kupuje. Te liczby posłużą w 01.5 do wyboru serii, a w 01.6 trafią do pliku.
#
# **Gdzie:** Funkcja `demand_stats` w komórce poniżej.
#
# **Wejście:** `values`: lista wartości jednej serii, miesiąc po miesiącu, jak trzecie pole z 01.2. Każdy element to liczba (`float`) albo `None` dla braku pomiaru. Listy nie zmieniasz.
#
# **Wynik:** Słownik (`dict`) z pięcioma kluczami:
#
# | Klucz | Znaczenie | Typ |
# |---|---|---|
# | `months` | liczba znanych miesięcy (bez `None`) | liczba całkowita (`int`) |
# | `missing` | liczba miesięcy z brakiem | liczba całkowita (`int`) |
# | `total` | suma znanych wartości, czyli sprzedane sztuki | liczba (`float`) |
# | `zero_share` | udział zer wśród znanych miesięcy, od 0 do 1. `None`, gdy znanych miesięcy nie ma | `float` albo `None` |
# | `adi` | średni odstęp między popytami: znane miesiące podzielone przez miesiące z popytem większym od zera. `None`, gdy popytu nie było | `float` albo `None` |
#
# ADI (average demand interval) to klasyczna miara przerywanego popytu. ADI 1 oznacza sprzedaż co miesiąc, ADI 4 sprzedaż średnio co cztery miesiące.
#
# Przykład: dla `[0.0, 2.0, None, 0.0, 6.0]` wynik to `{"months": 4, "missing": 1, "total": 8.0, "zero_share": 0.5, "adi": 2.0}`.
#
# **Skorzystaj z:**
#
# - comprehensions z wykładu 01. Budujesz nimi listę znanych wartości i listę miesięcy z popytem.
# - `if v is not None`, a nie `if v`, z pułapki w tej samej sekcji wykładu 01. Zero to prawdziwa obserwacja.
#
# **Kroki:**
#
# 1. Zbuduj listę znanych wartości (bez `None`).
# 2. Z niej zbuduj listę wartości większych od zera, czyli miesięcy z popytem.
# 3. Policz pięć pól z długości i sum tych dwóch list oraz długości `values`.
# 4. Przy dzieleniu sprawdź, czy mianownik nie jest zerem. Jeśli jest, pole ma wartość `None`.
#
# **Sprawdzenie:** `check("01.4", demand_stats)` wypisuje ✅. Sprawdzenie 01.4 dotyczy kroku 01.4a. Sprawdza przykład z tabeli, serię bez popytu `[0.0, None, 0.0]` i serię z samymi brakami `[None, None]`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Zacznij od dwóch list z comprehensions: znane wartości i wartości większe od zera. Resztę liczysz z ich długości i sum.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Uważaj na dzielenie przez zero. Seria z samymi brakami ma zero znanych miesięcy, seria z samymi zerami ma zero miesięcy z popytem. W obu przypadkach odpowiednie pole to `None`. Warunek `if v is not None`, nie `if v`: zero to prawdziwa obserwacja.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# known = [v for v in values if v is not None]
# demand = [v for v in known if v > 0]
# return {
#     "months": len(known),
#     "missing": ...,
#     "total": sum(known),
#     "zero_share": ... if known else None,
#     "adi": ... if demand else None,
# }
# ```
#
# </details>

# %%
def demand_stats(values):
    """Summarise one series: known months, missing months, total, zero share, ADI.

    Args:
        values: The monthly values of one series in month order, a list of
            float or None (None marks a missing month). It is not changed.

    Returns:
        A dict with five keys:
        "months": number of known months (int);
        "missing": number of missing months (int);
        "total": sum of the known values, the units sold;
        "zero_share": share of known months with zero demand, from 0 to 1,
        or None when no month is known;
        "adi": average demand interval, known months divided by months with
        demand above zero, or None when there was no demand.
    """
    # >>> SOLUTION 01.4
    known = [value for value in values if value is not None]
    demand = [value for value in known if value > 0]
    return {
        "months": len(known),
        "missing": len(values) - len(known),
        "total": sum(known),
        "zero_share": (len(known) - len(demand)) / len(known) if known else None,
        "adi": len(known) / len(demand) if demand else None,
    }
    # <<< SOLUTION


check("01.4", demand_stats)

# %% [markdown]
# ### 01.4b Braki i zera w całym zbiorze
#
# Odpowiadasz na dwa pytania: jaki odsetek wszystkich komórek pliku to braki, a jaki odsetek znanych miesięcy to zera?
#
# **Gdzie:** Zmienne `stats`, `missing_share` i `zero_share` w komórce poniżej.
#
# **Wynik:**
#
# - `stats`: słownik. Klucz to nazwa serii, wartość to słownik statystyk tej serii z `demand_stats`. Ten słownik dostaną funkcje z 01.5 i 01.6.
# - `missing_share`: liczba (`float`) od 0 do 1. Liczba wszystkich brakujących miesięcy ze wszystkich serii podzielona przez liczbę wszystkich miesięcy (znanych i brakujących).
# - `zero_share`: liczba (`float`) od 0 do 1. Liczba znanych miesięcy z zerową sprzedażą ze wszystkich serii podzielona przez liczbę wszystkich znanych miesięcy.
#
# Nie licz średniej z `zero_share` poszczególnych serii. Serie mają różną liczbę znanych miesięcy, więc średnia udziałów to nie jest udział w całości. Liczbę zer w jednej serii odtworzysz jako `zero_share * months`. Seria bez znanych miesięcy ma `zero_share` równe `None`. Nie wnosi ani zer, ani znanych miesięcy, więc pomijasz ją w tej sumie. W tym pliku takiej serii nie ma, ale kod ma działać i bez tej gwarancji.
#
# **Skorzystaj z:**
#
# - `series` z 01.3b. Daje wartości każdej serii.
# - `demand_stats` z 01.4a. Liczy statystyki jednej serii.
# - `sum()` na comprehension. Sumuje miesiące ze wszystkich serii.
#
# **Sprawdzenie:** Wypisane `zera` są bliskie temu, co mówi wstęp labu: trzy na cztery miesiące. Komórka z `assert` pod spodem nie zgłasza błędu.

# %%
# >>> SOLUTION 01.4
stats = {name: demand_stats(values) for name, values in series.items()}
all_months = sum(s["months"] + s["missing"] for s in stats.values())
missing_share = sum(s["missing"] for s in stats.values()) / all_months
known_months = sum(s["months"] for s in stats.values())
zero_months = sum(s["zero_share"] * s["months"] for s in stats.values() if s["months"])
zero_share = zero_months / known_months
# --- STUB
#| stats = ...
#| missing_share = ...
#| zero_share = ...
# <<< SOLUTION
print(f"Braki: {missing_share:.1%} komórek, zera: {zero_share:.1%} znanych miesięcy")

# %%
assert isinstance(stats, dict) and len(stats) == len(series), "stats: jeden wpis na serię."
assert 0 < missing_share < 1, "missing_share to udział: liczba od 0 do 1."
assert 0 < zero_share < 1, "zero_share to udział: liczba od 0 do 1."

# %% [markdown]
# ## 01.5 Najlepsze serie
#
# **Cel:** Ze statystyk 2 674 serii chcesz zobaczyć kilka skrajnych: które części sprzedały się najlepiej, które sprzedają się najrzadziej. Ta funkcja robi taki ranking dla dowolnej statystyki.
#
# **Gdzie:** Funkcja `top_series` w komórce poniżej.
#
# **Wejście:**
#
# - `stats`: słownik w kształcie wyniku 01.4b. Klucz to nazwa serii, wartość to słownik statystyk tej serii. Słownika nie zmieniasz.
# - `key`: napis, nazwa statystyki, po której układasz ranking, np. `"total"` albo `"adi"`. Nie myl go z argumentem `key` funkcji `sorted()`, który przyjmuje funkcję. Twój `key` to tylko napis, którym odczytujesz wartość ze słownika statystyk serii.
# - `n`: liczba całkowita, ile serii chcesz dostać.
#
# **Wynik:** Lista (`list`) najwyżej `n` krotek `(nazwa, wartość)`:
#
# - krotki idą od największej wartości do najmniejszej,
# - serie, dla których ta statystyka to `None`, pomijasz,
# - przy remisie pierwsza jest nazwa wcześniejsza alfabetycznie, żeby wynik był zawsze taki sam,
# - gdy serii z wartością jest mniej niż `n`, lista jest krótsza.
#
# Przykład: dla `{"T1": {"total": 5.0}, "T2": {"total": 9.0}, "T3": {"total": 9.0}}`, `key="total"` i `n=2` wynik to `[("T2", 9.0), ("T3", 9.0)]`.
#
# **Skorzystaj z:**
#
# - `sorted()` z argumentem `key` i krótką funkcją `lambda`, z wykładu 01, sekcja "Cztery kolekcje", część "Sortowanie po kluczu". Układa pary w kolejności rankingu.
# - wycinka `[:n]`. Bierze pierwsze `n` elementów listy.
#
# **Kroki:**
#
# 1. Zbuduj nową listę par `(nazwa, wartość)` dla serii, w których wartość `key` nie jest `None`.
# 2. Posortuj ją tak, żeby większa wartość była wcześniej, a przy równych wartościach nazwa rosnąco.
# 3. Zwróć pierwsze `n` elementów.
#
# **Sprawdzenie:** `check("01.5", top_series)` wypisuje ✅. Sprawdza remis, pomijanie `None` i to, że słownik wejściowy się nie zmienił. Komórka pod sprawdzeniem wypisuje ranking na prawdziwych danych.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `sorted(...)` przyjmuje argument `key`: funkcję, która dla elementu zwraca to, po czym sortujesz. Jeśli zwróci krotkę, Python porówna najpierw pierwsze pola, potem drugie.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Zbuduj listę par z pominięciem `None`, posortuj rosnąco po `(-wartość, nazwa)` i weź pierwsze `n` wycinkiem `[:n]`. Minus przed wartością daje kolejność malejącą, a nazwa rozstrzyga remisy rosnąco.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# rows = [(name, s[key]) for name, s in stats.items() if s[key] is not None]
# return sorted(rows, key=lambda row: ...)[:n]
# ```
#
# </details>

# %%
def top_series(stats, key, n):
    """Return the n (name, value) pairs with the largest `key`, ties by name.

    Args:
        stats: Statistics of many series, a dict from series name to the
            dict returned by demand_stats. It is not changed.
        key: Name of the statistic to rank by, such as "total" or "adi".
        n: How many series to return at most.

    Returns:
        A list of at most n tuples (name, value), largest value first; equal
        values in ascending name order. Series whose `key` is None are left
        out, so the list is shorter than n when fewer series have a value.
    """
    # >>> SOLUTION 01.5
    rows = [(name, s[key]) for name, s in stats.items() if s[key] is not None]
    return sorted(rows, key=lambda row: (-row[1], row[0]))[:n]
    # <<< SOLUTION


check("01.5", top_series)

# %%
print("Najwięcej sprzedanych sztuk:", top_series(stats, "total", 5))
print("Najrzadszy popyt (ADI):     ", top_series(stats, "adi", 5))

# %% [markdown]
# ## 01.6 Zapis wyniku
#
# **Cel:** Statystyki istnieją tylko w pamięci notebooka i znikną po jego zamknięciu. Zapisujesz je do pliku JSON, który przeczyta człowiek i każdy inny program.
#
# Posortowane klucze i wcięcia sprawiają, że dwa zapisy tych samych danych dają identyczne pliki, a różnica między wersjami jest czytelna w gicie.
#
# **Gdzie:** Funkcja `save_summary` w komórce poniżej.
#
# **Wejście:**
#
# - `stats`: słownik do zapisania, w kształcie wyniku 01.4b (nazwa serii → słownik statystyk). Słownika nie zmieniasz.
# - `path`: gdzie zapisać plik, obiekt `Path` albo napis. Katalog, w którym ma leżeć plik, może jeszcze nie istnieć. Istniejący plik zostaje nadpisany.
#
# **Wynik:** Funkcja zapisuje plik i zwraca jego ścieżkę:
#
# - plik to tekst JSON w kodowaniu UTF-8,
# - wcięcie ma 2 spacje,
# - klucze są posortowane alfabetycznie,
# - zwrócona ścieżka to obiekt `Path`.
#
# **Skorzystaj z:**
#
# - `json` z pierwszej komórki. Zamienia słownik na tekst JSON.
# - `Path` z pierwszej komórki. Tworzy katalog i zapisuje tekst do pliku.
# - wykładu 01, sekcja "Pliki i `with`", część "Zapis do pliku JSON". Pokazuje wszystkie trzy potrzebne kroki na wymyślonym słowniku.
#
# **Kroki:**
#
# 1. Zamień `path` na obiekt `Path`, żeby działał też napis.
# 2. Utwórz katalog, w którym ma leżeć plik, razem z brakującymi katalogami wyżej.
# 3. Zamień słownik na tekst JSON z wcięciem i posortowanymi kluczami.
# 4. Zapisz ten tekst do pliku i zwróć ścieżkę.
#
# **Sprawdzenie:** `check("01.6", save_summary)` wypisuje ✅. Komórka pod sprawdzeniem zapisuje Twoje statystyki do `data/processed/car_parts_summary.json`. Otwórz ten plik w edytorze i zobacz, jak wygląda.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Moduł `json` ma `json.dumps(obiekt, indent=..., sort_keys=...)`. `Path` ma `.parent.mkdir(...)` i `.write_text(...)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `mkdir(parents=True, exist_ok=True)` tworzy wszystkie brakujące katalogi i nie narzeka, gdy już są. Zapisz tekst z kodowaniem UTF-8.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# path = Path(path)
# path.parent.mkdir(parents=True, exist_ok=True)
# path.write_text(json.dumps(stats, indent=2, sort_keys=True), encoding="utf-8")
# return path
# ```
#
# </details>

# %%
def save_summary(stats, path):
    """Write the statistics as sorted, indented JSON and return the file path.

    Args:
        stats: The dict to save, from series name to its statistics. It is
            not changed.
        path: Where to write the file, a pathlib.Path or a string. Missing
            folders are created; an existing file is overwritten.

    Returns:
        The path of the written file as a pathlib.Path. The file is UTF-8
        JSON with an indent of 2 spaces and keys sorted alphabetically.
    """
    # >>> SOLUTION 01.6
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stats, indent=2, sort_keys=True), encoding="utf-8")
    return path
    # <<< SOLUTION


check("01.6", save_summary)

# %%
written = save_summary(stats, paths.PROCESSED_DIR / "car_parts_summary.json")
print(f"Zapisano {written.relative_to(paths.ROOT)}")

# %% [markdown]
# ## 01.7 Eksploracja
#
# Bez sprawdzeń. Na pytanie 1 odpowiadasz kodem, a pod nim jednym zdaniem: która grupa przeważa i czy zgadza się to ze wstępem labu. Na pytanie 2 odpowiadasz samymi słowami.
#
# **Pytanie 1.** Popyt dzieli się czasem na "regularny" (ADI do 1.32) i "przerywany" (ADI powyżej 1.32). Ile serii jest w każdej grupie?
#
# **Gdzie:** Zmienne `regular` i `intermittent` w komórce poniżej.
#
# **Wynik:** Dwie listy nazw serii (napisów):
#
# - `regular`: serie z `adi` mniejszym albo równym 1.32,
# - `intermittent`: serie z `adi` większym niż 1.32.
#
# Serie z `adi` równym `None` nie trafiają do żadnej listy.
#
# **Skorzystaj z:**
#
# - `stats` z 01.4b. Z niego czytasz `adi` każdej serii.
# - list comprehension z warunkiem. Buduje każdą z dwóch list.

# %%
# >>> SOLUTION 01.7
regular = [name for name, s in stats.items() if s["adi"] is not None and s["adi"] <= 1.32]
intermittent = [name for name, s in stats.items() if s["adi"] is not None and s["adi"] > 1.32]
# --- STUB
#| regular = ...
#| intermittent = ...
# <<< SOLUTION
print(f"Regularne: {len(regular)}, przerywane: {len(intermittent)}")

# %% [markdown]
# *Twoja odpowiedź:*
#
# **Pytanie 2.** Prognoza "taka sama sprzedaż jak w zeszłym miesiącu" dla serii przerywanej zwykle przewiduje zero. Wyobraź sobie ocenę prognozy jako średnią pomyłkę w sztukach: dla każdego miesiąca różnica między prognozą a sprzedażą bez znaku, uśredniona po miesiącach. Dlaczego ta prognoza może mieć małą średnią pomyłkę, a być bezużyteczna dla magazynu, który musi mieć część na stanie w miesiącu sprzedaży? Odpowiedz słowami, bez liczenia.

# %% [markdown]
# *Twoja odpowiedź:*
#
# ## Koniec labu
#
# Wszystkie sprawdzenia modułu naraz uruchomisz tylko z notebooka, bo dotyczą funkcji z komórek. Przejdź notebook od początku (Restart i Run All) i upewnij się, że każde sprawdzenie ma ✅.
#
# W module 02 te same sześć funkcji przeniesiesz do osobnego pliku `carparts.py`, dodasz im typy i sprawdzisz je narzędziami, których używa się w pracy. Przeniesiesz je razem z docstringami, więc zostaw je w notebooku w działającej wersji.
