# %% [markdown]
# # Lab 03: serie jako obiekty, typy popytu i pierwsze prognozy
#
# Do tej pory seria była krotką `(nazwa, data, wartości)`, a statystyki luźnymi funkcjami. W tym labie seria staje się obiektem, który sam pilnuje poprawności swoich danych i umie powiedzieć, jaki ma typ popytu. Potem napiszesz rodzinę prostych modeli prognozy ze wspólną umową i porównasz je na ostatnich sześciu miesiącach każdej serii.
#
# Te modele przeżyją cały kurs. W module 04 przeniesiesz je do pakietu i otestujesz, a od modułu 08 będą **baseline'em**: poziomem, który każdy prawdziwy model musi pobić.
#
# **Czas:** około 6 godzin.
#
# ## Jak pracujesz
#
# Tak jak w labie 02: kod piszesz w pliku `demand.py`, który leży obok notebooka (`labs/03-classes/demand.py`). Notebook importuje go jako `demand` i przekazuje do sprawdzeń: `check("03.1", demand)`. Dzięki `%autoreload 2` w pierwszej komórce notebook widzi każdą zapisaną zmianę w pliku bez restartu.
#
# W `demand.py` gotowe są: funkcja `read_tsf` (parser pisałeś już dwa razy), stałe `ADI_CUTOFF` i `CV2_CUTOFF` oraz importy, których używa gotowy kod. Każdy blok do napisania jest opisany komentarzem po angielsku: to umowa, czyli dokładny opis tego, co ma robić kod. Importy potrzebne w Twoim kodzie dopisujesz sam, na górze pliku; przy każdym zadaniu jest lista.
#
# Zadania większe niż jedna klasa są podzielone na kroki (03.1a, 03.1b, ...). Sprawdzenie `check(...)` jest jedno na całe zadanie, a po niektórych krokach stoi komórka z `assert`, która potwierdza sam krok.
#
# | Zadanie | Krok | Co piszesz | Gdzie | Czas |
# |---|---|---|---|---|
# | 03.1 | 03.1a | pola i walidacja | `demand.py`, klasa `DemandSeries` | 75 min |
# | | 03.1b | `from_record` | `demand.py`, `DemandSeries.from_record` | |
# | | 03.1c | `known`, `is_complete`, `adi`, `cv2` | `demand.py`, właściwości `DemandSeries` | |
# | | 03.1d | wszystkie serie jako obiekty | notebook, zmienne `series`, `complete` | |
# | 03.2 | 03.2a | `DemandType` | `demand.py` | 45 min |
# | | 03.2b | `classify` | `demand.py` | |
# | | 03.2c | liczba serii każdego typu | notebook, zmienna `counts` | |
# | 03.3 | 03.3a | `LocalForecaster` | `demand.py` | 60 min |
# | | 03.3b | `NaiveForecaster` | `demand.py` | |
# | 03.4 | 03.4a | `SeasonalNaiveForecaster` | `demand.py` | 45 min |
# | | 03.4b | `MovingAverageForecaster` | `demand.py` | |
# | 03.5 | 03.5a | `Forecaster` | `demand.py` | 60 min |
# | | 03.5b | `mae` | `demand.py` | |
# | | 03.5c | `evaluate` | `demand.py` | |
# | | 03.5d | porównanie modeli | notebook, zmienne `models`, `scores` | |
# | 03.6 | | eksploracja, trzy pytania | notebook | 45 min |
#
# **Dane.** `PATH` w pierwszej komórce wskazuje plik Car Parts z labów 01 i 02: 2 674 serie miesięcznej sprzedaży części samochodowych, każda ma 51 miesięcy od stycznia 1998, a brak zapisu w danym miesiącu to `?`, który `read_tsf` zamienia na `None`.

# %%
# %load_ext autoreload
# %autoreload 2

from collections import Counter
from datetime import date

import demand

from coursekit import paths
from coursekit.nb import check

PATH = paths.CAR_PARTS

# %% [markdown]
# ## 03.1 `DemandSeries`
#
# **Cel.** Seria ma być jednym obiektem, którego nie da się zbudować z błędnych danych (pusta seria albo ujemna sprzedaż) ani zmienić po utworzeniu. Statystyki serii z labów 01 i 02 stają się jego właściwościami, więc piszesz `one.adi` zamiast `adi(values)`.
#
# **Gdzie.** `demand.py`, klasa `DemandSeries`. Szkielet klasy z umową w docstringu już jest; piszesz jej ciało.
#
# **Skorzystaj z.** Wzorów na ADI i CV² z labu 02 (różnica w kroku 03.1c). Na górze `demand.py` dopisz importy tak, żeby blok importów wyglądał tak: `from collections.abc import Iterator, Sequence` (dopisujesz `Sequence` do istniejącej linii, nie w osobnej), `from dataclasses import dataclass`, `from datetime import date`, `from pathlib import Path`, `from typing import Self`, w tej kolejności. Kolejności importów pilnuje `ruff check` (reguła `I`), nie `ruff format`, a sprawdzenie 03.5 uruchamia `ruff check` na całym pliku. Gdy ruff zgłosi `I001 Import block is un-sorted`, uruchom w katalogu repozytorium `uv run ruff check --fix labs/03-classes/demand.py`: ruff sam ułoży importy.
#
# **Sprawdzenie.** `check("03.1", demand)` po kroku 03.1c. Wynik `✅ 03.1` znaczy, że całe zadanie przechodzi. Przy `❌` komunikat mówi, które wymaganie nie jest spełnione i na jakich danych.
#
# ### 03.1a Pola i walidacja
#
# **Gdzie.** `demand.py`, ciało klasy `DemandSeries` i jej metoda `__post_init__`.
#
# **Wejście.** Trzy pola, w tej kolejności:
#
# | Pole | Typ | Znaczenie |
# |---|---|---|
# | `name` | napis (`str`) | nazwa serii w pliku, np. `"T1"` |
# | `start` | data (`date`) | pierwszy miesiąc serii |
# | `values` | krotka liczb albo `None` (`tuple[float \| None, ...]`) | sprzedane sztuki w kolejnych miesiącach, od najstarszego; `None` to miesiąc bez zapisu |
#
# **Wynik.** Klasa, której obiekt tworzysz jako `DemandSeries("T1", date(1998, 1, 1), (0.0, 2.0, None))`. Obiekt jest **zamrożony**: przypisanie `one.name = "B"` rzuca `FrozenInstanceError`. Dwa obiekty z tych samych danych są równe (`==`) i dają się włożyć do zbioru. Pusta krotka `values` albo wartość ujemna w niej to `ValueError`.
#
# **Kroki.**
#
# 1. Nad klasą stoi już `@dataclass(frozen=True)`. Zadeklaruj w ciele klasy trzy pola jako `nazwa: typ`, w kolejności z tabeli.
# 2. Dopisz metodę `__post_init__(self) -> None`. Dataclass wywołuje ją sam na końcu `__init__`, więc każdy sposób utworzenia obiektu przez nią przejdzie.
# 3. W `__post_init__` rzuć `ValueError`, gdy `values` jest puste, i drugi, gdy któraś znana wartość (nie `None`) jest mniejsza od zera. W komunikacie podaj nazwę serii.
#
# Dlaczego `values` to krotka, a nie lista? Zamrożony obiekt, który trzyma listę, dalej da się zmienić przez tę listę, a do tego obiektu z listą nie włożysz do zbioru ani nie użyjesz jako klucza słownika.
#
# ### 03.1b `from_record`
#
# **Gdzie.** `demand.py`, metoda klasy `DemandSeries.from_record`.
#
# **Wejście.** `record`: krotka `(nazwa, start, wartości)`, dokładnie taka, jaką zwraca `read_tsf` dla jednej serii. `nazwa` to napis, `start` to data jako tekst `"YYYY-MM-DD"` (np. `"1998-01-01"`), `wartości` to lista liczb i `None`. Typ: `tuple[str, str, Sequence[float | None]]`.
#
# **Wynik.** Nowy obiekt `DemandSeries` (typ wyniku `Self`), w którym `start` jest już datą (`date`), a `values` krotką.
#
# **Kroki.**
#
# 1. Oznacz metodę `@classmethod`. Jej pierwszy argument to `cls`, czyli klasa, na której ją wywołano.
# 2. Rozpakuj `record` na trzy zmienne.
# 3. Zamień tekst daty na `date` metodą `date.fromisoformat`, a listę wartości na krotkę przez `tuple(...)`.
# 4. Zwróć obiekt utworzony przez `cls(...)`, nie przez `DemandSeries(...)` (wykład, sekcja "Właściwości i metody klasy").
#
# Komórka pod podpowiedziami sprawdza kroki 03.1a i 03.1b na jednej małej serii.
#
# ### 03.1c Właściwości
#
# **Gdzie.** `demand.py`, cztery metody `DemandSeries` z `@property`: wywołujesz je bez nawiasów, `one.adi`.
#
# **Wejście.** Tylko `self.values`.
#
# **Wynik.**
#
# | Właściwość | Typ | Znaczenie | Dla `(0.0, 2.0, None, 0.0, 6.0)` |
# |---|---|---|---|
# | `known` | lista liczb (`list[float]`) | znane wartości w tej samej kolejności, bez `None` | `[0.0, 2.0, 0.0, 6.0]` |
# | `is_complete` | `bool` | `True`, gdy żaden miesiąc nie jest `None` | `False` |
# | `adi` | `float` albo `None` | liczba znanych miesięcy podzielona przez liczbę miesięcy ze sprzedażą większą od zera; `None`, gdy takich miesięcy nie ma | `4 / 2 = 2.0` |
# | `cv2` | `float` albo `None` | wariancja populacyjna wartości większych od zera podzielona przez kwadrat ich średniej; `None`, gdy takich wartości jest mniej niż dwie | wartości 2 i 6: średnia 4, wariancja 4, `4 / 16 = 0.25` |
#
# **Kroki.**
#
# 1. `known` pisz najpierw: pozostałe trzy właściwości z niej korzystają.
# 2. `adi` liczysz tak jak w labie 01.
# 3. `cv2` liczysz jak w labie 02, z jedną różnicą: **bez** wymogu 12 znanych miesięcy. `DemandSeries.cv2` nie używa `requires_history`. Wariancja populacyjna: suma kwadratów odchyleń od średniej podzielona przez liczbę wartości (nie przez liczbę minus jeden).
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `@dataclass` sam pisze `__init__`, `__repr__` i `__eq__` z pól zadeklarowanych jako `nazwa: typ` w ciele klasy. `frozen=True` dodaje blokadę zmiany pól i `__hash__`. Własną walidację dopisujesz w `__post_init__`, które dataclass wywołuje na końcu `__init__`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `from_record` dostaje `cls` zamiast `self` i kończy się `return cls(...)`. Datę z tekstu zrobi `date.fromisoformat`, a krotkę z listy `tuple(values)`. Typ wyniku to `Self` z modułu `typing`. Właściwość to zwykła metoda z `@property` nad `def`: wywołujesz ją bez nawiasów.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# @dataclass(frozen=True)
# class DemandSeries:
#     """..."""
#
#     name: str
#     start: date
#     values: tuple[float | None, ...]
#
#     def __post_init__(self) -> None:
#         if not self.values:
#             raise ValueError(...)
#         ...
#
#     @classmethod
#     def from_record(cls, record: tuple[str, str, Sequence[float | None]]) -> Self:
#         name, start, values = record
#         return cls(name, date.fromisoformat(start), tuple(values))
#
#     @property
#     def known(self) -> list[float]:
#         return [...]
# ```
#
# </details>

# %% [markdown]
# Krok 03.1a i 03.1b: ta komórka tworzy jedną serię przez `from_record`. Gdy nie ma błędu, oba kroki działają.

# %%
probe = demand.DemandSeries.from_record(("X", "1998-01-01", [0.0, 2.0, None]))
assert probe.start == date(1998, 1, 1), f"start to {probe.start!r}, a ma być data"
assert probe.values == (0.0, 2.0, None), f"values to {probe.values!r}, a ma być krotka"
probe

# %% [markdown]
# Całe zadanie 03.1, po kroku 03.1c:

# %%
check("03.1", demand)

# %% [markdown]
# ### 03.1d Wszystkie serie jako obiekty
#
# **Gdzie.** Komórka poniżej, zmienne `series` i `complete`.
#
# **Wynik.** `series`: lista obiektów `DemandSeries`, jeden na każdą serię z pliku, w kolejności z pliku. `complete`: lista tych serii z `series`, które nie mają żadnego brakującego miesiąca.
#
# **Skorzystaj z.** `demand.read_tsf(PATH)` daje rekordy, `demand.DemandSeries.from_record` robi z rekordu obiekt, `is_complete` mówi, czy seria jest kompletna. Wystarczą dwa list comprehension.

# %%
# >>> SOLUTION 03.1
series = [demand.DemandSeries.from_record(record) for record in demand.read_tsf(PATH)]
complete = [one for one in series if one.is_complete]
# --- STUB
#| series = ...
#| complete = ...
# <<< SOLUTION
assert all(isinstance(one, demand.DemandSeries) for one in series)
assert 0 < len(complete) < len(series)
print(f"Serie: {len(series)}, kompletne: {len(complete)}")
series[0]

# %% [markdown]
# Zwróć uwagę, jak notebook wyświetlił obiekt: to `__repr__`, który napisał za Ciebie `@dataclass`.

# %% [markdown]
# ## 03.2 Typ popytu: `DemandType` i `classify`
#
# **Cel.** Rzadki popyt prognozuje się inaczej niż regularny. Syntetos i Boylan podzielili popyt na cztery typy według dwóch liczb: jak często jest popyt (ADI) i jak bardzo różnią się jego wielkości (CV²). Po tym zadaniu każda seria ma nazwany typ, a w 03.6 porównasz modele osobno dla każdego typu.
#
# | | CV² ≤ 0.49 | CV² > 0.49 |
# |---|---|---|
# | **ADI ≤ 1.32** | smooth: regularny | erratic: regularny, ale nierówny |
# | **ADI > 1.32** | intermittent: rzadki, ale równy | lumpy: rzadki i nierówny |
#
# **Gdzie.** `demand.py`, klasa `DemandType` i funkcja `classify`, pod `DemandSeries` (komentarz `# 03.2`).
#
# **Skorzystaj z.** Stałych `ADI_CUTOFF` (1.32) i `CV2_CUTOFF` (0.49), które są już w pliku. Wartości ADI i CV² dadzą `one.adi` i `one.cv2` z 03.1. Dopisz linię `from enum import StrEnum` między importem z `datetime` a importem z `pathlib` (moduły idą alfabetycznie; przy `I001` pomoże `uv run ruff check --fix labs/03-classes/demand.py`).
#
# **Sprawdzenie.** `check("03.2", demand)`. Sprawdzenie podaje `classify` m.in. wartości równe progom, `None` na każdej z dwóch pozycji i liczby całkowite.
#
# ### 03.2a `DemandType`
#
# **Wynik.** Klasa `DemandType`, która dziedziczy po `StrEnum`, z pięcioma członkami: `SMOOTH`, `ERRATIC`, `INTERMITTENT`, `LUMPY` i `INSUFFICIENT`. Wartość każdego członka to jego nazwa małymi literami: `DemandType.LUMPY == "lumpy"`. `INSUFFICIENT` oznacza serię, dla której ADI albo CV² jest `None`, więc typu nie da się ustalić.
#
# ### 03.2b `classify`
#
# **Wejście.** `adi`: liczba albo `None` (`float | None`), ADI serii. `cv2`: liczba albo `None`, CV² serii. Mogą przyjść też liczby całkowite, np. `classify(1, 0)`.
#
# **Wynik.** Jeden członek `DemandType`: `INSUFFICIENT`, gdy którakolwiek liczba to `None`, w przeciwnym razie typ z tabeli. Wartość równa progowi należy do niższej klasy: ADI równe 1.32 to jeszcze wiersz górny.
#
# **Kroki.**
#
# 1. Napisz funkcję z instrukcją `match adi, cv2:` (wykład, sekcja "StrEnum i match").
# 2. Pierwszy `case` łapie `None` na którejkolwiek pozycji.
# 3. Kolejne trzy przypadki odpowiadają trzem komórkom tabeli, każdy ze strażnikiem `if ...` porównującym liczby z progami przez `<=`.
# 4. Ostatni `case _:` zwraca `LUMPY`: to jedyna komórka tabeli, w której obie liczby są powyżej progów, więc nie opiszesz jej porównaniem `<=`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `match adi, cv2:` dopasowuje krotkę dwóch wartości. Pierwszy pasujący `case` wygrywa, więc kolejność ma znaczenie: przypadek z `None` sprawdź najpierw.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Wzorzec `case (None, _) | (_, None):` łapie brak którejkolwiek liczby. Kolejne przypadki mają **strażników**: `case (adi, cv2) if adi <= ADI_CUTOFF and cv2 <= CV2_CUTOFF:`. mypy wie, że po pierwszym przypadku żadna z liczb nie jest już `None`. Ostatni, `case _:`, łapie wszystko inne.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# class DemandType(StrEnum):
#     SMOOTH = "smooth"
#     ...
#
#
# def classify(adi: float | None, cv2: float | None) -> DemandType:
#     match adi, cv2:
#         case (None, _) | (_, None):
#             return DemandType.INSUFFICIENT
#         case (adi, cv2) if adi <= ADI_CUTOFF and cv2 <= CV2_CUTOFF:
#             return DemandType.SMOOTH
#         ...
# ```
#
# </details>

# %%
check("03.2", demand)

# %% [markdown]
# ### 03.2c Ile serii jest każdego typu
#
# **Gdzie.** Komórka poniżej, zmienna `counts`.
#
# **Wynik.** `counts`: obiekt `Counter`, w którym kluczem jest typ popytu (`DemandType`), a wartością liczba serii tego typu. Suma wartości równa się liczbie wszystkich serii.
#
# **Skorzystaj z.** `series` z 03.1d, `demand.classify(one.adi, one.cv2)` dla każdej serii. `Counter` z modułu `collections` jest zaimportowany w pierwszej komórce: dostaje ciąg wartości (listę albo generator) i liczy, ile razy wystąpiła każda z nich. Działa jak słownik, a jego metoda `most_common()`, której używa wydruk, zwraca pary (wartość, liczba) od najczęstszej.

# %%
# >>> SOLUTION 03.2
counts = Counter(demand.classify(one.adi, one.cv2) for one in series)
# --- STUB
#| counts = ...
# <<< SOLUTION
assert sum(counts.values()) == len(series)
for kind, count in counts.most_common():
    print(f"{kind:>13}: {count}")

# %% [markdown]
# ## 03.3 Umowa modelu: `LocalForecaster` i `NaiveForecaster`
#
# **Cel.** Każdy model prognozy będzie używany tak samo: `model.fit(historia).predict(horyzont)`. Sprawdzanie argumentów (pusta historia, horyzont 0, `predict` przed `fit`) zapisujesz raz, w klasie bazowej. Każdy model pisze potem tylko to, czym się różni: jak liczy prognozę.
#
# **Gdzie.** `demand.py`, klasy `LocalForecaster` i `NaiveForecaster`, pod `classify` (komentarz `# 03.3`).
#
# **Skorzystaj z.** Wykładu, sekcja "Dziedziczenie i umowy", podsekcja "Klasa abstrakcyjna". Dopisz linię `from abc import ABC, abstractmethod` na samej górze bloku importów, przed importem z `collections.abc`. `Sequence` i `Self` masz już z 03.1.
#
# **Sprawdzenie.** `check("03.3", demand)`. Sprawdzenie dopisuje też wartość do listy już po `fit` i patrzy, czy prognoza się zmieniła: nie może.
#
# ### 03.3a `LocalForecaster`
#
# **Wejście.**
#
# - `history` w `fit`: znane wartości jednej serii od najstarszej, ciąg liczb (`Sequence[float]`), np. lista `[1.0, 2.0, 5.0]`.
# - `horizon` w `predict`: liczba całkowita (`int`), na ile kroków (tu miesięcy) do przodu prognozować.
#
# **Wynik.**
#
# - `LocalForecaster` dziedziczy po `ABC`. W `__init__` ustawia `self._history = None`: model jeszcze nic nie widział.
# - `fit(history)` zapisuje w `self._history` **kopię** historii jako nową listę liczb `float` i zwraca `self` (typ wyniku `Self`). Pusta historia to `ValueError`.
# - `predict(horizon)` zwraca listę `horizon` liczb (`list[float]`), najbliższy miesiąc pierwszy. Przed `fit` rzuca `RuntimeError`, dla horyzontu mniejszego od 1 rzuca `ValueError`. Gdy wszystko jest w porządku, zwraca wynik `self._forecast(self._history, horizon)`.
# - `_forecast(history, horizon)` jest **metodą abstrakcyjną** (`@abstractmethod`): w tej klasie ma tylko docstring, a każda klasa pochodna ją implementuje.
#
# **Kroki.**
#
# 1. Klasa i `__init__`.
# 2. `fit`: najpierw walidacja, potem kopia, na końcu `return self`.
# 3. `predict`: dwa warunki błędu, potem wywołanie `_forecast`.
# 4. `_forecast` z `@abstractmethod`.
#
# ### 03.3b `NaiveForecaster`
#
# **Wynik.** Klasa dziedzicząca po `LocalForecaster`, która implementuje tylko `_forecast`: zwraca listę, w której ostatnia wartość historii powtarza się `horizon` razy. Dla historii `[1.0, 2.0, 5.0]` i horyzontu 3: `[5.0, 5.0, 5.0]`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Klasy abstrakcyjnej z `@abstractmethod` nie da się utworzyć: `LocalForecaster()` rzuca `TypeError`. Klasa pochodna, która implementuje wszystkie metody abstrakcyjne, już się tworzy. Tak Python pilnuje, że żaden model nie zapomni o `_forecast`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Walidacja siedzi w `fit` i `predict` klasy bazowej, więc `NaiveForecaster` jej nie powtarza. `fit` zwraca `self`, a typ wyniku to `Self`: wtedy `NaiveForecaster().fit(...)` ma dla mypy typ `NaiveForecaster`, a nie `LocalForecaster`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# class LocalForecaster(ABC):
#     def __init__(self) -> None:
#         self._history: list[float] | None = None
#
#     def fit(self, history: Sequence[float]) -> Self:
#         if len(history) == 0:
#             raise ValueError(...)
#         self._history = [float(value) for value in history]
#         return self
#
#     def predict(self, horizon: int) -> list[float]:
#         ...
#         return self._forecast(self._history, horizon)
#
#     @abstractmethod
#     def _forecast(self, history: list[float], horizon: int) -> list[float]:
#         """..."""
# ```
#
# </details>

# %%
check("03.3", demand)

# %% [markdown]
# ## 03.4 Dwa kolejne modele
#
# **Cel.** Sprzedaż części często powtarza się w rytmie roku albo zależy od kilku ostatnich miesięcy, a nie tylko od ostatniego. Dwa kolejne modele łapią te dwa wzorce i nadal korzystają z walidacji klasy bazowej.
#
# **Gdzie.** `demand.py`, klasy `SeasonalNaiveForecaster` i `MovingAverageForecaster`, pod `NaiveForecaster` (komentarz `# 03.4`). Obie dziedziczą po `LocalForecaster`.
#
# **Skorzystaj z.** `LocalForecaster` z 03.3 i `super()` (wykład, sekcja "Dziedziczenie i umowy").
#
# **Sprawdzenie.** `check("03.4", demand)`.
#
# Domyślne 7 w obu konstruktorach dotyczy danych dziennych, na których te klasy będą pracować od modułu 08. Na danych miesięcznych podajesz parametr jawnie, np. `season=12`.
#
# ### 03.4a `SeasonalNaiveForecaster`
#
# **Wejście.** `season`: liczba całkowita (`int`), długość sezonu w krokach, domyślnie 7. Dla danych miesięcznych z rytmem rocznym to 12.
#
# **Wynik.** Prognoza powtarza ostatni pełny sezon, krok po kroku: dla `season=12` prognoza na styczeń to ostatni styczeń. Horyzont dłuższy niż sezon zawija się. Dla `season=3`, historii `[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]` i horyzontu 5 wynik to `[4.0, 5.0, 6.0, 4.0, 5.0]`.
#
# Błędy: `season` mniejsze od 1 to `ValueError` w konstruktorze. Historia krótsza niż sezon to `ValueError` w `fit`.
#
# **Kroki.**
#
# 1. `__init__(self, season: int = 7)`: najpierw `super().__init__()`, potem walidacja, potem `self.season = season`.
# 2. `fit`: nadpisz metodę bazową, dodaj sprawdzenie długości historii i oddaj resztę pracy `super().fit(history)`.
# 3. `_forecast`: weź ostatnie `season` wartości historii i dla każdego kroku prognozy wybierz z nich właściwy element.
#
# ### 03.4b `MovingAverageForecaster`
#
# **Wejście.** `window`: liczba całkowita (`int`), ile ostatnich wartości uśredniać, domyślnie 7.
#
# **Wynik.** Prognoza powtarza `horizon` razy średnią z ostatnich `window` wartości historii. Gdy historia jest krótsza niż okno, średnią z całej historii. Dla `window=2` i historii `[1.0, 2.0, 3.0, 5.0]`: `[4.0, 4.0, ...]`. `window` mniejsze od 1 to `ValueError` w konstruktorze.
#
# **Kroki.** `__init__` jak w 03.4a, bez własnego `fit`. `_forecast` liczy jedną średnią i powtarza ją.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Oba mają własny `__init__` z parametrem. Na jego początku `super().__init__()`, żeby klasa bazowa ustawiła `_history`. `SeasonalNaiveForecaster` nadpisuje też `fit`, żeby dodać swoją walidację, i woła `super().fit(history)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Ostatni sezon to `history[-season:]`. Krok `step` prognozy bierze element `step % season` tego wycinka. Średnia: `history[-window:]` działa także, gdy historia jest krótsza niż okno.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# def _forecast(self, history: list[float], horizon: int) -> list[float]:
#     last_season = history[-self.season :]
#     return [last_season[step % self.season] for step in range(horizon)]
# ```
#
# </details>

# %%
check("03.4", demand)

# %% [markdown]
# ## 03.5 Ocena: `Forecaster`, `mae`, `evaluate`
#
# **Cel.** Masz cztery modele i chcesz wiedzieć, który prognozuje najlepiej. Uczciwy test: schowaj przed modelem ostatnie miesiące serii (**holdout**, okres testowy), naucz go na wcześniejszych, każ prognozować schowane i zmierz, o ile się pomylił. Wykład, sekcja "Dziedziczenie i umowy", podsekcja "Jak ocenić prognozę", pokazuje to na przykładzie.
#
# **Gdzie.** `demand.py`, klasa `Forecaster` i funkcje `mae` i `evaluate`, pod `MovingAverageForecaster` (komentarz `# 03.5`).
#
# **Skorzystaj z.** `DemandSeries.is_complete` i `DemandSeries.known` z 03.1. Nie dopisuj nowych linii importu, tylko rozszerz istniejące: `from collections.abc import Callable, Iterable, Iterator, Sequence` i `from typing import Protocol, Self`. Przy `I001` uruchom `uv run ruff check --fix labs/03-classes/demand.py`.
#
# **Sprawdzenie.** `check("03.5", demand)`. To sprawdzenie uruchamia też `ruff check`, `ruff format --check` i `mypy --strict` na całym pliku `demand.py`, więc pokaże też błędy z wcześniejszych zadań.
#
# ### 03.5a `Forecaster`
#
# **Wynik.** Klasa `Forecaster`, która dziedziczy po `Protocol`, z dwiema metodami: `fit(self, history: Sequence[float]) -> Self` i `predict(self, horizon: int) -> list[float]`. Ciało każdej z nich to `...`. Opisuje, co model **umie**, a nie po czym dziedziczy. Każda klasa z tymi dwiema metodami pasuje, nawet jeśli nigdy nie słyszała o `LocalForecaster`.
#
# ### 03.5b `mae`
#
# **Wejście.** `actual`: ciąg liczb (`Sequence[float]`), ile naprawdę sprzedano w kolejnych miesiącach. `forecast`: ciąg liczb tej samej długości, co model przewidział na te same miesiące.
#
# **Wynik.** `float`: **MAE** (mean absolute error, średni błąd bezwzględny), czyli średnia z `|actual - forecast|` po miesiącach, w sztukach. Dla `[0.0, 4.0]` i `[1.0, 1.0]`: (1 + 3) / 2 = 2.0. Ciągi różnej długości albo oba puste to `ValueError`. Jeśli łączysz oba ciągi w pary przez `zip`, podaj mu jawnie argument `strict`: `ruff check` w sprawdzeniu 03.5 zgłasza `zip` bez niego jako `B905`. Długość sprawdzasz i tak sam, przed liczeniem, żeby rzucić własny `ValueError` z czytelnym komunikatem.
#
# ### 03.5c `evaluate`
#
# **Wejście.**
#
# - `make_model`: funkcja bez argumentów, która przy każdym wywołaniu zwraca nowy, nienauczony model (`Callable[[], Forecaster]`). Klasa też jest taką funkcją, więc `evaluate(demand.NaiveForecaster, series)` działa. Model z parametrem przekażesz przez `lambda: demand.SeasonalNaiveForecaster(season=12)`.
# - `series`: serie `DemandSeries` do oceny, dowolny ciąg, po którym da się przejść pętlą `for` (`Iterable[DemandSeries]`), np. lista `series` z 03.1d.
# - `holdout`: dodatnia liczba całkowita, ile ostatnich miesięcy każdej serii schować przed modelem, domyślnie 6. Funkcja nie musi sprawdzać, czy jest dodatnia: to obowiązek wywołującego, a w tym labie zawsze podajesz 6 albo zostawiasz domyślne.
#
# **Wynik.** `float`: średnia z MAE policzonych osobno dla każdej ocenionej serii. Ocenione są tylko serie kompletne i dłuższe niż `holdout`; pozostałe pomijasz. Gdy nie zostaje żadna, `ValueError`.
#
# **Kroki.**
#
# 1. Pusta lista na błędy.
# 2. Dla każdej serii: pomiń ją, gdy ma brak albo jest za krótka.
# 3. Podziel `known` na historię (wszystko oprócz ostatnich `holdout` wartości) i prawdę (ostatnie `holdout` wartości).
# 4. Weź nowy model z `make_model()`, naucz go na historii, każ prognozować `holdout` kroków i dopisz MAE tej prognozy względem prawdy.
# 5. Pusta lista na końcu to `ValueError`, w przeciwnym razie zwróć średnią.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Protocol to klasa dziedzicząca po `typing.Protocol`, z metodami, których ciało to `...`. Typ parametru `make_model` to `Callable[[], Forecaster]`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Dla kompletnej serii `known` to wszystkie wartości jako `float`. Historia to `known[:-holdout]`, prawda to `known[-holdout:]`. Błędy zbieraj w liście. Pusta lista na końcu oznacza, że nie było czego ocenić.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# errors = []
# for one in series:
#     if not one.is_complete or len(one.values) <= holdout:
#         continue
#     history, actual = one.known[:-holdout], one.known[-holdout:]
#     forecast = make_model().fit(history).predict(holdout)
#     errors.append(mae(actual, forecast))
# ```
#
# </details>

# %% [markdown]
# Krok 03.5b: przykład z opisu `mae`.

# %%
assert demand.mae([0.0, 4.0], [1.0, 1.0]) == 2.0

# %%
check("03.5", demand)

# %% [markdown]
# ### 03.5d Porównanie modeli na wszystkich seriach
#
# **Gdzie.** Komórka poniżej, zmienne `models` i `scores`.
#
# **Wynik.**
#
# - `models`: słownik nazwa modelu → funkcja bez argumentów, która zwraca nowy model. Cztery wpisy, z tymi nazwami: `"naive"` (`NaiveForecaster`), `"seasonal 12"` (`SeasonalNaiveForecaster` z `season=12`), `"moving average 3"` i `"moving average 12"` (`MovingAverageForecaster` z `window=3` i `window=12`).
# - `scores`: słownik z tymi samymi nazwami → średnia MAE z `evaluate` (`float`, w sztukach na miesiąc).
#
# **Skorzystaj z.** `demand.evaluate` z 03.5c z domyślnym `holdout=6`, listy `series` z 03.1d i `lambda` dla modeli z parametrem. Słownik `scores` zbudujesz dict comprehension po `models.items()`.

# %%
# >>> SOLUTION 03.5
models = {
    "naive": demand.NaiveForecaster,
    "seasonal 12": lambda: demand.SeasonalNaiveForecaster(season=12),
    "moving average 3": lambda: demand.MovingAverageForecaster(window=3),
    "moving average 12": lambda: demand.MovingAverageForecaster(window=12),
}
scores = {name: demand.evaluate(make, series) for name, make in models.items()}
# --- STUB
#| models = ...
#| scores = ...
# <<< SOLUTION
assert set(scores) == set(models)
for name, score in sorted(scores.items(), key=lambda item: item[1]):
    print(f"{name:>18}: MAE {score:.3f}")

# %% [markdown]
# ## 03.6 Eksploracja
#
# **Cel.** Sprawdzić, czy najmniejsze MAE znaczy najlepszą prognozę dla magazynu. Bez sprawdzeń: odpowiedzi piszesz w komórkach "*Twoja odpowiedź:*".
#
# **Pytanie 1.** Napisz tu, w notebooku, klasę `ZeroForecaster`, która zawsze prognozuje zero. Nie dziedzicz po `LocalForecaster`. Oceń ją tym samym `evaluate`.
#
# - **Gdzie:** komórka poniżej, klasa `ZeroForecaster` i wpis `scores["zero"]`.
# - **Wynik:** `ZeroForecaster` ma metody `fit(history)`, która zwraca `self`, i `predict(horizon)`, która zwraca listę `horizon` zer typu `float`. `scores["zero"]`: `float`, średnia MAE tego modelu.
# - **Skorzystaj z:** `demand.evaluate`, listy `series`. Klasę przekazujesz jak `demand.NaiveForecaster` w 03.5d.

# %%
# >>> SOLUTION 03.6
class ZeroForecaster:
    """Always forecasts zero demand."""

    def fit(self, history):
        return self

    def predict(self, horizon):
        return [0.0] * horizon


scores["zero"] = demand.evaluate(ZeroForecaster, series)
# --- STUB
#| class ZeroForecaster:
#|     ...
#|
#|
#| scores["zero"] = ...
# <<< SOLUTION
print(f"zero: MAE {scores['zero']:.3f}")

# %% [markdown]
# Model, który nic nie wie, ma najmniejszy błąd. Policz, ile sztuk łącznie prognozuje każdy model na sześć miesięcy wszystkich kompletnych serii i ile sprzedano naprawdę.
#
# - **Gdzie:** komórka poniżej, zmienne `actual_total` i `forecast_totals`.
# - **Wynik:** `actual_total`: `float`, suma sprzedaży z ostatnich 6 miesięcy wszystkich serii z `complete`. `forecast_totals`: słownik nazwa modelu → `float`, suma prognoz tego modelu na te same miesiące, gdy uczy się na wszystkim oprócz ostatnich 6 miesięcy. Pięć wpisów: cztery z `models` i `"zero"`.
# - **Skorzystaj z:** `complete` z 03.1d, `models` z 03.5d, `ZeroForecaster`, `known` każdej serii. Dwa słowniki połączysz w jeden przez `{**models, "zero": ZeroForecaster}`.

# %%
# >>> SOLUTION 03.6
actual_total = sum(sum(one.known[-6:]) for one in complete)
forecast_totals = {
    name: sum(sum(make().fit(one.known[:-6]).predict(6)) for one in complete)
    for name, make in {**models, "zero": ZeroForecaster}.items()
}
# --- STUB
#| actual_total = ...
#| forecast_totals = ...
# <<< SOLUTION
print(f"Sprzedano: {actual_total:.0f} sztuk")
for name, total in forecast_totals.items():
    print(f"{name:>18}: {total:.0f} sztuk ({total / actual_total:.0%})")

# %% [markdown]
# Dlaczego prognoza zerowa wygrywa w MAE? Czego potrzebuje magazyn, który na jej podstawie zamawia części? Jaką własność powinna mieć metryka, której użyjesz do wyboru modelu? Odpowiedz własnymi słowami, bez nazwy fachowej. Punkt wyjścia: porównaj w wydruku powyżej sumę prognoz każdego modelu z tym, co sprzedano. Jakiego rodzaju pomyłki MAE nie zauważa?
#
# *Twoja odpowiedź:*
#
# **Pytanie 2.** Pogrupuj serie według typu popytu i porównaj modele osobno dla każdej grupy. Czy ranking modeli jest taki sam w każdej grupie?
#
# - **Gdzie:** komórka poniżej. Nazwy zmiennych wybierasz sam.
# - **Wynik:** typ serii liczysz z całej serii, tak jak w 03.2c, i grupujesz wszystkie serie z `series`. Wydruk: dla każdego typu popytu nazwa najlepszego z czterech modeli z `models` i jego MAE. Dla typu bez żadnej kompletnej serii `evaluate` rzuca `ValueError`: złap go (`try` / `except ValueError`) i wypisz, że brak kompletnych serii.
# - **Skorzystaj z:** `series`, `demand.classify`, `models`, `demand.evaluate`. Słownik typ → lista serii zbudujesz pętlą i metodą `setdefault` słownika. Najlepszy model to klucz słownika z najmniejszą wartością: znajdzie go wbudowana funkcja `min` z argumentem `key`, któremu podajesz metodę `get` tego słownika.

# %%
# >>> SOLUTION 03.6
by_type: dict[str, list] = {}
for one in series:
    by_type.setdefault(demand.classify(one.adi, one.cv2), []).append(one)
for kind, members in by_type.items():
    try:
        row = {name: demand.evaluate(make, members) for name, make in models.items()}
    except ValueError:
        print(f"{kind:>13}: brak kompletnych serii")
        continue
    best = min(row, key=row.get)
    print(f"{kind:>13}: najlepszy {best} (MAE {row[best]:.3f})")
# --- STUB
#| ...
# <<< SOLUTION

# %% [markdown]
# *Twoja odpowiedź:*
#
# **Pytanie 3.** `classify` jest funkcją, a nie metodą `DemandSeries`. Podaj jeden argument za zostawieniem jej jako funkcji i jeden za przeniesieniem do klasy.
#
# *Twoja odpowiedź:*
#
# ## Koniec labu
#
# W module 04 klasy prognoz przejdą do pakietu `freshcast`, do pliku `src/freshcast/models/local.py`, a Ty napiszesz do nich testy w `pytest`. Ten notebook zostaje jako zapis eksperymentu.
