# Plan laboratoriów do kursu A–F

Stan: cztery laboratoria A są przygotowane do pilotażu. B–F pozostają planem. [Raport dwóch rund rady](../reviews/af-laboratories-council.md) opisuje pierwotne uzasadnienia dydaktyczne. Poniższa wersja uwzględnia późniejsze decyzje o uproszczeniu struktury i numeracji.

## Forma kursu

Wykłady są bezpośrednio w lectures/, notebooki bezpośrednio w labs/, a wszystkie wspólne dane w labs/data/. Laboratorium ma numer wykładu lub zakres numerów, jeśli łączy kilka lekcji. A1 jest diagnozą, bez dodatkowego labu. Nie tworzymy osobnych folderów, README, kopii licencji ani archiwów dla każdego notebooka. Licencje i wspólna instrukcja pozostają w katalogu głównym repozytorium.

Krótkie ćwiczenia w wykładzie są rozgrzewką. Pełne zadanie ma jedną specyfikację w labie. Pytania do przemyślenia nie wymagają pisemnych odpowiedzi ani prowadzenia notatek z nauki. Uczestnik pisze kod samodzielnie, wykonuje sprawdzenia i próbuje nowego przykładu.

## Mapa laboratoriów

Numery odpowiadają lectures/curriculum.json. Bloki wielolekcyjne mają etapy, które wykonuje się po właściwym wykładzie, bez czekania na zakończenie całego bloku. Pierwsze lokalne notebooki uruchamiamy po wykładzie A3, dlatego lab A3 poprzedza utrwalenie A2.

| Lab | Lekcje i moment pracy | Co uczestnik przygotowuje i sprawdza | Materiał wyjściowy |
|---|---|---|---|
| A3 Środowisko | A3 | Zapisany notebook, poprawnie wybrane środowisko i wynik odtworzony po restarcie kernela | Nowy na podstawie A3 |
| A2.1–A2.3 Wartości, warunki i pętle | A1 jako diagnoza; A2.1–A2.3, utrwalenie po A3 | Podsumowanie małej listy pomiarów, z zerami i None; ręczny ślad pętli i przypadek pustej listy | Nowy; uproszczone motywy starego 01 |
| A2.4–A2.5 Rekordy i funkcja | A2.4–A2.5, po A3 | Funkcja pracująca na rekordach, poprawny return i zachowanie wejścia na nowym przykładzie | Stare 01–02, bez parsera pliku i dekoratorów |
| A4.1–A4.2 Pierwsza prognoza | A4.1–A4.2, dwa kroki | Prognoza zamrożona przed okresem oceny, ręczne MAE i interpretacja zer przy niedostępności towaru | Stare 03–05, bez klas i macierzy panelu |
| B5.1 Kolekcje | B5.1 | Nowa kolekcja bez utraty zer, powtórzeń i kolejności; demonstracja aliasu i kopii | Nowy na podstawie B5.1 |
| B5.2–B5.3 Plik i błędne dane | B5.2–B5.3 | Odczyt małego UTF-8, rozróżnienie znacznika braku i błędu, osobny raport, pomocny komunikat | Parser i JSON ze starego 01 w mniejszym formacie, bez TSF i generatora parsera |
| B6.1–B6.2 Funkcja i własne testy | B6.1–B6.2 | Funkcja w summary.py, testy wyniku, błędu i niezmienności wejścia; test wykrywa celową zmianę w importowanym pliku | Stare 02 i 04, bez fabryk i klas bazowych |
| B7.1–B7.2 Moduł i współpraca | B7.1–B7.2 | README z poleceniami, format/lint/typy/testy, przeczytany diff, lokalny commit oraz PR/CI przy dostępnym koncie | Stare 00 i 04, wybrane elementy 16, bez Dockera |
| C8.1–C8.2 Tabela i opis liczb | C8.1–C8.2 | Selekcja maską i nazwami kolumn przy indeksie różnym od pozycji, niezmienione wejście i ręczne statystyki potwierdzone w pandas; jawne ddof | Stare 05–06, mała tabela bez cache |
| C8.3 Wykres odpowiada na pytanie | C8.3 | Linia, histogram i scatter z opisanymi osiami; interpretacja luki i ograniczeń | Nowy; przydatne fragmenty eksploracji starego 06 |
| C9.1–C9.2 Tablice i osie | C9.1–C9.2 | Metryka z tablic, centrowanie, zapis kształtów i kontrola broadcasting na macierzy niekwadratowej | Stare 05, bez pakietowego API metryk |
| C10.1–C10.3 Klucze, grupy i złączenia | C10.1–C10.3, osobny krok po każdej lekcji | Raport braków i duplikatów, wynik grupowy oraz wierszowy, złączenie z wykrytą relacją i niedopasowaniem na wspólnym panelu kilku serii | Stare 06–07, bez Excel/cache/downcast |
| C11.1–C11.2 Czas i dostępność cech | C11.1–C11.2 | Posortowane dwie serie z kontrolowaną luką; lag i okno bez mieszania serii; tabela dostępności cech; własny test izolacji serii | Stare 07 i 09, bez grafu zależności funkcji |
| C12.1–C12.3 Pierwszy model | C12.1–C12.3, trzy etapy | Ręczna prognoza liniowa; projekt na development, baseline i model na tej samej walidacji; scaler i alpha dobierane bez testu | Stare 08, bez adaptera panelu i gradientu przed fit |
| D13.1–D13.4 Strata i uczenie | D13.1–D13.4, cztery krótkie kroki | Własna tabela strat, przybliżenie pochodnej, kilka kroków GD, jednoczesna aktualizacja dwóch parametrów | Fragmenty gradientu starego 08, napisane ponownie od jednej wagi |
| D13.5–D13.6 Wektory i macierze | D13.5–D13.6 | Iloczyn skalarny i prognozy macierzowe; gradient ręczny i NumPy na n różnym od liczby cech, z własnym testem kształtu i wyniku | Stare 05 i 08, bez własnej klasy estymatora |
| D14.1–D14.3 Uczciwe porównanie | D14.1–D14.3 | MAE/WAPE/bias i przypadek zerowego mianownika, przykład przeuczenia; trzy datowane podziały, świeży fit modelu i baseline dla każdego, rzeczywiste prognozy i sparowane wyniki | Stare 05 i 11, bez Optuna i MLflow |
| D15.1–D15.3 Cechy i drzewa | D15.1–D15.3 | Kalendarz i znane kategorie, ręczny podział drzewa, porównanie drzewa/lasu/boostingu na walidacji | Stare 09–10, bez target encoding i SHAP |
| D15.4 Prognoza wielodniowa | D15.4 | Osobne direct i recursive przy zamrożonej chwili prognozy; ślad użytych wartości i kumulacji błędu | Stare 10, niezależny mały szereg |
| D16.1–D16.3 Prawdopodobieństwo i alarm | D16.1–D16.3 | Częstości, macierz pomyłek i progi, etykieta jutra z granicą czasu, LogisticRegression z obiema klasami | Stare 12, mały syntetyczny szereg zamiast całego pipeline |
| E17.1–E17.2 Obiekt i eksperyment | E17.1–E17.2 | Dwa niezależne obiekty, błąd predict przed fit; odtworzenie dwóch przebiegów z zapisu | Stare 03 i 11, bez ABC/Protocol/MLflow |
| F18.1–F18.3 Generalizacja | F18.1–F18.3 | Dwie funkcje zgodne na treningu, wpływ kary, krzywe uczenia i kontrprzykład dla „więcej danych zawsze pomaga” | Nowy; wybrane porównania starego 11 |
| F19.1–F19.2 Prawdopodobieństwo i Bayes | F19.1–F19.2 | Rozkład sumujący się do 1, wartość oczekiwana niebędąca pojedynczym wynikiem, sprawdzenie niezależności przez P(A∩B) i P(A)P(B), częstości warunkowe i Bayes, przypadek warunku o prawdopodobieństwie 0 | Nowy |
| F19.3–F19.5 Likelihood i klasyfikatory | F19.3–F19.5 | Porównanie parametrów przy tych samych danych, log-loss dla obserwowanej klasy, mały Naive Bayes i porównanie z logistycznym | Nowy, dane wzorowane na starym 12 |
| F19.6–F19.7 Niepewność i przyczynowość | F19.6–F19.7 | Tabela kalibracji z licznością grup, dwa przypadki odróżniające zmienność danych od niepewności modelu, decyzja przy kosztach i rozróżnienie prognozy i interwencji na konkretnych scenariuszach | Nowy; bez wymogu SHAP lub formalnego causal inference |
| F20.1–F20.2 Geometria i reprezentacja | F20.1–F20.2 | Wpływ skali na odległość i k-means; projekcja PCA i utrata informacji | Stare 13, bez profili wszystkich serii i kosztownych backtestów |
| F20.3–F20.4 Chain rule i autograd | F20.3–F20.4 | Ręczna pochodna złożenia, autograd CPU, kumulowanie i zerowanie gradientu, zapis urządzenia | Nowy; mały fragment idei starego 13 |
| F20.5 Pierwsza sieć | F20.5 | Mała sieć i model liniowy na tych samych punktach; krzywe oraz jedna kontrolowana zmiana ustawienia | Stare 13, bez globalnego forecast wrappera, GPU, GRU i Lightning |
| F20.6–F20.7 Reprezentacje i tekst | F20.6–F20.7 | Źródła sygnału uczenia, tokeny/ID/embedding i przygotowanie par wejście–następny token | Nowy, bez pobierania modelu językowego i treningu LLM |
| F20.8 Attention | F20.8 | Ręczne scores, wagi i ważona suma; kontrola sumy wag i maskowania przyszłych tokenów | Nowy, małe macierze |
| F21.1 Wyszukiwanie | F21.1 | Stan, dozwolone przejścia i koszty; ślad BFS i uniform-cost search na małym grafie | Nowy |
| F21.2–F21.4 Wnioskowanie i decyzje | F21.2–F21.4, trzy kroki | Posterior ukrytego stanu, dyskontowany return, decyzja przy znanym modelu i przy nieznanych nagrodach; ryzyko eksploracji | Nowy, bez frameworka RL |
| F21.5 Raport końcowy | F21.5 | Zamrożony wybór modelu i baseline, jeden test, ograniczenia oraz rozwiązanie nowych przypadków AI | Wybrane pytania starego 19, bez produktu wdrożeniowego |

## Dane i ciągłość projektu

Używamy małych wspólnych danych: pomiarów i rekordów A–B, syntetycznego panelu kilku serii z opisami C–D, danych projektu, punktów geometrycznych oraz minimalnych danych tekstowych i grafowych F. Wszystko trafia do labs/data/. Pochodzenie danych i licencje opisuje główna licencja treści; nie dodajemy ich kopii do labów.

Wspólna nić projektu to C12, D14, D15, E17, F18 i F21.5. Zapis przebiegów zawiera daty, cechy, ustawienia, protokół oraz wynik modelu i baseline. To dane eksperymentu, nie obowiązek pisania osobistego komentarza po każdym ćwiczeniu. Inne laby mają samodzielne wejścia, aby nieukończony parser lub model nie blokował poznania kolejnego pojęcia.

Projekt korzysta z 42 dni treningu, 7 walidacji i 7 dni końcowego testu. Foldy backtestu na danych projektu kończą się do dnia 42. Walidację można wykorzystywać do porównań, zapisując liczbę prób; nie przedstawiamy jej jako niezależnego potwierdzenia przewagi. Holdout jest publiczny, ale otwieramy go dopiero po zamrożeniu wyboru w F21.5. Wcześniejsze obejrzenie jest ograniczeniem oceny. Weryfikator notebooków nie czyta tego pliku.

A4 wykorzystuje osobny, w pełni widoczny przykład FreshRetailNet. Kopia prognozy w kodzie poprzedza ocenę i nie wymaga pisemnej notatki. D15.4 pokazuje osobno zamrożony horyzont wielodniowy, a projekt C12 zachowuje codziennie aktualizowaną prognozę jednodniową bez ponownego fit na ocenianych dniach.

## Kontrakt uruchamiania do sprawdzenia w pilotażu

Uczestnik pracuje we własnej kopii repozytorium. Wszystkie notebooki otwiera ze wspólnego folderu labs, według instrukcji w głównym README. A korzysta z tymczasowego środowiska uv z Pythonem 3.12, JupyterLab i ipykernel. Kolejne biblioteki dodajemy przed lekcjami, które ich używają. PyTorch działa na CPU. Każdy notebook sprawdza katalog roboczy; dane odczytuje z data/ względem tego folderu.

W B6 i B7 uczestnik pisze także własny moduł i testy. Przy ich wdrażaniu trzeba wskazać jeden wspólny zestaw plików, dopasować importy oraz zawęzić polecenia pytest, mypy i Ruff do bieżącej pracy. Gotowy workflow z B7 pozostaje ćwiczeniem interpretacji CI, bez Dockera. Nie uruchamiamy wszystkich nierozwiązanych labów jako jednego zestawu testów.

## Odzyskanie starych materiałów

Korzystamy z treści dostępnych uczestnikowi w commicie c41404e, nie z gałęzi solutions. Zachowujemy specyfikacje, przypadki brzegowe, kontrolę niezmienności i małe dane. Stary lab 08 rozdzielamy między pierwszy fit C12 i późniejszy gradient D13. Stary 13 rozdzielamy między geometrię/PCA i małą sieć. Z 11 zachowujemy foldy i porównania bez Optuna/MLflow. Ze starego 19 wyłącznie pytania o jakość porównania i ograniczenia, bez opisywania testu przed zamrożeniem wyboru.

Nie przywracamy coursekit, catchup, pełnego panelu, cache, ABC, Protocol, infrastruktury, GPU ani produkcyjnego capstone. F21.5 zachowuje cztery aktualne przypadki: alarm i częstość bazową, trasę o znanych kosztach, weryfikację twierdzenia modelu językowego i odroczone nagrody.

## Kolejność wdrożenia i odbiór

1. Pilot A: gotowe notebooki A2.1–A2.3, A2.4–A2.5, A3 oraz A4.1–A4.2, z ośmioma sprawdzanymi zadaniami i doświadczeniem z kernelem. Kontrole techniczne są wykonane; pilotaż z początkującymi osobami pozostaje do przeprowadzenia.
2. B: pliki, funkcje i własne testy oraz jeden projekt Git. Brak dostępu do konta nie blokuje sprawdzania kodu lokalnie.
3. C: tabele i pierwszy projekt. Pilot C12 sprawdza rzeczywiste przejście od danych do walidacji.
4. D–E: rachunek, rzeczywisty backtest, modele i odtwarzanie eksperymentów. W backteście trzy podziały, świeży fit i rzeczywiste prognozy zamiast samych gotowych metryk.
5. F: małe eksperymenty i zadania pojęciowe. Pilot F19.6–F19.7 wykonuje osoba po odpowiednich wykładach, nie osoba rozpoczynająca programowanie.

Przy każdym wdrożonym bloku od razu aktualizujemy wykład, manifest i kontrole. Pełne zadania A3 i A4.2 są już w labach. Pozostałe zadania notebookowe przenosimy z odpowiednich lekcji C8.3, C12.2–C12.3, E17.2, F18.3, F19.7, F20.4–F20.6, F21.4–F21.5. Tak samo rozwinięcie projektu D15.1 oraz pełne zadania B6.2 i B7.1–B7.2. Nie utrzymujemy dwóch kopii specyfikacji.

## Weryfikacja autora

Manifest mapuje numery wykładów, wymagania z curriculum.json i identyfikatory zadań. tools/verify_labs.py sprawdza format notebooków, brak zapisanych wyjść, składnię, przygotowanie danych i rzeczywiste wykonanie w świeżych kernelach. Poprawne wartości z fixtures przechodzą checkery; puste startery i błędne wyniki są odrzucane. Funkcja testowa Mock zwraca skończone oczekiwane wyniki, nie implementuje rozwiązania zadania. Nie publikujemy referencyjnych funkcji pod nazwą fixtures.

Lokalne notebooki można odroczyć przy problemie instalacyjnym, wykazując podstawy w ćwiczeniach przeglądarkowych. Przed B6.2 potrzebne jest już działające środowisko plikowe. Sprawdzenia autora nie zastępują review kodu uczestnika ani pilotażu. Nie nazywamy przyszłych labów gotowymi na podstawie samego planu.
