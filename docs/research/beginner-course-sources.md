# Źródła do przebudowy kursu dla początkujących

Data weryfikacji: 27 października 2026. Dokument uzupełnia [audyt struktury kursu](beginner-curriculum-audit.md).

Porównuję publiczne programy, opisy ćwiczeń i wymagania wstępne. Nie przechodziłem płatnych kursów ani nie sprawdzałem jakości wszystkich nagrań. Publiczny syllabus pokazuje projekt kursu, ale nie dowodzi jego skuteczności. Liczby ocen, popularność i hasła marketingowe nie są podstawą zaleceń. Kolejność tematów jest punktem odniesienia, a nie uniwersalnym przepisem.

## Python for Everybody rozkłada podstawy na osobne kroki

[Autorska lista lekcji PY4E](https://www.py4e.com/lessons) prowadzi od instalacji i celu programowania przez zmienne, warunki, funkcje, pętle, stringi i pliki do list, słowników oraz tuples. Dopiero potem pojawiają się regex, sieć, web services, OOP, bazy i wizualizacja. Autor kieruje materiały także do osób bez doświadczenia programistycznego.

[Program specjalizacji University of Michigan na Coursera](https://www.coursera.org/specializations/python) dzieli naukę na pięć kursów: podstawy programowania, struktury danych, pobieranie danych z sieci, bazy danych i capstone. OOP jest wymienione w kursie baz danych. Nie stanowi warunku rozpoczęcia pracy z plikami i kolekcjami.

Wniosek projektowy dla mle-course: osobna ścieżka podstaw Pythona może poprzedzać właściwe ML Engineering. Osoba znająca składnię powinna móc ją ominąć po diagnozie. Dla osoby bez doświadczenia lista i słownik wymagają ćwiczeń przed panelami danych czy interfejsami modeli.

## Stanford rozróżnia naukę programowania od zaawansowanego ML

[Oficjalny opis CS106A](https://bulletin.stanford.edu/courses/1056441) nie wymaga wcześniejszego programowania. Akcentuje dekompozycję, abstrakcję, testowanie i styl. [Publiczny harmonogram CS106A](https://web.stanford.edu/class/cs106a/schedule) wprowadza funkcje i dekompozycję na początku, a klasy po pracy z listami, stringami, plikami, słownikami i strukturami zagnieżdżonymi, w tygodniu 8. Harmonogram zawiera zadania i dwa sprawdziany diagnostyczne.

Uwaga o wersji: podstrony CS106A nie są jednolite. Główna strona w dniu sprawdzenia opisuje Autumn 2026, a podstrona harmonogramu pokazuje inne daty rozpoczęcia zajęć. Dlatego powyższa kolejność odnosi się do wskazanego publicznego harmonogramu, nie do potwierdzonego planu bieżącego semestru.

[Archiwalny syllabus CS106A, aktualizacja 2 lipca 2022](https://web.stanford.edu/class/cs106a/syllabus) opisuje rozpoczęcie ćwiczeń w środowisku przeglądarkowym, a później większe zadania lokalnie. Przewiduje cotygodniowe małe grupy, konsultacje, krótkie aktywności podczas wykładu i programistyczne zadania domowe. To ważny kontekst: kurs samodzielny musi zaplanować własny odpowiednik takiej pomocy.

[CS229, Spring 2026](https://cs229.stanford.edu/index.html-spr26) wymaga umiejętności pisania nietrywialnego programu w Python i NumPy, rachunku prawdopodobieństwa, rachunku wielu zmiennych oraz algebry liniowej. Część materiałów tego wydania wymaga konta Stanford.

[CS230](https://cs230.stanford.edu/) wymienia prawdopodobieństwo, statystykę i data science, algebrę liniową oraz samodzielne pisanie nietrywialnych programów. Łączy wykłady, zadania programistyczne, quizy, konsultacje i projekt z etapami proposal, milestone, report.

Wniosek projektowy: CS229 i CS230 pomagają określić docelowe kompetencje. Ich wymagania nie pasują jako domyślny poziom wejścia dla osoby uczącej się pierwszych funkcji. Z CS106A warto przejąć stopniowanie złożoności, z CS230 etapowanie projektu, a nie kopiować cały zakres tych kursów do jednego kursu wprowadzającego.

## Coursera Machine Learning Specialization odróżnia początkującego w ML od początkującego w kodowaniu

[Program i FAQ specjalizacji DeepLearning.AI oraz Stanford Online](https://www.coursera.org/specializations/machine-learning-introduction/) wymagają podstaw kodowania, takich jak pętle, funkcje i warunki, oraz licealnej arytmetyki i algebry. Kursy idą kolejno przez regression i classification, advanced learning algorithms oraz unsupervised learning, recommenders i reinforcement learning.

FAQ opisuje wizualną intuicję przed implementacją, dodatkowe wyjaśnienia matematyczne i nieoceniane notebooki z przykładami oraz interaktywnymi wykresami przed ocenianymi zadaniami. To deklarowana konstrukcja materiałów, nie niezależny pomiar efektów.

Wniosek projektowy: w mle-course można zachować samodzielne pisanie rozwiązań i dodać poprzedzające je demonstracje na innych danych. Pokaz działania algorytmu nie musi zawierać rozwiązania ocenianego zadania. Osobny próg wejścia powinien sprawdzać podstawy programowania.

## CS50P pokazuje, że testy mogą poprzedzać OOP

[Publiczny kurs Harvard CS50P](https://cs50.harvard.edu/python/) obejmuje kolejno funkcje i zmienne, warunki, pętle, wyjątki, biblioteki, unit tests, pliki, regex i OOP. Można pracować w przeglądarce. Kurs zawiera problem sets oraz projekt końcowy i dopuszcza osoby bez wcześniejszego doświadczenia.

Wniosek projektowy: pierwsze testy zwykłych funkcji nie potrzebują wcześniejszej nauki dziedziczenia, ABC ani Protocol. Istnieje użyteczny wzorzec nauczania sprawdzania zachowania programu przed bardziej rozbudowaną organizacją kodu.

## Udemy daje przykłady małych ćwiczeń i widocznych rezultatów

[The Complete Python Bootcamp, Jose Portilla i Pierian Training](https://www.udemy.com/course/complete-python-bootcamp/) publikuje w syllabusie ćwiczenia dotyczące pojedynczych funkcji, np. warunków logicznych i filtrowania liczb. Przedstawia również zadania domowe, quizy oraz trzy większe projekty. W widocznym programie osobno występują warunki i pętle, metody i funkcje oraz obsługa wyjątków. Publiczna strona nie ujawnia wszystkich sekcji w takim samym zakresie, więc nie odtwarzam pełnej kolejności kursu.

[100 Days of Code, Angela Yu, publiczna strona Udemy](https://angelone.udemy.com/course/100-days-of-code/) pokazuje pierwsze dni poświęcone zmiennym, typom, warunkom, listom i pętlom, a potem funkcjom. Każdy z tych dni kończy mały projekt. [Companion przygotowany przez autora na JetBrains Academy](https://academy.jetbrains.com/course/25212) potwierdza rozłożenie funkcji na definicję, parametry i wartości zwracane w różnych dniach. W dniu 13 wymienia osobne ćwiczenia z odtwarzania błędu, przewidywania wykonania kodu i używania debuggera.

Wniosek projektowy: pojedyncza sesja powinna kończyć się konkretnym rezultatem. Wczesny moduł o funkcjach warto podzielić na zwykłe argumenty i return, a później kompozycję i bardziej zaawansowane mechanizmy. Długości filmów ani marketingowych "dni" nie należy przenosić wprost na szacunek czasu samodzielnej pracy.

## Co wynika z porównania, a czego źródła nie rozstrzygają

Powtarzają się rozłożenie podstaw na mniejsze zadania, praktyka przed dużym projektem i jawne wymagania wejściowe. Kilka programów umieszcza OOP po dłuższej praktyce na funkcjach i danych. To uzasadnia rozważenie innej kolejności mle-course, ale samo w sobie nie dowodzi, że każdemu odbiorcy pomoże ten sam układ.

Na podstawie syllabusów nie da się ustalić optymalnej długości lekcji, prawdopodobieństwa ukończenia kursu ani liczby potrzebnych podpowiedzi. Te decyzje trzeba sprawdzić na początkujących uczestnikach, obserwując samodzielne wykonanie zadań i rozumienie wyników.

Przegląd badań i rekomendacji dydaktycznych jest w głównym audycie. Powyższe przykłady kursów stanowią osobną kategorię dowodów.

## Pogłębienie ML i AI według Stanford

Ta część dotyczy dalszej zmiany kierunku programu: czas przewidziany na rozbudowę pipeline'u, CI, pracę w cudzym repozytorium i duży capstone ma służyć lepszemu rozumieniu ML oraz AI. To decyzja o celu kursu. Poniższe programy pomagają dobrać pojęcia, ale nie uzasadniają pomijania ćwiczeń, sprawdzania wyników czy utrwalania wiedzy.

### CS229 łączy algorytmy przez założenia i sposób uczenia

[Archiwalny harmonogram CS229, Autumn 2018](https://cs229.stanford.edu/syllabus-autumn2018.html) zaczyna od supervised learning i linear regression. Potem przechodzi do logistic regression, exponential family i generalized linear models, a następnie do Gaussian discriminant analysis, Naive Bayes, SVM i kernels. Kolejne bloki obejmują bias-variance, regularization i model selection, tree ensembles oraz neural networks. Po nich występują k-means, Gaussian mixtures, EM i redukcja wymiarów, a później MDP i reinforcement learning. Learning theory ma osobne zajęcia uzupełniające. To kolejność tego konkretnego wydania, nie stały plan wszystkich edycji.

[Oficjalny pakiet Stanford Engineering Everywhere CS229](https://see.stanford.edu/Course/CS229) udostępnia notatki o regression, classification, GLM i generative learning oraz wymienia learning theory, w tym bias-variance i VC theory. Wymaga samodzielnego programowania, prawdopodobieństwa i algebry liniowej. Poziom wejścia aktualniejszych wydań CS229 opisano wcześniej w tym dokumencie.

Moja propozycja dla początkującego to trzy powroty do znanych modeli:

1. Najpierw model jako funkcja, loss i uczenie parametrów. Uczestnik oblicza mały przykład i przewiduje skutek zmiany parametru.
2. Potem model jako założenie probabilistyczne. Gaussian noise i Bernoulli pomagają wrócić do regression oraz classification. Likelihood wyjaśnia, skąd bierze się cel uczenia. GLM jest nazwą wspólnej idei dopiero po tych przykładach, a pełna exponential family może być dodatkiem.
3. Następnie generalizacja. Learning curves, bias-variance i regularization prowadzą do pytania o wyniki na nowych danych. Learning theory można wprowadzić intuicyjnie jako ograniczenia wnioskowania ze skończonej próby. Dowody VC theory nie są konieczne w rdzeniu dla początkujących.

Osobna lekcja powinna zestawić discriminative i generative learning. W tym zestawieniu generative oznacza modelowanie rozkładu danych, a nie wyłącznie generowanie tekstu przez LLM. Prosty Naive Bayes jest użytecznym kolejnym przykładem po prawdopodobieństwie warunkowym. To moja propozycja zakresu, nie zalecenie przepisane z syllabusa.

### CS221 rozszerza AI poza przewidywanie etykiet

[CS221, Autumn 2025](https://stanford-cs221.github.io/autumn2025/) prowadzi od learning przez search i MDP do games, Bayesian networks oraz logic. Wymaga programowania na poziomie CS106A i CS106B, discrete math, probability i linear algebra. Autorzy wprost ostrzegają przed szybkim tempem i równoczesnym nadrabianiem podstaw. Program obejmuje też language models oraz AI & society.

Na tej podstawie proponuję krótszy blok pokazujący cztery różne pytania:

| Pytanie | Pojęcie | Małe doświadczenie uczestnika |
|---|---|---|
| Jak przewidzieć wynik na podstawie przykładów? | Learning | Porównać predictions dwóch znanych modeli |
| Jak znaleźć sekwencję działań do celu? | Search | Prześledzić wyszukiwanie drogi na małym grafie |
| Jak wybrać działanie przy niepewnych skutkach? | MDP i RL | Policzyć oczekiwany reward, potem odróżnić znane przejścia od uczenia przez doświadczenie |
| Jak zmienić przekonanie po nowej obserwacji? | Probabilistic inference | Uaktualnić prawdopodobieństwa w małej tabeli |

To autorskie uproszczenie zakresu CS221. Nie należy obiecywać opanowania całego AI na podstawie tych czterech doświadczeń. Search wymaga wcześniejszego wprowadzenia grafu, a MDP wymaga probability i expected value. Bez tych przygotowań zmiana tematu stworzy kolejne miejsce utknięcia.

### CS336 jest przykładem późniejszej specjalizacji LLM

[CS336, Spring 2025](https://cs336.stanford.edu/spring2025/index.html) obejmuje tokenization, architekturę Transformer, uczenie, scaling, evaluation, przygotowanie danych i alignment. Wymaga biegłego Pythona, doświadczenia w deep learning, PyTorch i optymalizacji systemów oraz matematyki akademickiej. Zadania obejmują samodzielny model językowy i optymalizację GPU. Strona określa kurs jako intensywny implementacyjnie.

Wniosek dla mle-course: przegląd idei tokenów, embeddings, attention i przewidywania następnego tokena może pokazać kierunek dalszej nauki. Implementacja i trenowanie LLM według CS336 powinny pozostać późniejszą gałęzią. Dodanie do rdzenia całego zakresu CS229, CS221 i CS336 ponownie przeciążyłoby początkującego. Lepsza jest mniejsza liczba pojęć, do których uczestnik wraca w kolejnych doświadczeniach.
