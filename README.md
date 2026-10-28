# ML Engineering from Scratch

Kurs po polsku: od pierwszego programu w Pythonie do samodzielnego eksperymentu i rozumienia ML/AI. Zawiera 70 lekcji w sekcjach A–F. Uczestnik pisze rozwiązania ćwiczeń samodzielnie.

Otwórz [mapę kursu](lectures/index.html). Jeśli zaczynasz od zera, przejdź do [A1: diagnoza podstaw](lectures/foundations/a1-diagnosis.html). Pierwsze ćwiczenia działają w przeglądarce; [A3](lectures/foundations/a3-environment.html) przeprowadza do lokalnego notebooka. Zapisuj ważne wyniki lokalnie: postęp przeglądarkowy pozostaje w tej przeglądarce.

| Sekcja | Lekcje | Czego się nauczysz |
|---|---:|---|
| A | 9 | Podstawy Pythona, notebook i pierwsza prognoza |
| B | 7 | Pliki, funkcje, błędy, testy i git |
| C | 13 | pandas, NumPy, statystyka i pierwszy model |
| D | 16 | Gradient, macierze, ocena, drzewa i klasyfikacja |
| E | 2 | Klasy i odtwarzanie eksperymentu |
| F | 23 | Generalizacja, prawdopodobieństwo, sieci, język i decyzje |

Każda lekcja podaje wymagania, przykład, zadanie i pytanie sprawdzające rozumienie. Zadania kodowe mają sprawdzenia, a zadania notebookowe kryteria samooceny. Diagramy wyjaśniają wybrane relacje. PyTorch działa na CPU; kurs nie wymaga GPU ani płatnych usług.

Instrukcje dla autora: [utrzymanie kursu](lectures/foundations/README.md). [Podsumowanie przeglądów językowych](docs/reviews/af-language-review.md) opisuje przyjęte uwagi i decyzje redakcyjne. [Standard](docs/standard.md) i [słownik](docs/glossary.md) dotyczą tej samej ścieżki A–F.

## Sprawdzenie materiałów przez autora

```bash
UV_HTTP_TIMEOUT=300 UV_HTTP_RETRIES=10 UV_CONCURRENT_DOWNLOADS=2 uv sync --locked --group neural
uv run --group neural python tools/verify_foundations.py
uv run ruff format --check tools
uv run ruff check tools
uv run mypy tools
uv run python -m playwright install chromium --only-shell
uv run python tools/verify_foundations_browser.py
```

Grupa neural instaluje PyTorch z indeksu CPU. Kontrola przykładów wykonuje również małą sieć; kontrola przeglądarkowa sprawdza strony i rzeczywiste działanie Pyodide. Sprawdzenia nie uzupełniają rozwiązań uczestnika. Nie zastępują pilotażu z osobami początkującymi.

Treści: [CC BY 4.0](LICENSE-CONTENT.md). Kod: [MIT](LICENSE). Pochodzenie publicznego wycinka danych i opis danych syntetycznych: [materiały A–F](lectures/foundations/README.md#dane-i-końcowy-test).
