# ML Engineering from Scratch: dokument projektowy

Ten plik istnieje tylko na gałęzi `solutions`. Zawiera spoilery (zasiane błędy w `shelfwise`, pułapki w labach), więc nie trafia do widoku kursanta.

Stan: ustalenia z sesji projektowej z 30.09.2026. Interfejsy pakietu w sekcji 5 to plan. Ostateczny kształt ustala kod referencyjny.

## 1. Cel, odbiorca, granice

**Odbiorca.** Student, analityk albo osoba zmieniająca zawód. Zna zmienne, pętle, funkcje, listy i słowniki. Nie zna klas, typowania, gita, terminala, NumPy, pandas ani statystyki. Matematyka na poziomie liceum.

**Wyjście.** Absolwent potrafi:
1. wziąć ticket w cudzym codebase (nowa cecha, nowa metryka, bug w pipeline) i oddać PR z testami, typami i zielonym CI, wymagający tylko zwykłego review,
2. samodzielnie przejść od baseline do dostrojonego modelu z walidacją po czasie i obronić wynik.

Capstone sprawdza jedno i drugie.

**Czas.** Około 160 h, nauka samodzielna. Tutor AI jest zalecany, ale kurs da się przejść bez niego.

**Język.** Wykłady, laby i README po polsku. Identyfikatory i komentarze w kodzie po angielsku. Terminy techniczne po angielsku, polski odpowiednik raz przy pierwszym użyciu, do tego `docs/glossary.md`. Pliki dla agenta (`AGENTS.md`, notatki tutora, skille) po angielsku.

**Granica poufności.** Kurs uczy mechanizmów potrzebnych w codebase do prognozowania popytu. Nie zawiera nazw klientów, schematów, nazw kolumn, reguł biznesowych ani struktury kodu z żadnego prywatnego repozytorium.

**Poza zakresem.** Hamilton, TFT i `pytorch-forecasting`, lab o lifcie promocyjnym, elastyczność cenowa, agregacja do tygodni, laby z NLP i obrazów, prawdziwe konto w chmurze.

**Licencja.** Kod MIT, treści CC BY 4.0, autor Jakub Eichner.

## 2. Dane

| Zbiór | Licencja | Rola |
|---|---|---|
| FreshRetailNet-50K | CC BY 4.0 | Zbiór przewodni od modułu 07 |
| Monash Car Parts | CC BY 4.0 | Moduły 01-04, parsowanie w czystym Pythonie |
| UCI Online Retail II | CC BY 4.0 | Moduł 06 (czyszczenie) i dane dla `shelfwise` w module 17 |

### FreshRetailNet-50K, fakty zmierzone

- `train.parquet`: 4,5 mln wierszy, 50 000 serii sklep × produkt, 90 dni (2024-03-28 do 2024-06-25), panel kompletny, bez duplikatów i braków.
- `eval.parquet`: te same serie, 7 kolejnych dni. To zamknięty zbiór testowy, używany raz, w capstone.
- Sprzedaż znormalizowana globalnym współczynnikiem (średnia 1,0). Brak cen, jednostek i nazw.
- Dwie kolumny zagnieżdżone po 24 wartości: sprzedaż godzinowa i status braku towaru (1 = brak).
- 44% wierszy ma co najmniej godzinę bez towaru między 6:00 a 22:00, 4% cały ten przedział.
- Anomalie: `discount == 0` w 16 tys. wierszy, rabat powyżej 1 w 34 wierszach, sprzedaż w godzinach bez towaru, data jako tekst.
- Zero w kolumnie `discount` ma dwa wzorce. Dwa produkty mają je prawie codziennie, sprzedają się 10-15 razy lepiej niż przeciętny i nie mają flagi akcji. Sześć innych ma je w pojedyncze dni, zawsze z flagą akcji, ze sprzedażą około trzy razy wyższą. Czy to darmowy produkt, czy znacznik, z danych nie wynika. Kurs zdejmuje zero ze skali: NaN plus flaga `discount_is_zero`.
- `holiday_flag` to dni wolne w Chinach: weekendy plus sześć świąt w dni robocze, zgodnych z `holidays.China(2024)`. Niedziela 2024-04-07 była robocza i ma flagę 0.
- Naiwne wczytanie całego pliku zajmuje 7,5 GB RAM. Same kolumny skalarne po zmianie typów zajmują 221 MB.
- LightGBM bez tuningu bije prognozę naiwną sezonową o 25% MAE na jednym mieście i 19% na całości.

### Profile danych

| Profil | Filtr | Serie | Kiedy |
|---|---|---|---|
| `small` | `city_id == 14` | 493 | Maszyny poniżej 6 GB RAM |
| `standard` | `city_id == 3` | 2 648 | Domyślny we wszystkich labach |
| `full` | brak | 50 000 | Moduł 14, 18 i capstone |

Profil wybiera `course doctor` na podstawie pamięci i zapisuje w `.course/config.toml`. Sprawdzenia zadań działają na małych danych z `src/coursekit/fixtures/`, więc nie zależą od profilu.

### Zadanie prognostyczne

- Cel: `sale_amount` na dzień, dla pary sklep × produkt.
- Horyzont: 7 dni.
- Walidacja: rolling origin, foldy po 7 dni. Przy 90 dniach i lagach do 28 mieszczą się 3-4 foldy.
- Metryki: WAPE, MAE i bias, liczone na wszystkich wierszach oraz osobno na wierszach bez braków towaru.
- Zmienne znane z góry: rabat, flaga akcji, święta i pogoda na horyzoncie traktujemy jako znane, tak jak autorzy zbioru. Moduł 08 nazywa to wprost ograniczeniem, bo prawdziwa prognoza pogody to nie to samo co pogoda zaobserwowana.
- Popyt ocenzurowany: kursant buduje korektę z profilu godzinowego (moduł 09), sprawdza ją w symulacji i w backteście, po czym zostaje przy prostszym rozwiązaniu, które wygrywa w pomiarze: trening tylko na dniach bez braku towaru. Bez modeli neuronowych do odtwarzania popytu. Liczby w sekcji 12.

## 3. Architektura repozytorium

### Dwie gałęzie, jedno źródło

`solutions` jest gałęzią autorską i jedynym źródłem prawdy. `main` to widok kursanta, generowany skryptem `tools/release.py`. Nikt nie edytuje `main` ręcznie.

Kod, który kursant ma napisać, jest w plikach referencyjnych otoczony blokiem:

```python
def load_sales(path: Path) -> pd.DataFrame:
    """Docstring zostaje widoczny dla kursanta."""
    # >>> SOLUTION 07.1
    kod referencyjny
    # --- STUB
    #| opcjonalny tekst zastępczy
    # <<< SOLUTION
```

Release zamienia każdy blok na jego zaślepkę (domyślnie `raise NotImplementedError("Zadanie 07.1")`). Z tego samego mechanizmu korzysta `course catchup N`, który dla plików pakietu wpisuje kod referencyjny zadań z modułów wcześniejszych niż N. Dzięki temu "migawka po każdym module" nie wymaga osobnych tagów ani kopii plików.

Notebooki powstają z plików `*.lab.py` w formacie percent (jupytext). Na `main` trafia wygenerowany `.ipynb` z zaślepkami, na `solutions` dodatkowo wersja rozwiązana `*.solution.ipynb`.

### Układ katalogów

```
lectures/              wykłady HTML, otwierane lokalnie lub z GitHub Pages
  assets/              wspólny CSS i JS: quizy, Pyodide, postęp
  NN-slug/index.html
labs/NN-slug/          notebook labu, README z listą zadań
src/freshcast/         pakiet budowany przez kursanta
src/coursekit/         narzędzia kursu: doctor, data, check, catchup
  checks/mNN.py        sprawdzenia zadań
  fixtures/            małe dane do sprawdzeń
tests/                 testy pisane przez kursanta (od modułu 04)
shelfwise/             gotowy codebase do modułu 17
tutor/notes/NN.md      notatki tutora per moduł
.claude/skills/        komendy tutora
docs/                  standard inżynierski, słowniczek
tools/                 narzędzia autora (tylko solutions)
```

### Polecenie `course`

| Polecenie | Działanie |
|---|---|
| `uv run course doctor` | Diagnoza środowiska, wybór profilu danych |
| `uv run course data` | Pobranie zbiorów z weryfikacją sum kontrolnych |
| `uv run course check 07` | Sprawdzenie zadań modułu albo jednego zadania (`07.2`) |
| `uv run course profile small` | Zmiana profilu danych |
| `uv run course catchup 08` | Kod referencyjny dla modułów przed podanym |

Wyniki sprawdzeń zapisują się w `.course/progress.json`. Tutor czyta ten plik, żeby wiedzieć, co kursant zaliczył i po ilu próbach.

### Weryfikacja kursu

`tools/verify.py` uruchamia na `solutions`: ruff, mypy, wszystkie sprawdzenia na kodzie referencyjnym (muszą przejść), te same sprawdzenia na wygenerowanym `main` (każde zadanie musi zaczynać jako niezrobione, a ticket w `shelfwise` jako niezaliczony) oraz wykonanie rozwiązanych notebooków od początku do końca. `tools/verify.py --module NN` sprawdza jeden moduł w izolacji, bez dotykania wspólnego katalogu `_main/`.

## 4. Format dydaktyczny

**Wykład.** Jedna strona HTML na moduł, 45-60 minut. Sekcje teorii przeplatane quizami i widżetami. W wykładach pythonowych (01-05) kod uruchamialny w przeglądarce przez Pyodide, wzorzec "przewidź wynik, potem uruchom". W wykładach ML widżety na danych wyliczonych wcześniej. Quizy tylko uczą: wyjaśnienie przy każdej odpowiedzi, dowolna liczba prób, wynik w `localStorage`. Na koniec każdej części quiz przekrojowy.

**Lab.** Notebook prowadzi przez zadania. Części 1 (01-03): funkcje pisane w notebooku. Część 2 (04-13): kursant pisze funkcje w `src/freshcast/`, notebook je importuje i używa na prawdziwych danych. Część 3 (14-19): zadania to tickety, notebook służy tylko do eksploracji i raportu.

**Sprawdzenia.** Każde zadanie ma sprawdzenie uruchamiane z notebooka (`check("07.2")`) i z terminala. Komunikat mówi, co jest nie tak, bez podawania rozwiązania.

**Podpowiedzi.** Trzy poziomy w zwijanych blokach pod zadaniem: kierunek, podejście, prawie-kod. Tutor ma dodatkowo notatki z typowymi błędami i pytaniami naprowadzającymi.

**Punkty kontrolne.** Cztery PR we własnym forku, sprawdzane komendą `/review` według `docs/standard.md`: po modułach 04, 11, 16 i 19.

**Zaplanowane pułapki.** Moduł 07: naiwne wczytanie pliku. Moduł 08: leakage z kolumn o brakach towaru z tego samego dnia. Moduł 09: target encoding dopasowany przed podziałem. Kursant ma w nie wpaść, zobaczyć objaw i znaleźć przyczynę.

## 5. Pakiet `freshcast`

Plan plików i właścicieli. Moduł-właściciel to ten, w którym kursant pisze dany plik.

```
data/schema.py          dany      nazwy kolumn, kontrakty
data/load.py            07.1      wczytanie z wyborem kolumn i filtrem
data/validate.py        07.2      niezmienniki panelu, zero rabatu poza skalą
data/dims.py            07.3      wymiary sklepu i produktu, merge z validate
data/hourly.py          07.4      podsumowania z tablic godzinowych
data/panel.py           07.5      lagi, okna, profil tygodnia
data/prepare.py         07.6      złożenie i zapis zbioru przetworzonego
warmup/*.py             06        czyszczenie UCI Online Retail II
metrics.py              05.1-05.3 mae, rmse, wape, bias, z maską
numeric.py              05.4      udziały w wierszach tablicy
models/local.py         04.1      LocalForecaster i trzy prognozy lokalne
models/panel.py         08.2, 08.4 PanelForecaster, PerSeriesForecaster, LinearForecaster
models/gradient.py      08.3      regresja liniowa przez gradient descent
models/tree.py          10.1      wybór podziału drzewa
models/gbm.py           10.2, 10.3 LightGBMForecaster, ważność cech, wkłady SHAP
models/mlp.py           13        MLP w PyTorch
forecast.py             10.4      prognoza bezpośrednia i rekurencyjna
split.py                08.1, 11.1 podział po dacie, foldy rolling origin
features/calendar.py    09.1      dzień tygodnia, kodowanie cykliczne, święta
features/lags.py        09.2      lagi i okna świadome horyzontu
features/demand.py      09.3      profil godzinowy, pokrycie, korekta popytu
features/encoding.py    09.4      TargetEncoder dopasowany tylko na train
features/build.py       09.5      rejestr cech i kolejność z grafu zależności
features/catalog.py     dany      cechy modelu kursu
evaluation/scores.py    08.5      metryki na wszystkich wierszach i bez braków
evaluation/backtest.py  11.2      backtest na foldach
tuning.py               11.3      Optuna z logowaniem do MLflow
tracking.py             dany      lokalny MLflow
classify/*.py           12        etykieta, metryki klasyfikacji, klasyfikator
segments.py             13        profil serii, k-means, PCA
config.py               14.1      pydantic-settings, YAML, zmienne środowiskowe
artifacts.py            14.2      zapis modelu z metadanymi i sygnaturą
pipeline.py             14.3, 14.4 przygotowanie miastami, train, forecast
cli.py                  14.5      freshcast train, freshcast forecast
storage/*.py            15        S3, retry, SQL w DuckDB
```

Pliki pisane przez kursanta w całości (Dockerfile, workflow CI, pre-commit) nie mają zaślepek. Ich wersje referencyjne leżą w `reference/16/` i `course catchup` kopiuje je na miejsce.

Testy kursanta (`tests/`) sprawdza mechanizm mutacji: `coursekit/mutation.py` podmienia w locie fragmenty kodu kursanta na celowo zepsute i wymaga, żeby testy to wykryły. Mutanty opakowują kod kursanta z zewnątrz, więc nie zawierają rozwiązania.

**Dwa interfejsy modeli.** `LocalForecaster` (moduł 03) prognozuje jedną serię: `fit(history)`, `predict(horizon)`. `PanelForecaster` (moduł 08) ma interfejs w stylu sklearn: `fit(X, y)`, `predict(X)`, gdzie `X` zawiera klucze serii i datę. Adapter `PerSeriesForecaster` stosuje prognozę lokalną do każdej serii panelu, więc prognozy naiwne z modułu 03 zostają baseline'em do końca kursu.

**Zbiór przetworzony (kontrakt modułu 07).** `data/processed/daily.parquet`: klucze `store_id`, `product_id`, `city_id`, data `dt` jako `datetime64`, `sale_amount`, `discount` (NaN w miejscu zera), `discount_is_zero`, `activity_flag`, `holiday_flag`, cztery kolumny pogody, `oos_hours`, `oos_hours_total`, `sales_in_stock`, `sales_while_oos`. Obok `store_dim.parquet` i `product_dim.parquet`. Posortowany po kluczu i dacie.

## 6. Sylabus

Godziny to czas kursanta: wykład, quiz i lab.

### Część 1: inżynieria w Pythonie (36 h)

**00 Setup (4 h).** Strona z ręcznym minimum dla Windows + WSL2 (Ubuntu 24.04), potem `/setup` z tutorem i `course doctor`. Ścieżka bez agenta korzysta z tego samego skryptu. Lab: fork, klon w systemie plików Linuksa, profil danych, pobranie danych, pierwszy PR z `notes/journal.md`.

**01 Struktury danych i przepływ (8 h).** Obiekty i nazwy, mutowalność, `==` a `is`, kopie płytkie i głębokie, list/tuple/dict/set, comprehensions, protokół iteracji, generatory, pliki i `with`, wyjątki. Lab na Monash Car Parts: parser formatu `.tsf`, generator serii, statystyki popytu bez pandas, obsługa braków, zapis podsumowania do JSON.

**02 Funkcje i style kodu (8 h).** Funkcje czyste, `*args`/`**kwargs`, domknięcia, dekoratory z `functools.wraps`, funkcje wyższego rzędu, moduły i importy, type hints, mypy, ruff, docstringi. Ten sam problem w stylu imperatywnym, funkcyjnym i obiektowym. Lab: refaktor labu 01 na typowany moduł, dekoratory `@timed` i walidujący, rejestr statystyk.

**03 Klasy (8 h).** Klasy, `dataclass`, właściwości, `classmethod`, dziedziczenie, ABC, `Protocol`, `StrEnum`, `match`, kiedy nie pisać klas. Lab: `Series` jako dataclass, klasyfikacja typu popytu (ADI i CV²), `LocalForecaster` z prognozą naiwną, sezonową i średnią kroczącą, ewaluacja na ostatnich 6 miesiącach.

**04 Testy i pakiet (8 h).** pytest, fixtures, parametryzacja, `pytest.raises`, mocki i `monkeypatch`, układ `src/`, `pyproject.toml`, uv, lock, pre-commit. Lekcja o Poetry w osobnej piaskownicy: ten sam mały pakiet zbudowany Poetry i porównanie z uv. Lab: przeniesienie prognoz z 03 do `freshcast/models/local.py`, testy w `tests/`. Sprawdzenie jakości testów: testy kursanta muszą przejść na kodzie referencyjnym i wyłapać celowo zepsute wersje. **Punkt kontrolny 1.**

### Część 2: dane i ML (71 h)

**05 NumPy (6 h).** Tablice, dtype, broadcasting, maski, `np.where`, NaN, pułapki floatów. Lab: `freshcast/metrics.py` z testami, normalizacja profilu godzinowego na tablicy (n, 24).

**06 pandas I, czyszczenie (7 h).** Typy, braki, duplikaty, `.loc`, łańcuchy metod, walidacja fail fast. Lab na UCI Online Retail II: anulowane faktury, ujemne ilości, brakujące identyfikatory, podejrzane ceny. Pierwszy krok to zapis xlsx do parquet, bo czytanie xlsx trwa długo. Wynik: czysta sprzedaż dzienna, używana ponownie przez `shelfwise` w module 17.

**07 pandas II, panel i relacje (9 h).** Moduł pilotażowy, szczegóły w sekcji 7.

**08 Podstawy ML (9 h).** Szczegóły w sekcji 7.

**09 Feature engineering (9 h).** Szczegóły w sekcji 7.

**10 Drzewa i boosting (8 h).** Drzewo decyzyjne, bagging i random forest, boosting, LightGBM (early stopping, cele L2, Poisson i Tweedie, kategorie, ograniczenia monotoniczne), kNN dla kontrastu, ważność cech i SHAP. Lab: szukanie najlepszego podziału w NumPy, `LightGBMForecaster`, ograniczenie monotoniczne na rabacie, prognoza bezpośrednia (lagi od 7 w górę) kontra rekurencyjna (krótkie lagi z podawaniem własnych prognoz).

**11 Walidacja i tuning (8 h).** Rolling origin, dlaczego K-fold przecieka w czasie, dobór metryki, Optuna (TPE, pruning), MLflow lokalnie. W wykładzie także wariant prostszy: artefakty w katalogu i sygnatura modelu. Lab: `rolling_origin_folds`, `backtest`, studium Optuny z logowaniem każdej próby do MLflow. **Punkt kontrolny 2.**

**12 Klasyfikacja (7 h).** Szczegóły w sekcji 7.

**13 Uczenie bez nadzoru, sieci, mapa ML (8 h).** k-means ze skalowaniem, dobór k, PCA na profilach godzinowych, segment jako cecha wracająca do modelu z 10 z uczciwym testem, czy pomaga. MLP w PyTorch na CPU: tensory, autograd, `nn.Module`, pętla treningowa. Wykład-mapa: SVM, naive Bayes, CNN, RNN, transformery i LLM, systemy rekomendacyjne, reinforcement learning.

### Część 3: produkcja (53 h)

**14 Od notebooka do pipeline'u (8 h).** Konfiguracja w pydantic-settings i YAML, CLI, logowanie, obsługa błędów, zapis modelu z metadanymi i sygnaturą, ziarna losowości. Lab: `freshcast train` i `freshcast forecast`, przebieg na profilu `full`.

**15 Dane w chmurze i SQL (10 h).** boto3, MinIO w Dockerze, klasa-serwis nad S3, testy z moto, retry z backoff, cache pobrań. SQL w DuckDB nad plikami parquet w MinIO: złączenia, grupowanie, funkcje okna. W wykładzie Feature Store, Athena i Lambda jako pojęcia. Tu kursant instaluje Dockera.

**16 Docker i CI (6 h).** Dockerfile z uv, GitHub Actions (ruff, mypy, pytest), pre-commit, standard inżynierski, review cudzego diffa. **Punkt kontrolny 3.**

**17 Cudzy kod (8 h).** Czytanie nieznanego kodu, debugowanie, tickety w `shelfwise`. Szczegóły w sekcji 8.

**18 Neuronowa prognoza na GPU (11 h).** Pętla treningowa w czystym PyTorch dla MLP na cechach lagowych (`Dataset`, `DataLoader`, `device`, mixed precision). Mały GRU: okno 28 dni, 7 dni prognozy, jeden model dla wszystkich serii. To samo w Lightning: callbacki, early stopping, checkpointy, trening na 50 tys. serii. Jedyny moduł wymagający karty NVIDIA.

**19 Capstone (10 h).** Pakiet z komendami `train` i `forecast`, testami, zielonym CI, obrazem Dockera, przebiegami w MLflow i raportem. Kryteria:
- model bije prognozę naiwną sezonową w backteście i na tygodniu testowym, WAPE na wierszach bez braków towaru, z raportowanym biasem,
- raport porównuje LightGBM z modelem neuronowym w tym samym backteście i uzasadnia wybór,
- raport tłumaczy schemat walidacji i to, że tydzień testowy jest cieplejszy niż prawie cały zbiór treningowy,
- `/review` bez uwag blokujących.

**Punkt kontrolny 4.**

### Co przechodzi między modułami

- Prognozy lokalne z 03 i 04 są baseline'em w 08, 10, 11 i 19 przez adapter `PerSeriesForecaster`.
- Metryki z 05 służą każdej ewaluacji od 08.
- Czyste dane UCI z 06 zasilają `shelfwise` w 17.
- Zbiór przetworzony z 07 zasila 08-13.
- Prymitywy `add_lag` i okna z 07 są budulcem cech w 09.
- Tabela cech z 09 zasila 10-13 i 18.
- Segmenty z 13 wracają jako cecha do modelu z 10.
- Backtest z 11 ocenia modele z 10, 13 i 18 tym samym kodem.
- Pakiet rośnie do końca i w 16 trafia do obrazu Dockera.

## 7. Moduły doprecyzowane

### 07 pandas II, panel i relacje

Wykład: tabela faktów i wymiary, `merge` i kardynalność (widżet: co robi zduplikowany klucz), `groupby` z `agg` a `transform`, sortowanie panelu, `shift` i `rolling` w grupach z granicą "tylko przeszłość", kolumny zagnieżdżone i pamięć, fail fast.

| Zadanie | Plik | Co powstaje |
|---|---|---|
| 07.1 | `data/load.py` | `load_sales`: wybór kolumn, filtr miast przy czytaniu, mniejsze typy, data jako `datetime64`, sortowanie |
| 07.2 | `data/validate.py` | `check_panel` (duplikaty, luki, braki, wartości ujemne) i `clean_discount` (zero na NaN z flagą `discount_is_zero`, reszta bez zmian) |
| 07.3 | `data/dims.py` | `build_store_dim`, `build_product_dim`, `attach_dim` z `validate="many_to_one"` |
| 07.4 | `data/hourly.py` | `summarise_hours`: godziny bez towaru, sprzedaż w godzinach z towarem, z tablic (n, 24) |
| 07.5 | `data/panel.py` | `add_lag`, `add_rolling_mean` tylko z przeszłości, `dow_profile` |
| 07.6 | `data/prepare.py` | `prepare_daily`, zapis i odczyt zbioru przetworzonego z kontrolą kontraktu |

Część bez oceny: EDA w notebooku (profil tygodnia, trend, rabat a sprzedaż) z pytaniami do przemyślenia.

### 08 Podstawy ML

Wykład: czym jest model i funkcja straty, gradient descent (widżet z krokiem uczenia), regresja liniowa, podział train/validation/test po czasie, leakage, baseline, regularyzacja, bias-variance, ograniczenie "zmienne znane z góry".

Lab:
1. `split_by_date`.
2. `PerSeriesForecaster` i baseline naiwny sezonowy na panelu, ocena metrykami z 05.
3. Regresja liniowa od zera w NumPy z gradient descent, porównanie z sklearn.
4. Pułapka: Ridge na "wszystkich dostępnych kolumnach", w tym godzinach bez towaru z tego samego dnia. Wynik jest podejrzanie dobry. Kursant szuka przyczyny i zapisuje regułę.
5. Dobór `alpha` na zbiorze walidacyjnym.
6. Tabela: baseline kontra model liniowy, wszystkie wiersze kontra wiersze bez braków.

### 09 Feature engineering

Wykład: cechy dla szeregów, lagi i okna świadome horyzontu, kalendarz i kodowanie cykliczne, święta, kodowanie kategorii (porządkowe, one-hot, target encoding i jego leakage, natywne kategorie LightGBM), `Pipeline` i `ColumnTransformer`, cechy jako czyste funkcje z jawnymi zależnościami, popyt ocenzurowany.

Lab:
1. `features/calendar.py`: dzień tygodnia, sin/cos, święta i dni do najbliższego święta z pakietu `holidays`, porównanie z `holiday_flag`.
2. `features/lags.py`: lagi i okna z warunkiem `lag >= horizon`.
3. `features/demand.py`: profil godzinowy, pokrycie i korekta popytu. Kursant sprawdza korektę dwa razy. W symulacji (sztuczne braki nałożone na dni bez braków) usuwa ona obciążenie. Jako cel treningu na prawdziwych danych zawyża prognozy. Wygrywa trening tylko na dniach bez braku towaru. Lekcja: symulacja losowała braki, a prawdziwe braki trafiają w dni wysokiego popytu.
4. `features/encoding.py`: target encoding. Pułapka na kodowaniu seria × dzień tygodnia: dopasowane także na tygodniu walidacyjnym poprawia walidację i psuje tydzień testowy.
5. `features/build.py`: rejestr funkcji-cech z deklaracją wejść, kolejność z grafu zależności.

Wynik: `data/processed/features.parquet`.

### 12 Klasyfikacja

Cel: czy jutro towaru nie będzie przez całe okno 6:00-22:00. Klasa pozytywna to około 4%.

Wykład: regresja logistyczna i log-loss, macierz pomyłek, precision, recall, F1, krzywe ROC i PR (widżet z progiem), kalibracja, niezbalansowane klasy, próg z kosztów biznesowych.

Lab: etykieta przez `shift(-1)` w grupie (uwaga na kierunek), podział po czasie, regresja logistyczna, klasyfikator LightGBM, PR-AUC, wybór progu z kosztu fałszywego alarmu i przegapionego braku, krzywa kalibracji.

## 8. `shelfwise`

Osobny mały pakiet w `shelfwise/`, 2-3 tys. linii, z własnymi testami. Tygodniowa prognoza popytu i sugestie zatowarowania dla sklepu internetowego, na danych UCI Online Retail II, które kursant czyścił w module 06. Zna więc dane, ale nie zna kodu.

Zasiane problemy (spoilery, nie trafiają na `main`):

| # | Problem | Objaw w tickecie |
|---|---|---|
| 1 | Zwroty odejmowane dwa razy | "Sumy w raporcie nie zgadzają się z fakturami" |
| 2 | `fillna(0)` chowa brakujące ceny | Zaniżony przychód w jednej kategorii |
| 3 | Skaler i target encoding dopasowane przed podziałem | "Walidacja jest dużo lepsza niż produkcja" |
| 4 | `merge` bez `validate` przy zduplikowanym kluczu wymiaru | Liczba wierszy rośnie po złączeniu |
| 5 | Granica tygodnia: ISO kontra poniedziałek | Pierwszy tydzień roku ma podwójną sprzedaż |
| 6 | Test zależny od bieżącej daty | Test pada raz na jakiś czas |
| 7 | Pętla `iterrows` | Raport liczy się 40 sekund |

Tickety: T1 bug z sumami (1), T2 nowa metryka per kategoria, T3 nowa cecha z konfiguracją, testami i dokumentacją, T4 śledztwo w sprawie zbyt dobrej walidacji (3), T5 niestabilny test (6), T6 wydajność (7). Problemy 2, 4 i 5 kursant może znaleźć po drodze. Zaliczenie modułu to cztery tickety, każdy jako osobny PR.

## 9. Tutor

- `AGENTS.md` trzyma zasady, `CLAUDE.md` go importuje.
- Skille wywoływane przez kursanta: `/setup`, `/hint`, `/check`, `/explain`, `/quiz`, `/review`. Narzędzia bez skilli dostają w `AGENTS.md` wskaźnik do tych samych plików.
- Tutor nie pisze rozwiązań zadań i nie edytuje plików kursanta w `src/freshcast/`, `labs/`, `tests/` ani `shelfwise/`. Reguły `deny` w `.claude/settings.json` robią z tego twardą blokadę.
- Po trzech podpowiedziach pokazuje przykład analogiczny na innych danych i przypomina o gałęzi `solutions`.
- Przy zepsutym środowisku pomaga wprost.
- Prowadzi `.course/progress.md`: gdzie kursant jest, co sprawiało trudność, co powtórzyć.
- Ma procedurę na brak pamięci: wybór kolumn, mniejsze typy, profil `small`, limit w `.wslconfig`.

## 10. Kolejność prac

1. Ten dokument.
2. Pilot: lekcja 00, moduł 07, fragment wykładu 01.
3. Review autora kursu i poprawka szablonu.
4. Kod referencyjny całego pakietu, sekwencyjnie.
5. Wykłady, notebooki i notatki tutora równolegle, z agentem sprawdzającym.

## 11. Ryzyka

- Kroki po stronie Windows (instalacja WSL, `.wslconfig`, sterownik NVIDIA, Docker Desktop) nie są testowane na maszynie autora. Wymagają jednego przejścia na prawdziwym Windowsie przed publikacją.
- Pyodide ładuje się z CDN, więc wykłady 01-05 wymagają sieci dla kodu uruchamialnego. Reszta strony działa offline.
- Nikt jeszcze nie porównał modelu neuronowego z LightGBM na tych danych.
- Tydzień testowy jest cieplejszy niż zbiór treningowy. Wynik na nim może być gorszy niż w backteście i kurs mówi o tym otwarcie.

## 12. Zmierzone wyniki referencyjne

Wszystkie liczby pochodzą z kodu referencyjnego na gałęzi `solutions`. WAPE "bez braków" liczy tylko dni bez godziny braku towaru.

### Profil `standard` (miasto 3), backtest 3-4 foldy po 7 dni

| Model | WAPE bez braków | Bias bez braków |
|---|---|---|
| Prognoza naiwna sezonowa | 0,559 | -6% |
| Średnia z 4 tych samych dni tygodnia | 0,473 | -5% |
| LightGBM, trening na wszystkich wierszach | 0,407 | -8% |
| LightGBM, trening tylko na dniach bez braków | 0,371-0,377 | +1 do +4% |
| LightGBM, cel skorygowany profilem godzinowym | 0,433 | +16% |
| LightGBM rekurencyjny (lagi 1-3) | 0,368 | +2% |
| LightGBM po 25 próbach Optuny | 0,374 | |

Profil `small` (miasto 14) daje te same relacje na niższym poziomie: 0,386, 0,339 i 0,278.

Wnioski wbudowane w kurs:
- Największy pojedynczy zysk po przejściu z baseline'u na model daje decyzja o danych treningowych (dni bez braków), nie tuning.
- Tuning daje 0,003. Kurs mówi to wprost.
- Prognoza rekurencyjna jest na tych danych praktycznie równa bezpośredniej.
- Identyfikatory sklepu i produktu jako kategorie dają 0,03-0,04.

### Pułapki, zmierzone

- Moduł 08: Ridge z kolumną `sales_in_stock` z tego samego dnia ma WAPE 0,034 zamiast 0,490. Z samymi godzinami braku 0,466.
- Moduł 09: target encoding seria × dzień tygodnia dopasowany także na tygodniu walidacyjnym: walidacja 0,503 (bez kodowania 0,512), test 0,537 (bez kodowania 0,501). Na `small`: 0,355 wobec 0,375 i 0,389 wobec 0,364.
- Moduł 09: symulowane braki na dniach bez braków: korekta z profilu zmienia bias z -27% na 0%.

### Profil `full`, tydzień testowy (`eval.parquet`)

| Model | WAPE bez braków | Bias bez braków | WAPE wszystkie |
|---|---|---|---|
| Prognoza naiwna sezonowa | 0,389 | -1% | 0,418 |
| LightGBM, ustawienia domyślne | 0,285 | -6% | 0,333 |

Backtest na `full`: 0,302-0,312. Szczyt pamięci 4,9 GB. Czas około 15 minut przy obciążonej maszynie, do zmierzenia ponownie na wolnej.

### Środowisko

- Na czystym Ubuntu 24.04 `import lightgbm` nie działa bez pakietu `libgomp1`. Lekcja 00, `course doctor` i Dockerfile to uwzględniają.
- Kroki Dockerfile (instalacja z `uv sync --locked --no-editable`, uruchomienie `freshcast` z samego środowiska) przećwiczone w czystym Ubuntu bez Dockera. Samego `docker build` nie uruchomiono: demon Dockera jest na maszynie autora wyłączony.
- Workflow GitHub Actions ma poprawną składnię, ale nie był uruchomiony na GitHubie.

