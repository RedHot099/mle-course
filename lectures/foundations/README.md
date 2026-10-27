# Utrzymanie ścieżki A–F

Punkt wejścia: [mapa 70 lekcji](index.html). Nowy rdzeń obejmuje wszystkie 21 punktów uzgodnionego planu A–F. [Plan i kontrola kolejności](../../docs/research/beginner-curriculum-audit.md) wyjaśniają zakres. Starsze moduły 00–19 są dostępne przez [wcześniejszą mapę](../legacy.html); ich ukończenie nie jest dodatkowym wymaganiem nowej ścieżki.

## Pokrycie planu

| Sekcja | Punkty planu | Lekcje | Zakres |
|---|---|---:|---|
| A | 1–4 | 9 | Diagnoza, Python, notebook, pierwsza prognoza |
| B | 5–7 | 7 | Kolekcje, pliki, błędy, funkcje, testy, moduł i git |
| C | 8–12 | 13 | Tabele, statystyka, wykresy, NumPy, relacje, czas, estimator i Pipeline |
| D | 13–16 | 16 | Strata, pochodne, gradient, macierze, ocena, drzewa i klasyfikacja |
| E | 17 | 2 | Własna klasa i odtworzenie eksperymentu |
| F | 18–21 | 23 | Generalizacja, prawdopodobieństwo, reprezentacje, sieci, język, search i decyzje |

Źródłem identyfikatorów, kolejności i wymagań jest [curriculum.json](curriculum.json). Treść lekcji znajduje się bezpośrednio w HTML. Weryfikator sprawdza kompletność katalogu, pokrycie punktów 1–21 i to, że wymagania nie wskazują późniejszych lekcji. Ścieżka jest gotowa do przeglądu autora i pilotażu. Sprawdzenia techniczne nie zastępują obserwacji początkujących uczestników.

Zadania na stronach mają dwa rodzaje zakończenia. Edytory z przyciskiem Sprawdź sprawdzają wynik małego ćwiczenia. Zadania notebookowe i wyjaśnienia mają jawne kryteria w sekcji „Sprawdź, co pamiętasz”. Nie pozorujemy ich zaliczenia przez szukanie słów kluczowych. Tutor wymaga wyniku, ręcznego przykładu i wyjaśnienia na nowych danych.

## Kolejność i źródła

Statystyka w C8 poprzedza scaler, geometria w F20.1 poprzedza k-means, a rzut i wariancja poprzedzają PCA. Model w C12 poprzedza wyprowadzanie algorytmu w D13. Prawdopodobieństwo i likelihood poprzedzają log-loss, a iloczyn skalarny i softmax poprzedzają attention. E17 nie jest warunkiem rozumienia F18 ani F19; wraca przy własnej klasie sieci.

Inspiracje programowe opisano w [notatce źródłowej](../../docs/research/beginner-course-sources.md). CS229 stanowi punkt odniesienia dla modelowania, generalizacji i probabilistycznego spojrzenia na uczenie. CS221 rozszerza zakres o search, inference i decyzje. Nie kopiujemy ich tempa, wymagań wejściowych ani pełnego zakresu.

Sprawdzone materiały pierwotne:

- [Stanford SEE, CS229](https://see.stanford.edu/Course/CS229).
- [Stanford CS221, Autumn 2025](https://stanford-cs221.github.io/autumn2025/).
- [Stanford CS336, Spring 2025](https://cs336.stanford.edu/spring2025/index.html), jako granica dalszej specjalizacji językowej.
- [pandas: wybór danych](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html).
- [scikit-learn: Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.make_pipeline.html), [Naive Bayes](https://scikit-learn.org/stable/modules/naive_bayes.html).
- [PyTorch: autograd](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html), [własny model](https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html).

Wyjaśnienia, ćwiczenia i dane syntetyczne są autorskie. Biblioteki służą do wykonywania eksperymentów, a nie zastępują wyjaśnienia pojęć. Pełne wdrożenie, GPU, ABC, Protocol, zaawansowane generyki, tuning i trenowanie LLM pozostają rozszerzeniami.

## Dane i końcowy test

`data/freshcast-sample.csv` zawiera 14 kolejnych obserwacji: sklep 70, produkt 116, 2024-03-28–2024-04-10. Pochodzi z publicznego `src/coursekit/fixtures/frn_sample.parquet`, FreshRetailNet-50K, Dingdong-Inc, CC BY 4.0. Zachowano `sale_amount`; `stock_hour6_22_cnt` nazwano `stockout_hours`. Cały wycinek jest widoczny w A4, więc nie służy jako zamknięty test.

Projekt od C12 korzysta z osobnych, jawnie syntetycznych danych: 56 dni od 2024-01-01. Pierwsze 49 są w `project-development.csv`, ostatnie 7 w `project-holdout.csv`. Trening obejmuje dni 1–42, walidacja 43–49, test 50–56. Wartości wygenerowano z trendu, cyklu tygodniowego i niewielkiego szumu, bez danych klientów. To demonstracja procesu, nie pomiar jakości biznesowej.

Projekt zaczyna od codziennie aktualizowanej prognozy jednodniowej: rzeczywisty poprzedni dzień może być cechą kolejnego. Zamrożony horyzont wielodniowy jest osobnym doświadczeniem D15.4. Finał F21.5 nie zmienia po fakcie protokołu C12. Plik holdoutu jest dostępny w repozytorium; ograniczenie jest dydaktyczne. Jeśli uczestnik obejrzy go wcześniej, odnotowuje to i nie nazywa późniejszego wyniku niezależnym testem.

## Środowisko i zapis pracy

Pola kodu używają istniejącego `course.js`, który ładuje Pyodide i potrzebne biblioteki przy pierwszym imporcie. Każde wykonanie zaczyna w osobnej przestrzeni nazw. Pliki w przeglądarce są tymczasowe. Kod i postęp są zapisywane w localStorage według `foundations-*`, bez zapisu do `.course/progress.json`.

B6.2 i dalsze doświadczenia lokalne korzystają z osobnego `~/mle-practice`. Biblioteki do C dodaje uczestnik, a Jupyter można uruchomić przez `uv run --with jupyterlab --with ipykernel jupyter lab`. PyTorch w F20 działa na CPU. Przykłady oznaczone `data-local-only` mają być wykonywane lokalnie; nie próbujemy pobierać PyTorch w Pyodide. Weryfikacja autora wykonuje je w swoim środowisku z CPU-owym PyTorch.

Przykłady pokazują inne małe problemy. Funkcje i testy uczestnika pozostają jego pracą. Katalog nie korzysta z gałęzi `solutions`. Identyfikatory A–F nie są numerami `course check` ani `catchup`.

## Diagramy i język

Tekst najpierw przedstawia problem, potem mały przykład i zadanie. Nowe terminy są wyjaśniane przed użyciem. Składnia, obliczenie i interpretacja wyniku są rozdzielone. Redakcja korzysta z technical-writing i unslop.

Dziesięć diagramów obejmuje: return i print, stan kernela, współdzielenie listy, dostępność cech w czasie, role danych, drzewo, przepływ przez sieć, attention, szukanie trasy i odroczoną nagrodę. Schematy służą pokazaniu relacji; rachunki, definicje i listy pozostają tekstem lub tabelą.

Styl pochodzi z `lectures/assets/course.css`: systemowy font, tło `--plane`, tekst `--ink`, opisy `--ink-2` i niebieski `--accent`. Każdy diagram ma samodzielny HTML w `diagrams/` i kopię SVG w lekcji. Weryfikator porównuje obie kopie oraz opisy dostępności. Przy zmianie aktualizuj oba miejsca. Nie dodajemy zewnętrznych fontów, rastrów ani animacji.

## Sprawdzanie zmian

Instrukcje tutora: [core.md](../../tutor/notes/core.md). Kontrole autora wykonuj z katalogu repozytorium:

```bash
uv sync
uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu "torch>=2.9,<2.10"
uv run --no-sync python tools/verify_foundations.py
uv run --no-sync ruff format --check tools
uv run --no-sync ruff check tools
uv run --no-sync --with playwright mypy tools
```

Przykłady PyTorch wymagają wersji CPU w środowisku autora. Opcja --no-sync zachowuje dodatkowo zainstalowany pakiet, bez pobierania całej grupy neural z wcześniejszej ścieżki. Nie uruchamiaj pełnych testów nieuzupełnionych zadań uczestnika jako zaliczenia nowych lekcji.

Kontrola przeglądarkowa wymaga opcjonalnego Playwright i Chromium:

```bash
uv run --with playwright python -m playwright install chromium --only-shell
uv run --with playwright python tools/verify_foundations_browser.py
```

Kontrola obejmuje układ na komputerze i telefonie, oba motywy diagramów, inicjalizację edytorów, zapis pracy i rzeczywiste wykonanie nieuzupełnionych sprawdzeń w Pyodide. Weryfikacja przykładów lokalnych obejmuje również małą pętlę sieci na CPU. Żadna z tych kontroli nie jest dowodem skuteczności dydaktycznej całej ścieżki.
