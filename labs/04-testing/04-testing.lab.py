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
# Zadania są podzielone na kroki (04.1a, 04.1b, ...). Sprawdzenie `check(...)` jest jedno na całe zadanie.
#
# | Zadanie | Krok | Co | Gdzie | Czas |
# |---|---|---|---|---|
# | 04.1 | 04.1a | `fit` i `predict` klasy bazowej | `src/freshcast/models/local.py`, `LocalForecaster` | 60 min |
# | | 04.1b | prognoza naiwna | to samo, `NaiveForecaster._forecast` | |
# | | 04.1c | prognoza sezonowa | to samo, `SeasonalNaiveForecaster`: `__init__`, `fit`, `_forecast` | |
# | | 04.1d | średnia krocząca | to samo, `MovingAverageForecaster`: `__init__`, `_forecast` | |
# | 04.2 | 04.2a | testy wartości prognoz | `tests/models/test_local.py` | 150 min |
# | | 04.2b | test liczby wartości prognozy | to samo | |
# | | 04.2c | testy błędów | to samo | |
# | | 04.2d | sprawdzenie i uzupełnienie testów | terminal albo notebook | |
# | 04.3 | | ten sam pakiet w Poetry i w uv | terminal, poza repozytorium; odpowiedzi w notebooku | 60 min |
# | PK1 | | pull request i review | terminal, GitHub | 60 min |
#
# Pliki w pakiecie edytujesz w VS Code. Pierwsza komórka włącza `%autoreload 2`, więc notebook widzi każdą zapisaną zmianę w `local.py` bez restartu.

# %%
# %load_ext autoreload
# %autoreload 2

from importlib.metadata import version

import freshcast

from coursekit.nb import check

print(freshcast.__file__)
print(version("mle-course"))

# %% [markdown]
# ## Skąd notebook zna `freshcast`
#
# `uv sync` zainstalował repozytorium kursu jako pakiet `mle-course` w trybie **edytowalnym**: środowisko nie ma kopii kodu, tylko wskazanie na katalog `src/`. Dlatego `import freshcast` działa w każdym notebooku i w każdym teście. Każdy nowy proces Pythona, np. `uv run pytest` albo `uv run course check`, czyta aktualne pliki z `src/`. Działający kernel notebooka pamięta raz zaimportowany moduł: zmiany zobaczy dzięki `%autoreload 2` z pierwszej komórki albo po restarcie kernela i uruchomieniu komórek od początku. Samo ponowne uruchomienie komórki z `import` nie wystarczy.
#
# Sprawdź to sam:

# %%
# !uv pip show mle-course

# %% [markdown]
# Linia `Editable project location` wskazuje katalog repozytorium. Kod pakietu leży w `src/freshcast/`, a nie w katalogu głównym. To **układ src**: przypadkowy import z bieżącego katalogu jest niemożliwy, więc testy zawsze sprawdzają zainstalowany pakiet, taki sam, jaki dostanie ktoś inny.

# %% [markdown]
# ## 04.1 Klasy prognoz w pakiecie
#
# **Cel.** Prognozy z labu 03 mają być dostępne z każdego labu i każdego testu przez `from freshcast.models.local import ...`. Od modułu 08 będą baseline'em dla danych dziennych, więc ich sygnatury są już ustalone.
#
# **Gdzie.** `src/freshcast/models/local.py`. Sygnatury, docstringi i importy już tam są. W miejscu każdego ciała metody stoi `raise NotImplementedError("Zadanie 04.1")`: zamień je na kod. Nie zmieniaj sygnatur ani wartości domyślnych, bo od modułu 08 używa ich reszta pakietu. Docstring każdej metody to dokładna umowa.
#
# **Wejście.** `history`: znane wartości jednej serii od najstarszej, ciąg liczb (`Sequence[float]`); może zawierać liczby całkowite. `horizon`: liczba całkowita (`int`), ile kroków do przodu. `season`, `window`: liczby całkowite, domyślnie 7.
#
# **Wynik.** Ta sama umowa co w 03.3 i 03.4. Jeśli Twój kod z labu 03 przeszedł sprawdzenia, przenosisz go bez zmian. Dwie rzeczy z tej umowy sprawdzenie 04.1 bada wprost:
#
# - domyślne `season` i `window` to 7, bo od modułu 08 prognozujesz dane dzienne (tydzień ma 7 dni); w labie 03 na danych miesięcznych podawałeś inne wartości jawnie,
# - `predict` zwraca listę długości `horizon`, w której każdy element jest typu `float`, także gdy historia była listą liczb całkowitych: `NaiveForecaster().fit([3, 5, 4]).predict(2)` daje `[4.0, 4.0]`, a nie `[4, 4]`.
#
# **Skorzystaj z.** Twojego `labs/03-classes/demand.py`, zadania 03.3 i 03.4: ciała metod przenosisz stamtąd. `Forecaster`, `mae` i `evaluate` zostają w labie 03.
#
# **Kroki.**
#
# - **04.1a** `LocalForecaster.fit` i `LocalForecaster.predict`: walidacja, kopia historii jako lista `float`, wywołanie `_forecast`. `__init__` i `_forecast` klasy bazowej są gotowe.
# - **04.1b** `NaiveForecaster._forecast`. Komórka z `assert` pod podpowiedziami potwierdza kroki 04.1a i 04.1b.
# - **04.1c** `SeasonalNaiveForecaster`: `__init__`, `fit` i `_forecast`.
# - **04.1d** `MovingAverageForecaster`: `__init__` i `_forecast`.
#
# **Sprawdzenie.** `check("04.1")` w notebooku albo `uv run course check 04.1` w terminalu, w katalogu repozytorium. Kod leży w pakiecie, nie w notebooku, więc `check` dostaje tylko numer zadania. Wynik `✅ 04.1` znaczy, że wszystkie cztery klasy działają zgodnie z docstringami.
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

# %% [markdown]
# Kroki 04.1a i 04.1b: prognoza naiwna z historii liczb całkowitych.

# %%
from freshcast.models import local

naive_check = local.NaiveForecaster().fit([3, 5, 4]).predict(2)
assert naive_check == [4.0, 4.0], naive_check
assert all(isinstance(value, float) for value in naive_check), naive_check

# %% [markdown]
# Całe zadanie 04.1, po kroku 04.1d:

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
# **Cel.** Testy mają złapać błąd w `local.py`, zanim zobaczy go ktoś inny: przy przenosinach, refaktoryzacji albo "drobnej poprawce" w module 08. Test, który przechodzi także na zepsutym kodzie, niczego nie chroni.
#
# **Gdzie.** `tests/models/test_local.py`, pod gotowym testem, w miejscu komentarza `# Your tests go here`. Każdy test to osobna funkcja z nazwą zaczynającą się od `test_`, bez argumentów (albo z argumentami z `@pytest.mark.parametrize`). Testy w innym pliku albo z inną nazwą nie zostaną policzone.
#
# **Wejście.** Klasy z `freshcast.models.local`, które napisałeś w 04.1. Testujesz je tylko tak, jak używa ich reszta kursu: przez `fit(...)` i `predict(...)`, jak w gotowym teście. Nie wołaj `_forecast` bezpośrednio.
#
# **Wynik.** W pliku co najmniej sześć testów, licząc gotowy. Żeby wykryć wszystkie błędy z kroku 04.2d, napiszesz ich więcej. Każdy przypadek parametryzacji liczy się jako osobny test, więc `@pytest.mark.parametrize("horizon", [0, -1])` to dwa testy.
#
# **Skorzystaj z.** Docstringów w `local.py`: każde zdanie, które mówi, co metoda zwraca albo kiedy zgłasza błąd, to kandydat na test. Z wykładu 04: `pytest.raises(..., match=...)`, `@pytest.mark.parametrize`, `pytest.approx`. Dopisz na górze pliku `import pytest` i dopisz do importu z `freshcast.models.local` klasy, których używasz (gotowy import ma tylko `NaiveForecaster`). Kolejność importów sprawdza `ruff check` w punkcie kontrolnym; gdy zgłosi `I001`, uruchom `uv run ruff check --fix tests/models/test_local.py`.
#
# **Sprawdzenie.** `check("04.2")` w notebooku albo `uv run course check 04.2` w terminalu. Opis, co dokładnie robi, jest w kroku 04.2d.
#
# Pierwszy test jest gotowy i pokazuje wzór:
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
# ### 04.2a Wartości prognoz
#
# Dla każdej z trzech klas co najmniej jeden test, który porównuje całą prognozę z listą policzoną przez Ciebie na kartce.
#
# | Klasa | Co test ma potwierdzić (z docstringu) |
# |---|---|
# | `NaiveForecaster` | prognoza to ostatnia wartość historii; gotowy test to pokazuje, dopisz drugi na innych danych |
# | `SeasonalNaiveForecaster` | prognoza to ostatni pełny sezon, krok po kroku, i zawija się, gdy horyzont jest dłuższy niż sezon |
# | `MovingAverageForecaster` | prognoza to średnia tylko z ostatnich `window` wartości; historia krótsza niż okno jest uśredniana w całości |
#
# Dobierz dane tak, żeby różne pomyłki dawały różne liczby: wartości w historii różne od siebie, historia dłuższa niż sezon i niż okno.
#
# ### 04.2b Liczba wartości
#
# `predict(horizon)` zwraca dokładnie `horizon` wartości. Sprawdź to dla każdej z trzech klas i dla więcej niż jednego horyzontu, najlepiej jednym testem z `@pytest.mark.parametrize`.
#
# ### 04.2c Błędy
#
# Docstringi `fit` i `predict` w `LocalForecaster` wymieniają sytuacje, w których kod ma zgłosić błąd, i jego typ (`ValueError`, `RuntimeError`). Na każdą napisz test z `pytest.raises(TypBłędu, match="...")`. W `match` podaj słowo z komunikatu, który napisałeś w 04.1. `SeasonalNaiveForecaster.fit` dodaje jeszcze jeden przypadek. Docstringi klas `SeasonalNaiveForecaster` i `MovingAverageForecaster` wymieniają też błędy konstruktora (`season` i `window` mniejsze od 1). Testy na nie też są dobre, choć sprawdzenie 04.2 ich nie wymaga.
#
# ### 04.2d Uruchom testy, potem sprawdzenie
#
# Najpierw same testy, na Twoim kodzie. Wszystkie muszą przejść. W terminalu, w katalogu repozytorium (tym z `pyproject.toml`): `uv run pytest tests/models -q`, albo komórka poniżej. Komórka zakłada, że kernel działa w katalogu notebooka, `labs/04-testing`, i dlatego przechodzi dwa katalogi wyżej. Gdy pytest zgłasza, że nie znalazł `tests/models`, uruchom polecenie w terminalu.

# %%
# !cd ../.. && uv run pytest tests/models -q

# %% [markdown]
# Potem `check("04.2")`. Sprawdzenie robi to, co dobry recenzent, w trzech etapach:
#
# 1. Liczy testy w `tests/models/test_local.py`, razem z gotowym. Mniej niż sześć to `❌` z liczbą znalezionych.
# 2. Uruchamia je na Twoim kodzie. Jeśli któryś nie przechodzi, `❌` i polecenie, którym zobaczysz który.
# 3. Uruchamia je osiem razy, za każdym razem na Twoim `local.py` z jednym celowo wprowadzonym błędem. Każdy taki błąd łamie jedno zdanie z docstringów. Na każdej zepsutej wersji co najmniej jeden Twój test musi **nie** przejść. Wersje, na których wszystkie testy przeszły, sprawdzenie wypisuje na liście: każda pozycja mówi, jakiego błędu Twoje testy nie zauważyły.
#
# Wynik `✅ 04.2` znaczy, że testy wykryły wszystkie osiem błędów. Dlatego dobry test spełnia dwa warunki. Wartość oczekiwaną liczysz sam, a nie tym samym kodem, który testujesz. Dane są takie, że poprawny i błędny kod dają na nich różne wyniki.
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
# **Cel.** Kurs używa uv. W wielu firmach spotkasz Poetry, starsze i nadal popularne narzędzie do tego samego. Zamiast czytać porównanie, zbuduj ten sam mały pakiet obydwoma.
#
# **Gdzie.** W terminalu, w katalogu `~/sandbox`, **poza repozytorium kursu**, żeby niczego w nim nie zmienić. Odpowiedzi na cztery pytania zapisz w komórce "*Twoje odpowiedzi:*" na końcu tej sekcji.
#
# **Wynik.** Dwa pakiety, `~/sandbox/demand-poetry` i `~/sandbox/demand-uv`, w każdym jedna funkcja i jeden przechodzący test, oraz odpowiedzi na pytania.
#
# **Sprawdzenie.** Bez sprawdzeń. Gotowe, gdy `poetry run pytest` i `uv run pytest` przechodzą, a w odpowiedziach jest uzupełniona tabela.
#
# **Krok 1.** Zainstaluj Poetry jako narzędzie uv. Tak instaluje się każde narzędzie wiersza poleceń napisane w Pythonie: dostaje własne, osobne środowisko.
#
# ```bash
# uv tool install poetry
# poetry --version
# ```
#
# Opis dotyczy Poetry 2 (wersja 2.x). W Poetry 2 `poetry new` tworzy układ `src/` i katalog `tests/`, a `poetry lock` nie podnosi wersji bez osobnej opcji. Starsze poradniki w internecie opisują Poetry 1, które działało inaczej.
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
# **Krok 4.** W obu pakietach napisz funkcję `naive(history, horizon)`: dostaje listę liczb i liczbę kroków, zwraca listę, w której ostatnia wartość historii powtarza się `horizon` razy. Dopisz ją do pliku `__init__.py` pakietu: `src/demand_poetry/__init__.py` i `src/demand_uv/__init__.py` (myślnik z nazwy projektu zamienia się w nazwie pakietu na podkreślnik). Test napisz w `tests/test_naive.py` każdego projektu (w `demand-uv` katalog `tests/` utwórz sam) i zaimportuj w nim funkcję: `from demand_poetry import naive` albo `from demand_uv import naive`. Uruchom testy: `poetry run pytest` w `demand-poetry` i `uv run pytest` w `demand-uv`.
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
# | uzgodnij plik lock z `pyproject.toml`, bez podnoszenia wersji | `uv lock` | |
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
# **3. Gałąź, commit, pull request.** Pull request idzie z gałęzi `checkpoint/01` do gałęzi `main` w **Twoim forku**, nie do repozytorium kursu. Tak ustawiłeś `gh` w module 00 (`gh repo set-default`). `gh pr create` wypisuje adres pull requesta: otwórz go i sprawdź, że repozytorium docelowe to `TWOJ-LOGIN/mle-course`, a baza to `main`.
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
# Bez tutora zrób review sam: otwórz `docs/standard.md`, weź reguły z kolumną "Od" do 04 włącznie i dla każdej przejrzyj zakładkę "Files changed" pull requesta. Dopisz do opisu PR (na stronie pull requesta przycisk edycji opisu albo `gh pr edit --body "..."`) listę identyfikatorów reguł, które sprawdziłeś, np. `K1, K2, T1, G3`, a przy każdej znalezionej uwadze jedno zdanie, co poprawiłeś.
#
# **5.** Gdy werdykt to "do scalenia", scal pull request: przycisk **Merge pull request** na jego stronie w Twoim forku albo `gh pr merge` w terminalu. Dopiero potem wróć lokalnie na `main` i pobierz scalone zmiany:
#
# ```bash
# git switch main && git pull
# ```
