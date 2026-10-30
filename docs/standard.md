# Standard pracy w kursie A–F

Reguły pomagają oceniać własny kod. Kolumna „Od” wskazuje lekcję, która wprowadza daną umiejętność. Wcześniej nie wymagamy narzędzi ani konstrukcji z późniejszych lekcji. Podczas review tutor podaje identyfikator reguły i konkretny przykład.

## Kod i testy

| ID | Reguła | Od |
|---|---|---|
| K2 | Opis funkcji podaje wejście, wynik, zachowanie przy brakujących danych i możliwe błędy. Opisuje działanie z perspektywy wywołującego. | B6.1 |
| K4 | Błędne dane powodują konkretny wyjątek z pomocnym komunikatem. Obsługa błędów rozróżnia typy wyjątków. | B5.3 |
| K9 | Formatowanie i lint przechodzą dla plików małego projektu; podstawowe adnotacje typów odpowiadają działaniu funkcji. | B7.1 |
| T2 | Test używa małych, jawnych danych i niezależnie ustalonego oczekiwanego wyniku. | B6.2 |
| T3 | Testy obejmują zera, brakujące obserwacje, pusty wynik, błędy i zachowanie wejścia, jeśli specyfikacja tego wymaga. | B6.2 |
| G4 | Sekrety i prywatne dane pozostają poza repozytorium. Przed commitem czytasz zmiany. Publiczne wycinki danych z licencją oraz dane syntetyczne dostarczone w kursie można wersjonować. | B7.2 |

## Dane i czas

| ID | Reguła | Od |
|---|---|---|
| D1 | Przed zmianą danych ustalasz klucz, typy i znaczenie brakujących wartości. Zero jest obserwacją, nie brakiem pomiaru. | C10.1 |
| D2 | Usuwanie i uzupełnianie danych ma uzasadnienie; zapisujesz, ilu wierszy dotyczy. Funkcja zachowuje wejście, jeśli tak podaje jej opis. | C10.1 |
| D3 | Złączenie ma jawne klucze i oczekiwaną liczność dopasowań. Sprawdzasz wiersze bez pary. | C10.3 |
| C1 | Przesunięcia i okna liczysz w uporządkowanej serii; sprawdzasz luki dni. | C11.1 |
| C2 | Każda cecha jest dostępna w zadeklarowanej chwili prognozy. Rozróżniasz zamrożony horyzont wielodniowy i codziennie aktualizowaną prognozę jednodniową. | C11.2 |
| C3 | Trening poprzedza walidację. Wiersz treningowy nie może mieć etykiety z późniejszego okresu oceny. | C12.2; etykiety jutra w D16.3 |
| C4 | Skalowanie i model dopasowujesz tylko na treningu. | C12.3 |
| C5 | Ustawienia wybierasz na walidacji. Holdout służy do jednej końcowej oceny zamrożonego wyboru; wcześniejsze obejrzenie zapisujesz jako ograniczenie. | C12.2, finał F21.5 |
| C6 | Baseline i model oceniasz na tych samych wierszach, w tych samych jednostkach i według tego samego protokołu. | C12.2 |
| E1 | Zapis eksperymentu pozwala odtworzyć dane, cechy, ustawienia, protokół i wynik po restarcie środowiska. | E17.2 |

Przed review wykonaj sprawdzenia z bieżącej lekcji. Wyniki sprawdzeń dołącz do wyjaśnienia. Jeśli czegoś nie da się uruchomić, podaj ograniczenie. Poprawny rachunek na małej próbce nie dowodzi jakości modelu na przyszłych danych.
