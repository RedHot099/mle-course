# Utrzymanie fundamentów A i B

Punkt wejścia uczestnika: [index.html](index.html). Materiały są osobną ścieżką przed modułami liczbowymi. Nie zmieniają ich identyfikatorów, `course check`, `catchup` ani kodu zadań w `src/freshcast`.

## Zakres

| Sekcja planu | Przygotowane materiały |
|---|---|
| A1 | Uruchomienie runnera przed diagnozą, diagnoza podstaw i wybór powtórek |
| A2 | Wartości, warunki, listy i pętle, rekordy, pierwsza funkcja |
| A3 | Minimalne środowisko lokalne, notebook, kernel i ponowne wykonanie od początku |
| A4 | Średnia i wartość bezwzględna przed MAE, historia i horyzont, baseline na publicznym wycinku danych |
| B5 | Kolekcje, mutowalność, pliki, błędy; generator jako dodatek po działającym odczycie |
| B6 | Umowa funkcji, obliczenie bez zmiany wejścia, pierwsze własne testy i kontrolowane zepsucie kodu |
| B7 | Własny moduł, podstawowe typy, ruff i mypy, mały PR oraz dostarczone CI |

B6.2 i B7 pracują w osobnym projekcie `~/mle-practice`. Pierwszy PR powstaje w jego kopii sklonowanej z własnego repozytorium GitHub. Dzięki temu testy nie zależą od nieukończonych zadań późniejszych modułów. Pełne projektowanie CI i infrastruktury pozostaje poza rdzeniem.

## Zasady redakcyjne i źródła

Podstawą zakresu jest [audyt i kontrola kolejności z Astrą](../../docs/research/beginner-curriculum-audit.md). [Notatka źródłowa](../../docs/research/beginner-course-sources.md) rozróżnia fakty z syllabusów i autorskie rekomendacje.

Zastosowane wzorce:

- PY4E i CS106A: stopniowe rozwiązywanie małych problemów przed pisaniem klas.
- CS50P: testy zwykłych funkcji przed OOP.
- Udemy: widoczny mały rezultat kolejnych etapów; bez przenoszenia marketingowych szacunków czasu.
- Rekomendacje IES: przykład na innym problemie, przewidywanie wyniku, własne zadanie, pytanie wymagające wyjaśnienia i powrót po przerwie.

Sprawdzone źródła techniczne: [uv scripts](https://docs.astral.sh/uv/guides/scripts/), [instalacja uv](https://docs.astral.sh/uv/getting-started/installation/), [środowiska Python](https://docs.python.org/3.12/tutorial/venv.html), [setup-uv](https://github.com/astral-sh/setup-uv). Polecenia małego projektu sprawdzono także lokalnie na dostarczonym przykładzie `half`, bez rozwiązywania zadań uczestnika.

Materiały wymagają pilotażu z początkującymi. Kontrola techniczna nie potwierdza czasu nauki ani skuteczności dydaktycznej.

## Wykonywanie i zapis pracy

Strony używają istniejących `lectures/assets/course.css` i `course.js`. Skrypt pobiera Pyodide przy pierwszym wykonaniu kodu. Każde pole kodu dostaje osobną przestrzeń nazw. Wirtualne pliki interpretera mogą istnieć między próbami, dlatego przykłady tworzą własne jawne wejście.

Quizy i pola kodu zapisują stan w localStorage według osobnych identyfikatorów `foundations-*`. Nie zapisują do `.course/progress.json`. Wynik poprzedniego przejścia jest historią, nie gwarancją poprawności później edytowanego kodu. Uczestnik ma wykonać bieżące sprawdzenie i zachować ważny kod lokalnie.

Specyfikacje i sprawdzenia ćwiczeń znajdują się przy odpowiednich polach w HTML. Przykłady pokazują inne problemy, a startery zadań pozostają nieuzupełnione. Przyciski Sprawdź nie korzystają z kodu gałęzi `solutions`.

Instrukcje dla tutora i zakres review są w [tutor/notes/foundations.md](../../tutor/notes/foundations.md).

## Dane pierwszej prognozy

`data/freshcast-sample.csv` zawiera 14 kolejnych obserwacji serii sklep 70, produkt 116, od 2024-03-28 do 2024-04-10. Źródłem jest publiczna próbka `src/coursekit/fixtures/frn_sample.parquet`, pochodząca z FreshRetailNet-50K, Dingdong-Inc, CC BY 4.0. Zachowano wartości `sale_amount`; `stock_hour6_22_cnt` nazwano czytelniej `stockout_hours`. Dane uporządkowano po `dt`.

Pierwsze siedem dni jest historią, drugie siedem służy ćwiczeniu oceny. Uczestnik widzi cały wycinek, więc nie jest to niezależny końcowy holdout. MAE dotyczy zaobserwowanej sprzedaży na wszystkich dniach, także z brakami towaru. Nie opisuje pełnego nieobserwowanego popytu.

## Weryfikacja zmian

Z katalogu repozytorium:

```bash
uv run python tools/verify_foundations.py
uv run ruff format --check tools
uv run ruff check tools
uv run --with playwright mypy tools
```

Weryfikator sprawdza strukturę HTML, unikalne identyfikatory, lokalne pliki i anchory, pojedynczą poprawną odpowiedź quizu, składnię ćwiczeń i wykonanie dostarczonych przykładów. Sprawdza także, że nieuzupełnione startery nie przechodzą i dają wyjaśniający AssertionError. Dodatkowa metadana `data-expected-output` pozwala porównać wynik przykładu z opisem, a `data-expected-error` oznacza celowy błąd demonstracyjny. Fragment importujący kod uczestnika ma `data-needs-learner` i nie jest wykonywany bez jego modułu.

Kontrola przeglądarkowa wymaga opcjonalnego Playwright i przeglądarki w katalogu użytkownika:

```bash
uv run --with playwright python -m playwright install chromium --only-shell
uv run --with playwright python tools/verify_foundations_browser.py
```

Ta kontrola sprawdza wszystkie strony na szerokości 1280 i 390 px, inicjalizację edytorów, brak błędów JavaScript i przewijania całej strony w poziomie. W rzeczywistym Pyodide wykonuje pierwszy program oraz wszystkie nieuzupełnione sprawdzenia, sprawdza zapis quizu i kodu po odświeżeniu, reset kodu oraz przełączanie motywu. Nie wpisuje rozwiązań ćwiczeń.

Pełna suite `tests/` dotyczy kodu pisanego przez uczestnika w obecnych modułach. Nie jest zaliczeniem ścieżki A/B ani podstawą do żądania rozwiązania późniejszych zadań.
