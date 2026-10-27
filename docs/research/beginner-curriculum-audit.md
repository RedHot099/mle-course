# Jak przebudować kurs dla początkującej osoby

Audyt z 27 października 2026, zaktualizowany po uwagach autora o przewadze infrastruktury nad rozumieniem ML/AI. Stan analizowanego repozytorium: `951c88c`, gałąź `main`. Dokument proponuje zmiany. Nie zmienia zadań ani nie zawiera ich rozwiązań.

## Najważniejsza decyzja

Rekomenduję zachować projekt Freshcast oraz podstawy jakości kodu, ale zmienić moment, w którym uczestnik musi je samodzielnie realizować. Najpierw powinien zbudować małą, zrozumiałą prognozę i umieć ją ocenić. Następnie porządkuje rozwiązanie w funkcje, testy i prosty moduł. Po zdobyciu tych kompetencji przechodzi do głębszego rozumienia uczenia, niepewności, reprezentacji i szerszych metod AI.

Usuwam z rdzenia wcześniejsze punkty propozycji: 18 "Pipeline i odtwarzalność", 20 "CI, kontener i praca z cudzym kodem" oraz 21 "Capstone główny". Ich miejsce zajmuje blok pojęciowy opisany poniżej. SQL z wcześniejszego punktu 19 może pozostać dodatkiem po tabelach; storage trafia do opcjonalnej ścieżki inżynierskiej. Odtwarzalny eksperyment i uczciwa walidacja nadal są potrzebne, ale nie wymagają osobnego projektu produkcyjnego.

Obecny kurs jest bliższy intensywnemu kursowi dla osoby, która już swobodnie programuje w Pythonie, niż nauce od zera. [README](../../README.md#dla-kogo) uczciwie wymaga pętli, funkcji, list i słowników. Hasło "od podstaw Pythona" może jednak sugerować inny poziom wejścia. Potrzebne są dwie ścieżki wejścia, zakończone tym samym sprawdzianem podstaw.

Nie da się obiecać, że nikt nigdy nie utknie. Można natomiast zaprojektować kurs tak, aby każda trudność miała rozpoznawalną przyczynę, krótkie ćwiczenie naprawcze i drogę dalszej nauki bez kopiowania całego rozwiązania.

## Co sprawdzono i czego jeszcze nie wiemy

Przejrzałem mapę wszystkich 20 modułów, strukturę wykładów i notebooków, README labów, wymagania zadań, cele w notatkach tutora, słowniczek, standard, ADR oraz mechanizm `check`, zapisu postępu i `catchup`. Szczegółowe porównanie wymagań dotyczy zwłaszcza modułów 00–08 oraz przejść do 09, 13, 15, 18 i 19. Nie otwierałem kodu na gałęzi `solutions` ani nie rozwiązywałem ćwiczeń.

To audyt programu i materiałów, a nie obserwacja zachowania uczestników. W tym checkoutcie nie było `.course/progress.md` ani `.course/progress.json`, więc nie ma podstaw do twierdzeń o rzeczywistych odsetkach rezygnacji lub czasie nauki. Ocena trudności i nowy program są moją rekomendacją, którą trzeba sprawdzić w pilotażu.

Porównanie z innymi kursami opiera się na publicznych stronach organizatorów i syllabusach. Nie oznacza ukończenia płatnych kursów ani oceny wszystkich ich ćwiczeń. Szczegóły, linki i ograniczenia znajdują się w [notatce źródłowej](beginner-course-sources.md). Dane o ocenach, liczbie zapisów i obietnicach zatrudnienia nie są podstawą rekomendacji.

## Co już działa i warto zachować

- Zadania mają konkretne wejścia, wyniki i zachowania błędów. W labach 01–08 układ "Cel, Gdzie, Wejście, Wynik, Skorzystaj z, Kroki, Sprawdzenie" ogranicza zgadywanie.
- Uczestnik pisze kod, zamiast tylko oglądać gotowe notebooki. To dobry fundament kursu praktycznego.
- Sprawdzenia pracują na małych przykładach i podają rozbieżność. Pozwalają oddzielić błąd implementacji od problemu na dużym zbiorze.
- Testy mutacyjne w 04, 05 i 15 pokazują, dlaczego zielony test może niczego nie chronić. Zachowałbym je po krótkim wprowadzeniu do zwykłych testów.
- Leakage, baseline, jawne założenia o danych i ocena na tych samych wierszach przewijają się przez projekt. To ważniejsze niż kolekcjonowanie modeli.
- `small`, lokalne atrapy usług i ścieżka bez tutora ograniczają zależności sprzętowe i usługowe.
- Moduł Shelfwise uczy pracy z cudzym kodem i odtwarzania objawu. Warto zachować go jako opcjonalny materiał dla osób wybierających dalszą ścieżkę inżynierską.

Kurs ma już też poprawkę kolejności pojęć. [Wykład 03](../../lectures/03-classes/index.html#prognoza) tłumaczy prognozę, horyzont, holdout i MAE przed klasami. [ADR 0001](../adr/0001-concept-before-interface.md) świadomie zachowuje dotychczasowy łańcuch labów. Nie rekomenduję ponownego dodania brakujących definicji. Rekomenduję osobną praktykę przed zadaniem wymagającym kilku nowych abstrakcji naraz.

## Gdzie początkujący może się zatrzymać

| Miejsce i dowód w repozytorium | Co uczestnik musi połączyć | Proponowana zmiana |
|---|---|---|
| [00: setup](../../lectures/00-setup/index.html) | WSL, terminal, fork, środowisko, editor, dane, autoryzacja i pierwszy PR przed pierwszym labem | Oddzielić uruchomienie pierwszej komórki od pełnego workflow GitHub. Dać ćwiczenie terminala i mapę "gdzie wpisuję polecenie". |
| [01: pierwszy lab](../../labs/01-python-data/README.md) | Parsowanie formatu TSF, generator, statystyki popytu, braki, sortowanie po kilku kryteriach, JSON | Przed plikiem przećwiczyć listę kilku liczb i pojedynczy rekord. Generator i ADI odłożyć do rozszerzenia albo osobnej lekcji. |
| [02: funkcje](../../labs/02-functions/README.md) | Migracja kodu, typowanie, `mypy --strict`, domknięcia, fabryka dekoratorów, rejestr, nowe statystyki | Rozdzielić zwykłe funkcje i moduły od zaawansowanych funkcji. Dekoratory pisać po doświadczeniu z testami, najlepiej przy retry. |
| [03: klasy](../../labs/03-classes/README.md) | Stan obiektu, dataclass, walidacja, `property`, `classmethod`, `Self`, ABC, Protocol, StrEnum, modele prognozy | Najpierw jedna zwykła klasa rozwiązująca znany problem. W osobnym kroku dataclass. ABC i Protocol po porównaniu kilku działających modeli. |
| [04: testy i pakiet](../../labs/04-testing/README.md) | Pierwsze własne testy dopiero po trudnych dekoratorach i klasach, do tego pakowanie i drugi manager zależności | Przenieść pierwsze `assert` i `pytest` do prostych funkcji. `uv` zostawić jako narzędzie główne, Poetry jako dodatek. |
| [05: NumPy](../../labs/05-numpy/README.md) | Macierz panelu, broadcasting, maski, cztery metryki i testy mutacyjne | Zacząć od jednej tablicy i ręcznego porównania wyniku. Osobno macierz i osie, potem broadcasting i pełny panel. |
| [06: pandas](../../labs/06-pandas-cleaning/README.md) | Pierwsza ramka od razu prowadzi do wieloarkuszowego cache, ośmiu reguł danych i rozróżniania duplikatów | Dodać lekcję orientacji w tabeli. Pierwszy cleaning lab mały i samodzielny; pełne Online Retail II po podstawach `groupby`. |
| [07: panel](../../labs/07-pandas-panel/README.md) | Wydajny odczyt, downcast, fakty i wymiary, merge, tablice godzinowe, lag, rolling i kontrakty | Podzielić na analizę tabel i czas w panelu. Kolumny godzinowe oraz optymalizację pamięci przenieść do rozszerzenia. |
| [08: pierwszy model uczony](../../labs/08-ml-basics/README.md) | Adapter baseline'u, gradient macierzowy, własny model liniowy, Ridge, scaler, pipeline i selekcja hiperparametru | Najpierw wytrenować gotowy prosty estimator na małych danych. Osobno zrozumieć uczenie od jednej wagi do zapisu macierzowego. |
| [09: cechy](../../labs/09-features/README.md) | Cechy czasowe, target encoding oraz `resolve_order` i zależności między funkcjami | Zacząć od dwóch jawnych funkcji cech. Target encoding i automatyczne porządkowanie zależności przenieść do rozszerzenia. |
| [10–11: modele i walidacja](../../labs/10-trees-boosting/README.md) | Drzewo od zera, boosting, interpretacja, prognoza wielokrokowa, potem backtest i tuning | Podstawowy backtest przed wieloma porównaniami modeli. Odseparować mechanikę prognozy wielokrokowej od rodziny estymatorów. |
| [12: klasyfikacja](../../labs/12-classification/README.md) | Od razu przyszła etykieta w panelu, krzywa PR, average precision, koszty i kalibracja | Najpierw ręczna confusion matrix i próg na kilku wynikach. Dopiero potem budowa etykiety czasowej i model. |
| [13: bez nadzoru i sieci](../../labs/13-unsupervised-nn/README.md) | k-means, PCA, ocena segmentów i pierwsza pętla PyTorch | Rozdzielić na lekcje o reprezentacjach, unsupervised learning i sieciach. Podstawy pojęciowe w rdzeniu, rozbudowany training loop w rozszerzeniu. |
| [14: pipeline](../../labs/14-pipeline/README.md) | Jednocześnie CLI, konfiguracja, artefakty, logowanie i przygotowanie w porcjach | Przenieść pełny moduł do ścieżki opcjonalnej. W rdzeniu wystarczy eksperyment uruchamiany od początku i zapis wyniku. |
| [15: cloud i SQL](../../labs/15-cloud-sql/README.md) | S3, serwer lokalny, retry, cache, atomowa publikacja, testy mutacyjne i pierwszy SQL | SQL jako dodatek po pandas. Storage i retry w opcjonalnej ścieżce inżynierskiej. |
| [16–17: CI i cudzy kod](../../labs/16-docker-ci/README.md) | Samodzielna konfiguracja narzędzi i nagłe przejście do ticketów | Gotowy workflow może wspierać ćwiczenia. Samodzielny Docker, CI i Shelfwise poza rdzeniem. |
| [18–19: finał](../../labs/19-capstone/README.md) | Zaliczenie obejmuje GRU z 18 i porównanie sieci z LightGBM | Pełny GRU i capstone produkcyjny jako rozszerzenia. Finał rdzenia sprawdza rozumienie na małych eksperymentach. |

Szczególnie ważna jest różnica między "pojęcie zostało opisane" a "uczestnik potrafi go użyć". Wykład 02 mówi, że sygnaturę generycznego dekoratora wystarczy rozpoznać i przepisać. To uczciwa pomoc, ale także sygnał, że narzędzie wyprzedza aktualny poziom rozumienia.

### Pierwszy model wymaga już rozbudowanego systemu

Rzeczywisty łańcuch zależności jest spójny technicznie. Pedagogicznie ma wysoki koszt wejścia:

```mermaid
flowchart LR
    A[03: klasy modeli] --> B[04: pakiet i testy]
    B --> C[05: metryki NumPy]
    C --> D[06: cleaning pandas]
    D --> E[07: pełny panel]
    E --> F[08: pierwszy uczony model]
    B --> F
    C --> F
```

Mała luka w klasach albo budowie panelu może zatrzymać naukę modelowania. `catchup` umożliwia dalsze wykonanie programu, ale nie potwierdza rozumienia poprzednich kroków.

### Sprawdzenie wykonania nie jest sprawdzeniem rozumienia

[Mechanizm sprawdzania](../../src/coursekit/checking.py) rozróżnia poprawny wynik, brak implementacji, niespełniony warunek i wyjątek. Nie sprawdza, czy uczestnik umie wyjaśnić wynik bez kodu. To naturalna granica automatyzacji, którą warto uzupełnić krótkimi pytaniami i nowymi danymi.

Jest też konkretna niespójność informacji o postępie. `check(...)` z notebooka zapisuje wynik, ale terminalowe sprawdzenie zadania notebookowego bez przekazanego obiektu zwraca `todo`. Następnie `record()` zapisuje ten status i zwiększa licznik prób. W efekcie zwykłe wyświetlenie sprawdzeń z terminala może zastąpić wcześniejsze `ok` statusem `todo`. README labów wyjaśniają komunikat "sprawdzasz w notebooku", lecz kursant nadal może odczytać podsumowanie jako utratę zaliczenia. To wniosek z odczytu kodu, nie odtworzony tu testem regresyjnym.

Docelowo potrzebne są osobne informacje: wynik ostatniej rzeczywistej próby, sposób sprawdzania, wykorzystane podpowiedzi i temat do powtórki. Wylistowanie zadania nie powinno liczyć się jako próba rozwiązania.

## Jak korzystać z wzorców innych kursów

Publiczne programy dają wzorce organizacji, nie dowód, że samo skopiowanie kolejności rozwiąże problemy tego kursu.

| Źródło | Co warto przenieść | Granica porównania |
|---|---|---|
| Stanford CS106A | Stopniowanie programowania, rozwiązywanie konkretnych problemów przed bardziej rozbudowaną strukturą programu | Kurs programowania, nie ML engineering. |
| Harvard CS50P | Wyjątki, funkcje i testy jako osobne kroki przed OOP | Inny zakres i model wsparcia uczestnika. |
| Coursera Python for Everybody | Wyraźna ścieżka podstaw Python przed kolejnymi obszarami pracy z danymi | Nie zastępuje docelowego projektu inżynierskiego. |
| Coursera Machine Learning Specialization | Oddzielenie podstaw supervised learning, bardziej zaawansowanych modeli oraz unsupervised learning | ML bez pełnej ścieżki utrzymania pakietu i CI. |
| Udemy: 100 Days of Code oraz Complete Python Bootcamp | Małe projekty, wyraźne sekcje i widoczny wynik kolejnych etapów | Publiczny syllabus nie pozwala ocenić jakości całej informacji zwrotnej. |
| Stanford CS229 i CS230 | Związki modeli z optymalizacją, probabilistycznym opisem danych i uczeniem reprezentacji | Wymagania akademickie są wyższe niż poziom wejścia tego kursu. |
| Stanford CS221 | Szerszy obraz AI: uczenie, search, podejmowanie decyzji, wnioskowanie i logika | W rdzeniu krótka mapa różnic i małe przykłady, bez kopiowania pełnego kursu. |

Odnośniki do konkretnych edycji i stron organizatorów są w [porównaniu źródeł](beginner-course-sources.md). Nie rekomenduję przenoszenia wszystkich tematów z żadnego z tych kursów. Freshcast ma pozostać osią nauki.

### Co wspierają badania, a co jest propozycją projektową

IES zaleca rozłożone w czasie powtórki, przeplatanie worked examples z zadaniami, łączenie obrazu z opisem oraz konkretu z abstrakcją. Wskazuje mocne dowody dla odtwarzania wiedzy w quizach i pytań wymagających wyjaśnienia, umiarkowane dla spacing i worked examples. To rekomendacje ogólne, nie badanie skuteczności tego kursu. [IES, Organizing Instruction and Study](https://ies.ed.gov/ncee/wwc/PracticeGuide/1).

Z tego wynika propozycja przejścia od krótkiego omówionego przykładu przez ćwiczenie z częściowym wsparciem do samodzielnego zadania. Przykłady muszą używać innych danych i nie podawać odpowiedzi do zadań ocenianych. Konkretne długości sesji, liczby ćwiczeń i poniższa kolejność są hipotezami do pilotażu, nie liczbami ustalonymi przez badania.

## Proponowana nowa kolejność

Poniższe oznaczenia A–G opisują bloki dydaktyczne, nie nowe numery `course check`. Punkty 18–21 mają nową treść, a dawny punkt o SQL i storage został rozdzielony. Nie należy od razu renumerować plików. Najpierw trzeba przygotować i sprawdzić ścieżkę nauki.

### A. Wejście i pierwszy samodzielny wynik

1. **Diagnoza podstaw.** Kilka zadań bez nowej biblioteki: prześledzenie pętli, funkcja zwracająca wynik, wybór danych z listy słowników, rozróżnienie zera i braku. Wynik kieruje do konkretnych lekcji, a nie do ogólnej etykiety "za słaby".
2. **Python od zera, jeśli potrzebny.** Zmienne i wartości, wywołania, warunki, pętle, listy, słowniki, funkcje i `return`. Każdy temat z krótkimi zadaniami. Uczestnik znający podstawy pomija ten blok po diagnozie.
3. **Minimalne środowisko.** Otworzenie notebooka, uruchomienie komórki, zapis i ponowne uruchomienie od początku. Oddzielnie wyjaśnione terminal, Python, kernel i katalog roboczy. Przed instalacjami dać możliwość pierwszego eksperymentu w istniejącym runnerze przeglądarkowym.
4. **Dane i mała prognoza.** Jedna seria kilkunastu dni na małym fragmencie danych. Co oznacza obserwacja, braki, historia, data wykonania prognozy i horyzont. Uczestnik oblicza baseline i MAE, potem ogląda prosty wykres historii oraz prognozy.

Rezultat A: uczestnik potrafi powiedzieć, co przewiduje i jak sprawdzi, czy przewidywanie ma sens. Nie potrzebuje jeszcze ABC, Protocol, pełnego panelu ani konta w usłudze AI.

### B. Python potrzebny do samodzielnej pracy z danymi

5. **Kolekcje, pliki i błędy.** Najpierw zwykła pętla, później comprehension. Jeden mały CSV albo uproszczony rekord, następnie pełny plik. `Path`, `with`, konkretne wyjątki, czytanie tracebacka. Generator dopiero po działającym odczycie i wyjaśnieniu zużycia pamięci.
6. **Funkcje i pierwsze testy.** Argument, wynik, lokalna zmienna, efekt uboczny, mutowalność. Ręczny przykład oczekiwanego wyniku, `assert`, jeden test pytest, przypadek brzegowy. Funkcję najpierw uruchamiamy, potem porządkujemy.
7. **Moduł, git i podstawowa jakość.** Przeniesienie jednej działającej funkcji do pliku, import i ponowny import w notebooku. Typy podstawowe, ruff, własny mały test. Pierwszy branch, commit i PR dopiero na kodzie, którego sens uczestnik rozumie. Pokazany gotowy workflow CI.

Rezultat B: mały moduł z testem i odtwarzalnym wynikiem. Pełne `mypy --strict` dla zaawansowanych generyków pozostaje późniejszym wymaganiem.

### C. Tabele, tablice i pierwszy uczony model

8. **pandas od pojedynczej tabeli.** Jeden wiersz, kolumna, indeks, typ, `.loc`, maska, nowa kolumna. Zanim pojawi się cleaning pipeline, uczestnik odpowiada na kilka pytań o dane i czyta wykres.
9. **NumPy potrzebne do obliczeń.** Tablica jednowymiarowa, elementowe operacje, maski, braki, shape. Potem dwie osie, redukcja i broadcasting. Wersja MAE porównana z wcześniejszym liczeniem ręcznym. Macierz wszystkich serii jest zadaniem późniejszym.
10. **Czyszczenie, agregacje i relacje.** Mała ramka, jawny klucz, proste `groupby().agg`, następnie `transform`, złączenie i sprawdzenie liczby wierszy. Dopiero potem trudne duplikaty z Online Retail II, cache i kontrakt pliku.
11. **Czas i cechy na małym panelu.** Jedna seria, potem dwie celowo różne. Sortowanie, brakujący dzień, lag i rolling. Na osi czasu zaznaczone, co wiadomo w chwili prognozy. Horyzont jednego dnia przed prognozą całego tygodnia.
12. **Pierwszy model ze scikit-learn.** Co oznaczają `X`, `y`, `fit`, `predict`; podział po czasie i baseline. Prosty model liniowy lub małe drzewo, gotowy estimator, kilka jawnych cech. Najpierw model i uczciwa ocena, potem scaler z `Pipeline` i porównanie wyników.

Rezultat C: mały projekt od danych do porównania baseline'u z modelem. Pełne API Freshcast nie jest warunkiem pierwszego uczenia. Dane demonstracyjne są częścią kursu, a kod ocenianego rozwiązania nadal pisze uczestnik.

### D. Zrozumienie modeli i oceny

13. **Matematyka modelu liniowego.** Średnia, wariancja i skala poznane wcześniej na danych. Teraz prosta z jedną wagą, strata dla kilku wartości wagi, nachylenie i krok uczenia. Potem dwie cechy, iloczyn skalarny, macierz i gradient. Własny gradient descent jako osobny lab po pierwszym estimatorze.
14. **Walidacja i porównanie.** Underfitting, overfitting, train i validation, kilka przesuwanych okien. MAE, RMSE, WAPE i bias wraz z ograniczeniami. Najpierw tabela wyników ręcznie wybranych ustawień, dopiero później automatyczne strojenie.
15. **Cechy, drzewa i boosting.** Kalendarz, proste kodowanie kategorii, regresyjne drzewo, las, boosting. Jedno porównanie zmienia jedną rzecz. Direct i recursive forecasting jako osobny odcinek z osią dostępności danych. Target encoding, SHAP i graf zależności cech jako rozszerzenia po podstawach.
16. **Klasyfikacja jako drugi rodzaj celu.** Kilka ręcznie ocenionych alarmów, confusion matrix, precision i recall, próg i koszt. Potem własna etykieta przyszłego dnia i model. Kalibracja po rozróżnieniu rankingu i prawdopodobieństwa.

Rezultat D: uczestnik umie wybrać model i uzasadnić ocenę. Nie musi jeszcze samodzielnie implementować każdej rodziny algorytmów ani używać PyTorch.

### E. Domknięcie potrzebnych kompetencji technicznych

17. **Klasy i organizacja eksperymentu.** Działający model pokazuje potrzebę przechowywania stanu. Zwykła klasa, konstruktor i metoda, potem dataclass. Czytanie API estymatora i prosty moduł z testami. ABC, Protocol, zaawansowane generyki oraz pełny pakiet nie są warunkiem dalszej nauki idei ML.

Rezultat E: uczestnik potrafi samodzielnie uruchomić mały eksperyment, zmienić jeden element i sprawdzić wynik. To wystarczająca baza techniczna dla następnego bloku.

### F. Dlaczego ML działa i jak mieści się w AI

To nowy cel drugiej części kursu. Nie powtarzamy instrukcji wywołania `fit`. Wyjaśniamy, jakie założenia stoją za tym wywołaniem i dlaczego poprawnie wykonany program może dawać złą odpowiedź.

18. **Uczenie i generalizacja.** Od funkcji straty na próbce do błędu na nowych danych. Rozdzielenie modelu, zbioru dopuszczalnych funkcji i algorytmu optymalizacji. Różne modele mają różne inductive biases. Regularizacja, ilość danych, szum oraz zmiana rozkładu wpływają na wynik. To pogłębienie wcześniejszej walidacji, a nie drugi kurs podziału na train i validation.
19. **Prawdopodobieństwo, niepewność i decyzja.** Wcześniejsze liczenie częstości prowadzi do rozkładu i prawdopodobieństwa warunkowego. Następnie likelihood i powiązanie z loss, generative versus discriminative models, rozróżnienie predykcji od decyzji. Niepewność danych i modelu oraz granice interpretowania confidence. Osobno wyjaśniamy kalibrację i ograniczenia wnioskowania przyczynowego z obserwacji.
20. **Reprezentacje i uczenie bez ręcznego celu.** Co zmienia wybór cech, odległości i przestrzeni opisu. Osobne krótkie lekcje o k-means, PCA, sieci z nieliniowością i embeddings. Od odtwarzania reprezentacji do self-supervised learning. Dopiero po tym intuicja attention i przewidywania kolejnego tokenu. Uczestnik rozumie, czego model językowy uczy się z takiego zadania, bez trenowania własnego LLM.
21. **AI poza przewidywaniem etykiety.** Rozdzielenie uczenia, wnioskowania i podejmowania działań. Search znajduje plan, inference odpowiada na pytanie o ukryty stan, a MDP opisuje decyzje rozłożone w czasie. Na małym przykładzie pojawiają się reward, policy oraz exploration versus exploitation. Na koniec porównujemy, do jakiej części problemu pasuje klasyczny model, search, system reguł lub model językowy, i jak oceniać błędy całego rozwiązania.

Każdy punkt F jest blokiem kilku lekcji. Obecny moduł 13 łączy unsupervised learning i pierwszą pętlę PyTorch. Nie powtarzamy tego przeciążenia przez dodanie attention do tej samej lekcji. Prawdopodobieństwo warunkowe i likelihood wymagają własnych ćwiczeń przed modelami probabilistycznymi. Podobnie embeddings i attention wymagają praktyki z wektorami, zanim pojawią się w opisie modelu językowego.

#### Co konkretnie bierzemy ze Stanford

CS229 daje wzorzec łączenia modeli, założeń probabilistycznych i generalizacji. Widać to w blokach GLM, generative learning oraz learning theory w [oficjalnych materiałach CS229](https://see.stanford.edu/Course/CS229). CS230 pomaga przejść do sieci. CS221 pokazuje AI obejmujące także search, decyzje, wnioskowanie probabilistyczne i logikę. Publiczny program CS221 wymaga już programowania, matematyki dyskretnej, prawdopodobieństwa i algebry liniowej. W tym kursie wybieramy ograniczone przykłady i dostarczamy potrzebne przygotowanie. [CS221, Autumn 2025](https://stanford-cs221.github.io/autumn2025/).

Nie jest to kopia semestru Stanford ani jego dokładnej kolejności. To propozycja dla uczestnika, który ma już podstawy kodowania i pierwsze eksperymenty ML. Szczegółowe źródła programu i poziomów wejścia zapisano w [uzupełnieniu porównania kursów](beginner-course-sources.md).

#### Jak uczyć tych idei w praktyce

| Blok | Kolejność krótkich lekcji | Eksperyment uczestnika | Dowód zrozumienia |
|---|---|---|---|
| 18: generalizacja | Próbka i populacja → model i optymalizacja → inductive bias i regularizacja → ilość danych oraz shift | Ten sam problem z małą i większą próbką, potem z nowym zakresem wejść. Porównanie prostego modelu z elastycznym | Wyjaśnienie, dlaczego mniejszy training loss nie gwarantuje lepszego działania i kiedy więcej danych nie usunie problemu |
| 19: niepewność | Prawdopodobieństwo warunkowe → likelihood i loss → modele generative i discriminative → niepewność i koszt decyzji | Dwie grupy z różną częstością zdarzenia. Porównanie modelu opartego na Bayesie i regresji logistycznej, następnie dwóch progów decyzji | Rozróżnienie prawdopodobieństwa zdarzenia, niepewności oszacowania i kosztu błędnej decyzji. Wskazanie założeń modelu |
| 20: reprezentacje | Cechy i odległość → k-means → PCA → nieliniowość i embeddings → self-supervision i attention | Najpierw zmiana skali i projekcja małych danych. W kolejnych lekcjach porównanie modelu liniowego z małą siecią na CPU oraz inspekcja gotowych wektorów | Wskazanie, co zachowuje reprezentacja, co traci i dlaczego podobieństwo w niej nie jest dowodem prawdziwości odpowiedzi |
| 21: szersze AI | Predykcja i plan → inference → MDP i reward → mapa metod oraz ograniczenia | Osobno mała trasa z kosztami, proste wnioskowanie z obserwacji i kilkustanowy problem decyzji. Potem wybór metody dla nowego problemu | Wyjaśnienie różnicy między przewidzeniem skutku działania a wyborem dobrego działania, oraz wskazanie brakującej informacji |

Średnia squared loss jako przykład estymacji, likelihood i cross-entropy mogą korzystać z małych danych. Nie wymagamy formalnych dowodów teorii uczenia. Nie utożsamiamy też generative classifier z dzisiejszym generatywnym AI: podobieństwo nazw wymaga osobnego wyjaśnienia. Wprowadzenie nowego pojęcia zawsze kończy się jego użyciem na małym przykładzie.

Freshcast pozostaje głównym projektem, ale nie ilustruje równie dobrze wszystkich idei. Geometria na punktach, krótki tekst i mały problem planowania pozwolą zrozumieć reprezentacje oraz decyzje. Uczestnik następnie sprawdza, które z tych idei przenoszą się na forecasting, a które wymagają innego zadania.

#### Zakończenie bez dodatkowego capstone produkcyjnego

Po każdym bloku uczestnik oddaje krótki wynik eksperymentu oraz własne wyjaśnienie. Finał to kilka nowych przypadków: dobór sposobu opisania problemu, wskazanie założeń, diagnoza błędu modelu i uzasadnienie decyzji. Nie powstaje kolejny duży projekt ani osobne wdrożenie.

Kryterium ukończenia brzmi: uczestnik umie przewidzieć zachowanie modelu, przeprowadzić mały eksperyment i wyjaśnić rozbieżność z oczekiwaniem. Znajomość nazw architektur albo przejście quizu wielokrotnego wyboru tego nie zastępują.

### G. Opcjonalne ścieżki po rdzeniu

- **Inżynieria ML.** Pełny pipeline, CLI, konfiguracja, artefakty, MLflow, lokalny storage, retry, CI, Docker i Shelfwise. Możliwy osobny capstone produkcyjny.
- **Sequence models i GPU.** Rozbudowany training loop, okna czasowe, Dataset, GRU, urządzenie i pamięć. Mixed precision i Lightning po działającej zwykłej pętli.
- **Zaawansowany forecasting.** Target encoding, korekta popytu ocenzurowanego, przetwarzanie dużych danych i bardziej wymagające porównania modeli.
- **Dalsze modele językowe.** Pełna implementacja transformera, pretraining i post-training po opanowaniu sieci, prawdopodobieństwa i reprezentacji. Te tematy wymagają osobnego zakresu i budżetu obliczeń.

Przesunięcie infrastruktury nie oznacza, że jej czas automatycznie wystarczy na cały blok F. Po pilotażu trzeba osobno oszacować rdzeń pojęciowy i rozszerzenia. Nazwa oraz opis kursu powinny odzwierciedlać nowe proporcje: Python i dane jako przygotowanie do rozumienia ML/AI, inżynieria produkcyjna jako dalsza ścieżka.

## Co zrobić z każdym obecnym modułem

| Obecny moduł | Los materiału |
|---|---|
| 00 | Podzielić na minimalne uruchomienie, obsługę środowiska oraz workflow GitHub. NVIDIA dopiero przed rozszerzeniem GPU. |
| 01 | Zachować większość, poprzedzić diagnostyką i podstawami. ADI oraz TSF po prostym odczycie. |
| 02 | Funkcje, importy i podstawowe typy wcześnie. Closures, dekoratory i typy generyczne rozłożyć na późniejsze potrzeby. |
| 03 | Prognozę przenieść wcześniej. Zwykłe klasy po pierwszym modelu, interfejsy w bloku inżynierskim. |
| 04 | Proste testy wcześniej. Pakiet po działającym małym projekcie. Poetry opcjonalnie. |
| 05 | Podzielić na podstawy tablic i zaawansowany panel. Metryki wprowadzać w miarę potrzeb, zaczynając od MAE. |
| 06 | Dodać podstawy pandas. Duży cleaning lab rozdzielić na samodzielne odcinki. |
| 07 | Oddzielić relacje od operacji czasowych. Godziny i pamięć jako drugi przebieg. |
| 08 | Rozdzielić użycie estymatora, uczciwą ocenę, matematykę uczenia i adapter do Freshcast. |
| 09 | Proste cechy w rdzeniu. Target encoding i graf zależności później. |
| 10 | Drzewa i boosting w rdzeniu. SHAP i forecasting wielokrokowy osobno. |
| 11 | Podstawowy backtest wcześniej. Optuna i MLflow po ręcznych eksperymentach. |
| 12 | Zachować jako kolejny rodzaj zadania po regresji i podstawach walidacji. Rozdzielić metryki od budowy etykiety. |
| 13 | Rozdzielić podstawy unsupervised learning, PCA i neural networks na krótkie lekcje rdzenia. Rozbudowaną implementację zostawić w rozszerzeniach. |
| 14 | Prosty, powtarzalny eksperyment w rdzeniu. Pełny pipeline, CLI i konfiguracja w opcjonalnej ścieżce inżynierskiej. |
| 15 | SQL jako dodatek po podstawach tabel. Storage po pipeline w ścieżce opcjonalnej. |
| 16 | Gotowe CI może wspierać naukę. Własne CI i Docker w ścieżce opcjonalnej. |
| 17 | Shelfwise jako opcjonalna praktyka dla osób zainteresowanych pracą w cudzym repozytorium. |
| 18 | Oddzielna ścieżka po podstawach PyTorch. GPU nie jest wymaganiem wejścia do rdzenia. |
| 19 | Capstone produkcyjny opcjonalny. W rdzeniu małe eksperymenty i wyjaśnienia po każdym bloku pojęciowym. |

## Jak przepisać treść lekcji i zadań

### Jedna lekcja kończy się jedną nową umiejętnością

Obecne moduły mogą pozostać rozdziałami, ale w ich wnętrzu potrzebne są krótsze lekcje. Startowa hipoteza to sesje około 30–60 minut, zawierające wyjaśnienie i praktykę. Nie należy dzielić według samej długości tekstu. Granicą jest rzecz, którą uczestnik potrafi samodzielnie zrobić.

Proponowany układ pojedynczej lekcji:

1. Pokazujemy problem, wejście i oczekiwany wynik. Uczestnik rozumie sens zadania, zanim pozna nowe API.
2. Sprawdzamy dwie lub trzy potrzebne umiejętności. Brak kieruje do konkretnego krótkiego materiału.
3. Omawiamy mały przykład na innych danych niż zadanie oceniane. Każda nowa operacja ma widoczny rezultat.
4. Uczestnik przewiduje wynik albo uzupełnia brakujący krok. Wyjaśnia, dlaczego tak uważa.
5. Rozwiązuje zadanie samodzielnie na nowych danych. Check bada zachowanie, a krótkie pytanie sprawdza rozumienie.
6. Wraca jedno pytanie z wcześniejszej lekcji. Na końcu zapisuje, co potrafi oraz co jeszcze wymaga powtórki.

Podpowiedzi i przykłady nadal nie piszą rozwiązania za uczestnika. Zmieniamy dostępność nauczania przed utknięciem. Worked example nie powinien pojawiać się dopiero po trzecim nieudanym podejściu do nowego pojęcia.

### Rozdzielić pojęcie, bibliotekę i jakość kodu

Przy `rolling` pierwsza próba dotyczy ręcznego wyniku i osi czasu. Druga dotyczy pandas. Trzecia dodaje walidację i test. Dopiero końcowe zadanie łączy wszystkie warstwy.

Ta sama zasada dotyczy modelu liniowego. Najpierw przewidywanie z jednej wagi, potem uczenie i ocena, dalej tablice, na końcu interfejs własnego modelu. Uczestnik nie powinien jednocześnie debugować matematyki, mypy i brakującego importu.

Typy i testy nie znikają. Wcześnie dajemy proste sygnatury i pojedynczy test. Wymagania K1, K9 i T1 z [obecnego standardu](../standard.md) trzeba przypisać do właściwego poziomu i ścieżki, zamiast wymagać pełnego standardu produkcyjnego w każdym eksperymencie pojęciowym. Zmiana wymaga też aktualizacji kolumny "Od", instrukcji review i zakresów uruchamianych sprawdzeń.

### Dodać matematykę wtedy, gdy ma zastosowanie

Brakuje wydzielonej ścieżki ćwiczeń łączącej deklarowane podstawy szkolne z gradientem macierzowym. Samo podanie wzoru i objaśnienie `X.T` w wykładzie 08 nie mówi, czy uczestnik umie z niego skorzystać.

| Przed czym | Krótkie przygotowanie | Dowód gotowości |
|---|---|---|
| ADI i CV² | Udział, średnia, wariancja oraz różnica zera i braku | Obliczenie statystyk kilku obserwacji i opis jednostek |
| NumPy i scaler | Wektor, tabela liczb, shape, osie, odchylenie standardowe | Przewidzenie kształtu wyniku i ręczna standaryzacja jednej wartości |
| Model liniowy | Wykres prostej, waga, intercept i błąd | Ręczne obliczenie prognozy i wpływu zmiany wagi |
| Gradient descent | Strata jako funkcja wagi, nachylenie i wielkość kroku | Wybór kierunku kroku na rysunku, potem wynik liczbowy |
| Klasyfikacja | Częstość zdarzenia, proporcja i koszt decyzji | Porównanie dwóch progów na małej confusion matrix |
| PCA i sieci | Rzutowanie lub pochodna złożenia, zależnie od ścieżki | Osobne ćwiczenie przed użyciem biblioteki |
| Likelihood i niepewność | Rozkład, prawdopodobieństwo warunkowe, niezależność i Bayes na małej tabeli | Wyjaśnienie różnicy między prawdopodobieństwem danych przy modelu a prawdopodobieństwem modelu po obserwacji |
| Search i MDP | Graf, stan, działanie, koszt i wartość oczekiwana | Ręczne porównanie dwóch tras i dwóch działań z losowym wynikiem |

Nie dodawałbym na początku obowiązkowego wielkiego kursu matematyki. Przygotowanie ma odpowiadać zadaniu i zawierać praktykę, nie sam link do zewnętrznego wykładu.

### Mniej zmiany kontekstu, więcej samodzielnego sprawdzania

Car Parts i Online Retail II mają uzasadnienie, a drugi zbiór wraca w Shelfwise. Nie usuwałbym ich automatycznie. Rdzeń prowadziłbym jednak po jednym małym wycinku FreshRetailNet. Inne dane służą sprawdzeniu przenoszenia umiejętności, a nie każdorazowemu uczeniu nowej domeny, formatu i biblioteki jednocześnie.

Na początku każdej lekcji potrzebny jest schemat miejsca pracy: czytam wykład, edytuję notebook albo konkretny plik, uruchamiam wskazane sprawdzenie. Warto dodać osobne materiały o kolejności wykonania komórek, restartowaniu kernela, autoreload, tracebacku i różnicy między błędem środowiska a błędem rozwiązania.

Instrukcje mają umożliwiać taki sam postęp bez płatnego tutora. Pytania bez automatycznej oceny potrzebują krótkiej rubryki samooceny i przykładu poprawnego uzasadnienia na innym problemie. Samo "porozmawiaj z tutorem" nie wystarcza jako jedyna informacja zwrotna.

### Doprecyzować dwa komunikaty o wynikach

Wykład 08 mówi, że model niebijący baseline'u niczego się nie nauczył. Zastąpiłbym to stwierdzeniem, że model nie wykazał użytecznej poprawy w tym porównaniu. Słaby wynik nie rozstrzyga sam, czy przyczyną są cechy, dane, ograniczenia modelu czy implementacja.

Capstone wymaga pobicia baseline'u także na końcowym tygodniu testowym. Ten warunek może zachęcić do ponawiania oceny i dopasowania do testu. Zaliczenie powinno wymagać poprawnej metody, zamrożonych decyzji i uczciwego raportu. Nieudany eksperyment z poprawnymi dowodami jest wartościowym wynikiem nauki.

Dodatkowo należy wyraźnie nazwać testy ćwiczeniowe oraz końcowy zbiór capstone. Lab 08 odkłada końcówkę danych treningowych, a 19 korzysta z `eval.parquet`, więc samo zajrzenie do testu w 08 nie dowodzi naruszenia końcowego holdoutu. Potrzebna jest mapa: które dane służą nauce, które walidacji, a które pozostają zamknięte do finału.

## Jak umożliwić dalszą naukę bez ukrywania braków

### Trzy rodzaje trudności dostają różne odpowiedzi

| Trudność | Rozpoznanie | Droga powrotu |
|---|---|---|
| Środowisko | Notebook lub import nie uruchamia się przed próbą rozwiązania | Oddzielny doctor, instrukcja naprawy i mały test środowiska |
| Brak podstaw | Uczestnik nie potrafi ręcznie przewidzieć wyniku na kilku danych | Krótka lekcja pojęcia i dwa nowe mikroćwiczenia |
| Błąd implementacji | Ręczny wynik jest poprawny, kod daje inny | Minimalne dane, traceback, wskazanie warstwy błędu i kolejny poziom podpowiedzi |

Tutor już stosuje część tego rozróżnienia. Należy udostępnić je także osobie uczącej się bez AI.

### Zależność od wcześniejszego labu nie może być jedyną drogą

Dla dużych etapów danych kurs powinien dostarczać mały, wersjonowany zbiór wejściowy, zgodny z kontraktem następnej lekcji. Uczestnik wybiera własny wynik poprzedniego etapu albo dane startowe. W drugim przypadku wcześniejsze zadanie pozostaje niezaliczone, ale można ćwiczyć nową umiejętność.

To inne narzędzie niż istniejący [catchup](../../src/coursekit/catchup.py), który przepisuje wcześniejsze pliki kodem referencyjnym i wykonuje backup. Dostarczony plik danych nie zastępuje funkcji uczestnika. Pozwala oddzielić "chcę dziś uczyć się modelu" od "muszę najpierw naprawić cache".

Dla zależności programistycznych można udostępnić jawny, gotowy komponent kursowy z małą publiczną umową. Uczestnik nie edytuje go i nie dostaje za niego zaliczenia. W późniejszej lekcji zastępuje komponent własną implementacją.

### Zaliczenia nie muszą blokować całego kursu

Warunkiem przejścia są umiejętności niezbędne do następnego zadania, nie wszystkie dodatki bieżącego modułu. Słabe rozumienie dat i dostępności informacji wymaga poprawy przed forecastingiem. Brak własnego target encodera nie musi blokować drzew. Niepewne prawdopodobieństwo warunkowe wymaga ćwiczenia przed likelihood, ale nieukończony Docker nie wpływa na gotowość do tej lekcji.

Przy każdym punkcie kontrolnym potrzebne są dwa krótkie zadania na nowych danych: jedno przewidywanie wyniku i jedno wyjaśnienie błędu. Zachowujemy istniejące review kodu. Dodajemy dowód, że uczestnik potrafi użyć poznanej umiejętności poza konkretnym checkiem.

## Plan wdrożenia

### Etap 1. Zmniejszyć obecne bariery bez zmiany numeracji

1. Uzgodnić opis odbiorcy i dodać diagnozę wejścia wraz z uzupełnieniem podstaw Python.
2. Dodać miniścieżkę prognoza → MAE → wykres przed klasami. Nie wystarczy kolejna definicja we wstępie 03.
3. Dodać proste testy funkcji przed dekoratorami i pierwszą lekcję orientacji w pandas przed cleaning pipeline.
4. Przygotować małe wejścia do etapów 07 i 08 oraz nowych eksperymentów pojęciowych. Opisać, jak wrócić do własnego przygotowania danych.
5. Rozdzielić status notebooka od terminalowego listowania. Uzgodnić raport postępu między CLI, notebookiem i przeglądarką.
6. Przenieść pełny pipeline, samodzielne CI, Docker, Shelfwise i capstone produkcyjny do ścieżki opcjonalnej. Przygotować małe zaliczenia pojęciowe bez wymogu GRU, GPU i zwycięstwa na teście.
7. Usunąć rozbieżność README "gotowe 00, 07 i fragment 01" z faktyczną obecnością materiałów. Zamiast domyślać się kompletności, nadać modułom jawne statusy: szkic, gotowy redakcyjnie, zweryfikowany technicznie, sprawdzony z uczestnikami.

Etap 1 ogranicza tarcie, ale pozostawia przeciążenie modułów 02–03. Nie traktowałbym go jako docelowej przebudowy.

### Etap 2. Sprawdzić nowy początek na uczestnikach

Przygotować bloki A–C na wydzielonej ścieżce materiałów. Dwie grupy wejścia: osoby od zera oraz osoby umiejące już napisać prostą funkcję i pętlę. Wystarczy zacząć od małego pilotażu jakościowego, na przykład kilku osób o różnym poziomie. Nie będzie to dowód statystyczny skuteczności. Osobno sprawdzić blok F z osobami, które potrafią już przygotować dane i uruchomić prosty model. Ustalić, które podstawy matematyczne trzeba uzupełnić, zanim pełny program dostaną uczestnicy od zera.

Zapisywać, za zgodą uczestników: czas do pierwszego samodzielnego wyniku, miejsce przerwania, rodzaj pomocy, wykonane zadania naprawcze oraz wynik nowego zadania po przerwie. Rozmowa o tym, co uczestnik myślał, jest równie ważna jak czerwony check. Sam licznik `attempts` nie wystarcza.

### Etap 3. Przebudować zależności i dopiero potem numery

Po pilotażu rozdzielić obecne 02, 03, 07, 08, 13 i 15. Zmienić mapę wymagań, standard, tutor notes i rubryki review. Na końcu zmieniać task IDs, `course check`, `catchup`, bookmarki wykładów i odnośniki w notebookach. Przygotować migrację postępu oraz kopię starych notatek uczestnika.

Nowy ADR powinien zastąpić ograniczenie "lab order stays fixed" z ADR 0001, opisując koszt migracji oraz wynik pilotażu. Koszt zachowania działającego łańcucha jest realny, ale nie powinien sam wyznaczać kolejności nauki nowej edycji.

### Jak ocenić, czy zmiana pomogła

| Pytanie | Co mierzyć | Jak nie pomylić wyniku |
|---|---|---|
| Czy start jest dostępniejszy? | Czas do samodzielnej małej prognozy, błędy środowiska, miejsca rezygnacji | Osobno dla osób od zera i ze znajomością podstaw |
| Czy uczestnik rozumie? | Nowe dane, ręczne przewidywanie wyniku i krótkie uzasadnienie | Zielony check i odtworzenie przykładu nie wystarczają |
| Czy wiedza zostaje? | Krótka próba po kilku dniach i po dalszym module | Rozdzielić wynik bez pomocy od wyniku z podpowiedzią |
| Czy pomoc odblokowuje? | Powrót do samodzielnego zadania po ćwiczeniu naprawczym | Samo przejście dalej przez catchup nie oznacza zrozumienia |
| Czy uczestnik lepiej rozumie ML/AI? | Dobór modelu do nowego problemu, wyjaśnienie generalizacji i niepewności, odróżnienie predykcji od decyzji | Nie zastępować wyjaśnienia listą nazw modeli. Jakość wdrożenia oceniać osobno w ścieżce inżynierskiej |

Nie podaję nowej obietnicy liczby godzin. Obecne około 160 godzin nie zostało tu zweryfikowane z początkującymi. Pełne podstawy Python i utrwalanie zwiększą czas dla części osób. Uczciwe oszacowanie powinno pokazać osobno przygotowanie, rdzeń i rozszerzenia oraz opierać się na pilotażu.

## Od czego zacząłbym

Pierwszy konkretny fragment do przebudowy to droga od wejścia do pierwszej małej prognozy i jej testu. Następnie funkcje, proste pytest i tabela pandas. Dopiero po sprawdzeniu tego początku przesuwałbym klasy, zmieniał API pakietu i renumerował resztę kursu.

Największa oczekiwana korzyść to samodzielne rozumowanie o modelach po zdobyciu wystarczających umiejętności technicznych. Rdzeń kończy się wyjaśnieniem, kiedy i dlaczego metoda działa oraz czego jej wynik nie uzasadnia. Pełny poziom inżynierii produkcyjnej pozostaje dostępny w osobnej ścieżce.
