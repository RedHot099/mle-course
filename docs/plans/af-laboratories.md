# Plan laboratoriów do kursu A–F

Status: propozycja po dwóch rundach konsultacji z Opus 5.5, GPT-6.1 Sol i Grok 4.7. Wnioski i rozbieżności opisuje [raport rady](../reviews/af-laboratories-council.md). Pierwotnie dokument był samym planem. Stan wdrożenia: cztery laby sekcji A są teraz przygotowane technicznie do pilotażu; zobacz [laboratoria A](../../labs/index.html). Laby B–F nadal pozostają planem. Pilotaż z początkującymi uczestnikami nie został jeszcze przeprowadzony. Punktem odniesienia jest kurs z commita 2eceb38. Oryginalne materiały analizujemy w commicie c41404e, przed usunięciem labów. Nie korzystamy z gałęzi solutions.

## Jak uczestnik ma pracować

Każdy blok ma wykład i osobne laboratorium. Krótkie ćwiczenia w HTML pozostają częścią wykładu: służą przewidywaniu wyniku i sprawdzaniu pojedynczej operacji. Laboratorium łączy poznane kroki na innych danych i kończy się własnym wynikiem oraz wyjaśnieniem. Zadanie rozbudowane przenosimy z wykładu do jednego laboratorium, a w wykładzie pozostawiamy odnośnik. Nie utrzymujemy dwóch kopii tej samej specyfikacji.

Proponuję 33 laboratoria, zwykle po 1–3 lekcje, z dłuższymi blokami podzielonymi na krótkie etapy. Każda z 70 lekcji ma przypisany lab lub jawnie wskazaną rolę przygotowawczą. A1 jest diagnozą, nie nowym obowiązkiem do zaliczenia. A3 jest warsztatem środowiska. B7 wymaga rzeczywistych plików i terminala; laboratoria pojęciowe w F mogą kończyć się rachunkiem lub notatką, bez sztucznego obowiązku trenowania modelu.

Pierwszy lokalny lab otwieramy dopiero po A3. Do tego momentu uczestnik korzysta z ćwiczeń A2 w przeglądarce. Po A3 wykonuje krótkie utrwalenie A2 w notebooku, z możliwością pominięcia części już wykazanych w diagnozie. Nie wymagamy instalacji notebooka przed lekcją wyjaśniającą, czym jest kernel.

## Mapa laboratoriów

Identyfikatory są propozycją nazw folderów pod labs/. Każdy wiersz określa obowiązkowy wynik, nie tylko temat. Gdy blok obejmuje kilka lekcji, ma kroki odblokowywane po wskazanej lekcji. Uczestnik nie musi najpierw przeczytać całego bloku.

| Lab | Lekcje i moment pracy | Co uczestnik przygotowuje i sprawdza | Materiał wyjściowy |
|---|---|---|---|
| A00 Środowisko | A3 | Zapisany notebook, poprawnie wybrane środowisko i wynik odtworzony po restarcie kernela | Nowy na podstawie A3 |
| A01 Wartości, warunki i pętle | A1 jako diagnoza; A2.1–A2.3, utrwalenie po A3 | Podsumowanie małej listy pomiarów, z zerami i None; ręczny ślad pętli i przypadek pustej listy | Nowy; uproszczone motywy starego 01 |
| A02 Rekordy i funkcja | A2.4–A2.5, po A3 | Funkcja pracująca na rekordach, poprawny return i zachowanie wejścia na nowym przykładzie | Stare 01–02, bez parsera pliku i dekoratorów |
| A03 Pierwsza prognoza | A4.1–A4.2, dwa kroki | Prognoza zamrożona przed okresem oceny, ręczne MAE i interpretacja zer przy niedostępności towaru | Stare 03–05, bez klas i macierzy panelu |
| B01 Kolekcje | B5.1 | Nowa kolekcja bez utraty zer, powtórzeń i kolejności; demonstracja aliasu i kopii | Nowy na podstawie B5.1 |
| B02 Plik i błędne dane | B5.2–B5.3 | Odczyt małego UTF-8, rozróżnienie znacznika braku i błędu, osobny raport, pomocny komunikat | Parser i JSON ze starego 01 w mniejszym formacie, bez TSF i generatora parsera |
| B03 Funkcja i własne testy | B6.1–B6.2 | Funkcja w summary.py, testy wyniku, błędu i niezmienności wejścia; test wykrywa celową zmianę w importowanym pliku | Stare 02 i 04, bez fabryk i klas bazowych |
| B04 Moduł i współpraca | B7.1–B7.2 | README z poleceniami, format/lint/typy/testy, przeczytany diff, lokalny commit oraz PR/CI przy dostępnym koncie | Stare 00 i 04, wybrane elementy 16, bez Dockera |
| C01 Tabela i opis liczb | C8.1–C8.2 | Selekcja maską i nazwami kolumn przy indeksie różnym od pozycji, niezmienione wejście i ręczne statystyki potwierdzone w pandas; jawne ddof | Stare 05–06, mała tabela bez cache |
| C02 Wykres odpowiada na pytanie | C8.3 | Linia, histogram i scatter z opisanymi osiami; interpretacja luki i ograniczeń | Nowy; przydatne fragmenty eksploracji starego 06 |
| C03 Tablice i osie | C9.1–C9.2 | Metryka z tablic, centrowanie, zapis kształtów i kontrola broadcasting na macierzy niekwadratowej | Stare 05, bez pakietowego API metryk |
| C04 Klucze, grupy i złączenia | C10.1–C10.3, osobny krok po każdej lekcji | Raport braków i duplikatów, wynik grupowy oraz wierszowy, złączenie z wykrytą relacją i niedopasowaniem na wspólnym panelu kilku serii | Stare 06–07, bez Excel/cache/downcast |
| C05 Czas i dostępność cech | C11.1–C11.2 | Posortowane dwie serie z kontrolowaną luką; lag i okno bez mieszania serii; tabela dostępności cech; własny test izolacji serii | Stare 07 i 09, bez grafu zależności funkcji |
| C06 Pierwszy model | C12.1–C12.3, trzy etapy | Ręczna prognoza liniowa; projekt na development, baseline i model na tej samej walidacji; scaler i alpha dobierane bez testu | Stare 08, bez adaptera panelu i gradientu przed fit |
| D01 Strata i uczenie | D13.1–D13.4, cztery krótkie kroki | Własna tabela strat, przybliżenie pochodnej, kilka kroków GD, jednoczesna aktualizacja dwóch parametrów | Fragmenty gradientu starego 08, napisane ponownie od jednej wagi |
| D02 Wektory i macierze | D13.5–D13.6 | Iloczyn skalarny i prognozy macierzowe; gradient ręczny i NumPy na n różnym od liczby cech, z własnym testem kształtu i wyniku | Stare 05 i 08, bez własnej klasy estymatora |
| D03 Uczciwe porównanie | D14.1–D14.3 | MAE/WAPE/bias i przypadek zerowego mianownika, przykład przeuczenia; trzy datowane podziały, świeży fit modelu i baseline dla każdego, rzeczywiste prognozy i sparowane wyniki | Stare 05 i 11, bez Optuna i MLflow |
| D04 Cechy i drzewa | D15.1–D15.3 | Kalendarz i znane kategorie, ręczny podział drzewa, porównanie drzewa/lasu/boostingu na walidacji | Stare 09–10, bez target encoding i SHAP |
| D05 Prognoza wielodniowa | D15.4 | Osobne direct i recursive przy zamrożonej chwili prognozy; ślad użytych wartości i kumulacji błędu | Stare 10, niezależny mały szereg |
| D06 Prawdopodobieństwo i alarm | D16.1–D16.3 | Częstości, macierz pomyłek i progi, etykieta jutra z granicą czasu, LogisticRegression z obiema klasami | Stare 12, mały syntetyczny szereg zamiast całego pipeline |
| E01 Obiekt i eksperyment | E17.1–E17.2 | Dwa niezależne obiekty, błąd predict przed fit; odtworzenie dwóch przebiegów z zapisu | Stare 03 i 11, bez ABC/Protocol/MLflow |
| F01 Generalizacja | F18.1–F18.3 | Dwie funkcje zgodne na treningu, wpływ kary, krzywe uczenia i kontrprzykład dla „więcej danych zawsze pomaga” | Nowy; wybrane porównania starego 11 |
| F02 Prawdopodobieństwo i Bayes | F19.1–F19.2 | Rozkład sumujący się do 1, wartość oczekiwana niebędąca pojedynczym wynikiem, sprawdzenie niezależności przez P(A∩B) i P(A)P(B), częstości warunkowe i Bayes, przypadek warunku o prawdopodobieństwie 0 | Nowy |
| F03 Likelihood i klasyfikatory | F19.3–F19.5 | Porównanie parametrów przy tych samych danych, log-loss dla obserwowanej klasy, mały Naive Bayes i porównanie z logistycznym | Nowy, dane wzorowane na starym 12 |
| F04 Niepewność i przyczynowość | F19.6–F19.7 | Tabela kalibracji z licznością grup, dwa przypadki odróżniające zmienność danych od niepewności modelu, decyzja przy kosztach i notatka rozróżniająca prognozę od interwencji | Nowy; bez wymogu SHAP lub formalnego causal inference |
| F05 Geometria i reprezentacja | F20.1–F20.2 | Wpływ skali na odległość i k-means; projekcja PCA i utrata informacji | Stare 13, bez profili wszystkich serii i kosztownych backtestów |
| F06 Chain rule i autograd | F20.3–F20.4 | Ręczna pochodna złożenia, autograd CPU, kumulowanie i zerowanie gradientu, zapis urządzenia | Nowy; mały fragment idei starego 13 |
| F07 Pierwsza sieć | F20.5 | Mała sieć i model liniowy na tych samych punktach; krzywe oraz jedna kontrolowana zmiana ustawienia | Stare 13, bez globalnego forecast wrappera, GPU, GRU i Lightning |
| F08 Reprezentacje i tekst | F20.6–F20.7 | Źródła sygnału uczenia, tokeny/ID/embedding i przygotowanie par wejście–następny token | Nowy, bez pobierania modelu językowego i treningu LLM |
| F09 Attention | F20.8 | Ręczne scores, wagi i ważona suma; kontrola sumy wag i maskowania przyszłych tokenów | Nowy, małe macierze |
| F10 Wyszukiwanie | F21.1 | Stan, dozwolone przejścia i koszty; ślad BFS i uniform-cost search na małym grafie | Nowy |
| F11 Wnioskowanie i decyzje | F21.2–F21.4, trzy kroki | Posterior ukrytego stanu, dyskontowany return, decyzja przy znanym modelu i przy nieznanych nagrodach; ryzyko eksploracji | Nowy, bez frameworka RL |
| F12 Raport końcowy | F21.5 | Zamrożony wybór modelu i baseline, jeden test, ograniczenia oraz rozwiązanie nowych przypadków AI | Wybrane pytania starego 19, bez produktu wdrożeniowego |

Nie wszystkie zadania muszą być programistyczne. F04 i część F11 wymagają uzasadnienia. Automatyczny test nie oceni poprawności twierdzenia przyczynowego. Lab D01 ma przerwy po każdej mikro-lekcji; nie jest jednym zadaniem wymagającym czterech nowych pojęć naraz.

## Format oddzielnego laboratorium

Każdy folder labs/lab-<id>/ zawiera README.md. Lab programistyczny ma notebook lab.ipynb, a od B6 także potrzebne pliki .py. Lab czysto pojęciowy może mieć szablon odpowiedzi w Markdown, ręczny rachunek i rubrykę zamiast pustego notebooka. README podaje wymagane lekcje, dane, polecenie uruchomienia i konkretny wynik do oddania. Notebook zawiera kolejno problem, mały przykład na innych danych, przewidywanie, miejsca na kod, lokalne sprawdzenia, dwie podpowiedzi i rubrykę wyjaśnienia. W B03 i B04 notebook porządkuje pracę, natomiast moduł i testy pozostają w plikach. Nie każemy wykonywać git w komórkach Pythona.

Nie wpisujemy gotowych implementacji zadań do starterów. Każde zadanie kodowe ma stabilny identyfikator, sygnaturę lub nazwy wyników oraz opis wejścia, wyniku i błędów. Nierozwiązany notebook otwiera się bez instalowania niepotrzebnych bibliotek; check zgłasza czytelną informację o nieuzupełnionym zadaniu. Testy sprawdzają zachowanie i nowe małe przypadki, nie tekst kodu. Nie dziedziczymy starego CLI course ani struktury całego src/freshcast.

Przykłady i zadania pojęciowe można liczyć ręcznie. Nie oceniamy wypowiedzi szukaniem słów kluczowych. Rubryki sprawdzają rachunek, artefakt, interpretację i ograniczenie. Nie wymagamy, żeby model uczestnika zawsze wygrywał z baseline.

## Dane i niezależność laboratoriów

Każdy lab ma małe, wersjonowane dane publiczne lub syntetyczne, ich opis i licencję. Notebook wykonujemy z katalogiem roboczym folderu danego labu, zgodnie z kontraktem poniżej. Ścieżki wejściowe są względem tego katalogu. Pierwsza komórka wyjaśnia katalog roboczy i sprawdza dostępność pliku. Wyniki uczestnika zapisujemy oddzielnie od wejścia. Repozytorium autora nie zawiera wyników notebooków.

Poza świadomą kontynuacją B03→B04 oraz nicią projektu C06→D03→D04→E01→F01→F12 lab nie wymaga wygenerowanego pliku z innego labu. Dostarczony CSV jest materiałem do bieżącego pojęcia, a nie referencyjną implementacją zadania. Brak rozwiązania własnego parsera nie blokuje nauki pandas. Klasy nie blokują prawdopodobieństwa; E17 jest wymagane przy własnej klasie sieci w F07.

C06 używa project-development.csv: 42 dni treningu i 7 walidacji. F12 otwiera project-holdout.csv z ostatnimi 7 dniami po zapisaniu modelu, cech, ustawień i protokołu. Pozostałe laby nie czytają holdoutu nawet w komórkach demonstracyjnych. Narzędzie weryfikujące startery nie otwiera tego pliku. Holdout jest publiczny, więc wcześniejsze obejrzenie odnotowujemy i nie nazywamy późniejszego wyniku niezależnym.

D05 używa innych danych i jawnie zamrożonej prognozy wielodniowej. Nie zmienia protokołu projektu C06: to codziennie aktualizowana prognoza jednodniowa, bez ponownego fit na ocenianych dniach. Backtest D03 oraz próby krzywych F01 korzystają z development lub osobnych danych, nigdy z końcowego testu.

W F12 uczestnik może przedstawić wariant z C06 lub później wybrany na walidacji, ale musi zapisać wszystkie próby i zamrozić wybór przed testem. Jeśli projekt jest nieukończony, może nadal rozwiązać przypadki pojęciowe F12; ukończenie części projektowej wymaga własnego działającego modelu, nie wgranego rozwiązania.

## Co odzyskać z oryginału

Źródło to publiczne treści w commicie c41404e: labs/01-python-data do labs/13-unsupervised-nn oraz pytania raportowe labs/19-capstone. B04 może korzystać także z objaśnień lectures/00-setup i wybranych instrukcji Git/CI w labs/16-docker-ci, bez przywracania jego wymagań. Odczytujemy notebooki, README, docstringi i testy dostępne uczestnikowi. Samo występowanie zadania w starym labie nie oznacza możliwości jego skopiowania.

- Zachować specyfikacje, przypadki zer i braków, kontrolę niezmienności wejścia, małe oczekiwane wyniki i pytania o ograniczenia.
- Rozbić stary 08 na C06, D01 i D02. Fit gotowego modelu poprzedza własny gradient i zapis macierzowy.
- Rozbić stary 13 na F05 i F07. Clustering, PCA i sieć nie wymagają wspólnego wrappera prognozy.
- Ze starego 11 zachować foldy i porównania, a dziennik uprościć do jawnego pliku wyników.
- Nie przywracać zależności od coursekit, catchup, pełnego panelu, cache, ABC, Protocol, Docker, AWS, MLflow, Optuna i GPU. Stare 14–18 nie wracają jako ukryte wymagania; wybrane objaśnienia Git/CI ze starego 16 są wyłącznie źródłem do redakcji B04. SQL i inżynieria wdrożeń pozostają poza tym planem.

## Kolejność wdrożenia i warunki odbioru

1. Mapa i jeden wzorzec. Utworzyć manifest mapujący 70 ID lekcji na laby, ustalić identyfikatory zadań, jeden sposób uruchamiania i zapisu wyników. Przygotować pilotaż A00→A01, C06 i F04, bo sprawdzają trzy różne formy nauki. Odbiór: jednoznaczne wymagania i brak nienauczonej operacji. A00/A01 przechodzi osoba zaczynająca programowanie, C06 osoba po wymaganych lekcjach C, a F04 osoba po F19.7. Każda pracuje z tekstem bez dodatkowego wykładu autora. Zmierzyć czas zamiast obiecywać z góry określoną długość.
2. A i B. Przygotować A00–B04 z małymi plikami i sprawdzeniami. Odbiór: kod uruchamia się po restarcie, testy wykrywają konkretny kontrolowany błąd; niedostępne GitHub nie blokuje dalszego Pythona.
3. C i projekt. Przygotować C01–C06 wraz z opisami danych i zamkniętym na tym etapie testem. Odbiór: nowa osoba potrafi przejść od CSV do uczciwej walidacji bez ukończenia starego panelu i klas.
4. D i E. Przygotować rachunki, modele i odtwarzanie eksperymentu. Odbiór: dane o czasie i etykietach są poprawne na granicach podziału, ręczny rachunek odpowiada macierzom, wszystkie części mają artefakt i kryteria.
5. F. Przygotować małe eksperymenty i przypadki rozumowania, PyTorch na CPU. Odbiór: brak dużych pobrań modeli i zewnętrznych API, wynik liczbowy jest oddzielony od interpretacji, F12 zachowuje politykę testu.
6. Integracja. Wykład linkuje konkretny etap labu, lab wraca do potrzebnych objaśnień. Decyzje o przenoszeniu zadań zapadają w etapie 1; przy wdrażaniu każdego bloku od razu aktualizujemy wykład i walidator. Zaktualizować README, mapę kursu, AGENTS, wskazówki tutora i licencję treści tak, żeby laby były pełnoprawną częścią kursu.

Kontrola autora obejmuje poprawny format notebooków, stabilne ID komórek, składnię, brak zapisanych wyjść, działanie komórek przygotowawczych w czystym środowisku i czytelne niezaliczenie pustych starterów. Niezależne przykłady muszą się wykonać. Autor sprawdza pozytywną i negatywną ścieżkę checkerów na tymczasowych małych obiektach; nie publikuje implementacji zadań. Notebook uczestnika nie musi przechodzić Run All jako komplet zaliczonych zadań. Po uzupełnieniu przez uczestnika Run All od świeżego kernela musi odtwarzać pracę w kolejności.

Gotowość całego kursu do ogłoszenia wymaga wszystkich labów z mapy, działających odnośników i pilotażu przynajmniej części A, pierwszego projektu C i pojęciowego F. Nie nazywamy samego szkicu ani nieuruchomionych notebooków ukończonymi laboratoriami.

## Ustalenia techniczne przed pisaniem notebooków

Nazwy A00–F12 w tabeli są skrótami labów, nie ID lekcji. Folder i identyfikator mają obowiązkowy prefiks, np. lab-a00, lab-c06. Manifest oddziela lesson_ids, lab_id i task_ids. Tutor przyjmuje np. lab-c06.2 zamiast domyślać się, czy A1 oznacza wykład, czy ćwiczenie.

Uczestnik pobiera paczkę konkretnego labu, zawierającą notebook, README i potrzebne dane. Rozpakowuje ją do ~/mle-practice/labs/lab-<id>/. Kurs autora pozostaje źródłem materiałów. Nie uruchamiamy wszystkich nierozwiązanych labów jako jednego zestawu pytest. Sprawdzenie wskazuje konkretny plik danego zadania.

Przed B7 uruchamiamy notebook z folderu labu w środowisku tymczasowym uv jak w A3. Po B7 jedynym projektem uczestnika pozostaje ~/mle-practice z pyproject.toml i lockiem; biblioteki dodawane są dopiero przed lekcjami, które ich używają. Jupyter uruchamiamy z folderu labu, ze wskazaniem głównego projektu przez --project ../... Dla struktury labs/lab-c01 poprawny argument to --project ../..; pełny kontrakt poleceń podano poniżej. Pierwsza komórka sprawdza umówiony katalog roboczy i podaje instrukcję naprawy zamiast po cichu zgadywać ścieżki. Moduły .py lokalizują własne dane przez __file__, nie przez katalog uruchomienia notebooka.

B03 i B04 pracują na tych samych summary.py i test_summary.py w ~/mle-practice/labs/lab-b03/. Lab B04 zawiera instrukcje pracy i ewentualny notebook raportowy, ale nie drugą kopię tych plików. Przy wdrażaniu ujednolicamy B7.2 tak, aby nie przenosiło pracy do drugiego klonu ml-basics. Zachowujemy dane uczestnika; GitHub jest podłączany do jego istniejącego projektu. Każde polecenie pytest, formatowania i mypy obejmuje jawne pliki, nie cały katalog labów. Od C uczestnik dopisuje małe testy także w C05 i D02; po większym etapie zapisuje lokalny commit. Nie wymaga to wysyłania zmian ani dostępu do konta.

C06 wprowadza prostą tabelę przebiegów: run_id, daty treningu i walidacji, cechy, model, ustawienia, protokół oraz wynik modelu i baseline. D03, D04, E01 i F01 rozwijają tę samą konwencję. Na potrzeby nauki bieżącego pojęcia można użyć osobnego małego doświadczenia z dostarczonym wejściem. Nie zastępuje ono jednak ukończenia własnego projektu wymaganego do części projektowej F12.

Zestaw danych nie oznacza nowego schematu dla każdego labu. Wystarczą wspólne małe rodziny: pomiary/rekordy A–B, syntetyczny panel kilku serii z tabelą opisową C–D, development projektu, punkty geometryczne/nieliniowe oraz minimalne tablice tekstowe i grafowe F. Każdy lab otrzymuje tylko swój potrzebny wycinek. Paczki przed F12 nie zawierają holdoutu. Dotychczasowy plik w repo pozostaje publiczny i nie jest zabezpieczeniem technicznym; ograniczenie oraz wcześniejszą ekspozycję opisujemy uczciwie.

W etapie 1 powstaje specyfikacja i prototyp polecenia tools/verify_labs.py, z nbformat i nbclient jako zależnościami autora. Walidator sprawdza manifest względem 70 ID, kolejność etapów, istnienie zadań i checkerów, format notebooków, komórki przygotowawcze i puste startery. Osobno sprawdza pozytywną i negatywną ścieżkę checkerów na jawnych syntetycznych danych i oczekiwanych wynikach. Używa fixtures z wejściami i oczekiwanymi wynikami, a nie referencyjnych implementacji funkcji ani odczytu gałęzi solutions. Testy poprawności wyników numerycznych mają niezależne rachunki lub wynik drugiej metody bibliotecznej. Nie zastępujemy weryfikacji poprawności checkera samym sprawdzeniem, że starter nie przechodzi. W B03 wystarcza jedna kontrolowana zmiana własnej funkcji uczestnika, po kopii zapasowej; nie przywracamy ośmiu mutantów i ich osobnego frameworka.

Etap 1 określa migrację wszystkich 11 zadań notebookowych obecnie sprawdzanych licznikiem rubryk HTML. C8.3 przechodzi do lab-c02, C12.2–C12.3 do lab-c06, E17.2 do lab-e01, F18.3 do lab-f01, F19.7 do lab-f04, F20.4 do lab-f06, F20.5 do lab-f07, F20.6 do lab-f08, F21.4 do lab-f11, F21.5 do lab-f12. Wykład zachowuje krótkie pytanie o pojęcie i link do zadania; pełna specyfikacja i rubryka mają jedno źródło w labie. Walidator przestaje wymagać sztywno 11 rubryk w HTML. Te zmiany trafiają razem z odpowiednim labem, nie dopiero na końcu całego wdrożenia.

## Kontrakt uruchamiania do sprawdzenia w pilotażu

Poniższe polecenia są projektowaną instrukcją uczestnika, a nie poleceniami wykonanymi na maszynie autora. Katalog główny ~/mle-practice powstaje w A3, a paczki nie nadpisują istniejącej pracy. Kolejne wydanie labu wymaga porównania zmian albo rozpakowania obok, nie automatycznego zastąpienia rozwiązania.

Przed B7, po rozpakowaniu paczki A00:

```bash
cd ~/mle-practice/labs/lab-a00
uv run --no-project --python 3.12 --with jupyterlab --with ipykernel jupyter lab
```

W B03 notebook otwieramy tym samym sposobem z labs/lab-b03. Moduł oraz test leżą obok niego. Testy wykonujemy w terminalu w tym samym folderze:

```bash
uv run --no-project --python 3.12 --with pytest python -m pytest -q test_summary.py
```

B7 tworzy projekt uv w istniejącym katalogu głównym, nie wewnątrz labu, dodaje Jupyter i narzędzia poznane w B, a następnie podłącza git do tego katalogu. Nie inicjalizuje drugiego repozytorium w lab-b03 i nie kopiuje rozwiązania do innego projektu. Przykładowe docelowe sprawdzenia uruchamiane z korzenia:

```bash
uv run pytest -q labs/lab-b03/test_summary.py
uv run ruff check labs/lab-b03/summary.py labs/lab-b03/test_summary.py
uv run ruff format --check labs/lab-b03/summary.py labs/lab-b03/test_summary.py
uv run mypy --disallow-untyped-defs labs/lab-b03/summary.py
```

Gotowy checks.yml wykonuje dokładnie ten sam zakres, bez przeszukiwania nierozwiązanych labów. B04 uczy interpretacji CI, nie pisania frameworka ani kontenera.

Przed C01, w korzeniu projektu, uczestnik dodaje numpy, pandas, matplotlib i scikit-learn. Notebook uruchamia następująco:

```bash
cd ~/mle-practice/labs/lab-c01
uv run --project ../.. jupyter lab
```

Przed F06 dodaje torch z indeksu CPU poleceniem z F20.4, w korzeniu projektu. F07 korzysta z tego samego środowiska. Biblioteki nie są pobierane przy samym otwieraniu notebooka. Pilotaż sprawdza przejścia A00→B03→B04→C01 oraz F06 od świeżego kernela. Konkretne polecenia tworzenia projektu, instalacji i wyboru kernela muszą zostać przećwiczone na kopii roboczej, zanim nazwiemy ten kontrakt zweryfikowanym.

Manifest przechowuje wymagane ID lekcji dla każdego kroku i kontroluje ich zależności z curriculum.json. Zgrupowanie lekcji w jednym folderze nie dodaje zależności od późniejszych kroków. Na przykład krok rachunku w F06 wymaga pełnego requires F20.3, a krok autograd również F20.4. Kontrola wykrywa etap wymagający pojęcia dopiero wprowadzanego później. Pilotaż obejmuje osobę na rzeczywistym poziomie danego labu.

Poza 11 zadaniami notebookowymi przenosimy pełne zadanie restartu A3 do lab-a00, zadanie własnych testów B6.2 do lab-b03 oraz pełne zadanie README i sprawdzeń B7.1 i workflow B7.2 do lab-b04. Wykład zachowuje objaśnienie i krótki przykład. Nie mnożymy czynności do zaliczenia: pojedynczy artefakt ma jedną specyfikację i jedno miejsce oddania.

Wielokrotne wybieranie na tej samej walidacji może prowadzić do dopasowania decyzji do tego okresu. Dziennik zapisuje także słabe próby i liczbę wariantów; nie przedstawiamy najlepszej walidacji jako niezależnego potwierdzenia przewagi. Tydzień testu jest krótki, a jego wynik także wymaga ostrożnej interpretacji. Foldy D03 w projekcie kończą się najpóźniej w dniu 42, np. oceniane dni 15–21, 22–28 i 29–35. Alternatywą jest osobny szereg; F01 może celowo utrzymywać walidację projektu, żeby porównanie krzywych miało wspólny punkt odniesienia.

F12 zachowuje wszystkie cztery przypadki obecnej lekcji F21.5: alarm i częstość bazową, trasę o znanych kosztach, sprawdzanie twierdzenia modelu językowego oraz odroczone nagrody. Ze starego capstone nie kopiujemy instrukcji obejrzenia lub opisania testu przed zamrożeniem wyboru, ani wymagań produktu, kontenera, MLflow, GRU czy wygrania z baseline. Odzyskujemy tylko strukturę uzasadnionego porównania i pytania o ograniczenia.

C01 sprawdza oczekiwane wiersze i kolumny oraz niezmienność całego wejścia, na indeksie z etykietami różnymi od pozycji. Uczy .loc, ale checker nie przeszukuje tekstu rozwiązania. Poprawna równoważna implementacja również spełnia wymaganie.

Odbiór prototypu verify_labs obejmuje rzeczywiste wywołanie checkera z notebooka po restarcie kernela: poprawny syntetyczny wynik przechodzi, błędny i pusty starter dostają pomocny komunikat. Syntetyczna próba zamrożenie→ocena sprawdza integrację finału bez odczytu prawdziwego holdoutu. Te kontrole nie są jeszcze wykonane; stanowią kryteria przyszłego wdrożenia.

Lokalne wykonanie części A01–B02 można odroczyć do B6.2 przy problemie instalacyjnym. Potrzebne pojęcia sprawdzamy wcześniej w ćwiczeniach przeglądarkowych i własnym wyjaśnieniu; nie skreślamy praktyki z programu. B03 wymaga już rzeczywistych plików i działającego środowiska. Nie oceniamy braku dostępu do instalacji jako braku zrozumienia Pythona.

Do wykazu migracji dopisujemy także rozwinięcie projektu z D15.1 do lab-d04. Wszystkie pozostałe zadania HTML przechodzą w etapie 1 przegląd retain/move/extend. Nowe wymaganie labu musi wskazywać nowy artefakt lub decyzję; samo użycie innych liczb nie uzasadnia ponownego obowiązku.

Dla pozytywnych testów checkerów wybieramy fixtures z wejściami, oczekiwanymi wartościami i uzasadnieniem rachunku, bez implementacji funkcji będących rozwiązaniami zadań. Checker porównujący wyniki testujemy, podając te wartości i kontrolowane błędy. Zestaw przypadków obejmuje zera, braki, niezmienność i błędne kształty, jeśli należą do umowy zadania. Wywołanie funkcji uczestnika i przekazanie jej wyników do checkera jest osobną częścią integracji. Nie publikujemy referencyjnych funkcji pod nazwą „obiekty testowe”. Jeżeli danej integracji nie da się udowodnić samymi fixtures i przygotowanym szkieletem, oznaczamy ją jako nieweryfikowaną do pilotażu zamiast deklarować test pełnego poprawnego rozwiązania.

## Decyzja o liczbie labów

Zachowujemy 33 krótkie bloki zamiast automatycznie łączyć F02 z F03 oraz F10 z F11. Wspólny folder nie zlikwidowałby wymagań poszczególnych kroków, a rozdzielenie ułatwia powrót do konkretnej trudności. F08 pozostaje krótkim ćwiczeniem sygnału uczenia i reprezentacji tekstu. Nie obiecujemy 33 pełnych spotkań ani określonej liczby godzin. Czas i ewentualne dalsze połączenia rozstrzygnie pilotaż.
