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

[Dwadzieścia osobnych laboratoriów sekcji A–D](labs/index.html) jest gotowych do pilotażu. Zadania notebookowe A4.2, C8.3 i C12.2–C12.3 wykonujesz w labach. Sekcje E–F nie mają jeszcze osobnych labów.

Instrukcje dla autora: [utrzymanie kursu](docs/course-maintenance.md). [Podsumowanie przeglądów językowych](docs/reviews/af-language-review.md) opisuje przyjęte uwagi i decyzje redakcyjne. [Standard](docs/standard.md) i [słownik](docs/glossary.md) dotyczą tej samej ścieżki A–F.

## Laboratoria

Notebooki są bezpośrednio w folderze `labs`, ponumerowane w kolejności wykonywania, a wszystkie dane kursu w `labs/data`:

- [Lab 1 · Notebook, który działa po restarcie](labs/lab-01-notebook.ipynb), wykład A3.
- [Lab 2 · Co naprawdę jest pomiarem](labs/lab-02-pomiary.ipynb), wykłady A2.1, A2.2, A2.3.
- [Lab 3 · Rekordy i funkcja, z której można skorzystać ponownie](labs/lab-03-rekordy-i-funkcja.ipynb), wykłady A2.4, A2.5.
- [Lab 4 · Prognoza powstaje przed oceną](labs/lab-04-prognoza-i-ocena.ipynb), wykłady A4.1, A4.2.
- [Lab 5 · Kopia i kolekcja to dwie różne decyzje](labs/lab-05-kopie-i-kolekcje.ipynb), wykład B5.1.
- [Lab 6 · Odczyt, zapis i błędne dane](labs/lab-06-pliki-i-bledy.ipynb), wykłady B5.2, B5.3.
- [Lab 7 · Funkcja i testy wykrywające błąd](labs/lab-07-funkcja-i-testy.ipynb), wykłady B6.1, B6.2.
- [Lab 8 · Moduł, narzędzia i historia zmiany](labs/lab-08-modul-i-git.ipynb), wykłady B7.1, B7.2.
- [Lab 9 · Tabela i opis liczb](labs/lab-09-tabela-i-opis.ipynb), wykłady C8.1, C8.2.
- [Lab 10 · Wykres odpowiada na pytanie](labs/lab-10-wykres.ipynb), wykład C8.3.
- [Lab 11 · Tablice i osie](labs/lab-11-tablice-i-osie.ipynb), wykłady C9.1, C9.2.
- [Lab 12 · Klucze, grupy i złączenia](labs/lab-12-klucze-grupy-zlaczenia.ipynb), wykłady C10.1, C10.2, C10.3.
- [Lab 13 · Czas i dostępność cech](labs/lab-13-czas-i-cechy.ipynb), wykłady C11.1, C11.2.
- [Lab 14 · Pierwszy model na danych projektu](labs/lab-14-pierwszy-model.ipynb), wykłady C12.1, C12.2, C12.3.
- [Lab 15 · Strata i uczenie](labs/lab-15-strata-i-uczenie.ipynb), wykłady D13.1, D13.2, D13.3, D13.4.
- [Lab 16 · Wektory i macierze](labs/lab-16-wektory-i-macierze.ipynb), wykłady D13.5, D13.6.
- [Lab 17 · Uczciwe porównanie](labs/lab-17-uczciwe-porownanie.ipynb), wykłady D14.1, D14.2, D14.3.
- [Lab 18 · Cechy i drzewa](labs/lab-18-cechy-i-drzewa.ipynb), wykłady D15.1, D15.2, D15.3.
- [Lab 19 · Prognoza wielodniowa](labs/lab-19-prognoza-wielodniowa.ipynb), wykład D15.4.
- [Lab 20 · Prawdopodobieństwo i alarm](labs/lab-20-prawdopodobienstwo-i-alarm.ipynb), wykłady D16.1, D16.2, D16.3.

Pracuj we własnej kopii repozytorium. W terminalu przejdź do jej folderu `labs` i uruchom JupyterLab:

```bash
cd labs
UV_HTTP_TIMEOUT=300 UV_HTTP_RETRIES=10 UV_CONCURRENT_DOWNLOADS=2 uv run --no-project --python 3.12 --with jupyterlab --with ipykernel jupyter lab
```

Otwórz wybrany notebook z kernelem Python 3.12. Kod wykonujesz przez Shift+Enter, a plik zapisujesz przez Ctrl+S. Po uzupełnieniu zadań zrestartuj kernel i wykonaj komórki od początku. Czerwone sprawdzenie pustego startera oznacza zadanie do uzupełnienia. A3 jest doświadczeniem z kernelem, bez automatycznego zaliczenia.

Nie potrzeba oddzielnych paczek, pobierania danych ani bibliotek ML do sekcji A. Wszystkie notebooki uruchamiaj z tego samego folderu `labs`. Po pracy zatrzymaj kernel, a serwer Jupyter przez Ctrl+C w terminalu. Pytania do przemyślenia nie wymagają pisemnych odpowiedzi. Pilotaż z początkującymi uczestnikami jest jeszcze przed nami.

W B6 i B7 używasz tych samych plików `practice/summary.py` i `practice/test_summary.py`. To jeden wspólny mały projekt, nie folder na każdy notebook. Funkcja i testy są starterami do samodzielnego uzupełnienia; początkowe niepowodzenia są oczekiwane. Testy uruchamiaj ze wskazaniem `test_summary.py`, a nie wszystkich nieukończonych ćwiczeń.

B7 dodaje zależności do podprojektu `practice`. Kolejne notebooki korzystające z tych bibliotek uruchamiaj z `labs` przez `uv run --project ../practice --with jupyterlab --with ipykernel jupyter lab`. Wcześniejsze notebooki A i B działają z poleceniem tymczasowym pokazanym wyżej. W części Git pracujesz na własnej gałęzi kopii repozytorium; nie tworzysz drugiego repozytorium wewnątrz practice. GitHub i zdalne CI są opcjonalne.

Od C8.1 dodajesz w `practice` biblioteki sekcji C: `uv add numpy pandas matplotlib scikit-learn`, a notebooki C uruchamiasz z `labs` poleceniem z `--project ../practice` pokazanym wyżej. Lab 9 podaje te polecenia. W C11 piszesz `practice/features.py` i `practice/test_features.py`; mypy potrzebuje tam `uv add --dev pandas-stubs`. W D14 dochodzi `practice/metrics.py` z `practice/test_metrics.py`. Laby D używają tych samych bibliotek co C i danych projektu. Wyniki labów (B5, C12) trafiają do `labs/results`, poza Gitem. Plik `labs/data/project-holdout.csv` pozostaje nieotwarty do F21.5.

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

Grupa neural instaluje PyTorch z indeksu CPU. Kontrola przykładów wykonuje również małą sieć; kontrola przeglądarkowa sprawdza strony i rzeczywiste działanie Pyodide. Weryfikator notebooków obejmuje również startery testów B, C i D: pięć, trzy i trzy niepowodzenia są w nich celowe. Nie jest to wynik testów ukończonego rozwiązania uczestnika. Sprawdzenia nie uzupełniają jego kodu. Nie zastępują pilotażu z osobami początkującymi.

Treści: [CC BY 4.0](LICENSE-CONTENT.md). Kod: [MIT](LICENSE). Pochodzenie publicznego wycinka danych i opis danych syntetycznych: [materiały A–F](docs/course-maintenance.md#dane-i-końcowy-test).
