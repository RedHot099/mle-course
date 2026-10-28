# lab-a02 · Rekordy i funkcja, z której można skorzystać ponownie

Wymagane lekcje: A2.4, A2.5. Najpierw wykonaj lab-a00.

## Uruchom swoją kopię

Pobierz paczkę ZIP z odnośnika przy wykładzie. Rozpakuj folder `lab-a02` do `~/mle-practice/labs/`. Nie otwieraj notebooka bezpośrednio wewnątrz archiwum. Gotowy plik ma leżeć w `~/mle-practice/labs/lab-a02/lab.ipynb`.

Jeśli folder już zawiera Twoją pracę, nie zastępuj go nową paczką. Zrób kopię albo rozpakuj nowe wydanie obok i porównaj pliki. Na Windowsie z WSL skopiuj rozpakowany folder do katalogu domowego Ubuntu. Możesz otworzyć go w Eksploratorze Windows przez ścieżkę `\\wsl.localhost\Ubuntu\home\NAZWA_UŻYTKOWNIKA\mle-practice\labs`; podstaw nazwę swojej dystrybucji i konta. Jeśli nie znasz ścieżki, wpisz `pwd` w terminalu Ubuntu.

W terminalu Linux lub Ubuntu WSL uruchom:

```bash
cd ~/mle-practice/labs/lab-a02
UV_HTTP_TIMEOUT=300 UV_HTTP_RETRIES=10 UV_CONCURRENT_DOWNLOADS=2 uv run --no-project --python 3.12 --with jupyterlab --with ipykernel jupyter lab
```

Polecenie przygotowuje środowisko z Pythonem 3.12 i JupyterLab. Nie instaluje bibliotek modeli z całego kursu. Pierwsze uruchomienie wymaga internetu; kolejne korzystają z pamięci podręcznej uv. Otwórz wypisany lokalny adres w przeglądarce, a w JupyterLab plik `lab.ipynb`. Wybierz kernel Python 3. Polecenia terminala pozostają w terminalu; komórki notebooka zawierają Python.

Ważne wyniki zapisuj przez Ctrl+S. Po uzupełnieniu zadań wybierz w menu Kernel restart i wykonanie wszystkich komórek. Sam zapis pliku nie zachowuje pamięci kernela. Na zakończenie zatrzymaj kernel, a potem serwer Jupyter przez Ctrl+C w terminalu. Nie udostępniaj tokenu z adresu serwera.

## Co oddajesz

Własny notebook z uzupełnionym kodem i wynikami sprawdzeń. Końcowe pytania możesz przemyśleć bez zapisywania odpowiedzi. W sekcji A nie potrzebujesz modułu .py, pytest, gita, pandas ani dodatkowych pobrań danych.

Ten lab jest gotowy do pilotażu, ale nie został jeszcze sprawdzony przez grupę początkujących uczestników. Czerwone sprawdzenie pustego startera oznacza zadanie do uzupełnienia, nie zepsutą instalację.

Treść: Jakub Eichner, CC BY 4.0. Kod: MIT. Pełne licencje są w paczce. Dane, jeśli są dołączone, opisuje DATA.md.
