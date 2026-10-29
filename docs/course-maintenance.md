# Utrzymanie ścieżki A–F

Punkt wejścia: [mapa 70 lekcji](../lectures/index.html). Nowy rdzeń obejmuje wszystkie 21 punktów uzgodnionego planu A–F. [Plan i kontrola kolejności](research/beginner-curriculum-audit.md) wyjaśniają zakres.

## Osobne laboratoria

[Czternaście labów A, B i C](../labs/index.html) znajduje się bezpośrednio w labs/. Wspólne dane są w labs/data/. Uruchamianie i kontrole autora opisuje [główne README](../README.md). Pełne zadania A3, A4.2, C8.3 i C12.2–C12.3 wykonuje się w labach; krótkie ćwiczenia w wykładach pozostają rozgrzewką. B6 i B7 rozwijają wspólny podprojekt practice z własną funkcją i testami; C11 dodaje tam features.py z testem izolacji serii. C12 zapisuje przebieg projektu w labs/results/c12-project.json. Laby D–F nie są jeszcze wdrożone.

## Pokrycie planu

| Sekcja | Punkty planu | Lekcje | Zakres |
|---|---|---:|---|
| A | 1–4 | 9 | Diagnoza, Python, notebook, pierwsza prognoza |
| B | 5–7 | 7 | Kolekcje, pliki, błędy, funkcje, testy, moduł i git |
| C | 8–12 | 13 | Tabele, statystyka, wykresy, NumPy, relacje, czas, estimator i Pipeline |
| D | 13–16 | 16 | Strata, pochodne, gradient, macierze, ocena, drzewa i klasyfikacja |
| E | 17 | 2 | Własna klasa i odtworzenie eksperymentu |
| F | 18–21 | 23 | Generalizacja, prawdopodobieństwo, reprezentacje, sieci, język, search i decyzje |

Źródłem identyfikatorów, kolejności i wymagań jest [curriculum.json](../lectures/curriculum.json). Treść lekcji znajduje się bezpośrednio w HTML. Weryfikator sprawdza kompletność katalogu, pokrycie punktów 1–21 i to, że wymagania nie wskazują późniejszych lekcji. Ścieżka jest gotowa do przeglądu autora i pilotażu. Sprawdzenia techniczne nie zastępują obserwacji początkujących uczestników.

Zadania na stronach mają dwa rodzaje zakończenia. Edytory z przyciskiem Sprawdź sprawdzają wynik małego ćwiczenia. Zadania notebookowe i wyjaśnienia mają jawne kryteria w rozwijanej części „Sprawdź swoją pracę” przy zadaniu, a pytania kontrolne w sekcji „Sprawdź, co pamiętasz”. Nie pozorujemy ich zaliczenia przez szukanie słów kluczowych. Tutor wymaga wyniku, ręcznego przykładu i wyjaśnienia na nowych danych.

## Kolejność i źródła

Statystyka w C8 poprzedza scaler, geometria w F20.1 poprzedza k-means, a rzut i wariancja poprzedzają PCA. Model w C12 poprzedza wyprowadzanie algorytmu w D13. Prawdopodobieństwo i likelihood poprzedzają log-loss, a iloczyn skalarny i softmax poprzedzają attention. E17 nie jest warunkiem rozumienia F18 ani F19; wraca przy własnej klasie sieci.

Inspiracje programowe opisano w [notatce źródłowej](research/beginner-course-sources.md). CS229 stanowi punkt odniesienia dla modelowania, generalizacji i probabilistycznego spojrzenia na uczenie. CS221 rozszerza zakres o search, inference i decyzje. Nie kopiujemy ich tempa, wymagań wejściowych ani pełnego zakresu.

Sprawdzone materiały pierwotne:

- [Stanford SEE, CS229](https://see.stanford.edu/Course/CS229).
- [Stanford CS221, Autumn 2025](https://stanford-cs221.github.io/autumn2025/).
- [Stanford CS336, Spring 2025](https://cs336.stanford.edu/spring2025/index.html), jako granica dalszej specjalizacji językowej.
- [pandas: wybór danych](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html).
- [scikit-learn: Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.make_pipeline.html), [Naive Bayes](https://scikit-learn.org/stable/modules/naive_bayes.html).
- [PyTorch: autograd](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html), [własny model](https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html).

Wyjaśnienia, ćwiczenia i dane syntetyczne są autorskie. Biblioteki służą do wykonywania eksperymentów, a nie zastępują wyjaśnienia pojęć. Pełne wdrożenie, GPU, ABC, Protocol, zaawansowane generyki, tuning i trenowanie LLM pozostają rozszerzeniami.

## Dane i końcowy test

`labs/data/freshcast-sample.csv` zawiera 14 kolejnych obserwacji: sklep 70, produkt 116, 2024-03-28–2024-04-10. To wycinek publicznego zbioru [FreshRetailNet-50K](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K), Dingdong-Inc, CC BY 4.0. Zachowano `sale_amount`; `stock_hour6_22_cnt` nazwano `stockout_hours`. Cały wycinek jest widoczny w A4, więc nie służy jako zamknięty test.

`labs/data/c-panel-sales.csv` i `labs/data/c-items.csv` to syntetyczny panel trzech produktów z dni 1–6 dla C10 i C11: wiersze celowo nieuporządkowane, jedna kopia wiersza pear dnia 3, brak sprzedaży plum dnia 4 i brak dnia 5 u apple, a w opisach brak produktu plum. Laby zapisują decyzję: kopię usuwamy, brak sprzedaży zostaje.

Projekt od C12 korzysta z osobnych, jawnie syntetycznych danych: 56 dni od 2024-01-01. Pierwsze 49 są w `project-development.csv`, ostatnie 7 w `project-holdout.csv`. Trening obejmuje dni 1–42, walidacja 43–49, test 50–56. Wartości wygenerowano z trendu, cyklu tygodniowego i niewielkiego szumu, bez danych klientów. To demonstracja procesu, nie pomiar jakości biznesowej. Na tych danych baseline „tak samo jak wczoraj” ma na walidacji niższe MAE niż regresja z lag 1; lab C12 wymaga zapisania tego wyniku, nie ukrycia go.

Projekt zaczyna od codziennie aktualizowanej prognozy jednodniowej: rzeczywisty poprzedni dzień może być cechą kolejnego. Zamrożony horyzont wielodniowy jest osobnym doświadczeniem D15.4. Finał F21.5 nie zmienia po fakcie protokołu C12. Plik holdoutu jest dostępny w repozytorium; ograniczenie jest dydaktyczne. Jeśli uczestnik obejrzy go wcześniej, odnotowuje to i nie nazywa późniejszego wyniku niezależnym testem.

## Środowisko i zapis pracy

Pola kodu używają istniejącego `course.js`, który ładuje Pyodide i potrzebne biblioteki przy pierwszym imporcie. Każde wykonanie zaczyna w osobnej przestrzeni nazw. Pliki w przeglądarce są tymczasowe. Kod i postęp są zapisywane w localStorage według `foundations-*`, bez zapisu do `.course/progress.json`.

B6 i B7 używają wspólnego podprojektu practice w kopii repozytorium kursu. Biblioteki do C dodaje uczestnik w practice; Jupyter uruchamia z labs przez `uv run --project ../practice --with jupyterlab --with ipykernel jupyter lab`. PyTorch w F20 działa na CPU. Przykłady oznaczone `data-local-only` mają być wykonywane lokalnie; nie próbujemy pobierać PyTorch w Pyodide. Weryfikacja autora wykonuje je w swoim środowisku z CPU-owym PyTorch.

Przykłady pokazują inne małe problemy. Funkcje i testy uczestnika pozostają jego pracą. Katalog nie korzysta z gałęzi `solutions`. Identyfikatory A–F określają lekcje i ich wymagania.

## Diagramy i język

Tekst najpierw przedstawia problem, potem mały przykład i zadanie. Nowe terminy są wyjaśniane przed użyciem. Składnia, obliczenie i interpretacja wyniku są rozdzielone. Redakcja korzysta z technical-writing i unslop.

Dziesięć diagramów obejmuje: return i print, stan kernela, współdzielenie listy, dostępność cech w czasie, role danych, drzewo, przepływ przez sieć, attention, szukanie trasy i odroczoną nagrodę. Schematy służą pokazaniu relacji; rachunki, definicje i listy pozostają tekstem lub tabelą.

Styl pochodzi z `lectures/assets/course.css`: systemowy font, tło `--plane`, tekst `--ink`, opisy `--ink-2` i niebieski `--accent`. Każdy diagram ma samodzielny HTML w `diagrams/` i kopię SVG w lekcji. Weryfikator porównuje obie kopie oraz opisy dostępności. Przy zmianie aktualizuj oba miejsca. Nie dodajemy zewnętrznych fontów, rastrów ani animacji.

## Sprawdzanie zmian

Instrukcje tutora: [core.md](../tutor/notes/core.md). Polecenia kontroli autora znajdują się w [głównym README](../README.md#sprawdzenie-materiałów-przez-autora).

Weryfikator sprawdza katalog, wymagania, linki, diagramy, przykłady i nieuzupełnione startery. Kontrola przeglądarkowa obejmuje komputer i telefon, oba motywy diagramów, zapis pracy i rzeczywiste wykonanie sprawdzeń w Pyodide. Grupa neural zapewnia PyTorch CPU do wykonania przykładów lokalnych. Żadna z tych kontroli nie jest dowodem skuteczności dydaktycznej całej ścieżki.
