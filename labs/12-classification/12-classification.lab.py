# %% [markdown]
# # Lab 12: czy jutro zabraknie towaru na cały dzień
#
# Nowe pytanie, nowy rodzaj modelu. Na koniec dnia `t` chcesz wiedzieć, czy produkt w sklepie będzie niedostępny przez **całe** okno 6:00-22:00 dnia `t + 1`. Jeśli model podniesie alarm, ktoś sprawdzi zapas i zamówi dostawę. Alarm, który okaże się fałszywy, kosztuje trochę czasu. Przegapiony brak kosztuje pusty regał przez cały dzień.
#
# To klasyfikacja binarna z rzadką klasą pozytywną. Zbudujesz etykietę tak, żeby nie przeciekła, policzysz precision i recall od zera, dobierzesz próg z kosztów, a nie z przyzwyczajenia, i sprawdzisz, czy prawdopodobieństwa modelu znaczą to, co mówią.
#
# **Czas:** około 6 godzin.
#
# | Zadanie | Co piszesz w `src/freshcast/classify/` | Czas |
# |---|---|---|
# | 12.1 | `stockout.py`: etykieta na jutro | 40 min |
# | 12.2 | `stockout.py`: cechy znane na koniec dnia | 50 min |
# | 12.3 | `metrics.py`: macierz pomyłek, precision, recall, F1 | 30 min |
# | 12.4 | `metrics.py`: krzywa precision-recall, average precision | 50 min |
# | 12.7 | `models.py`: `StockoutClassifier` | 50 min |
# | 12.5 | `metrics.py`: próg z kosztów | 30 min |
# | 12.6 | `metrics.py`: tabela kalibracji | 30 min |
# | 12.8 | Pułapki i pytania | 60 min |

# %%
# %load_ext autoreload
# %autoreload 2

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from coursekit import paths
from coursekit.nb import check
from coursekit.plotting import use_course_style
from freshcast.classify import metrics, stockout
from freshcast.classify.models import StockoutClassifier
from freshcast.data.prepare import load_processed
from freshcast.data.schema import DATE, OOS_HOURS, SERIES_KEY

use_course_style()
daily = load_processed(paths.PROCESSED_DIR)
LABEL = stockout.LABEL
COST_FALSE_ALARM, COST_MISSED = 1.0, 5.0

# %% [markdown]
# ## 12.1 Etykieta na jutro
#
# Etykieta wiersza dnia `t` to wynik dnia `t + 1` **tej samej serii**: 1, gdy jutro towaru nie było przez wszystkie 16 godzin okna, 0 w przeciwnym razie. Ostatni dzień każdej serii nie ma jutra: jego etykieta jest nieznana, a nie zerowa.
#
# W `stockout.py` napisz `next_day_value`, `add_stockout_label` i `drop_unlabelled` według docstringów.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `shift(-1)` przesuwa wartości w górę: w wierszu dnia `t` ląduje wartość dnia `t + 1`. Tylko wewnątrz serii, czyli po `groupby(SERIES_KEY)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `NaN == 16` daje `False`, więc porównanie zamieni "nie wiem" w "nie". Najpierw zapamiętaj, gdzie jutra nie ma, potem porównaj, potem przywróć brak (etykieta jako `float` z `NaN`).
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# tomorrow = next_day_value(df, OOS_HOURS)
# label = (tomorrow == FULL_STOCKOUT_HOURS).astype(float).where(tomorrow.notna())
# return df.assign(**{LABEL: label})
# ```
#
# </details>

# %%
check("12.1")

# %%
labelled = stockout.drop_unlabelled(stockout.add_stockout_label(daily))
print(f"Wiersze z etykietą: {len(labelled):,} z {len(daily):,} (bez ostatniego dnia każdej z {daily.groupby(SERIES_KEY).ngroups:,} serii)")
print(f"Udział pełnych braków jutro: {labelled[LABEL].mean():.2%}")

# %% [markdown]
# ## 12.2 Cechy znane na koniec dnia
#
# Prognoza powstaje wieczorem dnia `t`. Dzisiejszy dzień już się skończył, więc wszystko o nim jest znane: sprzedaż, godziny braku. Z jutra znasz tylko to, co ustalono z góry: kalendarz i zaplanowany rabat. W `stockout.py` napisz `rolling_mean_through_today` i `add_stockout_features`.
#
# Zwróć uwagę na różnicę wobec modułu 09: tam prognoza na tydzień naprzód wymagała lagów od 7 dni. Tu horyzont to jeden dzień i prognoza powstaje po jego końcu, więc okno może kończyć się dziś.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `groupby(SERIES_KEY)[kolumna].rolling(okno, min_periods=okno).mean()`. Pełne okno albo brak: udział pełnych braków z 3 dni to nie to samo co z 28.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Rabat na jutro to `next_day_value(df, DISCOUNT)`, a jutrzejszy dzień wolny to `next_day_value(df, HOLIDAY_FLAG)`. Każdą cechę dodawaj przez `assign`, bez zmiany ramki wejściowej.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# rolled = df.groupby(SERIES_KEY, sort=False)[column].rolling(window, min_periods=window).mean()
# return pd.Series(rolled.to_numpy(), index=df.index)   # the frame is sorted, so the order matches
# ```
#
# </details>

# %%
check("12.2")

# %% [markdown]
# Podział po czasie. Test to ostatnie 7 dni z etykietą, walidacja 7 dni przed nim. Etykieta dnia tuż przed granicą to wynik pierwszego dnia po niej, więc `split_by_label_date` usuwa ten dzień z części wcześniejszej.

# %%
table = stockout.drop_unlabelled(stockout.add_stockout_features(stockout.add_stockout_label(daily)))
FEATURES = stockout.FEATURES
rest, test = stockout.split_by_label_date(table, table[DATE].max() - pd.Timedelta(days=6))
train, valid = stockout.split_by_label_date(rest, rest[DATE].max() - pd.Timedelta(days=6))
for name, part in [("trening", train), ("walidacja", valid), ("test", test)]:
    print(f"{name:>10}: {len(part):>7,} wierszy, {part[DATE].min().date()}..{part[DATE].max().date()}, pozytywnych {part[LABEL].mean():.1%}")

# %% [markdown]
# ## 12.3 Precision, recall, F1
#
# W `metrics.py` napisz `confusion_counts`, `precision`, `recall` i `f1` w NumPy. Precision: jaka część alarmów była trafiona. Recall: jaka część braków została złapana. Gdy mianownik jest zerowy, wynik to 0.0.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Cztery liczby: alarm i brak (tp), alarm bez braku (fp), brak bez alarmu (fn), cisza i spokój (tn). Każda to suma jednej maski.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Najpierw sprawdź, że etykiety to same 0 i 1, bez `NaN`: nieznana etykieta nie może po cichu stać się klasą. F1 to średnia harmoniczna: `2 p r / (p + r)`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# truth, predicted = binary_array("y_true", y_true), binary_array("y_pred", y_pred)
# tp = int(((truth == 1) & (predicted == 1)).sum())
# ...
# ```
#
# </details>

# %%
check("12.3")

# %% [markdown]
# Dwa punkty odniesienia na walidacji: model, który nigdy nie podnosi alarmu, i baseline "jutro tak jak dziś".

# %%
y_valid = valid[LABEL].to_numpy()
never = np.zeros_like(y_valid)
same_as_today = valid["oos_full_today"].to_numpy()
for name, predicted in [("nigdy", never), ("tak jak dziś", same_as_today)]:
    accuracy = (predicted == y_valid).mean()
    print(
        f"{name:>13}: accuracy {accuracy:.3f}, precision {metrics.precision(y_valid, predicted):.3f}, "
        f"recall {metrics.recall(y_valid, predicted):.3f}, F1 {metrics.f1(y_valid, predicted):.3f}"
    )

# %% [markdown]
# ## 12.4 Krzywa precision-recall
#
# Model zwraca wynik, nie decyzję. Każdy próg daje inną parę precision i recall. W `metrics.py` napisz `counts_by_threshold`, `precision_recall_curve` i `average_precision`, bez pętli po progach.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Posortuj wiersze malejąco po wyniku. Alarmy przy progu to początek tej listy, więc liczby trafionych i fałszywych alarmów to sumy kumulatywne etykiet i ich odwrotności.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Wiersze z równym wynikiem wchodzą razem: bierz sumy kumulatywne tylko na ostatniej pozycji każdej grupy równych wyników. Average precision to suma `(recall_k - recall_{k-1}) * precision_k` po progach.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# order = np.argsort(-scores, kind="stable")
# sorted_scores, sorted_labels = scores[order], labels[order]
# last_of_group = np.r_[sorted_scores[1:] != sorted_scores[:-1], True]
# tp = np.cumsum(sorted_labels)[last_of_group]
# fp = np.cumsum(1 - sorted_labels)[last_of_group]
# ```
#
# </details>

# %%
check("12.4")

# %% [markdown]
# Twoje funkcje obok scikit-learn, na wyniku baseline'u i na prawdziwym rozkładzie:

# %%
from sklearn.metrics import average_precision_score

rng = np.random.default_rng(0)
noisy_scores = same_as_today + rng.normal(0, 0.3, size=len(y_valid))
print(f"AP baseline: własne {metrics.average_precision(y_valid, same_as_today):.6f}, scikit-learn {average_precision_score(y_valid, same_as_today):.6f}")
print(f"AP zaszumiony: własne {metrics.average_precision(y_valid, noisy_scores):.6f}, scikit-learn {average_precision_score(y_valid, noisy_scores):.6f}")

# %% [markdown]
# ## 12.7 Dwa modele, jeden interfejs
#
# `StockoutClassifier` w `models.py` opakowuje regresję logistyczną albo klasyfikator LightGBM. Regresja logistyczna nie przyjmuje braków, więc wrapper zastępuje je medianą z treningu i dodaje kolumnę-wskaźnik "tu był brak". LightGBM bierze braki takie, jakie są.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Wszystko, co się dopasowuje (mediana, skala), musi siedzieć w jednym obiekcie scikit-learn dopasowanym w `fit`. `SimpleImputer(strategy="median", add_indicator=True)`, `StandardScaler`, `LogisticRegression` w `make_pipeline`.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `predict_proba` scikit-learn zwraca dwie kolumny. Twoja metoda zwraca jedną: prawdopodobieństwo klasy 1.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# if self.kind is ModelKind.LOGISTIC:
#     return make_pipeline(
#         SimpleImputer(strategy="median", add_indicator=True),
#         StandardScaler(),
#         LogisticRegression(max_iter=MAX_LOGISTIC_ITERATIONS, class_weight=self.class_weight, **self.params),
#     )
# ```
#
# </details>

# %%
check("12.7")

# %%
# >>> SOLUTION 12.7
models = {
    "logistyczna": StockoutClassifier(FEATURES, "logistic").fit(train, train[LABEL]),
    "LightGBM": StockoutClassifier(FEATURES, "lightgbm").fit(train, train[LABEL]),
}
scores_valid = {"tak jak dziś": same_as_today, **{name: model.predict_proba(valid) for name, model in models.items()}}
# --- STUB
#| models = ...
#| scores_valid = ...
# <<< SOLUTION
fig, ax = plt.subplots(figsize=(6, 4.5))
for name, scores in scores_valid.items():
    precision, recall, _ = metrics.precision_recall_curve(y_valid, scores)
    ax.step(recall, precision, where="post", label=f"{name} (AP {metrics.average_precision(y_valid, scores):.3f})")
ax.axhline(y_valid.mean(), linestyle=":", label="losowy ranking")
ax.set(xlabel="recall", ylabel="precision", title="Walidacja: krzywe precision-recall")
ax.legend()
plt.show()

# %% [markdown]
# ## 12.5 Próg z kosztów
#
# Fałszywy alarm kosztuje 1 (ktoś sprawdza magazyn), przegapiony pełny brak kosztuje 5 (dzień pustej półki). W `metrics.py` napisz `best_threshold`: próg o najniższym łącznym koszcie, łącznie z opcją "nigdy nie alarmuj".
#
# Próg wybierasz na walidacji, raportujesz na teście.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# `counts_by_threshold` daje trafione i fałszywe alarmy przy każdym progu. Przegapione to wszystkie pozytywne minus trafione.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# Koszt przy progu to `fp * koszt_alarmu + (pozytywne - tp) * koszt_przegapienia`. Dołóż kandydata "bez alarmu" (próg `inf`, koszt `pozytywne * koszt_przegapienia`). Przy remisie wygrywa wyższy próg.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# thresholds, tp, fp = counts_by_threshold(y_true, scores)
# positives = int(binary_array("y_true", y_true).sum())
# costs = fp * cost_false_alarm + (positives - tp) * cost_missed
# ```
#
# </details>

# %%
check("12.5")

# %%
y_test = test[LABEL].to_numpy()
# >>> SOLUTION 12.5
scores_test = {"tak jak dziś": test["oos_full_today"].to_numpy(), **{name: model.predict_proba(test) for name, model in models.items()}}
rows = {}
for name in scores_valid:
    choice = metrics.best_threshold(y_valid, scores_valid[name], COST_FALSE_ALARM, COST_MISSED)
    alarms = (scores_test[name] >= choice.threshold).astype(int)
    counts = metrics.confusion_counts(y_test, alarms)
    rows[name] = {
        "AP test": metrics.average_precision(y_test, scores_test[name]),
        "próg": choice.threshold,
        "precision": metrics.precision(y_test, alarms),
        "recall": metrics.recall(y_test, alarms),
        "koszt na teście": counts.fp * COST_FALSE_ALARM + counts.fn * COST_MISSED,
    }
rows["nigdy"] = {"koszt na teście": y_test.sum() * COST_MISSED}
decision_table = pd.DataFrame(rows).T
# --- STUB
#| decision_table = ...
# <<< SOLUTION
decision_table.round(3)

# %% [markdown]
# ## 12.6 Czy prawdopodobieństwo znaczy to, co mówi
#
# Model jest **skalibrowany**, gdy wśród wierszy z prawdopodobieństwem 0.3 około 30% to naprawdę pozytywne. W `metrics.py` napisz `calibration_table`: przedziały prawdopodobieństwa, w każdym średnie przewidywanie i obserwowana częstość.
#
# <details>
# <summary>Podpowiedź 1: kierunek</summary>
#
# Numer przedziału to `floor(p * bins)`, z wyjątkiem `p = 1.0`, które należy do ostatniego przedziału.
#
# </details>
#
# <details>
# <summary>Podpowiedź 2: podejście</summary>
#
# `np.minimum((p * bins).astype(int), bins - 1)`, potem `groupby` po numerze przedziału z `size`, średnią `p` i średnią etykiety. Puste przedziały pomijasz.
#
# </details>
#
# <details>
# <summary>Podpowiedź 3: prawie kod</summary>
#
# ```python
# index = np.minimum((probabilities * bins).astype(int), bins - 1)
# frame = pd.DataFrame({"bin": index, "p": probabilities, "y": labels})
# grouped = frame.groupby("bin").agg(rows=("y", "size"), mean_predicted=("p", "mean"), observed_rate=("y", "mean"))
# ```
#
# </details>

# %%
check("12.6")

# %% [markdown]
# Kalibracja obu modeli na teście i wariantu, który wiele tutoriali poleca przy rzadkiej klasie: wagi klas `class_weight="balanced"`.

# %%
# >>> SOLUTION 12.6
weighted = StockoutClassifier(FEATURES, "logistic", class_weight="balanced").fit(train, train[LABEL])
calibration = {
    "logistyczna": metrics.calibration_table(y_test, scores_test["logistyczna"], bins=5),
    "LightGBM": metrics.calibration_table(y_test, scores_test["LightGBM"], bins=5),
    "logistyczna z wagami": metrics.calibration_table(y_test, weighted.predict_proba(test), bins=5),
}
# --- STUB
#| weighted = ...
#| calibration = ...
# <<< SOLUTION
for name, frame in calibration.items():
    print(name)
    print(frame.round(3).to_string(index=False), "\n")
print(f"Średnie prawdopodobieństwo na teście: logistyczna {scores_test['logistyczna'].mean():.3f}, z wagami {weighted.predict_proba(test).mean():.3f}, częstość {y_test.mean():.3f}")
print(f"AP z wagami: {metrics.average_precision(y_test, weighted.predict_proba(test)):.3f}")

# %% [markdown]
# ## 12.8 Pułapki
#
# **Kolumny z jutra.** Tabela ma też sprzedaż jutra i łączne godziny braku jutra: wystarczy je przesunąć tak samo jak etykietę. Dodaj jedną z nich do cech LightGBM i zobacz average precision na teście. Spróbuj z czterema kolumnami wyniku: `sale_amount`, `sales_in_stock`, `oos_hours_total`, `sales_while_oos`.

# %%
# The whole panel, before the unlabelled last days are dropped: the rows of
# 2024-06-24 need the values of 2024-06-25.
full = stockout.add_stockout_features(stockout.add_stockout_label(daily))

# >>> SOLUTION 12.8
leak_results = {}
for column in ["sale_amount", "sales_in_stock", "oos_hours_total", "sales_while_oos"]:
    name = f"{column}_tomorrow"
    extended = full.assign(**{name: stockout.next_day_value(full, column)})
    leak_train, leak_test = extended.loc[train.index], extended.loc[test.index]
    model = StockoutClassifier([*FEATURES, name], "lightgbm").fit(leak_train, leak_train[LABEL])
    leak_results[name] = metrics.average_precision(y_test, model.predict_proba(leak_test))
# --- STUB
#| leak_results = ...
# <<< SOLUTION
print(f"Bez kolumn z jutra: AP {decision_table.loc['LightGBM', 'AP test']:.3f}")
for name, value in leak_results.items():
    print(f"z {name}: AP {value:.3f}")

# %% [markdown]
# Jedna z czterech kolumn niemal nic nie dodaje. Czy to znaczy, że jest bezpieczna? Sprawdź, co ta kolumna znaczy, zanim odpowiesz.
#
# *Twoja odpowiedź:*
#
# ## Pytania
#
# Bez sprawdzeń. Odpowiedz krótko, z liczbami z tego notebooka.
#
# 1. Model "nigdy" ma accuracy około 0.9. Dlaczego ta liczba nic nie mówi o przydatności modelu?
# 2. O ile LightGBM obniża koszt wobec baseline'u "tak jak dziś" i wobec "nigdy"? Czy to dużo?
# 3. Dla prawdopodobieństw skalibrowanych opłaca się alarmować, gdy `p · 5 > (1 − p) · 1`. Jaki to próg? Jak ma się do progów wybranych na walidacji? Co by się stało przy koszcie przegapienia 10?
# 4. Co wagi klas zrobiły z prawdopodobieństwami, a co z rankingiem? Kiedy to jest problem?
# 5. Dlaczego próg wybierasz na walidacji, a koszt raportujesz na teście?
# 6. Model używa zaplanowanego rabatu na jutro. Co musiałoby być prawdą, żeby ta cecha była dozwolona? Wytrenuj LightGBM bez niej i podaj oba wyniki.
# 7. Dlaczego LightGBM wygrywa z regresją logistyczną na tych samych cechach?
#
# *Twoje odpowiedzi:*
