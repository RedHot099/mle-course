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
# Każde zadanie to funkcja w komórce notebooka. Tam, gdzie widzisz `raise NotImplementedError`, piszesz jej ciało. Pod funkcją jest komórka `check("01.x", nazwa_funkcji)`, która sprawdza ją na małych, wymyślonych danych.
#
# Pod każdym zadaniem są trzy podpowiedzi. Otwieraj je po kolei. Jeśli pracujesz z tutorem, wpisz `/hint 01.3`.
#
# | Zadanie | Funkcja | Czas |
# |---|---|---|
# | 01.1 | `parse_value` | 30 min |
# | 01.2 | `parse_series_line` | 45 min |
# | 01.3 | `read_series` | 60 min |
# | 01.4 | `demand_stats` | 60 min |
# | 01.5 | `top_series` | 45 min |
# | 01.6 | `save_summary` | 30 min |
# | 01.7 | Eksploracja | 45 min |

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
# Znak zapytania oznacza miesiąc, dla którego nie ma pomiaru. To coś innego niż zero.

# %% [markdown]
# ## 01.1 Jedna wartość
#
# Napisz `parse_value(text)`:
#
# - `"?"` zamienia na `None`,
# - liczbę zamienia na `float`, także gdy dookoła są spacje,
# - tekst, który nie jest liczbą, albo liczba ujemna (popyt nie bywa ujemny) to `ValueError` z komunikatem pokazującym ten tekst.
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
    """Turn one value of a .tsf series into a float, or None for a missing month."""
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
# Napisz `parse_series_line(line)`, która z linii
#
# ```
# T7:1998-01-01 00-00-00:0,2,?,1
# ```
#
# robi krotkę `("T7", "1998-01-01", [0.0, 2.0, None, 1.0])`: nazwa, sama data (bez godziny) i lista wartości. Linia bez dwóch dwukropków to `ValueError`.
#
# Dlaczego krotka, a nie lista? Te trzy pola mają stałe, różne znaczenia. Krotka mówi czytelnikowi: "to jest jeden rekord, nie ciąg podobnych rzeczy".
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
    """Split one data line into (name, start date, list of values)."""
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
# Napisz **generator** `read_series(path)`, który otwiera plik i oddaje (`yield`) kolejne serie jako krotki z 01.2. Pomija komentarze, nagłówek i puste linie. Serie zaczynają się po linii `@data`.
#
# Generator nie trzyma w pamięci całego pliku. Ten plik jest mały, ale ten sam wzorzec przeczyta plik z milionem serii.
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
    """Yield (name, start, values) for every series of a .tsf file."""
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
# Wczytaj cały plik do słownika: nazwa serii to klucz, lista wartości to wartość. Ile jest serii i jak długa jest każda?

# %%
# >>> SOLUTION 01.3
series = {name: values for name, _start, values in read_series(PATH)}
lengths = {len(values) for values in series.values()}
# --- STUB
#| series = ...
#| lengths = ...
# <<< SOLUTION
print(f"Serie: {len(series)}, długości: {lengths}")

# %% [markdown]
# ## 01.4 Statystyki jednej serii
#
# Napisz `demand_stats(values)`, która zwraca słownik:
#
# | Klucz | Znaczenie |
# |---|---|
# | `months` | liczba znanych miesięcy (bez `None`) |
# | `missing` | liczba miesięcy z brakiem |
# | `total` | suma znanych wartości |
# | `zero_share` | udział zer wśród znanych miesięcy, `None` gdy znanych nie ma |
# | `adi` | średni odstęp między popytami: znane miesiące podzielone przez miesiące z popytem większym od zera, `None` gdy popytu nie było |
#
# ADI (average demand interval) to klasyczna miara przerywanego popytu. ADI 1 oznacza sprzedaż co miesiąc, ADI 4 sprzedaż średnio co cztery miesiące.
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
    """Summarise one series: known months, missing months, total, zero share, ADI."""
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
# Policz statystyki wszystkich serii (słownik nazwa → statystyki) i odpowiedz: jaki odsetek wszystkich komórek to braki, a jaki odsetek znanych miesięcy to zera?

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

# %% [markdown]
# ## 01.5 Najlepsze serie
#
# Napisz `top_series(stats, key, n)`: lista `n` par `(nazwa, wartość)` z największą wartością statystyki `key`, malejąco. Serie z wartością `None` pomijasz. Przy remisie wygrywa nazwa wcześniejsza alfabetycznie, żeby wynik był zawsze taki sam. Słownika wejściowego nie zmieniasz.
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
    """Return the n (name, value) pairs with the largest `key`, ties by name."""
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
# Napisz `save_summary(stats, path)`: zapisuje słownik jako JSON z wcięciem 2 i posortowanymi kluczami, tworzy brakujący katalog, zwraca ścieżkę pliku.
#
# Posortowane klucze i wcięcia sprawiają, że dwa zapisy tych samych danych dają identyczne pliki, a różnica między wersjami jest czytelna w gicie.
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
    """Write the statistics as sorted, indented JSON and return the file path."""
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
# Bez sprawdzeń. Odpowiedz kodem, a pod spodem jednym, dwoma zdaniami.
#
# **Pytanie 1.** Popyt dzieli się czasem na "regularny" (ADI do 1.32) i "przerywany" (ADI powyżej 1.32). Ile serii jest w każdej grupie? Policz to comprehension na słowniku `stats`.

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
# **Pytanie 2.** Prognoza "taka sama sprzedaż jak w zeszłym miesiącu" dla serii przerywanej zwykle przewiduje zero. Dlaczego to może wyglądać na dobrą prognozę w jednej metryce, a być bezużyteczne dla magazynu?

# %% [markdown]
# *Twoja odpowiedź:*
#
# ## Koniec labu
#
# Wszystkie sprawdzenia modułu naraz uruchomisz tylko z notebooka, bo dotyczą funkcji z komórek. Przejdź notebook od początku (Restart i Run All) i upewnij się, że każde sprawdzenie ma ✅.
#
# W module 02 te same funkcje przeniesiesz do osobnego pliku `.py`, dodasz im typy i sprawdzisz je narzędziami, które używa się w pracy.
