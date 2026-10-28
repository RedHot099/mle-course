# Laboratoria kursu A–F

[Otwórz stronę laboratoriów sekcji A](index.html). Cztery laby są dostępne pilotażowo:

| Lab | Kiedy | Wynik pracy |
|---|---|---|
| [A00](lab-a00/README.md) | Po A3 | Zapisany notebook i doświadczenie z restartem kernela |
| [A01](lab-a01/README.md) | Po A3, utrwalenie A2.1–A2.3 | Rozróżnienie zer i braków, podsumowanie listy |
| [A02](lab-a02/README.md) | Po A2.4–A2.5 i A3 | Obliczenia na rekordach i własna funkcja |
| [A03](lab-a03/README.md) | Po A4.1–A4.2 i A3 | Prognoza zamrożona przed oceną, MAE i interpretacja |

A1 jest diagnozą, a nie dodatkowym zadaniem do przepisania. Własne dowody opanowania podstaw mogą skrócić powtórkę w A01. Przy problemach instalacyjnych można najpierw pracować w ćwiczeniach przeglądarkowych, a lokalne notebooki uzupełnić później.

Pobierz ZIP i rozpakuj do `~/mle-practice/labs/`, zgodnie z README danego labu. Uczestnik pracuje we własnej kopii. Nie uruchamiaj poleceń wymagających rozwiązania wszystkich nierozwiązanych notebooków naraz. Obecne laby nie korzystają z `coursekit`, gałęzi `solutions` ani danych końcowego testu.

## Weryfikacja autora

Z katalogu repozytorium:

```bash
uv run python tools/build_labs.py --check
uv run python tools/verify_labs.py
```

Pierwsze polecenie porównuje paczki do pobrania z materiałami źródłowymi. Po zmianie labu odtwórz paczki przez `uv run python tools/build_labs.py`.

Drugie polecenie sprawdza manifest, notebooki bez zapisanych wyjść, składnię, przygotowanie danych i wykonanie w świeżych kernelach. Dla każdego sprawdzenia wykonuje trzy próby: wartości oczekiwane z fixtures, pusty starter i błędne wyniki. Dla funkcji używa Mock zwracającego skończony zestaw wartości z jawnej tabeli przypadków. To sprawdza checker i jego wywołanie, nie stanowi implementacji zadania ani dowodu poprawności przyszłego kodu uczestnika. Nie ma referencyjnych funkcji rozwiązujących laby.

A00 ma rubrykę doświadczenia, bez automatycznego zaliczenia. Weryfikator osobno wykonuje próbę pamięci w dwóch świeżych kernelach. Wyjaśnienia, własne dodatkowe przypadki oraz pełne rozwiązania wymagają review pracy uczestnika.

Manifest obejmuje wszystkie 9 lekcji A, w tym A1 jako diagnozę. Sekcje B–F mają [plan laboratoriów](../docs/plans/af-laboratories.md), ale nie są jeszcze wdrożone. Gotowość techniczna pilotażu nie oznacza zakończonego pilotażu z osobami początkującymi.
