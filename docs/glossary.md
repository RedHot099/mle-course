# Słowniczek

Kurs używa angielskich terminów, bo takich używa się w pracy i w dokumentacji. Tu jest ich polskie znaczenie. Definicje dotyczą ścieżki A–F.

| Termin | Po polsku | Znaczenie |
|---|---|---|
| axis | oś | Kierunek w tablicy NumPy: `axis=0` to wiersze (w dół), `axis=1` to kolumny (w poprzek) |
| backtest | test wsteczny | Ocena modelu na kilku kolejnych okresach z przeszłości, każdy z treningiem tylko na danych sprzed niego |
| baseline | punkt odniesienia | Najprostsza sensowna prognoza, z którą porównujesz każdy model |
| batch | partia | Porcja przykładów, na której model robi jeden krok uczenia |
| bias | obciążenie | Metryka: (suma prognoz − suma rzeczywista) / suma rzeczywista. Plus to prognoza za wysoka, minus za niska |
| broadcasting |  | Reguła NumPy dopasowująca kształty dwóch tablic w jednym działaniu |
| calibration | kalibracja | Zgodność przewidywanych prawdopodobieństw z obserwowanymi częstościami |
| CI | ciągła integracja | Automatyczne sprawdzenia uruchamiane na czystej maszynie przy każdej zmianie |
| closure | domknięcie | Funkcja razem ze zmiennymi z otaczającej funkcji, które zapamiętała |
| commit | zatwierdzenie | Zapisany stan zmian w gicie |
| comprehension |  | Wyrażenie budujące listę, słownik albo zbiór z innej kolekcji: `[f(x) for x in xs]` |
| correlation | korelacja | Liczba od −1 do 1 mówiąca, na ile dwie kolumny rosną i maleją razem |
| cutoff | data podziału | Pierwszy dzień, od którego dane trafiają do części walidacyjnej albo testowej |
| dimension table | tabela wymiaru | Tabela z jednym wierszem na obiekt (sklep, produkt), opisująca jego stałe cechy |
| docstring |  | Opis funkcji w potrójnym cudzysłowie zaraz pod `def`; określa jej działanie |
| drift | dryf | Zmiana danych albo zależności w czasie, przez którą model działa gorzej |
| dtype | typ danych | Typ wartości w kolumnie albo tablicy, np. `int8`, `float64` |
| embedding |  | Wyuczony wektor liczb zastępujący wartość kategorii, np. sklep albo produkt |
| epoch | epoka | Jedno przejście uczenia przez wszystkie przykłady treningowe |
| exit code | kod wyjścia | Liczba, którą proces kończy działanie. 0 znaczy sukces |
| F1 |  | Średnia harmoniczna precision i recall |
| fail fast | | Podejście, w którym program przerywa działanie przy pierwszym złamanym założeniu |
| feature | cecha | Kolumna wejściowa modelu |
| fit | dopasowanie | Krok, w którym model zapamiętuje albo wyznacza to, czego potrzebuje do prognozy: dla modeli naiwnych historię, dla modeli uczonych parametry |
| fork | | Własna kopia cudzego repozytorium na GitHubie |
| generator |  | Funkcja z `yield`, która oddaje wartości po jednej, na żądanie |
| gradient descent | spadek gradientu | Uczenie przez przesuwanie parametrów małymi krokami przeciwnie do gradientu straty |
| holdout | okres testowy | Ostatnie okresy danych schowane przed modelem, na których mierzysz jego błąd |
| horizon | horyzont prognozy | Liczba okresów naprzód, na które liczysz prognozę |
| hyperparameter | hiperparametr | Ustawienie modelu wybierane przez człowieka, nie przez uczenie, np. `alpha` albo liczba drzew |
| intercept | wyraz wolny | Stała dodawana do sumy ważonej cech w modelu liniowym |
| JSON |  | Tekstowy format zapisu danych: słowniki, listy, liczby i napisy |
| k-means |  | Klastrowanie, które przypisuje punkty do najbliższego z k środków i przesuwa środki do średnich |
| lag | opóźnienie | Wartość sprzed k wierszy tej samej serii; oznacza k dni tylko przy kolejnych dniach bez luk |
| lambda |  | Krótka funkcja bez nazwy zapisana w jednej linii: `lambda x: x[1]` |
| leakage | przeciek | Użycie w przygotowaniu lub ocenie modelu informacji niedostępnej w chwili podejmowania danej decyzji |
| learning rate | krok uczenia | O ile parametry przesuwają się w jednym kroku gradient descent albo boostingu |
| loss function | funkcja straty | Liczba mierząca, jak bardzo model myli się na danych treningowych. Uczenie ją minimalizuje |
| MAE | średni błąd bezwzględny | Średnia z wartości bezwzględnych różnic między prognozą a rzeczywistością |
| mask | maska | Tablica wartości logicznych wybierająca elementy albo wiersze |
| merge | złączenie | Połączenie dwóch tabel po kluczu |
| moving average | średnia krocząca | Prognoza równa średniej z ostatnich kilku wartości historii |
| MSE | średni błąd kwadratowy | Średnia z kwadratów różnic między prognozą a rzeczywistością |
| mutation testing | testowanie mutacyjne | Sprawdzanie testów przez celowe psucie kodu: dobry test wykrywa zepsutą wersję |
| NaN | brak wartości | Specjalna wartość zmiennoprzecinkowa oznaczająca brak liczby |
| oos (out of stock) | brak towaru | Skrót używany w nazwach kolumn: godziny, w których produktu nie było na półce |
| overfitting | przeuczenie | Dopasowanie modelu do szumu danych treningowych: dobry wynik na treningu, słaby na nowych danych |
| panel | dane panelowe | Wiele szeregów czasowych w jednej tabeli |
| PCA | analiza głównych składowych | Rzutowanie danych na kierunki, wzdłuż których różnią się najbardziej |
| pipeline | potok | Ciąg kroków od surowych danych do wyniku, uruchamiany jednym poleceniem |
| precision | precyzja | Jaka część alarmów była trafiona: TP / (TP + FP) |
| pull request | | Prośba o włączenie zmian z jednej gałęzi do drugiej, razem z miejscem na review |
| recall | czułość | Jaka część zdarzeń została złapana: TP / (TP + FN) |
| regularization | regularyzacja | Ograniczenie lub kara preferująca określone rozwiązania; może pomóc ograniczyć przeuczenie |
| reshape | zmiana kształtu | Ułożenie tych samych wartości tablicy w innej liczbie wierszy i kolumn |
| review | przegląd kodu | Czytanie cudzych zmian przed ich scaleniem |
| Ridge |  | Regresja liniowa z karą za duże wagi (kara L2) |
| rolling origin |  | Schemat backtestu: kolejne okna walidacji, każde po całym treningu |
| rolling window | okno kroczące | Stałej długości wycinek kolejnych dni, przesuwany wzdłuż serii |
| seasonal naive | naiwna sezonowa | Prognoza "tak jak jeden sezon temu", np. jak w tym samym dniu tygodnia tydzień wcześniej |
| series | seria | Jeden szereg czasowy. W tym kursie: jeden produkt w jednym sklepie |
| stable sort | sortowanie stabilne | Sortowanie, które zostawia równe elementy w ich pierwotnej kolejności |
| standardization | standaryzacja | Przeskalowanie cechy tak, żeby miała średnią 0 i odchylenie standardowe 1 |
| stockout | brak towaru | Niedostępność towaru; jest zdarzeniem, a nie brakiem pomiaru |
| target | zmienna celu | Wartość, którą model ma przewidzieć. Na przykład sprzedaż następnego dnia lub zdarzenie niedostępności towaru |
| test set | zbiór testowy | Dane odłożone do jednorazowej, końcowej oceny modelu |
| threshold | próg | Wartość wyniku modelu, od której podnosisz alarm |
| training set | zbiór treningowy | Dane, na których model uczy się parametrów |
| underfitting | niedouczenie | Model zbyt prosty, żeby uchwycić zależność: myli się i na treningu, i na walidacji |
| validation set | zbiór walidacyjny | Dane do porównywania modeli i wyboru ustawień, oddzielne od treningowych |
| vectorization | wektoryzacja | Zastąpienie pętli w Pythonie jednym działaniem na całej tablicy |
| view | widok | Tablica NumPy, która dzieli pamięć z inną tablicą: zmianę w jednej widać w drugiej |
| WAPE |  | Suma błędów bezwzględnych podzielona przez sumę wartości rzeczywistych |
| weights | wagi | Liczby, przez które model liniowy mnoży cechy |
| accuracy | trafność klasyfikacji | Udział wszystkich poprawnych decyzji wśród wszystkich przykładów. |
| likelihood | wiarygodność | Prawdopodobieństwo ustalonych obserwacji traktowane jako funkcja parametru. |
| posterior | rozkład po obserwacji | Rozkład nieznanej wielkości po uwzględnieniu nowych danych i wcześniejszych założeń. |
| self-supervised learning | uczenie z celem z danych | Uczenie, w którym odpowiedź do odtworzenia tworzymy z samych danych. |
| attention | mechanizm uwagi | Ważona suma wektorów wartości; wagi zależą od zgodności zapytania i kluczy. |
| token | jednostka tekstu | Element reprezentacji tekstu przetwarzanego przez model; nie musi być całym słowem. |
| policy | strategia działania | Reguła wyboru działania na podstawie dostępnego stanu lub obserwacji. |
| return | zwrot | Suma przyszłych nagród, ewentualnie pomniejszanych przez dyskontowanie. Nie mylić z instrukcją return w Pythonie. |
| planning | planowanie | Wybór działań przy znanym modelu przejść i nagród. |
| reinforcement learning | uczenie przez wzmacnianie | Uczenie wyboru działań z doświadczenia i nagród, z uwzględnieniem przyszłych skutków. |
