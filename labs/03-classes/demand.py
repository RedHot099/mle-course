"""Car Parts demand series as objects: demand types and local forecasts."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Protocol, Self

MISSING = "?"
# Syntetos-Boylan cut-offs: above ADI_CUTOFF demand is intermittent, above
# CV2_CUTOFF the sizes of the orders vary a lot.
ADI_CUTOFF = 1.32
CV2_CUTOFF = 0.49


def read_tsf(path: str | Path) -> Iterator[tuple[str, str, list[float | None]]]:
    """Yield (name, start, values) for every series of a .tsf file.

    The same job as ``read_series`` from labs 01 and 02, kept short here.
    """
    in_data = False
    with Path(path).open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower() == "@data":
                in_data = True
            elif in_data:
                name, start, values = line.split(":", 2)
                parsed = [None if v == MISSING else float(v) for v in values.split(",")]
                yield name, start.split(" ")[0], parsed


# >>> SOLUTION 03.1
@dataclass(frozen=True)
class DemandSeries:
    """One monthly demand series, oldest value first; None marks a missing month.

    Raises:
        ValueError: ``values`` is empty or holds a negative number.
    """

    name: str
    start: date
    values: tuple[float | None, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError(f"Series {self.name!r} has no values.")
        negative = [value for value in self.values if value is not None and value < 0]
        if negative:
            raise ValueError(
                f"Series {self.name!r} has negative demand: {negative[:3]}"
            )

    @classmethod
    def from_record(cls, record: tuple[str, str, Sequence[float | None]]) -> Self:
        """Build a series from a (name, "YYYY-MM-DD", values) record of read_tsf."""
        name, start, values = record
        return cls(name, date.fromisoformat(start), tuple(values))

    @property
    def known(self) -> list[float]:
        """The values without the missing months."""
        return [value for value in self.values if value is not None]

    @property
    def is_complete(self) -> bool:
        """True when no month is missing."""
        return all(value is not None for value in self.values)

    @property
    def adi(self) -> float | None:
        """Average demand interval: known months per month with demand."""
        known = self.known
        demand = sum(value > 0 for value in known)
        return len(known) / demand if demand else None

    @property
    def cv2(self) -> float | None:
        """Squared coefficient of variation of the non-zero demand sizes."""
        sizes = [value for value in self.known if value > 0]
        if len(sizes) < 2:
            return None
        mean = sum(sizes) / len(sizes)
        variance = sum((size - mean) ** 2 for size in sizes) / len(sizes)
        return variance / mean**2


# --- STUB
#| @dataclass(frozen=True)
#| class DemandSeries:
#|     """One monthly demand series, oldest value first; None marks a missing month.
#|
#|     03.1: fields name, start, values; from_record, known, is_complete, adi
#|     and cv2. The notebook describes each of them.
#|     """
# <<< SOLUTION


# >>> SOLUTION 03.2
class DemandType(StrEnum):
    """Demand pattern of a series, after Syntetos and Boylan."""

    SMOOTH = "smooth"
    ERRATIC = "erratic"
    INTERMITTENT = "intermittent"
    LUMPY = "lumpy"
    INSUFFICIENT = "insufficient"


def classify(adi: float | None, cv2: float | None) -> DemandType:
    """Name the demand pattern; INSUFFICIENT when either statistic is unknown."""
    match adi, cv2:
        case (None, _) | (_, None):
            return DemandType.INSUFFICIENT
        case (adi, cv2) if adi <= ADI_CUTOFF and cv2 <= CV2_CUTOFF:
            return DemandType.SMOOTH
        case (adi, _) if adi <= ADI_CUTOFF:
            return DemandType.ERRATIC
        case (_, cv2) if cv2 <= CV2_CUTOFF:
            return DemandType.INTERMITTENT
        case _:
            return DemandType.LUMPY


# --- STUB
#| # 03.2: DemandType and classify.
# <<< SOLUTION


# >>> SOLUTION 03.3
class LocalForecaster(ABC):
    """Base class of forecasters that learn from one series.

    Usage is always ``SomeForecaster().fit(history).predict(horizon)``.
    Subclasses implement ``_forecast``; the checks live here, once.
    """

    def __init__(self) -> None:
        self._history: list[float] | None = None

    def fit(self, history: Sequence[float]) -> Self:
        """Remember a copy of the history and return the forecaster itself.

        Raises:
            ValueError: ``history`` is empty.
        """
        if len(history) == 0:
            raise ValueError("Cannot fit on an empty history.")
        self._history = [float(value) for value in history]
        return self

    def predict(self, horizon: int) -> list[float]:
        """Forecast the next ``horizon`` values, nearest first.

        Raises:
            RuntimeError: ``fit`` has not been called.
            ValueError: ``horizon`` is below 1.
        """
        if self._history is None:
            raise RuntimeError("Call fit before predict.")
        if horizon < 1:
            raise ValueError(f"horizon must be at least 1, got {horizon}.")
        return self._forecast(self._history, horizon)

    @abstractmethod
    def _forecast(self, history: list[float], horizon: int) -> list[float]:
        """Return ``horizon`` forecasts from a non-empty ``history``."""


class NaiveForecaster(LocalForecaster):
    """Repeats the last observed value."""

    def _forecast(self, history: list[float], horizon: int) -> list[float]:
        return [history[-1]] * horizon


# --- STUB
#| # 03.3: LocalForecaster and NaiveForecaster.
# <<< SOLUTION


# >>> SOLUTION 03.4
class SeasonalNaiveForecaster(LocalForecaster):
    """Repeats the last full season, step by step.

    Raises:
        ValueError: ``season`` is below 1, or (in ``fit``) the history is
            shorter than one season.
    """

    def __init__(self, season: int = 7) -> None:
        super().__init__()
        if season < 1:
            raise ValueError(f"season must be at least 1, got {season}.")
        self.season = season

    def fit(self, history: Sequence[float]) -> Self:
        """Like LocalForecaster.fit; the history must cover one season."""
        if len(history) < self.season:
            raise ValueError(
                f"History of {len(history)} values is shorter than one season "
                f"of {self.season}."
            )
        return super().fit(history)

    def _forecast(self, history: list[float], horizon: int) -> list[float]:
        last_season = history[-self.season :]
        return [last_season[step % self.season] for step in range(horizon)]


class MovingAverageForecaster(LocalForecaster):
    """Repeats the mean of the last ``window`` values (all, if fewer).

    Raises:
        ValueError: ``window`` is below 1.
    """

    def __init__(self, window: int = 7) -> None:
        super().__init__()
        if window < 1:
            raise ValueError(f"window must be at least 1, got {window}.")
        self.window = window

    def _forecast(self, history: list[float], horizon: int) -> list[float]:
        recent = history[-self.window :]
        return [sum(recent) / len(recent)] * horizon


# --- STUB
#| # 03.4: SeasonalNaiveForecaster and MovingAverageForecaster.
# <<< SOLUTION


# >>> SOLUTION 03.5
class Forecaster(Protocol):
    """Anything that can be fitted on a history and asked for a forecast."""

    def fit(self, history: Sequence[float]) -> Self:
        """Learn from ``history`` and return the forecaster."""
        ...

    def predict(self, horizon: int) -> list[float]:
        """Forecast the next ``horizon`` values."""
        ...


def mae(actual: Sequence[float], forecast: Sequence[float]) -> float:
    """Mean absolute error of two equally long sequences.

    Raises:
        ValueError: The lengths differ or both are empty.
    """
    if len(actual) != len(forecast) or not actual:
        raise ValueError(
            f"Need two equally long, non-empty sequences, got {len(actual)} "
            f"and {len(forecast)}."
        )
    return sum(abs(a - f) for a, f in zip(actual, forecast, strict=True)) / len(actual)


def evaluate(
    make_model: Callable[[], Forecaster],
    series: Iterable[DemandSeries],
    holdout: int = 6,
) -> float:
    """Mean MAE over the last ``holdout`` months of every complete series.

    Each series gets a fresh model from ``make_model``, fitted on all months
    before the holdout. Series with a missing month are skipped.

    Raises:
        ValueError: No series is complete and longer than ``holdout``.
    """
    errors = []
    for one in series:
        if not one.is_complete or len(one.values) <= holdout:
            continue
        history, actual = one.known[:-holdout], one.known[-holdout:]
        forecast = make_model().fit(history).predict(holdout)
        errors.append(mae(actual, forecast))
    if not errors:
        raise ValueError(f"No complete series longer than {holdout} months.")
    return sum(errors) / len(errors)


# --- STUB
#| # 03.5: Forecaster, mae and evaluate.
# <<< SOLUTION
