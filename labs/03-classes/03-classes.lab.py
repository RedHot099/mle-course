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
# Tak jak w labie 02: kod piszesz w `demand.py`, notebook go importuje i sprawdza. Funkcja `read_tsf` jest w pliku gotowa, bo parser pisałeś już dwa razy.
#
# | Zadanie | Co piszesz w `demand.py` | Czas |
# |---|---|---|
# | 03.1 | `DemandSeries` | 75 min |
# | 03.2 | `DemandType`, `classify` | 45 min |
# | 03.3 | `LocalForecaster`, `NaiveForecaster` | 60 min |
# | 03.4 | `SeasonalNaiveForecaster`, `MovingAverageForecaster` | 45 min |
# | 03.5 | `Forecaster`, `mae`, `evaluate` | 60 min |
# | 03.6 | Eksploracja w notebooku | 45 min |

# %%
# %load_ext autoreload
# %autoreload 2

from collections import Counter

import demand

from coursekit import paths
from coursekit.nb import check

PATH = paths.CAR_PARTS

# %% [markdown]
# ## 03.1 `DemandSeries`
#
# Napisz klasę `DemandSeries` jako **zamrożony dataclass** (`@dataclass(frozen=True)`) z polami, w tej kolejności:
#
# | Pole | Typ | Znaczenie |
# |---|---|---|
# | `name` | `str` | nazwa serii |
# | `start` | `date` | pierwszy miesiąc |
# | `values` | `tuple[float \| None, ...]` | wartości od najstarszej, `None` to brak |
#
# Do tego:
#
# - `__post_init__`: `ValueError`, gdy `values` jest puste albo ma wartość ujemną,
# - `from_record(record)`: **metoda klasy**, która robi serię z krotki `(nazwa, "YYYY-MM-DD", wartości)` zwracanej przez `read_tsf`,
# - **właściwości** (`@property`): `known` (lista znanych wartości), `is_complete` (czy nie ma braków), `adi` i `cv2` (jak w labie 02, `None`, gdy nie da się policzyć).
#
# Dlaczego `values` to krotka, a nie lista? Zamrożony obiekt, który trzyma listę, dalej da się zmienić przez tę listę, a do tego obiektu z listą nie włożysz do zbioru ani nie użyjesz jako klucza słownika.
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

# %%
check("03.1", demand)

# %% [markdown]
# Wczytaj wszystkie serie jako obiekty. Ile z nich jest kompletnych?

# %%
# >>> SOLUTION 03.1
series = [demand.DemandSeries.from_record(record) for record in demand.read_tsf(PATH)]
complete = [one for one in series if one.is_complete]
# --- STUB
#| series = ...
#| complete = ...
# <<< SOLUTION
print(f"Serie: {len(series)}, kompletne: {len(complete)}")
series[0]

# %% [markdown]
# Zwróć uwagę, jak notebook wyświetlił obiekt: to `__repr__`, który napisał za Ciebie `@dataclass`.

# %% [markdown]
# ## 03.2 Typ popytu: `DemandType` i `classify`
#
# Syntetos i Boylan podzielili popyt na cztery typy według dwóch liczb: jak często jest popyt (ADI) i jak bardzo różnią się jego wielkości (CV²).
#
# | | CV² ≤ 0.49 | CV² > 0.49 |
# |---|---|---|
# | **ADI ≤ 1.32** | smooth: regularny | erratic: regularny, ale nierówny |
# | **ADI > 1.32** | intermittent: rzadki, ale równy | lumpy: rzadki i nierówny |
#
# Napisz:
#
# - `DemandType`: `StrEnum` z członkami `SMOOTH`, `ERRATIC`, `INTERMITTENT`, `LUMPY` i piątym, `INSUFFICIENT`, dla serii, której ADI albo CV² jest `None`. Wartości to nazwy małymi literami (`"smooth"`, ...).
# - `classify(adi, cv2) -> DemandType` z instrukcją `match`. Progi są już w pliku jako stałe `ADI_CUTOFF` i `CV2_CUTOFF`. Wartość równa progowi należy do niższej klasy.
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
# Policz, ile serii jest każdego typu.

# %%
# >>> SOLUTION 03.2
counts = Counter(demand.classify(one.adi, one.cv2) for one in series)
# --- STUB
#| counts = ...
# <<< SOLUTION
for kind, count in counts.most_common():
    print(f"{kind:>13}: {count}")

# %% [markdown]
# ## 03.3 Umowa modelu: `LocalForecaster` i `NaiveForecaster`
#
# Każdy model prognozy będzie używany tak samo: `model.fit(historia).predict(horyzont)`. Tę umowę i jej pilnowanie zapisz raz, w klasie bazowej:
#
# - `LocalForecaster` dziedziczy po `ABC`. W `__init__` ustawia `self._history = None`.
# - `fit(history)` zapamiętuje **kopię** historii jako listę `float` i zwraca `self`. Pusta historia to `ValueError`.
# - `predict(horizon)` rzuca `RuntimeError` przed `fit` i `ValueError` dla horyzontu mniejszego od 1. Potem wywołuje `self._forecast(self._history, horizon)`.
# - `_forecast(history, horizon)` jest **metodą abstrakcyjną**: każda klasa pochodna ją implementuje.
#
# `NaiveForecaster` dziedziczy po `LocalForecaster` i implementuje tylko `_forecast`: powtarza ostatnią wartość.
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
# Oba dziedziczą po `LocalForecaster`:
#
# - `SeasonalNaiveForecaster(season=7)` powtarza ostatni pełny sezon, krok po kroku: dla danych miesięcznych i `season=12` prognoza na styczeń to ostatni styczeń. Horyzont dłuższy niż sezon zawija się. `season` mniejsze od 1 to `ValueError` w konstruktorze, a historia krótsza niż sezon to `ValueError` w `fit`.
# - `MovingAverageForecaster(window=7)` powtarza średnią z ostatnich `window` wartości, a gdy historia jest krótsza, z całej. `window` mniejsze od 1 to `ValueError`.
#
# Domyślne 7 dotyczy danych dziennych, na których te klasy będą pracować od modułu 08. Na danych miesięcznych podajesz parametr jawnie.
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
# Napisz:
#
# - `Forecaster`: `Protocol` z metodami `fit(history) -> Self` i `predict(horizon) -> list[float]`. Opisuje, co model **umie**, a nie po czym dziedziczy. Każda klasa z tymi dwiema metodami pasuje, nawet jeśli nigdy nie słyszała o `LocalForecaster`.
# - `mae(actual, forecast)`: średni błąd bezwzględny. Różne długości albo puste ciągi to `ValueError`.
# - `evaluate(make_model, series, holdout=6)`: dla każdej kompletnej serii dłuższej niż `holdout` bierze nowy model z `make_model()`, uczy go na wszystkim oprócz ostatnich `holdout` miesięcy i liczy MAE prognozy na tych miesiącach. Zwraca średnią MAE po seriach. Gdy żadna seria się nie nadaje, `ValueError`.
#
# `make_model` to funkcja bez argumentów, która zwraca nowy model. Klasa też jest taką funkcją: `evaluate(demand.NaiveForecaster, series)` działa. Model z parametrem przekażesz przez `lambda: demand.SeasonalNaiveForecaster(season=12)`.
#
# Sprawdzenie 03.5 uruchamia też `ruff check`, `ruff format --check` i `mypy --strict` na całym pliku.
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

# %%
check("03.5", demand)

# %% [markdown]
# Porównaj modele na wszystkich seriach.

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
for name, score in sorted(scores.items(), key=lambda item: item[1]):
    print(f"{name:>18}: MAE {score:.3f}")

# %% [markdown]
# ## 03.6 Eksploracja
#
# Bez sprawdzeń.
#
# **Pytanie 1.** Napisz tu, w notebooku, klasę `ZeroForecaster`, która zawsze prognozuje zero. Nie dziedzicz po `LocalForecaster`. Oceń ją tym samym `evaluate`.

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
# Dlaczego prognoza zerowa wygrywa w MAE? Czego potrzebuje magazyn, który na jej podstawie zamawia części? Jaką własność powinna mieć metryka, której użyjesz do wyboru modelu?
#
# *Twoja odpowiedź:*
#
# **Pytanie 2.** Pogrupuj serie według typu popytu i porównaj modele osobno dla każdej grupy. Czy ranking modeli jest taki sam w każdej grupie?

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
