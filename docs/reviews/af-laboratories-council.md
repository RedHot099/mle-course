# Wnioski rady: laboratoria A–F

Przedmiotem konsultacji był plan przywrócenia formy wykład + osobne laboratorium do kursu 70 lekcji w commicie 2eceb38. Rada wykonała dwie rundy: trzy niezależne oceny, a następnie sprawdzenie wspólnej listy uwag i sprzeciwów autora. Ostateczny [plan laboratoriów](../plans/af-laboratories.md) uwzględnia poprawki po obu rundach. Laby nie zostały jeszcze wdrożone.

Uczestnicy: claude-opus-5-5 przez claudeAgent, gpt-6.1-sol przez Codex i grok-4.7 przez Cursor. W tej konsultacji Grok był dostępny przez Cursor; wyłączony natywny dostawca Grok nie był używany. Recenzenci czytali bieżące lekcje, katalog i narzędzia oraz oryginalne materiały uczestnika w commicie c41404e. Nie czytali gałęzi solutions ani zawartości holdoutu. Nie wykonali przyszłych notebooków, bo jeszcze nie istnieją.

## Wniosek

Wszyscy potwierdzili pokrycie 70 lekcji i zasadność podziału praktyki na mniejsze bloki. Proponuję 33 laboratoria, z etapami odblokowywanymi po odpowiednich lekcjach. To decyzja autora po konsultacji, nie jednomyślne zalecenie konkretnej liczby. Część pojęciowa może kończyć się rachunkiem i notatką; nie każdy lab wymaga treningu modelu lub notebooka.

## Najważniejsze uwagi i rozstrzygnięcia

1. [High, C1, wszyscy] Jedno miejsce pracy i sprawdzalny start. Plan określa ~/mle-practice, dostarczenie paczek do labs/lab-<id>, wspólny katalog B03/B04, uruchamianie Jupyter, etapowe zależności i ograniczony zakres pytest. Wdrożenie musi jednocześnie poprawić polecenia B7 oraz dostarczony workflow. Dowód pierwotnej rozbieżności: B7.1 tworzy osobny projekt, a B7.2 kopiuje pliki do innego klonu. [Kontrakt](../plans/af-laboratories.md#kontrakt-uruchamiania-do-sprawdzenia-w-pilotażu) jest teraz konkretny, ale wymaga wykonania w pilotażu.
2. [High, C2, wszyscy] Jedno zadanie ma jedno źródło. Plan mapuje migrację 11 zadań z rubrykami i pełnych zadań A3, B6.2, B7.1–B7.2 oraz D15.1. Zmiana wykładu, labu i walidatora następuje razem. Dotychczas tools/verify_foundations.py wymaga dokładnie 11 rubryk w HTML; wdrożenie musi usunąć to założenie, nie zostawić dwóch kopii zadań. Krótkie ćwiczenia HTML pozostają rozgrzewką.
3. [High/Medium, C3, Opus i Sol; potwierdzone przez Groka] Checker wymaga dowodu poprawnego przejścia, a nie tylko odrzucenia pustego startera. Plan wybiera fixtures z wynikami i niezależnym rachunkiem, bez publicznych referencyjnych implementacji. Prototyp sprawdzi także notebookowe wywołanie checkera po restarcie. Nieweryfikowalną jeszcze integrację trzeba oznaczyć, a nie nazwać przetestowaną. Nie przyjęto wymogu gałęzi rozwiązań ani frameworka ośmiu mutantów; obecne B6.2 uczy jednej kontrolowanej zmiany własnej funkcji.
4. [High, C4, Opus; potwierdzone w drugiej rundzie] Projekt trwa przez C06, D03, D04, E01, F01 i F12. Wynika to z powrotów do własnego projektu w D15.1, E17.2 i F18.3. Plan wprowadza wspólny dziennik przebiegów od C06. Osobne małe wejścia pomagają ćwiczyć temat, ale nie zastępują własnego projektu na finał.
5. [Medium, C5, Sol; potwierdzone przez pozostałych] D03 rzeczywiście wykonuje backtest. Uczestnik tworzy trzy podziały, dopasowuje świeży model i baseline, wykonuje prognozy i liczy sparowane wyniki. Samo odejmowanie gotowych wyników, obecne w ćwiczeniu D14.3, nie wystarcza jako całe laboratorium.
6. [Medium, C6, Sol; potwierdzone przez pozostałych] Mapa ID nie zastępuje mapy umiejętności. F02 obejmuje wartość oczekiwaną, niezależność i niemożliwe warunkowanie. F04 obejmuje dwa źródła niepewności, liczności grup kalibracyjnych i ograniczenia wniosków. Te umiejętności wynikają z F19.1 i F19.6.
7. [Medium, C7, Opus; potwierdzone przez pozostałych] Wspólne małe dane i dalsza praktyka inżynierska. Plan uwzględnia panel kilku serii, własne testy w C05 i D02 oraz commity po większych etapach. Nie wymaga commita po każdym rachunku ani jednego nowego schematu danych na każdy lab. Pilotaż obejmuje ryzykowny projekt C06.
8. [Medium, C10, wszyscy] Wymagania obowiązują na poziomie kroku. Manifest zachowuje requires z curriculum.json, np. F20.3 wymaga D13.6 i F19.4. Pilotaż A, C i F przechodzą osoby po odpowiednim przygotowaniu. Lokalna konfiguracja może poczekać do B6.2, ale potrzebna praktyka pojęć pozostaje obowiązkowa; można ją wykazać wcześniej w przeglądarce.
9. [Low, C12, Grok; potwierdzone przez pozostałych] C01 wymaga rzeczywistego wyboru po etykietach i zachowania wejścia. Plan dodaje indeks różny od pozycji i testy oczekiwanego wyniku. Odrzucono kontrolowanie tekstu kodu w celu wymuszenia jednej implementacji.

## Rozbieżności

- C8: Grok początkowo uznał ponowne używanie walidacji za zużycie końcowej oceny. W drugiej rundzie wszyscy odrzucili ten zakaz. Walidacja służy do wyboru; ryzykiem jest wielokrotne dopasowywanie decyzji do tego samego tygodnia. Plan wymaga zapisu prób i ostrożnych wniosków. Foldy D03 w projekcie kończą się do dnia 42; dni 43–49 są walidacją, 50–56 jednorazowym testem.
- C9: nie potwierdzono, że odzyskanie pytań raportowych starego capstone przywraca cały produkt z Dockerem i GRU. Plan wprost je wyklucza, zachowuje cztery aktualne przypadki F21.5 i zabrania kopiowania starej instrukcji oglądania tygodnia testowego przed oceną.
- C11: odrzucono usunięcie dostarczonego workflow. B7.2 już wprowadza checks.yml i CI. Lab zachowuje tę praktykę przy dostępnym koncie, bez pisania infrastruktury i bez Dockera.
- Liczba labów: Opus dopuszczał połączenie F02 z F03 i F10 z F11, Grok zalecał osobne bloki. Zachowujemy je osobno ze względu na różne cele i wymagania kroków. F08 pozostaje krótkim ćwiczeniem reprezentacji i tekstu. Foldery nie oznaczają pełnych jednostek godzinowych; czas sprawdzi pilotaż.

## Zalecana kolejność prac

Najpierw manifest, kontrakt uruchamiania i prototyp weryfikacji, wraz z pilotażem A00/A01, C06 i F04. Następnie A–B, C z projektem, D–E oraz F z finałem. Integracja odnośników i migracja zadań odbywają się w każdej części. Na końcu sprawdzenie całej ścieżki i braków połączeń.

Odzyskujemy zadania, specyfikacje, przypadki brzegowe i pytania ze starych labów, nie ich łańcuch zależności. Szczególnie stary 08 rozdzielamy między pierwszy fit i późniejszy gradient, a stary 13 między geometrię, PCA i sieć CPU. Nie przywracamy coursekit, catchup, pełnego panelu, chmury, GPU ani produkcyjnego capstone.

Kontrola planu potwierdziła 33 bloki i przypisanie wszystkich 70 ID lekcji bez pominięć i powtórzeń. Nie jest to kontrola poprawności przyszłych labów. Przed ogłoszeniem ich gotowości potrzebne są rzeczywiste notebooki, sprawdzenia oraz pilotaż opisany w planie.
