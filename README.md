# ML Engineering from Scratch

Otwarty kurs po polsku: od pierwszych programów w Pythonie do samodzielnych eksperymentów i rozumienia ML oraz AI.

Nowy rdzeń to [70 lekcji w sekcjach A–F](lectures/foundations/index.html). Najpierw poznasz Python, dane i prostą prognozę. Potem przejdziesz do uczenia modeli, ich oceny, generalizacji, prawdopodobieństwa, reprezentacji, sieci neuronowych i decyzji. Każde pojęcie sprawdzisz w małym przykładzie, własnym kodzie lub wyjaśnieniu.

## Dla kogo

Możesz zacząć bez doświadczenia programistycznego. Lekcja A1 pomoże Ci wybrać podstawy do nauki lub powtórki. Potrzebną matematykę wprowadzamy przed jej użyciem: od średniej i odległości, przez pochodną, do prawdopodobieństwa i reprezentacji.

Pierwsze ćwiczenia wykonasz w przeglądarce. W dalszej części przygotujesz lokalny notebook i niewielki projekt. Rdzeń nie wymaga GPU, konta w chmurze ani płatnego API. Małe sieci działają na CPU.

## Jak zacząć

1. Otwórz [mapę A–F](lectures/foundations/index.html), a następnie [A1: pierwszy program i diagnozę](lectures/foundations/a1-diagnosis.html).
2. Jeśli zaczynasz od zera, wykonaj A2 po kolei. Jeśli znasz podstawy, wybierz potrzebne powtórki na podstawie ćwiczeń.
3. W A3 przygotuj notebook. Przed każdą dalszą lekcją sprawdź podane wymagania.

Przykłady działają w HTML. W polach kodu piszesz rozwiązanie i korzystasz z przycisku Sprawdź. Zadania notebookowe i pytania o rozumienie mają widoczne kryteria oceny. Ważny kod zapisuj lokalnie: stan przeglądarki nie przenosi się automatycznie na inne urządzenie.

Identyfikatory A–F mają własne ćwiczenia i kryteria. Nie przekazuj ich do `course check` ani `catchup`, które obsługują wcześniejsze moduły liczbowe.

## Co obejmuje rdzeń

| Sekcja | Co przygotujesz lub wyjaśnisz |
|---|---|
| A | Pierwsze programy, notebook i mała prognoza |
| B | Funkcje, pliki, testy i własny moduł |
| C | Tabele, statystyka, wykresy, NumPy i pierwszy uczony model |
| D | Strata, gradient, macierze, porównanie modeli, drzewa i klasyfikacja |
| E | Własna klasa i odtworzenie eksperymentu |
| F | Generalizacja, niepewność, reprezentacje, sieci, modele językowe, search i decyzje |

W projekcie wybierasz model na walidacji i raz oceniasz zamrożone rozwiązanie na osobnym okresie. Finał obejmuje krótki raport i nowe przypadki wymagające uzasadnienia. Pełne wdrożenie nie jest dodatkowym warunkiem ukończenia.

Przykład A4 korzysta z publicznego [FreshRetailNet-50K](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K). Późniejszy mały projekt ma osobne, jawnie syntetyczne dane i odłożony test. Szczegóły pochodzenia, zakresu i kontroli opisuje [dokumentacja ścieżki](lectures/foundations/README.md).

## Tutor

Agent uruchomiony w katalogu kursu korzysta z `AGENTS.md`. Możesz pisać do niego po polsku, na przykład: „Utknąłem w C11.1” albo „Sprawdź moje wyjaśnienie z F19.2”. Tutor czyta aktualną lekcję, zadaje pytania i podaje wskazówki. Rozwiązania ćwiczeń piszesz samodzielnie.

Instrukcja konfiguracji tutora jest dostępna w [starszej lekcji środowiska](lectures/00-setup/index.html). Tutor jest pomocą, a nie wymaganiem rozpoczęcia kursu. Postępy przeglądarkowe nie zapisują się do `.course/progress.json`; notatki tutora są w `.course/progress.md`.

## Materiały do dalszej praktyki

[Wcześniejsza mapa modułów 00–19](lectures/legacy.html) pozostaje dostępna. Zawiera laboratoria Freshcast oraz rozszerzenia: pełny pakiet, CLI, magazyn obiektów, SQL, CI, Docker, pracę z cudzym kodem i sieci na GPU. Ta ścieżka ma własne wymagania sprzętowe i nie jest obowiązkową kontynuacją A/B.

Polecenia poniżej dotyczą tych wcześniejszych modułów:

| Polecenie | Co robi |
|---|---|
| `uv run course doctor` | Sprawdza środowisko i dobiera profil danych |
| `uv run course data` | Pobiera dane |
| `uv run course check 07` | Sprawdza zadania modułu 07 |
| `uv run course profile small` | Zmienia profil danych |
| `uv run course catchup 08` | Wpisuje kod referencyjny wcześniejszych modułów, zachowując kopię pracy |

Repozytorium: [RedHot099/mle-course](https://github.com/RedHot099/mle-course). Starsza instrukcja pracy wykorzystuje własny fork jako `origin` i repozytorium kursu jako `upstream`. Gałąź `solutions` i polecenie `catchup` odnoszą się do wcześniejszych laboratoriów, nie są zbiorem rozwiązań całej nowej ścieżki.

## Stan materiałów

Wszystkie 21 punktów planu A–F ma przygotowane lekcje. Materiały są gotowe do przeglądu autora i pilotażu z początkującymi. Sprawdzenia techniczne obejmują przykłady, nieuzupełnione zadania, linki, diagramy i działanie stron. Nie potwierdzają czasu nauki ani skuteczności dydaktycznej.

## Licencja

Kod: MIT (`LICENSE`). Treści: CC BY 4.0 (`LICENSE-CONTENT.md`). Autor: Jakub Eichner.

Dane FreshRetailNet-50K: Dingdong-Inc, CC BY 4.0. Wang i in., "FreshRetailNet-50K: A Stockout-Annotated Censored Demand Dataset for Latent Demand Recovery and Forecasting in Fresh Retail", arXiv:2505.16319. Dane syntetyczne do nowego projektu przygotowano na potrzeby kursu.
