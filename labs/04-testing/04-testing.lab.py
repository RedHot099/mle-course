# %% [markdown]
# # Lab 04: prognozy w pakiecie, testy, które łapią błędy
#
# Klasy prognoz z labu 03 żyją w pliku obok notebooka. Żeby użyć ich w innym labie, trzeba by kopiować plik albo grzebać w `sys.path`. W tym labie przenosisz je do pakietu `freshcast`, który będzie rósł do końca kursu, i piszesz do nich testy w `pytest`.
#
# Testy ocenia sprawdzenie, które robi to, co robi dobry recenzent: psuje kod na osiem sposobów i patrzy, czy Twoje testy to zauważą. Test, który przechodzi zawsze, niczego nie chroni.
#
# Lab kończy się **punktem kontrolnym 1**: pull requestem z modułami 01-04 i review według `docs/standard.md`.
#
# **Czas:** około 6 godzin.
#
# | Zadanie | Co | Czas |
# |---|---|---|
# | 04.1 | Klasy prognoz w `src/freshcast/models/local.py` | 60 min |
# | 04.2 | Testy w `tests/models/test_local.py` | 150 min |
# | 04.3 | Piaskownica: ten sam pakiet w Poetry i w uv | 60 min |
# | PK1 | Pull request i review | 60 min |

# %%
from importlib.metadata import version

import freshcast

from coursekit.nb import check

print(freshcast.__file__)
print(version("mle-course"))

# %% [markdown]
# ## Skąd notebook zna `freshcast`
#
# `uv sync` zainstalował repozytorium kursu jako pakiet `mle-course` w trybie **edytowalnym**: środowisko nie ma kopii kodu, tylko wskazanie na katalog `src/`. Dlatego `import freshcast` działa w każdym notebooku i w każdym teście, a zmiana w pliku jest widoczna po ponownym imporcie.
#
# Sprawdź to sam:

# %%
# !uv pip show mle-course

# %% [markdown]
# Linia `Editable project location` wskazuje katalog repozytorium. Kod pakietu leży w `src/freshcast/`, a nie w katalogu głównym. To **układ src**: przypadkowy import z bieżącego katalogu jest niemożliwy, więc testy zawsze sprawdzają zainstalowany pakiet, taki sam, jaki dostanie ktoś inny.

# %% [markdown]
# ## 04.1 Klasy prognoz w pakiecie
#
# Otwórz `src/freshcast/models/local.py`. Sygnatury, docstringi i klasa bazowa już tam są, brakuje ciał metod. Uzupełnij je kodem z `demand.py` z labu 03. Nie zmieniaj sygnatur: od modułu 08 używa ich reszta pakietu.
#
# Dwie różnice wobec labu 03:
#
# - domyślne `season` i `window` to 7, bo od modułu 08 prognozujesz dane dzienne,
# - `predict` zwraca zawsze `float`, także gdy historia była listą liczb całkowitych.
#
# Sprawdzenie pakietu wywołujesz bez drugiego argumentu, bo kod nie leży w notebooku. To samo sprawdzenie uruchomisz w terminalu: `uv run course check 04.1`.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# To przeniesienie, nie nowe zadanie. Jeśli coś nie przechodzi, porównaj docstring metody w pakiecie z tym, co napisałeś w labie 03: docstring jest umową.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `float` na wyjściu dostajesz za darmo, jeśli `fit` zapisuje historię jako `[float(value) for value in history]`. Wtedy każdy `_forecast` liczy już na liczbach zmiennoprzecinkowych.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# Ciała metod są takie same jak w podpowiedziach 3 z labu 03, zadania 03.3 i 03.4.
#
# </details>

# %%
check("04.1")

# %% [markdown]
# Pakiet działa z każdego miejsca. Sprawdź modele na wymyślonym tygodniowym wzorze sprzedaży: dużo w weekend, mało w środku tygodnia.

# %%
from freshcast.models.local import (
    MovingAverageForecaster,
    NaiveForecaster,
    SeasonalNaiveForecaster,
)

week = [5.0, 3.0, 3.0, 4.0, 6.0, 9.0, 8.0]
history = week * 3
for model in (NaiveForecaster(), SeasonalNaiveForecaster(), MovingAverageForecaster()):
    print(f"{type(model).__name__:>24}: {model.fit(history).predict(7)}")

# %% [markdown]
# ## 04.2 Testy
#
# Otwórz `tests/models/test_local.py`. Pierwszy test jest gotowy i pokazuje wzór:
#
# ```python
# def test_naive_repeats_the_last_value() -> None:
#     forecast = NaiveForecaster().fit([3.0, 5.0, 4.0]).predict(horizon=2)
#
#     assert forecast == [4.0, 4.0]
# ```
#
# Nazwa mówi, jakie zachowanie test sprawdza. Dane są małe i widać je w teście. Asercja porównuje z konkretną wartością, policzoną w głowie, a nie przez ten sam kod.
#
# Napisz co najmniej sześć kolejnych testów (przypadek parametryzacji liczy się jako test). Uruchamiasz je tak:

# %%
# !cd ../.. && uv run pytest tests/models -q

# %% [markdown]
# Gdy przechodzą, uruchom sprawdzenie. Podmienia ono Twój kod na osiem wersji z celowym błędem, po jednej naraz, i uruchamia na każdej Twoje testy. Każdy błąd, którego testy nie zauważą, pojawi się na liście.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Lista przeżytych błędów mówi dokładnie, czego brakuje. Przy każdym zadaj pytanie: jakie dane wejściowe dałyby inny wynik w kodzie poprawnym i w zepsutym?
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Dane dobieraj tak, żeby błąd był widoczny. Historia `[1.0, 1.0, 1.0]` nie odróżni pierwszej wartości od ostatniej. Sezon `[1, 2, 3]` odróżni przesunięcie o krok. Błędy testujesz przez `pytest.raises(ValueError, match="...")`, a kilka podobnych przypadków przez `@pytest.mark.parametrize`. Liczby z dzielenia porównuj przez `pytest.approx`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# def test_seasonal_naive_repeats_the_last_season() -> None:
#     history = [1.0, 2.0, 3.0, 10.0, 20.0, 30.0]
#
#     forecast = SeasonalNaiveForecaster(season=3).fit(history).predict(horizon=3)
#
#     assert forecast == [10.0, 20.0, 30.0]
#
#
# @pytest.mark.parametrize("horizon", [0, -1])
# def test_predict_rejects_a_horizon_below_one(horizon: int) -> None:
#     forecaster = NaiveForecaster().fit([1.0])
#
#     with pytest.raises(ValueError, match="horizon"):
#         forecaster.predict(horizon=horizon)
# ```
#
# </details>

# %%
check("04.2")

# %% [markdown]
# ## 04.3 Piaskownica: Poetry i uv
#
# Kurs używa uv. W wielu firmach spotkasz Poetry, starsze i nadal popularne narzędzie do tego samego. Zamiast czytać porównanie, zbuduj ten sam mały pakiet obydwoma. Rób to **w terminalu, poza repozytorium kursu**, żeby niczego w nim nie zmienić.
#
# Bez sprawdzeń. Odpowiedzi zapisz na dole notebooka.
#
# **Krok 1.** Zainstaluj Poetry jako narzędzie uv. Tak instaluje się każde narzędzie wiersza poleceń napisane w Pythonie: dostaje własne, osobne środowisko.
#
# ```bash
# uv tool install poetry
# poetry --version
# ```
#
# **Krok 2.** Dwa puste pakiety obok siebie:
#
# ```bash
# mkdir -p ~/sandbox && cd ~/sandbox
# poetry new demand-poetry
# uv init --package demand-uv
# ```
#
# **Krok 3.** W każdym dodaj `pytest` jako zależność deweloperską i zainstaluj środowisko:
#
# ```bash
# cd ~/sandbox/demand-poetry && poetry add --group dev pytest && poetry install
# cd ~/sandbox/demand-uv && uv add --dev pytest && uv sync
# ```
#
# **Krok 4.** W obu pakietach dopisz do `src/<nazwa>/__init__.py` funkcję `naive(history, horizon)` i test w `tests/test_naive.py`. Uruchom testy: `poetry run pytest` i `uv run pytest`.
#
# **Krok 5.** Porównaj. Otwórz oba `pyproject.toml` i oba pliki lock.
#
# Pytania:
#
# 1. Gdzie każde z narzędzi założyło środowisko wirtualne? Podpowiedź: `poetry env info --path`.
# 2. Jak każde z nich zapisało w `pyproject.toml` wymaganie na wersję `pytest`? Co z tego wynika, gdy wyjdzie `pytest` w nowej wersji głównej?
# 3. Jak nazywa się plik lock w każdym z nich? Czy powinien trafić do gita? Dlaczego?
# 4. Uzupełnij tabelę odpowiedników:
#
# | Czynność | uv | Poetry |
# |---|---|---|
# | nowy pakiet | `uv init --package` | |
# | dodaj zależność | | `poetry add` |
# | zainstaluj środowisko z locka | `uv sync` | |
# | uruchom w środowisku | | `poetry run` |
# | odśwież lock | `uv lock` | |
#
# *Twoje odpowiedzi:*

# %% [markdown]
# ## Punkt kontrolny 1
#
# Moduły 01-04 są za Tobą. Pora na pierwszy pull request, który ktoś oceni według standardu kursu.
#
# **1. Sprawdź wszystko lokalnie** (reguła G3). W katalogu repozytorium:
#
# ```bash
# uv run ruff format --check .
# uv run ruff check .
# uv run mypy
# uv run pytest
# uv run course check 04
# ```
#
# **2. Wyczyść wyjścia notebooków** (reguła G4: w repozytorium nie ma wyjść z danymi):
#
# ```bash
# uv run jupyter nbconvert --clear-output --inplace labs/0[1-4]-*/*.ipynb
# ```
#
# **3. Gałąź, commit, pull request:**
#
# ```bash
# git switch -c checkpoint/01
# git add labs src tests
# git commit -m "Add local forecasters with tests"
# git push -u origin checkpoint/01
# gh pr create --fill
# ```
#
# **4. Review.** W Claude Code w katalogu repozytorium wpisz `/review`. Tutor przeczyta cały diff według `docs/standard.md` i powie "do scalenia" albo "do poprawy". Poprawki robisz sam, kolejnymi commitami na tej samej gałęzi, i prosisz o review jeszcze raz.
#
# Bez tutora zrób review sam: otwórz `docs/standard.md`, weź reguły z kolumną "Od" do 04 włącznie i dla każdej przejrzyj zakładkę "Files changed" pull requesta. Zapisz w opisie PR, które reguły sprawdziłeś.
#
# **5.** Gdy werdykt to "do scalenia", scal pull request i wróć na `main`:
#
# ```bash
# git switch main && git pull
# ```
