# Przegląd języka i zrozumiałości A–F

Przegląd obejmował 70 lekcji na feature/foundations-ab, w wersji c41404e. Oba modele przeczytały cały tekst lekcji, bez uruchamiania przeglądarki i przykładów. Weryfikację techniczną po poprawkach przeprowadził autor zmian.

- Fable: claude-fable-5-1. Zadania, testy, podpowiedzi, mapy i teksty diagramów przeczytane; rachunki testów sprawdzone ręcznie.
- Opus: claude-opus-5-5. Zadania, podpowiedzi i teksty diagramów przeczytane; kilka dłuższych skryptów sprawdzających odczytanych tylko częściowo.
- Grok: niedostępny w konfiguracji dostawcy. Przegląd niewykonany, bez zastępowania innym modelem.

F i O oznaczają punkty raportów Fable i Opus. Uwagi porównano z treścią, a nie przyjęto automatycznie.

| Uwagi | Decyzja |
|---|---|
| F1, O2 | Przyjęte: 11 rubryk „Sprawdź swoją pracę” z kryteriami rzeczywistego zadania. Pytania kontrolne pozostają dodatkowym sprawdzeniem pojęcia. |
| F2–3, O1 | Przyjęte konkretne luki C8.1: przykład maski i .loc na innej tabeli, assign z istniejącą kolumną units, instalacja przed lekcją. Odczyt CSV projektu przeniesiony do C12.2. |
| F4, O11 | Przyjęte: D16.3 ma trening 1–5 przygotowany wieczorem dnia 6, wiersze 6–7 do prognoz na dni 7–8 i nieznaną ostatnią etykietę. Poprawiono exp(0). |
| F5, O2 | Przyjęte: pytanie o lukę na wykresie jest jawnie hipotetyczne. |
| F6, O8–9 | Przyjęte: usunięto wtręt o fakturach i cache; keep ma wyjaśnienie i zrozumiałą podpowiedź. |
| F7, O7 | Przyjęte: standaryzacja jest wprowadzona wzorem i ręcznym rachunkiem w C12.3. |
| F8, O5 | Przyjęte: poprawiono etykiety w D16.1 i rozróżnienie braku pomiaru od niedostępności towaru. |
| F9, O3 | Przyjęte: utworzenie README w B7.1 i link do checks.yml w B7.2. |
| F10, O14 | Przyjęte: A1 odsyła do tabeli powyżej. |
| F11, O15 | Przyjęte: wprowadzenie i link standardu, identyfikatory z opisami w nawiasach. Standard dotyczy A–F. |
| F12, O7, O9 | Przyjęte: usunięto nieobjaśnione listy frameworków, SHAP, ABC, Protocol i uwagi autora; hiperparametry oraz estymator mają definicje. Pytanie o przyczynowość używa znanych pojęć. |
| F13, O1 | Częściowo: wspólne wskazówki pracy, nazwa sekcji wyjaśnienia i osiem pytań przy trudnych przejściach. Odrzucono obowiązkowy quiz w każdej C–F i wyrównywanie liczby słów: rachunki oraz doświadczenia już wymagają aktywnego użycia, a dopisywanie dla długości zwiększa obciążenie. |
| F14, O15 | Przyjęte wybrane formy neutralne w A2.5, A3, B5.2, B7.2 i F21.1. |
| F15 | Przyjęte: iteracja, wspólna nazwa prognozy jednodniowej, uv „na podstawie” instrukcji, licznik bez narzuconej nazwy i objaśnienie +=. |
| O1 | Przyjęte konkretne luki: rolling, dziedziczenie, Adam, epoka, no_grad, urządzenie, optymalizator i batch mają objaśnienia. |
| O4 | Przyjęte: backup służy do odtworzenia; błąd wprowadzany jest w importowanym summary.py. |
| O5 | Częściowo: doprecyzowano niedostępność towaru, brak pomiaru, cechę 0 i wartość niewidzianą w treningu. Odrzucono globalny zakaz słowa „brak” i zamianę każdego stockoutu na „wyczerpanie”: brak pliku jest naturalny, a niedostępność nie dowodzi wyczerpania zapasu. |
| O6 | Przyjęte: and w A2.2 i if wewnątrz for w A2.3, z objaśnieniem wcięcia na innych danych. |
| O10, O12–13 | Przyjęte: numery dni, jawnie zamrożona prognoza tygodniowa w pytaniu o lag i trzecia kategoria dla klastrowania bez odpowiedzi do odtworzenia. |
| O14–15 | Przyjęte: wynik Pythona, mediana po sortowaniu, dni oceny, token notebooka, PCA, chain rule, attention, niepewność i przykład przyczynowości. Linki źródłowe mają nazwy źródeł. |

Zachowano angielskie nazwy API z polskim objaśnieniem, krótkie lekcje D13, stopniowane podpowiedzi, zero różne od braku pomiaru i ograniczenia małych przykładów. Nie dodano formalnych dowodów, sprawdzania wypowiedzi słowami kluczowymi ani rozwiązań zadań.

Po przeglądzie usunięto wcześniejsze moduły, laboratoria i zależne narzędzia. Konfiguracja, tutor, słownik, standard i środowisko dotyczą jednej ścieżki A–F. Notatki docs/research są zapisem analizy autora, nie drugim kursem.

Kontrola końcowa: 70 lekcji, 29 quizów, 56 edytorów, 94 wykonane przykłady i 11 rubryk. Wszystkie wymagania wskazują wcześniejsze lekcje. Przeglądarka: układ 1280 i 390 px, oba motywy diagramów, zapis i reset kodu, informacja zwrotna quizu oraz 55 sprawdzeń nieuzupełnionych zadań w rzeczywistym Pyodide. Formatowanie, lint i mypy przechodzą dla narzędzi autora. Repozytorium nie ma konfiguracji SonarCloud ani oddzielnego zestawu testów autora; pełną kontrolą materiałów są dwa skrypty verify_foundations.

Dodatkowo doprecyzowano F18.2: prosty rachunek używa MSE z karą, natomiast Ridge ze scikit-learn sumy kwadratów błędów z karą. Nie przenosimy wartości alpha pomiędzy tymi konwencjami bez przeliczenia. Wyjaśniono także różne znaczenia słowa bias.
