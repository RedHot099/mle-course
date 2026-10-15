# %% [markdown]
# # Lab 02: z notebooka do typowanego modułu
#
# W labie 01 funkcje żyły w komórkach notebooka. Tak się zaczyna, ale tak się nie pracuje dłużej niż kilka dni: kodu z komórek nie zaimportujesz w innym notebooku, nie sprawdzi go mypy, trudno go przejrzeć komuś innemu.
#
# W tym labie przenosisz funkcje z labu 01 do modułu `carparts.py`, dajesz im typy i doprowadzasz do tego, że `ruff` i `mypy --strict` nie mają uwag. Potem dopisujesz do modułu dwa dekoratory i rejestr statystyk, który zastąpi jedną dużą funkcję `demand_stats` zestawem małych.
#
# **Czas:** około 6 godzin.
#
# ## Jak pracujesz
#
# Kod piszesz w pliku `carparts.py` obok tego notebooka. Otwórz go w edytorze obok notebooka. Notebook tylko importuje moduł, sprawdza go i używa na danych. W notebooku piszesz jedynie odpowiedzi na pytania z eksploracji, w miejscach z `...`.
#
# W `carparts.py` czekają już: aliasy typów `Values`, `Stats`, `Statistic`, stała `MISSING`, słownik `STATISTICS` oraz sygnatury i docstringi funkcji z zadań 02.2-02.5. Docstring to dokładna umowa funkcji (po angielsku). Opis w notebooku mówi to samo prostszymi słowami.
#
# Pierwsza komórka włącza `autoreload`: po zapisaniu pliku następna uruchomiona komórka widzi nową wersję modułu, bez restartu kernela.
#
# | Zadanie | Krok | Co piszesz | Gdzie | Czas |
# |---|---|---|---|---|
# | 02.1 | 02.1a | sześć funkcji z labu 01, przeniesione bez zmian, z importami | `carparts.py`, w miejscu komentarza `# 02.1` | 30 min |
# | | 02.1b | typy parametrów i wyników tych funkcji, czysty `ruff` i `mypy` | `carparts.py` | 60 min |
# | 02.2 | | dekorator `timed` | `carparts.py` | 45 min |
# | 02.3 | | fabryka dekoratorów `requires_history` | `carparts.py` | 60 min |
# | 02.4 | 02.4a | dekorator `register` | `carparts.py` | 15 min |
# | | 02.4b | sześć statystyk w rejestrze | `carparts.py`, w miejscu komentarza `# 02.4` | 30 min |
# | | 02.4c | `summarise` | `carparts.py` | 15 min |
# | | 02.4d | zmienne `stats`, `with_cv2` | notebook | 15 min |
# | 02.5 | 02.5a | `at_least` | `carparts.py` | 20 min |
# | | 02.5b | `select` | `carparts.py` | 15 min |
# | | 02.5c | zmienna `steady` | notebook | 10 min |
# | 02.6 | | eksploracja: statystyka `peak`, zmienne `peaks`, `spiky`, dwie odpowiedzi tekstem | notebook | 45 min |

# %% [markdown]
# Pierwsza komórka importuje Twój moduł jako `carparts`. Funkcje z niego wołasz z przedrostkiem: `carparts.read_series(PATH)`. `PATH` to ta sama ścieżka do pliku z danymi co w labie 01.

# %%
# %load_ext autoreload
# %autoreload 2

import carparts

from coursekit import paths
from coursekit.nb import check

PATH = paths.CAR_PARTS

# %% [markdown]
# ## 02.1 Moduł z typami
#
# **Cel.** Funkcje z labu 01 mają żyć w jednym pliku, który da się zaimportować i sprawdzić narzędziami. Typy mówią czytelnikowi i mypy, co każda funkcja przyjmuje i zwraca. Każdy kolejny lab zakłada, że kod przechodzi `ruff` i `mypy --strict` (reguła K1 i K9 w `docs/standard.md`).
#
# Zadanie ma dwa kroki: 02.1a przenosi funkcje bez zmian, 02.1b dodaje typy. Sprawdzenie `check("02.1", carparts)` przejdzie dopiero po obu.
#
# ### 02.1a Przeniesienie
#
# **Gdzie.** `carparts.py`, w miejscu komentarza `# 02.1: paste your six functions from lab 01 here...`, między aliasami typów a funkcją `timed`. Komentarz usuń.
#
# **Wejście.** Twoje funkcje z notebooka `labs/01-python-data/01-python-data.ipynb`. Każdą kopiujesz w całości: linię `def`, docstring i ciało.
#
# | Funkcja z labu 01 | Zadanie w labie 01 | Czego potrzebuje w `carparts.py` |
# |---|---|---|
# | `parse_value` | 01.1 | stałej `MISSING`: już jest na górze pliku, nie kopiuj jej drugi raz |
# | `parse_series_line` | 01.2 | `parse_value` |
# | `read_series` | 01.3a | `parse_series_line`, `Path` z `pathlib` |
# | `demand_stats` | 01.4a | niczego |
# | `top_series` | 01.5 | niczego |
# | `save_summary` | 01.6 | `json`, `Path` |
#
# Nie kopiuj komórek z `check(...)`, zmiennych z eksploracji (`series`, `stats`, ...) ani `PATH`. W module stoją tylko definicje i stałe (wykład 02, sekcja "Moduły i importy").
#
# **Wynik.** Plik z sześcioma funkcjami, które działają tak samo jak w labie 01. Importy stoją na górze pliku, w jednym bloku z tymi, które już tam są, w kolejności, której wymaga `ruff check`.
#
# **Skorzystaj z.** `ruff check` w komórce z komendami poniżej. Brakujący import zgłasza jako nieznaną nazwę (`F821 Undefined name`).
#
# **Kroki.**
#
# 1. Skopiuj sześć funkcji w kolejności z tabeli.
# 2. Dopisz na górze pliku importy, których potrzebują: `json` i `Path` z `pathlib`. Kolejności importów pilnuje `ruff check` (reguła `I`), a nie `ruff format`. Import dopisany w złym miejscu daje uwagę `I001 Import block is un-sorted or un-formatted`. Po tym kroku blok importów ma wyglądać tak:
#
#    ```python
#    import json
#    from collections.abc import Callable, Mapping, Sequence
#    from pathlib import Path
#    ```
#
#    Gdy `ruff check` zgłosi `I001`, uruchom w terminalu `uv run ruff check --fix labs/02-functions/carparts.py` (albo w notebooku `!uv run ruff check --fix carparts.py`). Gwiazdka `[*]` przy kodzie uwagi znaczy, że ruff umie ją naprawić sam.
# 3. Uruchom komórkę z komendami. `ruff check` nie ma mieć uwag. Uwagi mypy o brakujących typach są na tym etapie spodziewane.
#
# **Sprawdzenie.** Komórka z `assert` pod komendami nie zgłasza błędu: wczytuje Twoim `carparts.read_series` cały plik.
#
# ### 02.1b Typy
#
# **Gdzie.** Te same sześć funkcji w `carparts.py`: ich linie `def`.
#
# **Wejście.** Co przyjmują i zwracają, mówią docstringi, które przeniosłeś. Twoje zadanie to zapisać to samo adnotacjami. Pomocne nazwy:
#
# - `Values`: alias na górze pliku. Sekwencja tylko do odczytu (lista albo krotka) wartości jednej serii, każda `float` albo `None`. To typ `values` w `demand_stats`.
# - `Stats`: alias. Słownik statystyk jednej serii: nazwa statystyki (`str`) → wartość (`float` albo `None`). To wynik `demand_stats`.
# - `Mapping`, `Sequence`, `Iterator` z `collections.abc` (wykład 02, sekcja "Typy", tabela zapisów). `Mapping` i `Sequence` są już zaimportowane. `Iterator` dopisz do tej samej linii, w kolejności alfabetycznej: `from collections.abc import Callable, Iterator, Mapping, Sequence`. Nie dodawaj drugiej linii `from collections.abc import ...`, bo `ruff check` zgłosi `I001`.
#
# **Wynik.** Każdy parametr i każdy wynik sześciu funkcji ma adnotację. Zasada z wykładu: parametry typujesz szeroko (czego funkcja potrzebuje), wynik wąsko (co dokładnie zwraca).
#
# Co się zmienia poza sygnaturami:
#
# - **Docstringi.** Zostają, bo sprawdzenie wymaga docstringu w każdej z sześciu funkcji. Opisują typy słowami. Jeśli adnotacja jest szersza niż te słowa, popraw słowa. Przykład: gdy `values` w `demand_stats` dostaje typ `Values`, napisz "a sequence (list or tuple)" zamiast "a list".
# - **Ciało `top_series`.** Może wymagać drobnej zmiany, bo mypy nie zawęża typu wyrażenia `s[key]` liczonego drugi raz (wykład 02, sekcja "Typy", część "Zawężanie"). Zachowanie funkcji ma zostać takie samo.
# - Ciała pozostałych pięciu funkcji zwykle zostają bez zmian.
#
# **Skorzystaj z.** Wykładu 02, sekcja "Typy": tabela zapisów, aliasy typów i zawężanie.
#
# **Kroki.**
#
# 1. Dopisz typy po kolei, od `parse_value` do `save_summary`. Po każdej funkcji uruchom komórkę z komendami.
# 2. Czytaj komunikaty mypy od góry: pierwszy błąd często wywołuje kolejne.
# 3. Na koniec komórka nie pokazuje żadnej uwagi `ruff check` ani `mypy`.
#
# **Sprawdzenie.** `check("02.1", carparts)` wypisuje ✅. Uruchamia na Twoich funkcjach te same sprawdzenia co w labie 01, potem sprawdza, że każda funkcja ma typy i docstring, a na końcu uruchamia `ruff check`, `ruff format --check` i `mypy --strict` na całym pliku. Trwa kilka sekund.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Typ parametru opisuje, co funkcja przyjmuje, a nie co dziś do niej wkładasz. `read_series` przyjmie i `str`, i `Path`, więc `str | Path`. `demand_stats` tylko czyta wartości, więc wystarczy jej `Sequence`, nie `list`. Generator zwraca `Iterator[...]`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Zacznij od `ruff check`, bo jego uwagi są proste (zwykle brakujący albo zbędny import). Potem mypy. Jeśli mypy mówi o `float | None` tam, gdzie spodziewasz się `float`, zobacz, czy sprawdzenie `is not None` dotyczy tej samej zmiennej, której potem używasz. mypy zawęża typ zmiennej, ale nie wyrażenia `row[key]` wyliczanego drugi raz.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# Sygnatury:
#
# ```python
# def parse_value(text: str) -> float | None:
# def parse_series_line(line: str) -> tuple[str, str, list[float | None]]:
# def read_series(path: str | Path) -> Iterator[tuple[str, str, list[float | None]]]:
# def demand_stats(values: Values) -> Stats:
# def top_series(stats: Mapping[str, Stats], key: str, n: int) -> list[tuple[str, float]]:
# def save_summary(stats: Mapping[str, Stats], path: str | Path) -> Path:
# ```
#
# W `top_series` zapamiętaj wartość w zmiennej, żeby mypy widział zawężenie: `if (value := row.get(key)) is not None`.
#
# </details>
#
# Komórka poniżej najpierw formatuje plik (`ruff format`), potem go sprawdza. Uruchamiaj ją po każdej zmianie. Działa w katalogu notebooka, dlatego wystarcza sama nazwa `carparts.py`. W terminalu otwartym w katalogu repozytorium podajesz ścieżkę `labs/02-functions/carparts.py`.

# %%
# !uv run ruff format carparts.py
# !uv run ruff check carparts.py
# !uv run mypy --strict carparts.py

# %% [markdown]
# Ta komórka potwierdza krok 02.1a: przeniesione funkcje czytają cały plik i liczą statystyki.

# %%
_rows = list(carparts.read_series(PATH))
assert len(_rows) == 2674, "read_series z carparts.py ma oddać 2 674 serie."
assert carparts.demand_stats([0.0, 2.0, None, 0.0, 6.0])["adi"] == 2.0

# %%
check("02.1", carparts)

# %% [markdown]
# ## 02.2 Ile to trwa: `timed`
#
# **Cel.** Zanim przyspieszysz kod, musisz wiedzieć, która część trwa długo. Dekorator `timed` mierzy czas każdego wywołania dowolnej funkcji, bez zmieniania jej kodu.
#
# **Gdzie.** Funkcja `timed` w `carparts.py`, w miejscu `raise NotImplementedError("Zadanie 02.2")`. Sygnatura i docstring są gotowe.
#
# **Wejście.** `func`: dowolna funkcja. Typ `Callable[P, R]` mówi: funkcja z jakimiś argumentami `P`, zwracająca coś typu `R`.
#
# **Wynik.** Nowa funkcja (`Callable[P, R]`), która:
#
# - przyjmuje te same argumenty co `func` i zwraca to samo,
# - ma nazwę i docstring `func`,
# - po każdym wywołaniu wypisuje jedną linię `nazwa_funkcji: 0.123 s`: nazwa, dwukropek, czas wywołania w sekundach z trzema miejscami po przecinku, spacja, `s`,
# - wypisuje tę linię także wtedy, gdy `func` zgłosi wyjątek. Sam wyjątek leci dalej, do wywołującego.
#
# Sygnatura z `[**P, R]` jest już w pliku. Mówi mypy: "opakowana funkcja przyjmuje te same argumenty i zwraca to samo co oryginał". Bez niej każda udekorowana funkcja traciłaby typy.
#
# **Skorzystaj z.** Wykład 02, sekcja "Dekoratory": kształt dekoratora z `functools.wraps` i część "Typ dekoratora". Zegar do mierzenia odcinków czasu to `time.perf_counter()`, a kod, który ma się wykonać także przy wyjątku, stawiasz w `finally` (ta sama sekcja wykładu, część "Kod, który działa zawsze"). Dopisz importy `functools` i `time` na górze pliku. Po tym zadaniu cały blok importów wygląda tak (kolejność poprawi też `ruff check --fix`, jak w 02.1a):
#
# ```python
# import functools
# import json
# import time
# from collections.abc import Callable, Iterator, Mapping, Sequence
# from pathlib import Path
# ```
#
# **Kroki.**
#
# 1. Wewnątrz `timed` zdefiniuj funkcję opakowującą, która przyjmuje `*args, **kwargs` i przekazuje je do `func`.
# 2. Zapamiętaj czas przed wywołaniem `func`.
# 3. Wywołaj `func` i zwróć jej wynik. Wypisanie linii z czasem umieść tak, żeby wykonało się także przy wyjątku.
# 4. Opakowanie oznacz `@functools.wraps(func)` i zwróć je z `timed`.
#
# **Sprawdzenie.** `check("02.2", carparts.timed)` wypisuje ✅. Sprawdza wynik, format linii, zachowaną nazwę, czas funkcji, która śpi 0,05 s, i funkcję, która zgłasza wyjątek. Na koniec komórka z komendami z 02.1 nadal nie ma uwag.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Dekorator to funkcja, która dostaje funkcję i zwraca nową funkcję. Czas mierzysz `time.perf_counter()`: przed wywołaniem i po nim.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Wewnątrz `timed` zdefiniuj `wrapper(*args, **kwargs)`, który wywołuje `func(*args, **kwargs)`. Wypisanie czasu włóż do `finally`, a nad `wrapper` postaw `@functools.wraps(func)`, żeby zachować nazwę i docstring.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# @functools.wraps(func)
# def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
#     start = time.perf_counter()
#     try:
#         return func(*args, **kwargs)
#     finally:
#         ...
# return wrapper
# ```
#
# </details>

# %%
check("02.2", carparts.timed)

# %% [markdown]
# Zmierz, ile trwa wczytanie całego pliku. Najpierw tak:

# %%
series_iterator = carparts.timed(carparts.read_series)(PATH)

# %% [markdown]
# A teraz przez funkcję, która zbiera wynik do słownika. `series` to ten sam słownik co w labie 01: nazwa serii → lista wartości. Użyjesz go w 02.4d i 02.6.

# %%
@carparts.timed
def load_all(path):
    """Read every series of a .tsf file into a dict: name -> values."""
    return {name: values for name, _start, values in carparts.read_series(path)}


series = load_all(PATH)
print(len(series), "serii")

# %% [markdown]
# **Pytanie.** Pierwszy pomiar pokazał prawie zero. Co właściwie zmierzył? Dlaczego drugi jest dłuższy? Wskazówka: co zwraca wywołanie generatora (wykład 01, sekcja "Iteracja i generatory")?
#
# *Twoja odpowiedź:*

# %% [markdown]
# ## 02.3 Za krótka historia: `requires_history`
#
# **Cel.** Niektórych statystyk nie warto liczyć dla serii, która ma mało danych. Zmienność policzona z trzech miesięcy więcej mówi o przypadku niż o produkcie. Zamiast powtarzać ten warunek w każdej statystyce, piszesz go raz, jako dekorator z parametrem.
#
# **Gdzie.** Funkcja `requires_history` w `carparts.py`, w miejscu `raise NotImplementedError("Zadanie 02.3")`.
#
# **Wejście.** `min_months`: liczba całkowita (`int`), najmniejsza liczba znanych miesięcy, przy której statystyka ma sens. Znany miesiąc to wartość różna od `None`. Zero też jest znanym miesiącem.
#
# **Wynik.** Dekorator (`Callable[[Statistic], Statistic]`). `Statistic` to alias z góry pliku: funkcja, która dostaje wartości jednej serii (`Values`) i zwraca `float | None`. Dekorator opakowuje statystykę tak, że:
#
# - dla serii z mniej niż `min_months` znanymi miesiącami zwraca `None` i w ogóle nie wywołuje statystyki,
# - dla pozostałych zwraca wynik statystyki,
# - opakowana statystyka ma nazwę i docstring oryginału.
#
# Błąd: `min_months` mniejsze od 1 to `ValueError`. `requires_history(0)` to błąd programisty, więc `ValueError` ma polecieć od razu, już przy wywołaniu `requires_history(0)`, zanim dekorator dostanie jakąkolwiek statystykę. Nie przy pierwszym liczeniu statystyki gdzieś w środku przeliczenia.
#
# **Skorzystaj z.** Wykład 02, sekcja "Dekoratory", część "Dekorator z parametrem": fabryka `repeat` ma ten sam kształt trzech poziomów. Liczenie znanych miesięcy znasz z `demand_stats`.
#
# **Kroki.**
#
# 1. Na początku `requires_history` sprawdź `min_months` i zgłoś `ValueError` z wartością w komunikacie.
# 2. Zdefiniuj `decorator(statistic)`, a w nim opakowanie `wrapper(values)` z `@functools.wraps(statistic)`.
# 3. W opakowaniu policz znane miesiące. Za mało: zwróć `None`. Dosyć: zwróć `statistic(values)`.
# 4. Zwróć opakowanie z `decorator`, a `decorator` z `requires_history`.
#
# **Sprawdzenie.** `check("02.3", carparts.requires_history)` wypisuje ✅. Sprawdza `requires_history(0)`, serię z dwoma i serię z trzema znanymi miesiącami (z zerem w środku) oraz zachowaną nazwę.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Trzy poziomy funkcji: `requires_history(min_months)` zwraca `decorator(statistic)`, który zwraca `wrapper(values)`. `wrapper` widzi `min_months` dzięki domknięciu.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Walidacja `min_months` stoi w najbardziej zewnętrznej funkcji, przed definicją `decorator`. W `wrapper` policz znane miesiące. Zero to znany miesiąc: `is not None`, nie prawdziwość.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# if min_months < 1:
#     raise ValueError(...)
#
# def decorator(statistic: Statistic) -> Statistic:
#     @functools.wraps(statistic)
#     def wrapper(values: Values) -> float | None:
#         known = ...
#         return None if known < min_months else statistic(values)
#     return wrapper
#
# return decorator
# ```
#
# </details>

# %%
check("02.3", carparts.requires_history)

# %% [markdown]
# ## 02.4 Rejestr statystyk
#
# **Cel.** `demand_stats` liczy pięć statystyk w jednej funkcji. Każda nowa statystyka to zmiana w środku tej funkcji i ryzyko, że zepsujesz pozostałe. Rejestr odwraca to: każda statystyka to osobna mała funkcja, która sama się zapisuje do słownika `STATISTICS`, a `summarise` liczy wszystko, co w nim jest.
#
# Zadanie ma cztery kroki: 02.4a `register`, 02.4b sześć statystyk, 02.4c `summarise`, 02.4d użycie w notebooku. `demand_stats` z 02.1 zostaje w pliku bez zmian.
#
# ### 02.4a `register`
#
# **Gdzie.** Funkcja `register` w `carparts.py`, w miejscu `raise NotImplementedError("Zadanie 02.4")`.
#
# **Wejście.** `name`: napis (`str`), nazwa, pod którą statystyka trafi do `STATISTICS` i do wyniku `summarise`, np. `"total"`.
#
# **Wynik.** Dekorator. Dostaje statystykę, zapisuje ją w `STATISTICS[name]` i zwraca **tę samą** funkcję, bez opakowania. Gdy w `STATISTICS` jest już coś pod tą nazwą: `ValueError`.
#
# **Skorzystaj z.** Kształtu fabryki z 02.3. Słownik `STATISTICS` jest już w pliku, nad `register`.
#
# ### 02.4b Sześć statystyk
#
# **Gdzie.** `carparts.py`, w miejscu komentarza `# 02.4: register the statistics here...`, między `register` a `summarise`.
#
# **Wejście.** Każda statystyka to osobna funkcja z jednym parametrem `values: Values` (wartości jednej serii) i wynikiem `float | None`, z docstringiem. Nazwę funkcji wybierasz sam. Nazwa w rejestrze musi być dokładnie taka jak w tabeli.
#
# **Wynik.** Sześć funkcji, każda oznaczona `@register("nazwa")`:
#
# | Nazwa w rejestrze | Co zwraca | Kiedy `None` |
# |---|---|---|
# | `"months"` | liczba znanych miesięcy | nigdy |
# | `"missing"` | liczba miesięcy z brakiem | nigdy |
# | `"total"` | suma znanych wartości | nigdy |
# | `"zero_share"` | udział zer wśród znanych miesięcy, od 0 do 1 | brak znanych miesięcy |
# | `"adi"` | znane miesiące podzielone przez miesiące z popytem większym od zera | brak popytu |
# | `"cv2"` | zmienność wielkości sprzedaży, opis niżej | mniej niż 12 znanych miesięcy albo mniej niż 2 miesiące z popytem |
#
# Pierwsze pięć daje te same liczby co odpowiednie pola `demand_stats`. Kolejność rejestracji to kolejność kluczy w wyniku `summarise`.
#
# **`cv2`** to kwadrat współczynnika zmienności niezerowych sprzedaży. Mówi, jak bardzo różnią się wielkości zamówień: 0 znaczy, że w każdym miesiącu z popytem sprzedano tyle samo sztuk. Liczysz ją tak:
#
# 1. Weź **wielkości popytu**: znane wartości większe od zera. Miesiące z zerem i braki pomijasz.
# 2. **Średnia**: suma wielkości podzielona przez ich liczbę.
# 3. **Wariancja** (variance, miara rozrzutu): dla każdej wielkości odległość od średniej, podniesiona do kwadratu, potem średnia tych kwadratów. To wariancja populacyjna: dzielisz przez liczbę wielkości, nie przez liczbę mniejszą o jeden.
# 4. **`cv2`** = wariancja podzielona przez kwadrat średniej.
#
# Wynik to jedna liczba albo `None`, jak w każdej statystyce. `None` daje seria z mniej niż 12 znanymi miesiącami (użyj `requires_history`) albo z mniej niż dwoma miesiącami z popytem.
#
# Przykład `cv2`: dla `[0, 2, 0, 4]` powtórzonego 3 razy (12 miesięcy) wielkości popytu to 2 i 4, średnia 3, wariancja 1, więc `cv2` to 1/9.
#
# **Skorzystaj z.** `register` z 02.4a, `requires_history` z 02.3, logiki `demand_stats` z labu 01. Kolejność dwóch dekoratorów nad `cv2` ma znaczenie (wykład 02, sekcja "Dekoratory": nakładają się od dołu).
#
# **Sprawdzenie.** Komórka z `assert` pod opisem 02.4c nie zgłasza błędu.
#
# ### 02.4c `summarise`
#
# **Gdzie.** Funkcja `summarise` w `carparts.py`, w miejscu `raise NotImplementedError("Zadanie 02.4")`.
#
# **Wejście.**
#
# - `values: Values`: wartości jednej serii.
# - `names: Sequence[str] | None`: nazwy statystyk z rejestru, które chcesz policzyć, w wybranej kolejności. Domyślnie `None`, czyli wszystkie z `STATISTICS`, w kolejności rejestracji.
#
# **Wynik.** Słownik `Stats`: nazwa statystyki → jej wynik dla tej serii, klucze w kolejności `names`. Nazwa, której nie ma w `STATISTICS`, to `ValueError`, którego komunikat wymienia znane nazwy.
#
# Przykład: `summarise([0.0, 2.0, None, 0.0, 6.0])` daje `{"months": 4, "missing": 1, "total": 8.0, "zero_share": 0.5, "adi": 2.0, "cv2": None}`. `cv2` to `None`, bo seria ma tylko 4 znane miesiące.
#
# **Kroki (02.4a-02.4c).**
#
# 1. `register`: fabryka, której dekorator sprawdza nazwę, zapisuje funkcję w słowniku i ją zwraca.
# 2. Pięć prostych statystyk, każda w kilku liniach.
# 3. `cv2`: najpierw wielkości popytu (znane wartości większe od zera), potem średnia, wariancja i wynik. Nad funkcją dwa dekoratory w dobrej kolejności.
# 4. `summarise`: ustal listę nazw, sprawdź nieznane, zbuduj słownik wyników dict comprehension.
#
# **Sprawdzenie.** `check("02.4", carparts)` wypisuje ✅. Sprawdza `register` (także drugą rejestrację pod tą samą nazwą), obecność sześciu nazw, `cv2` na 12 i na 11 miesiącach oraz `summarise` z przykładu, z jedną nazwą i z nieznaną nazwą. Komórka z komendami z 02.1 nadal nie ma uwag.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `register` ma ten sam kształt co `requires_history`: fabryka, która zwraca dekorator. Tym razem dekorator niczego nie opakowuje, tylko zapisuje funkcję w słowniku i ją oddaje.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Dekoratory nakładają się od dołu. Nad `cv2` stoją dwa: ten bliżej `def` działa pierwszy. Zastanów się, którą wersję funkcji ma zobaczyć rejestr: gołą czy już zabezpieczoną przez `requires_history`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# def register(name: str) -> Callable[[Statistic], Statistic]:
#     def decorator(statistic: Statistic) -> Statistic:
#         if name in STATISTICS:
#             raise ValueError(...)
#         STATISTICS[name] = statistic
#         return statistic
#     return decorator
#
#
# @register("cv2")
# @requires_history(12)
# def cv2(values: Values) -> float | None:
#     sizes = [...]
#     ...
# ```
#
# </details>

# %% [markdown]
# Ta komórka potwierdza krok 02.4b: sześć nazw jest w rejestrze, a statystyki dają te same liczby co `demand_stats`.

# %%
_sample = [0.0, 2.0, None, 0.0, 6.0]
_names = ["months", "missing", "total", "zero_share", "adi", "cv2"]
assert set(_names) <= set(carparts.STATISTICS), "W STATISTICS brakuje którejś z sześciu nazw."
assert [carparts.STATISTICS[_n](_sample) for _n in _names] == [4, 1, 8.0, 0.5, 2.0, None]

# %%
check("02.4", carparts)

# %% [markdown]
# ### 02.4d Rejestr na prawdziwych danych
#
# Policz `summarise` dla wszystkich serii. Dla ilu serii `cv2` jest znane?
#
# **Gdzie.** Zmienne `stats` i `with_cv2` w komórce poniżej.
#
# **Wynik.**
#
# - `stats`: słownik nazwa serii → wynik `carparts.summarise` dla jej wartości, czyli słownik sześciu statystyk. Ten sam kształt co `stats` w labie 01, z dodatkowym kluczem `cv2`.
# - `with_cv2`: lista nazw serii (napisów), dla których `cv2` nie jest `None`.
#
# **Skorzystaj z.** Słownika `series` z komórki z `load_all` (02.2) i dict comprehension.

# %%
# >>> SOLUTION 02.4
stats = {name: carparts.summarise(values) for name, values in series.items()}
with_cv2 = [name for name, row in stats.items() if row["cv2"] is not None]
# --- STUB
#| stats = ...
#| with_cv2 = ...
# <<< SOLUTION
print(f"cv2 znane dla {len(with_cv2)} z {len(stats)} serii")

# %% [markdown]
# ## 02.5 Filtry jako funkcje: `at_least` i `select`
#
# **Cel.** Pytania typu "które serie mają pełną historię i sprzedały co najmniej 60 sztuk" zadasz w tym kursie wiele razy. Zamiast pisać za każdym razem nową pętlę z warunkami, budujesz małe testy i jedną funkcję, która je łączy.
#
# ### 02.5a `at_least`
#
# **Gdzie.** Funkcja `at_least` w `carparts.py`, w miejscu `raise NotImplementedError("Zadanie 02.5")`.
#
# **Wejście.**
#
# - `key`: napis, nazwa statystyki, np. `"total"`.
# - `threshold`: liczba (`float`, liczba całkowita też pasuje), najmniejsza wartość, która przechodzi.
#
# **Wynik.** **Test**: funkcja (`Callable[[Stats], bool]`). "Test" znaczy tu warunek do filtrowania, a nie sprawdzenie `check`. Ta funkcja dostaje słownik statystyk jednej serii (`Stats`, jak jeden wpis `stats` z 02.4d) i zwraca `True`, gdy wartość `key` jest w słowniku, nie jest `None` i jest nie mniejsza niż `threshold`. W każdym innym przypadku `False`, także gdy klucza brak.
#
# **Skorzystaj z.** Wykład 02, sekcja "Domknięcia": wewnętrzna funkcja pamięta `key` i `threshold`. Ćwiczenie `between` z tego wykładu ma ten sam kształt.
#
# ### 02.5b `select`
#
# **Gdzie.** Funkcja `select` w `carparts.py`, w miejscu `raise NotImplementedError("Zadanie 02.5")`.
#
# **Wejście.**
#
# - `stats`: słownik nazwa serii → `Stats`, jak `stats` z 02.4d. Nie zmieniasz go.
# - `*tests`: dowolna liczba testów, np. z `at_least`, podanych po przecinku: `select(stats, test_1, test_2)`.
#
# **Wynik.** Lista nazw serii (`list[str]`), dla których każdy test zwraca `True`, posortowana rosnąco. Bez testów: wszystkie nazwy, posortowane.
#
# **Skorzystaj z.** Wykład 02, sekcja "Sygnatura to umowa": `*args` zbiera argumenty pozycyjne w krotkę.
#
# **Kroki (02.5a-02.5b).**
#
# 1. W `at_least` zdefiniuj wewnętrzną funkcję z jednym parametrem `stats: Stats`. Odczytaj wartość tak, żeby brak klucza nie zgłaszał `KeyError`, i porównaj z progiem.
# 2. Zwróć tę funkcję.
# 3. W `select` przejdź po seriach, zostaw te, które przechodzą wszystkie testy, i posortuj nazwy.
#
# **Sprawdzenie.** `check("02.5", carparts)` wypisuje ✅. Sprawdza progi, brak klucza i `None`, `select` bez testów i z dwoma testami.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `at_least` to znowu domknięcie: wewnętrzna funkcja pamięta `key` i `threshold`. `*tests` zbiera dowolną liczbę argumentów pozycyjnych w krotkę.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# W teście użyj `stats.get(key)`, żeby brakujący klucz nie rzucał `KeyError`. W `select` funkcja `all(...)` na pustej krotce testów daje `True`, więc przypadek "bez testów" nie wymaga osobnego kodu.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# def passes(stats: Stats) -> bool:
#     value = stats.get(key)
#     return value is not None and value >= threshold
#
# return sorted(name for name, row in stats.items() if all(test(row) for test in tests))
# ```
#
# </details>

# %%
check("02.5", carparts)

# %% [markdown]
# ### 02.5c Wybór serii
#
# Które serie mają pełną historię i sprzedały co najmniej 60 sztuk? Każda seria w pliku ma 51 miesięcy, więc pełna historia to co najmniej 51 znanych miesięcy: próg 51 w `at_least` przepuszcza dokładnie serie bez braków.
#
# **Gdzie.** Zmienna `steady` w komórce poniżej.
#
# **Wynik.** Posortowana lista nazw serii (napisów), wynik jednego wywołania `carparts.select`.
#
# **Skorzystaj z.** `stats` z 02.4d, `carparts.select` i dwóch testów z `carparts.at_least`, dla statystyk `"months"` i `"total"`.

# %%
# >>> SOLUTION 02.5
steady = carparts.select(stats, carparts.at_least("months", 51), carparts.at_least("total", 60))
# --- STUB
#| steady = ...
# <<< SOLUTION
print(len(steady), steady[:5])

# %% [markdown]
# ## 02.6 Eksploracja
#
# Bez sprawdzeń.
#
# **Pytanie 1.** Dopisz nową statystykę `peak` (największa znana wartość) tu, w notebooku, dekoratorem `@carparts.register("peak")`. Policz ją dla wszystkich serii i wybierz serie z `peak` co najmniej 10.
#
# **Gdzie.** Komórka poniżej: najpierw funkcja `peak` z dekoratorem `@carparts.register("peak")` (napisz ją nad `peaks`, w miejscu komentarza), potem zmienne `peaks` i `spiky`.
#
# **Wynik.**
#
# - `peak(values)`: największa znana wartość serii (`float`), `None`, gdy znanych miesięcy nie ma.
# - `peaks`: słownik nazwa serii → wynik `carparts.summarise` z samą statystyką `"peak"`, czyli słownik z jednym kluczem.
# - `spiky`: posortowana lista nazw serii z `peak` co najmniej 10.
#
# **Skorzystaj z.** `series` z 02.2, `carparts.register`, `carparts.summarise` z argumentem `names`, `carparts.select` i `carparts.at_least`.

# %%
# >>> SOLUTION 02.6
@carparts.register("peak")
def peak(values):
    """Largest known value; None without known months."""
    known = [value for value in values if value is not None]
    return max(known) if known else None


peaks = {name: carparts.summarise(values, ["peak"]) for name, values in series.items()}
spiky = carparts.select(peaks, carparts.at_least("peak", 10))
# --- STUB
#| # tu funkcja peak z dekoratorem @carparts.register("peak")
#|
#| peaks = ...
#| spiky = ...
# <<< SOLUTION
print(len(spiky), "serii z miesiącem, w którym sprzedano 10 sztuk albo więcej")

# %% [markdown]
# Uruchom komórkę z `peak` drugi raz. Co się stało i dlaczego to dobrze, że tak się dzieje? Błąd przy drugim uruchomieniu jest zamierzony. Rejestr pamięta `peak` do restartu kernela, więc przed Restart i Run All nic nie musisz poprawiać.
#
# *Twoja odpowiedź:*
#
# **Pytanie 2.** Żeby dodać statystykę do `demand_stats`, musisz edytować ciało istniejącej, sprawdzonej funkcji. A żeby dodać ją do rejestru? Potem dwie rzeczy, których rejestr nie daje za darmo: od czego zależy kolejność kluczy w wyniku `summarise` i czy kod spoza `carparts.py` może zmienić `STATISTICS` (sam to zrobiłeś w pytaniu 1). Odpowiedź słowna wystarczy.
#
# *Twoja odpowiedź:*
#
# ## Koniec labu
#
# Na koniec uruchom komórkę z komendami z 02.1 jeszcze raz. Cały plik, razem z dekoratorami i rejestrem, ma przejść `ruff check` i `mypy --strict`.
#
# W module 03 statystyki `adi` i `cv2` posłużą do podziału serii na typy popytu, a serie staną się obiektami.
