# shelfwise: rozwiązania (tylko dla autora)

Plik nie trafia do widoku kursanta. Liczby zmierzone na pełnych danych UCI Online Retail II, na wersji dostarczanej kursantowi ("wadliwa") i na referencyjnej ("poprawiona").

| # | Blok | Plik | Przyczyna | Objaw (wadliwa → poprawiona) | Ticket |
|---|---|---|---|---|---|
| 1 | 17.1 | `cleaning.py`, `net_units` | Zwroty odejmowane dwa razy: `quantity` jest już ujemne na fakturach korygujących, a kod odejmuje jeszcze `qty_returned`. Odpisy magazynowe (ujemne ilości bez "C") liczą się jako ujemna sprzedaż | 85123A: 93 025 → 97 111 sztuk netto. Suma wszystkich produktów przy samym tym defekcie: 9 533 533 → 10 268 766 | T1 |
| 2 | 17.7 | `weekly.py`, `current_prices`; `report.py` | Cena tylko z ostatnich 13 tygodni, z cenami 0 w medianie. Produkt bez sprzedaży w tym oknie dostaje NaN, a raport robi `fillna(0)` | 602 wiersze raportu z ceną 0. Przychód przy samym tym defekcie 242 160 → 249 232 | brak |
| 3 | 17.4 | `model.py`, `train_and_validate` | Enkoder produktu ("średnia z ostatnich 13 tygodni") i skaler dopasowane na całości przed podziałem. Ostatnie 13 tygodni zawiera 8 tygodni walidacji | WAPE walidacji 0,648 → 0,700 (przy samym tym defekcie); w wersji dostarczonej raportowane 0,682 | T4 |
| 4 | 17.8 | `io.py`, `build_catalogue`; `weekly.py`, `add_catalogue` | Katalog z `drop_duplicates` na parze kod + opis. Kody mają do 9 opisów. `merge` w raporcie mnoży wiersze | Raport: 3 999 wierszy dla 2 766 produktów; 85123A 5 razy | brak |
| 5 | 17.9 | `calendar.py`, `week_start` | `(weekday + 1) % 7`: tygodnie niedziela-sobota zamiast poniedziałek-niedziela | Tydzień z 7 marca 2011 opisany jako 6 marca; sprzedaż niedzielna w następnym tygodniu | brak |
| 6 | 17.5 | `tests/test_report.py` | Test porównuje `%V` (z zerem wiodącym) z `isocalendar().week` (bez zera) i bierze bieżącą datę | Pada w tygodniach ISO 1-9 (styczeń-luty), przechodzi w pozostałych | T5 |
| 7 | 17.6 | `report.py`, `build_report` | `iterrows` i filtrowanie całej tabeli tygodni dla każdego produktu | 5 070 produktów: 7,4 s → 0,6 s. Syntetyczne 3 000 × 60 tygodni: poniżej 2 s po poprawce | T6 |
| - | 17.2 | `report.py`, `cli.py` | Nowa funkcja `wape_by_category` i plik `categories.csv` | | T2 |
| - | 17.3 | `config.py`, `features.py`, `model.py`, `cli.py`, README | Nowe ustawienie `model.use_season` i cecha `is_season`. README po poprawce leży w `reference/17/shelfwise/README.md` | | T3 |

## Jak kursant zwykle dochodzi do przyczyny

- **T1:** policzyć sprzedaż jednego produktu ręcznie z faktur i porównać krok po kroku: `clean` → `net_qty`. Zwykle widzi ujemne `quantity` na fakturach "C" dopiero po wypisaniu kilku linii.
- **T4:** podmienić sprzedaż w tygodniach walidacyjnych (np. ×100) i zobaczyć, że prognoza pierwszego tygodnia walidacji się zmienia. To jest dokładnie test z rozwiązania.
- **T5:** uruchomić test pod `freezegun` z datą w styczniu. Poprawka: `now` jako argument i test z ustaloną datą.
- **T6:** profilowanie (`cProfile` albo `time.perf_counter` wokół kroków) wskazuje pętlę. Poprawka: jedno złączenie z ostatnim tygodniem wszystkich produktów.
- **2, 4, 5** wychodzą przy okazji: raport ma więcej wierszy niż produktów (4), ceny 0 w raporcie (2), tydzień zaczyna się w niedzielę w `report.csv` (5).

## Wersje i sprawdzanie

- `uv run --group authoring python tools/verify.py --module 17`: sprawdzenia przechodzą na poprawionej i zaczynają jako niezaliczone na wadliwej.
- Własne testy shelfwise: poprawiona 23 zaliczone, wadliwa 11 zaliczonych (defekty nie mają testów; test daty pada tylko w tygodniach 1-9).
- Fixture: `src/coursekit/fixtures/shelfwise_lines.parquet`, 9 produktów, 21 227 linii, 226 KB, budowany przez `tools/make_fixtures_m17.py`.
