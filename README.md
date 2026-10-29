# ML Engineering from Scratch

Kurs po polsku: od pierwszego programu w Pythonie do samodzielnego eksperymentu i rozumienia ML/AI. Zawiera 70 lekcji w sekcjach A–F. Uczestnik pisze rozwiązania ćwiczeń samodzielnie.

Otwórz [mapę kursu](lectures/index.html). Jeśli zaczynasz od zera, przejdź do [A1: diagnoza podstaw](lectures/a1-diagnosis.html). Pierwsze ćwiczenia działają w przeglądarce; [A3](lectures/a3-environment.html) przeprowadza do lokalnego notebooka. Zapisuj ważne wyniki lokalnie: postęp przeglądarkowy pozostaje w tej przeglądarce.

| Sekcja | Lekcje | Czego się nauczysz |
|---|---:|---|
| A | 9 | Podstawy Pythona, notebook i pierwsza prognoza |
| B | 7 | Pliki, funkcje, błędy, testy i git |
| C | 13 | pandas, NumPy, statystyka i pierwszy model |
| D | 16 | Gradient, macierze, ocena, drzewa i klasyfikacja |
| E | 2 | Klasy i odtwarzanie eksperymentu |
| F | 23 | Generalizacja, prawdopodobieństwo, sieci, język i decyzje |

Każda lekcja podaje wymagania, przykład, zadanie i pytanie sprawdzające rozumienie. Zadania kodowe mają sprawdzenia, a zadania notebookowe kryteria samooceny. Diagramy wyjaśniają wybrane relacje. PyTorch działa na CPU; kurs nie wymaga GPU ani płatnych usług.

[Czternaście osobnych laboratoriów sekcji A, B i C](labs/index.html) jest gotowych do pilotażu. Zadania notebookowe A4.2, C8.3 i C12.2–C12.3 wykonujesz w labach. Sekcje D–F nie mają jeszcze osobnych labów.

Instrukcje dla autora: [utrzymanie kursu](docs/course-maintenance.md). [Podsumowanie przeglądów językowych](docs/reviews/af-language-review.md) opisuje przyjęte uwagi i decyzje redakcyjne. [Standard](docs/standard.md) i [słownik](docs/glossary.md) dotyczą tej samej ścieżki A–F.

## Laboratoria

Notebooki są bezpośrednio w folderze `labs`, a wszystkie dane kursu w `labs/data`:

- [A3: środowisko i restart kernela](labs/lab-a3.ipynb), po A3.
- [A2.1–A2.3: wartości, warunki i pętle](labs/lab-a2-1-a2-3.ipynb), utrwalenie A2.1–A2.3 po A3.
- [A2.4–A2.5: rekordy i funkcja](labs/lab-a2-4-a2-5.ipynb), po A2.4–A2.5 i A3.
- [A4.1–A4.2: prognoza i MAE](labs/lab-a4-1-a4-2.ipynb), po A4.1–A4.2 i A3.
- [B5.1: kopia i kolekcje](labs/lab-b5-1.ipynb).
- [B5.2–B5.3: pliki i błędy](labs/lab-b5-2-b5-3.ipynb).
- [B6.1–B6.2: funkcja i własne testy](labs/lab-b6-1-b6-2.ipynb).
- [B7.1–B7.2: moduł, narzędzia i git](labs/lab-b7-1-b7-2.ipynb).
- [C8.1–C8.2: tabela i opis liczb](labs/lab-c8-1-c8-2.ipynb).
- [C8.3: wykres odpowiada na pytanie](labs/lab-c8-3.ipynb).
- [C9.1–C9.2: tablice i osie](labs/lab-c9-1-c9-2.ipynb).
- [C10.1–C10.3: klucze, grupy i złączenia](labs/lab-c10-1-c10-3.ipynb).
- [C11.1–C11.2: czas i dostępność cech](labs/lab-c11-1-c11-2.ipynb).
- [C12.1–C12.3: pierwszy model na danych projektu](labs/lab-c12-1-c12-3.ipynb).

Pracuj we własnej kopii repozytorium. W terminalu przejdź do jej folderu `labs` i uruchom JupyterLab:

```bash
cd labs
UV_HTTP_TIMEOUT=300 UV_HTTP_RETRIES=10 UV_CONCURRENT_DOWNLOADS=2 uv run --no-project --python 3.12 --with jupyterlab --with ipykernel jupyter lab
```

Otwórz wybrany notebook z kernelem Python 3.12. Kod wykonujesz przez Shift+Enter, a plik zapisujesz przez Ctrl+S. Po uzupełnieniu zadań zrestartuj kernel i wykonaj komórki od początku. Czerwone sprawdzenie pustego startera oznacza zadanie do uzupełnienia. A3 jest doświadczeniem z kernelem, bez automatycznego zaliczenia.

Nie potrzeba oddzielnych paczek, pobierania danych ani bibliotek ML do sekcji A. Wszystkie notebooki uruchamiaj z tego samego folderu `labs`. Po pracy zatrzymaj kernel, a serwer Jupyter przez Ctrl+C w terminalu. Pytania do przemyślenia nie wymagają pisemnych odpowiedzi. Pilotaż z początkującymi uczestnikami jest jeszcze przed nami.

W B6 i B7 używasz tych samych plików `practice/summary.py` i `practice/test_summary.py`. To jeden wspólny mały projekt, nie folder na każdy notebook. Funkcja i testy są starterami do samodzielnego uzupełnienia; początkowe niepowodzenia są oczekiwane. Testy uruchamiaj ze wskazaniem `test_summary.py`, a nie wszystkich nieukończonych ćwiczeń.

B7 dodaje zależności do podprojektu `practice`. Kolejne notebooki korzystające z tych bibliotek uruchamiaj z `labs` przez `uv run --project ../practice --with jupyterlab --with ipykernel jupyter lab`. Wcześniejsze notebooki A i B działają z poleceniem tymczasowym pokazanym wyżej. W części Git pracujesz na własnej gałęzi kopii repozytorium; nie tworzysz drugiego repozytorium wewnątrz practice. GitHub i zdalne CI są opcjonalne.

Od C8.1 dodajesz w `practice` biblioteki sekcji C: `uv add numpy pandas matplotlib scikit-learn`, a notebooki C uruchamiasz z `labs` poleceniem z `--project ../practice` pokazanym wyżej. Lab C8.1–C8.2 podaje te polecenia. W C11 piszesz `practice/features.py` i `practice/test_features.py`; mypy potrzebuje tam `uv add --dev pandas-stubs`. Wyniki labów (B5, C12) trafiają do `labs/results`, poza Gitem. Plik `labs/data/project-holdout.csv` pozostaje nieotwarty do F21.5.

## Sprawdzenie materiałów przez autora

```bash
UV_HTTP_TIMEOUT=300 UV_HTTP_RETRIES=10 UV_CONCURRENT_DOWNLOADS=2 uv sync --locked --group neural
uv run --group neural python tools/verify_foundations.py
uv run ruff format --check tools practice
uv run ruff check tools practice
uv run mypy tools
uv run python tools/verify_labs.py
uv run python -m playwright install chromium --only-shell
uv run python tools/verify_foundations_browser.py
```

Grupa neural instaluje PyTorch z indeksu CPU. Kontrola przykładów wykonuje również małą sieć; kontrola przeglądarkowa sprawdza strony i rzeczywiste działanie Pyodide. Weryfikator notebooków obejmuje również startery testów B i C: pięć i trzy niepowodzenia są w nich celowe. Nie jest to wynik testów ukończonego rozwiązania uczestnika. Sprawdzenia nie uzupełniają jego kodu. Nie zastępują pilotażu z osobami początkującymi.

Treści: [CC BY 4.0](LICENSE-CONTENT.md). Kod: [MIT](LICENSE). Pochodzenie publicznego wycinka danych i opis danych syntetycznych: [materiały A–F](docs/course-maintenance.md#dane-i-końcowy-test).
