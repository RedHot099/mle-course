# Lab 04 krok po kroku

Ta sama praca co w `README.md` i w notebooku, tylko pocięta na małe kroki.
Rób **jeden krok naraz**. Każdy krok kończy się poleceniem, które coś sprawdza,
i opisem tego, co powinnaś zobaczyć. Jeśli zobaczysz coś innego, zatrzymaj się
i napisz do tutora, co wpisałaś i co zobaczyłaś.

Odhaczaj kroki: zmień `[ ]` na `[x]`.

---

## Część 0. Przygotowanie (10 min)

- [ ] **0.1** Otwórz w VS Code dwa pliki obok siebie:
  - po lewej `labs/03-classes/demand.py` (Twój kod z labu 03, linie od `class LocalForecaster` do `class Forecaster`),
  - po prawej `src/freshcast/models/local.py` (tu będziesz pisać).
- [ ] **0.2** W terminalu, w katalogu kursu, wpisz:
  ```bash
  uv run course check 04.1
  ```
  **Powinnaś zobaczyć:** `❌`.
  To dobrze: znaczy, że zadanie jeszcze nie jest zrobione.

**O co chodzi w tej części kursu, jednym zdaniem:** te same klasy prognoz, które
napisałaś w labie 03, przenosisz do „prawdziwego” pakietu, a potem piszesz testy,
które sprawdzają, że działają.

---

## Część 1. Przenosiny klas (zadanie 04.1)

W `local.py` w każdej metodzie stoi linia `raise NotImplementedError("Zadanie 04.1")`.
W każdym kroku zamieniasz **jedną** taką linię na kod. Kod masz już w `demand.py`.

**Zasada:** nie zmieniaj linii z `def ...` ani docstringów (tekstu w `"""..."""`).
Zmieniasz tylko linię z `raise NotImplementedError`.

### Krok 1.1: `LocalForecaster.fit`

- [ ] Znajdź w `demand.py` ciało metody `fit` klasy `LocalForecaster`.
- [ ] Skopiuj je do `local.py` w miejsce `raise NotImplementedError` w `fit`.
- [ ] Przeczytaj docstring `fit` w `local.py`. Odpowiedz sobie na dwa pytania:
  1. Co ma się stać, gdy `history` jest pusta?
  2. Czy zapisujesz listę rozmówcy, czy **własną kopię z liczbami typu `float`**?

  Jeśli Twój kod z labu 03 nie robi którejś z tych rzeczy, dopisz to teraz.

### Krok 1.2: `LocalForecaster.predict`

- [ ] Skopiuj ciało `predict` z `demand.py`.
- [ ] Przeczytaj sekcję `Raises:` w docstringu. Są tam **dwa** błędy. Sprawdź, czy Twój kod zgłasza oba.

### Krok 1.3: `NaiveForecaster._forecast`

- [ ] Skopiuj ciało z `demand.py`.
- [ ] Teraz pierwsza kontrola. W notebooku `04-testing.ipynb` uruchom **pierwszą komórkę**
  (z `%autoreload`), a potem komórkę z `naive_check` (pod napisem „Kroki 04.1a i 04.1b”).

  **Powinnaś zobaczyć:** brak błędu (komórka nic nie wypisuje).
  Jeśli widzisz `AssertionError: [4, 4]`, to znaczy, że w kroku 1.1 nie zamieniasz liczb na `float`.

### Krok 1.4: `SeasonalNaiveForecaster.__init__`

- [ ] Skopiuj ciało `__init__` z `demand.py`.
- [ ] Sprawdź: domyślny `season` w linii `def __init__` ma być **7**. Nie zmieniaj go.

### Krok 1.5: `SeasonalNaiveForecaster.fit`

- [ ] Skopiuj ciało `fit` z `demand.py`.
- [ ] Pytanie kontrolne: co się dzieje, gdy historia jest krótsza niż `season`?
  Odpowiedź jest w docstringu.

### Krok 1.6: `SeasonalNaiveForecaster._forecast`

- [ ] Skopiuj ciało z `demand.py`.

### Krok 1.7: `MovingAverageForecaster.__init__` i `_forecast`

- [ ] Skopiuj oba ciała z `demand.py`. Domyślne `window` to **7**.

### Krok 1.8: sprawdzenie całości

- [ ] W terminalu:
  ```bash
  uv run course check 04.1
  ```
  **Powinnaś zobaczyć:** `✅ 04.1`.
  Jeśli widzisz `❌`, skopiuj komunikat do tutora. Nie poprawiaj kilku rzeczy naraz.
- [ ] W notebooku uruchom komórkę z `week = [5.0, 3.0, ...]`. Zobaczysz trzy prognozy.
  Popatrz na nie: która wygląda najbardziej jak tydzień sprzedaży?

**Część 1 gotowa.** Dobry moment na przerwę.

---

## Część 2. Testy (zadanie 04.2)

### Co to jest test, w trzech zdaniach

Test to mała funkcja, której nazwa zaczyna się od `test_`. W środku: dajesz
modelowi **małe dane, które sama wymyślasz**, prosisz o prognozę i porównujesz
ją (`assert`) z wynikiem, który **policzyłaś sama w głowie albo na kartce**.
Jeśli ktoś kiedyś zepsuje kod, wynik się nie zgodzi i test to pokaże.

Wzór już jest w pliku `tests/models/test_local.py`: `test_naive_repeats_the_last_value`.
Każdy Twój test będzie wyglądał podobnie: 1 linia z prognozą, pusta linia, 1 linia z `assert`.

### Krok 2.0: uruchom gotowy test

- [ ] W terminalu:
  ```bash
  uv run pytest tests/models -q
  ```
  **Powinnaś zobaczyć:** `1 passed`.

### Krok 2.1: importy

- [ ] Na samej górze `test_local.py` dopisz linię `import pytest`.
- [ ] W nawiasie `from freshcast.models.local import (...)` dopisz pod `NaiveForecaster,`
  dwie pozostałe klasy prognoz (każda w osobnej linii, z przecinkiem).
- [ ] Uruchom `uv run pytest tests/models -q`. Nadal `1 passed`.

### Krok 2.2: pierwszy własny test, prognoza naiwna

- [ ] Wymyśl historię z **trzech różnych** liczb, np. pierwsza mała, ostatnia duża.
- [ ] Na kartce: jaka powinna być prognoza naiwna na 3 kroki?
- [ ] Skopiuj gotowy test, zmień nazwę funkcji (np. dopisz `_2`), wstaw swoje dane i swój wynik z kartki.
- [ ] `uv run pytest tests/models -q` → **powinno być `2 passed`.**

Pytanie do przemyślenia: dlaczego historia `[1.0, 1.0, 1.0]` byłaby złym wyborem?

### Krok 2.3: test prognozy sezonowej

- [ ] Wymyśl historię i `season`, np. `season=3`, historia z 6 różnych liczb.
- [ ] Na kartce: które 3 liczby to „ostatni sezon”? Jaka będzie prognoza na 3 kroki?
- [ ] Napisz test (pamiętaj: `SeasonalNaiveForecaster(season=3)`).
- [ ] `uv run pytest tests/models -q` → `3 passed`.

### Krok 2.4: sezonowa, horyzont dłuższy niż sezon

- [ ] Te same dane, ale prognoza na **5** kroków. Na kartce: co jest po 3. kroku? (docstring: „wrap around”)
- [ ] Napisz test, uruchom pytest → `4 passed`.

### Krok 2.5: test średniej kroczącej

- [ ] Wymyśl historię z 5 liczb i `window=2`.
- [ ] Na kartce: średnia z **dwóch ostatnich** liczb. Wybierz liczby tak, żeby średnia
  z całej historii była **inna** niż z dwóch ostatnich.
- [ ] Napisz test. Jeśli średnia wychodzi z ułamkiem, porównuj tak: `forecast == pytest.approx([...])`.
- [ ] pytest → `5 passed`.

### Krok 2.6: test długości prognozy

- [ ] Napisz test, który sprawdza, że `predict(horizon=4)` daje listę o długości dokładnie 4.
  Podpowiedź: `len(...)`.
- [ ] pytest → `6 passed`. Masz już wymagane minimum sześciu testów.

### Krok 2.7: pierwszy test błędu

Testy błędów wyglądają inaczej. Zamiast `assert` piszesz blok `with pytest.raises(...)`
(wykład 04, sekcja o `pytest.raises`). Kod, który ma zgłosić błąd, idzie do środka bloku.

- [ ] Docstring `fit`: pusta historia → `ValueError`. Napisz test, który to sprawdza.
- [ ] pytest → `7 passed`.

### Krok 2.8: pozostałe błędy z docstringów

Przejdź po sekcjach `Raises:` w `local.py` i odhaczaj. Na każdy punkt jeden test:

- [ ] `predict` przed `fit` → `RuntimeError`
- [ ] `predict` z `horizon` mniejszym niż 1 → `ValueError`
- [ ] `season` mniejszy niż 1 → `ValueError`
- [ ] historia krótsza niż `season` → `ValueError`
- [ ] `window` mniejszy niż 1 → `ValueError`

Po każdym teście: `uv run pytest tests/models -q`. Wszystkie mają przechodzić.

### Krok 2.9: sprawdzenie, czy testy łapią błędy

- [ ] W terminalu:
  ```bash
  uv run course check 04.2
  ```
  Sprawdzenie psuje Twój kod na 8 sposobów i patrzy, czy któryś test to zauważy.
  **Powinnaś zobaczyć:** `✅ 04.2`.
  Jeśli widzisz listę „nie wykryto”, weź **pierwszą** pozycję i zadaj sobie pytanie:
  jakie dane dałyby inny wynik w kodzie dobrym i zepsutym? Dopisz jeden test i uruchom ponownie.
  Z każdą pozycją możesz przyjść do tutora.

**Część 2 gotowa.**

---

## Część 3. Poetry i uv (zadanie 04.3, bez sprawdzania)

To ćwiczenie w terminalu, poza kursem. Instrukcja w notebooku (sekcja „04.3”)
jest już podana jako polecenia do skopiowania. Rób ją tak:

- [ ] Wykonaj **jeden** blok poleceń z notebooka (Krok 1).
- [ ] Sprawdź, czy nie było czerwonego błędu. Jeśli był, wklej go tutorowi.
- [ ] Dopiero wtedy następny blok.
- [ ] Na końcu odpowiedz na pytania w komórce „Twoje odpowiedzi”. Jedno zdanie na pytanie wystarczy.

---

## Część 4. Punkt kontrolny 1 (pull request)

Też jest w notebooku, na samym dole. Tak samo: **jedno polecenie naraz**.

- [ ] Krok 1 z notebooka ma 5 poleceń. Uruchamiaj po jednym. Każde ma skończyć się bez błędu.
  Jeśli któreś pokaże błąd, zatrzymaj się i napisz do tutora.
- [ ] Krok 2: wyczyść wyjścia notebooków (jedno polecenie).
- [ ] Krok 3: gałąź, commit, pull request. Ten krok możesz zrobić razem z tutorem: napisz `/review`.
