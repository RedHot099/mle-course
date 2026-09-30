# %% [markdown]
# # Lab 02: z notebooka do typowanego modułu
#
# W labie 01 funkcje żyły w komórkach notebooka. Tak się zaczyna, ale tak się nie pracuje dłużej niż kilka dni: kodu z komórek nie zaimportujesz w innym notebooku, nie sprawdzi go mypy, trudno go przejrzeć w pull requeście.
#
# W tym labie przenosisz funkcje z labu 01 do modułu `carparts.py`, dajesz im typy i doprowadzasz do tego, że `ruff` i `mypy --strict` nie mają uwag. Potem dopisujesz do modułu dwa dekoratory i rejestr statystyk, który zastąpi jedną dużą funkcję `demand_stats` zestawem małych.
#
# **Czas:** około 6 godzin.
#
# ## Jak pracujesz
#
# Kod piszesz w pliku `carparts.py` obok tego notebooka. Otwórz go w edytorze obok notebooka. Notebook tylko importuje moduł, sprawdza go i używa na danych.
#
# Pierwsza komórka włącza `autoreload`: po zapisaniu pliku następna uruchomiona komórka widzi nową wersję modułu, bez restartu kernela.
#
# | Zadanie | Co piszesz w `carparts.py` | Czas |
# |---|---|---|
# | 02.1 | Funkcje z labu 01 z typami | 90 min |
# | 02.2 | `timed` | 45 min |
# | 02.3 | `requires_history` | 60 min |
# | 02.4 | `register`, statystyki, `summarise` | 75 min |
# | 02.5 | `at_least`, `select` | 45 min |
# | 02.6 | Eksploracja w notebooku | 45 min |

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
# Przenieś do `carparts.py` sześć funkcji z labu 01: `parse_value`, `parse_series_line`, `read_series`, `demand_stats`, `top_series`, `save_summary`. Wklej je w miejsce komentarza `# 02.1` i dopisz importy, których potrzebują.
#
# Potem daj każdej funkcji:
#
# - typy wszystkich parametrów i wyniku,
# - docstring w jednym zdaniu, mówiący co funkcja zwraca.
#
# Na górze pliku czekają aliasy typów `Values` i `Stats`. Użyj ich: `demand_stats(values: Values) -> Stats` czyta się lepiej niż rozpisany typ.
#
# Komórka poniżej najpierw formatuje plik (`ruff format`), potem go sprawdza. Zadanie jest zrobione, gdy `ruff check` i `mypy` nie mają uwag. Uruchamiaj je po każdej zmianie. Komunikaty mypy czytaj od góry: pierwszy błąd często wywołuje kolejne.
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

# %%
# !uv run ruff format carparts.py
# !uv run ruff check carparts.py
# !uv run mypy --strict carparts.py

# %%
check("02.1", carparts)

# %% [markdown]
# ## 02.2 Ile to trwa: `timed`
#
# Napisz dekorator `timed`. Opakowana funkcja działa jak oryginał, a po każdym wywołaniu wypisuje linię `nazwa_funkcji: 0.123 s`. Linia ma się pojawić także wtedy, gdy funkcja rzuci wyjątek, a sam wyjątek ma polecieć dalej.
#
# Sygnatura z `[**P, R]` jest już w pliku. Mówi mypy: "opakowana funkcja przyjmuje te same argumenty i zwraca to samo co oryginał". Bez niej każda udekorowana funkcja traciłaby typy.
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
# A teraz przez funkcję, która zbiera wynik do słownika:

# %%
@carparts.timed
def load_all(path):
    """Read every series of a .tsf file into a dict: name -> values."""
    return {name: values for name, _start, values in carparts.read_series(path)}


series = load_all(PATH)
print(len(series), "serii")

# %% [markdown]
# **Pytanie.** Pierwszy pomiar pokazał prawie zero. Co właściwie zmierzył? Dlaczego drugi jest dłuższy?
#
# *Twoja odpowiedź:*

# %% [markdown]
# ## 02.3 Za krótka historia: `requires_history`
#
# Niektórych statystyk nie warto liczyć dla serii, która ma mało danych. Zmienność policzona z trzech miesięcy więcej mówi o przypadku niż o produkcie.
#
# Napisz **fabrykę dekoratorów** `requires_history(min_months)`. Zwraca dekorator, a ten opakowuje statystykę tak, że dla serii z mniej niż `min_months` znanymi miesiącami zwraca `None`, bez wywoływania statystyki.
#
# `requires_history(0)` to błąd programisty, więc `ValueError` ma polecieć od razu, przy nakładaniu dekoratora, a nie przy pierwszym wywołaniu gdzieś w środku przeliczenia.
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
# `demand_stats` liczy pięć statystyk w jednej funkcji. Każda nowa statystyka to zmiana w środku tej funkcji i ryzyko, że zepsujesz pozostałe.
#
# Zbuduj rejestr:
#
# 1. `register(name)`: dekorator, który dopisuje funkcję do słownika `STATISTICS` pod nazwą `name` i zwraca ją bez zmian. Druga funkcja pod tą samą nazwą to `ValueError`.
# 2. Sześć małych statystyk, każda z `@register(...)`: `months`, `missing`, `total`, `zero_share`, `adi` (znaczenia jak w `demand_stats`) oraz `cv2`.
# 3. `summarise(values, names=None)`: słownik z wynikami wskazanych statystyk albo wszystkich, gdy `names` jest `None`. Nieznana nazwa to `ValueError`, który wymienia znane nazwy.
#
# **`cv2`** to kwadrat współczynnika zmienności niezerowych sprzedaży: wariancja podzielona przez kwadrat średniej, liczone tylko z miesięcy z popytem większym od zera. Mówi, jak bardzo różnią się wielkości zamówień. Liczysz ją dla serii z co najmniej 12 znanymi miesiącami (użyj `requires_history`) i co najmniej dwoma miesiącami z popytem, inaczej `None`. Wariancja populacyjna: dzielisz przez liczbę elementów.
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

# %%
check("02.4", carparts)

# %% [markdown]
# Policz `summarise` dla wszystkich serii. Dla ilu serii `cv2` jest znane?

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
# Napisz dwie funkcje:
#
# - `at_least(key, threshold)` zwraca **test**: funkcję, która dla słownika statystyk jednej serii mówi, czy wartość `key` jest znana i nie mniejsza niż `threshold`,
# - `select(stats, *tests)` zwraca posortowane nazwy serii, które przechodzą wszystkie testy. Bez testów zwraca wszystkie nazwy.
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
# Które serie mają pełną historię (51 znanych miesięcy) i sprzedały co najmniej 60 sztuk?

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
#| peaks = ...
#| spiky = ...
# <<< SOLUTION
print(len(spiky), "serii z miesiącem, w którym sprzedano 10 sztuk albo więcej")

# %% [markdown]
# Uruchom komórkę z `peak` drugi raz. Co się stało i dlaczego to dobrze, że tak się dzieje?
#
# *Twoja odpowiedź:*
#
# **Pytanie 2.** Ile miejsc w kodzie zmieniasz, żeby dodać statystykę do `demand_stats`, a ile, żeby dodać ją do rejestru? Czego rejestr nie daje za darmo? Pomyśl o kolejności wyników i o tym, kto widzi słownik `STATISTICS`.
#
# *Twoja odpowiedź:*
#
# ## Koniec labu
#
# Na koniec uruchom komórkę z komendami z 02.1 jeszcze raz. Cały plik, razem z dekoratorami i rejestrem, ma przejść `ruff check` i `mypy --strict`.
#
# W module 03 statystyki `adi` i `cv2` posłużą do podziału serii na typy popytu, a serie staną się obiektami.
