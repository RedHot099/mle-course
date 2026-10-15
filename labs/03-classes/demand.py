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
    """One monthly demand series of one car part, oldest month first.

    Fields, in this order:
        name: Name of the series in the .tsf file, for example ``"T1"``.
        start: Date of the first month of the series.
        values: Units sold in each month, oldest first. ``None`` marks a
            month without a record. A tuple, so a frozen series cannot change.

    Equal data give equal series, and a series can be put into a set.

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
        """Build a series from one record yielded by ``read_tsf``.

        Args:
            record: ``(name, start, values)``: the series name, the first
                month as text ``"YYYY-MM-DD"`` and the list of monthly values
                with ``None`` for a missing month.

        Returns:
            A series of the class this method was called on, with ``start``
            as a ``date`` and ``values`` as a tuple.

        Raises:
            ValueError: The values are empty or negative (see the class).
        """
        name, start, values = record
        return cls(name, date.fromisoformat(start), tuple(values))

    @property
    def known(self) -> list[float]:
        """The known values, in their order, with the missing months left out."""
        return [value for value in self.values if value is not None]

    @property
    def is_complete(self) -> bool:
        """True when no month is missing."""
        return all(value is not None for value in self.values)

    @property
    def adi(self) -> float | None:
        """Average demand interval: known months per month with demand.

        Months with demand are known months with a value above zero. None
        when no month has demand.
        """
        known = self.known
        demand = sum(value > 0 for value in known)
        return len(known) / demand if demand else None

    @property
    def cv2(self) -> float | None:
        """Squared coefficient of variation of the non-zero demand sizes.

        Population variance of the known values above zero, divided by the
        square of their mean. None when fewer than two months have demand.
        Unlike ``cv2`` in lab 02 there is no minimum of 12 known months.
        """
        sizes = [value for value in self.known if value > 0]
        if len(sizes) < 2:
            return None
        mean = sum(sizes) / len(sizes)
        variance = sum((size - mean) ** 2 for size in sizes) / len(sizes)
        return variance / mean**2


# --- STUB
#| @dataclass(frozen=True)
#| class DemandSeries:
#|     """One monthly demand series of one car part, oldest month first.
#|
#|     03.1, the contract (the notebook explains each step in Polish):
#|
#|     Fields, in this order:
#|         name (str): name of the series in the .tsf file, for example "T1".
#|         start (date): date of the first month of the series.
#|         values (tuple of float or None): units sold in each month, oldest
#|             first; None marks a month without a record.
#|
#|     __post_init__: ValueError when values is empty or holds a negative number.
#|     from_record(record) (classmethod): build a series from one
#|         (name, "YYYY-MM-DD", list of values) record yielded by read_tsf.
#|     known (property): list of the known values, missing months left out.
#|     is_complete (property): True when no month is missing.
#|     adi (property): known months / months with demand above zero;
#|         None when no month has demand.
#|     cv2 (property): population variance of the values above zero divided
#|         by the square of their mean; None when fewer than two months have
#|         demand.
#|     """
# <<< SOLUTION


# >>> SOLUTION 03.2
class DemandType(StrEnum):
    """Demand pattern of a series, after Syntetos and Boylan.

    A StrEnum: every member equals its lower-case name, for example
    ``DemandType.LUMPY == "lumpy"``. INSUFFICIENT marks a series whose ADI or
    CV2 cannot be computed.
    """

    SMOOTH = "smooth"
    ERRATIC = "erratic"
    INTERMITTENT = "intermittent"
    LUMPY = "lumpy"
    INSUFFICIENT = "insufficient"


def classify(adi: float | None, cv2: float | None) -> DemandType:
    """Name the demand pattern of a series from its two statistics.

    Args:
        adi: Average demand interval of the series (``DemandSeries.adi``),
            or None when unknown.
        cv2: Squared coefficient of variation of its demand sizes
            (``DemandSeries.cv2``), or None when unknown.

    Returns:
        INSUFFICIENT when either statistic is None. Otherwise SMOOTH, ERRATIC,
        INTERMITTENT or LUMPY by the table of Syntetos and Boylan with the
        cut-offs ``ADI_CUTOFF`` and ``CV2_CUTOFF``. A value equal to a cut-off
        belongs to the lower class.
    """
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
#| #
#| # DemandType: a StrEnum with members SMOOTH, ERRATIC, INTERMITTENT, LUMPY
#| # and INSUFFICIENT; each value is the member name in lower case.
#| #
#| # classify(adi, cv2) -> DemandType: adi and cv2 are floats or None, as
#| # DemandSeries.adi and DemandSeries.cv2 return them. INSUFFICIENT when
#| # either is None; otherwise the class from the table in the notebook, with
#| # ADI_CUTOFF and CV2_CUTOFF above. A value equal to a cut-off belongs to the
#| # lower class. Write it with a match statement.
# <<< SOLUTION


# >>> SOLUTION 03.3
class LocalForecaster(ABC):
    """Base class of forecasters that learn from one series.

    Usage is always ``SomeForecaster().fit(history).predict(horizon)``.
    Subclasses implement ``_forecast``; the checks of the arguments and the
    fit-before-predict rule live here, once.
    """

    def __init__(self) -> None:
        self._history: list[float] | None = None

    def fit(self, history: Sequence[float]) -> Self:
        """Remember a copy of the history and return the forecaster itself.

        Args:
            history: Past monthly values of one series, oldest first, with
                no missing months. Stored as a new list of floats, so later
                changes to the caller's list do not reach the forecaster.

        Returns:
            The forecaster itself, so calls can be chained.

        Raises:
            ValueError: ``history`` is empty.
        """
        if len(history) == 0:
            raise ValueError("Cannot fit on an empty history.")
        self._history = [float(value) for value in history]
        return self

    def predict(self, horizon: int) -> list[float]:
        """Forecast the next ``horizon`` values, nearest first.

        Args:
            horizon: Number of steps (months here) to forecast, at least 1.

        Returns:
            A list of ``horizon`` floats computed by ``_forecast``.

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
#| #
#| # LocalForecaster: abstract base class (ABC) of every forecaster.
#| #   __init__(): sets self._history to None (not fitted yet).
#| #   fit(history) -> Self: history is a sequence of floats, oldest first.
#| #     Stores a copy as a list of floats and returns self.
#| #     ValueError when history is empty.
#| #   predict(horizon) -> list[float]: RuntimeError before fit, ValueError
#| #     when horizon is below 1; otherwise returns
#| #     self._forecast(self._history, horizon).
#| #   _forecast(history, horizon) -> list[float]: abstract method; returns
#| #     horizon forecasts, nearest first.
#| #
#| # NaiveForecaster(LocalForecaster): _forecast repeats the last value of
#| # the history horizon times.
# <<< SOLUTION


# >>> SOLUTION 03.4
class SeasonalNaiveForecaster(LocalForecaster):
    """Repeats the last full season, step by step.

    Step ``k`` of the forecast (counting from 0) is value ``k % season`` of the
    last ``season`` values of the history, so horizons longer than a season
    wrap around.

    Args:
        season: Length of the season in steps, at least 1. The default 7 is
            for daily data; on monthly data pass 12.

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

    Args:
        window: Number of most recent values to average, at least 1. The
            default 7 is for daily data.

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
#| # 03.4: SeasonalNaiveForecaster and MovingAverageForecaster, both
#| # subclasses of LocalForecaster.
#| #
#| # SeasonalNaiveForecaster(season=7): ValueError when season is below 1.
#| #   fit(history): ValueError when history is shorter than one season,
#| #   otherwise as LocalForecaster.fit. The forecast repeats the last
#| #   `season` values in order and wraps around for longer horizons.
#| #
#| # MovingAverageForecaster(window=7): ValueError when window is below 1.
#| #   The forecast repeats the mean of the last `window` values, or of the
#| #   whole history when it is shorter than the window.
# <<< SOLUTION


# >>> SOLUTION 03.5
class Forecaster(Protocol):
    """Anything that can be fitted on a history and asked for a forecast.

    Every LocalForecaster fits, and so does any other class with these two
    methods, inherited or not.
    """

    def fit(self, history: Sequence[float]) -> Self:
        """Learn from ``history`` and return the forecaster."""
        ...

    def predict(self, horizon: int) -> list[float]:
        """Forecast the next ``horizon`` values."""
        ...


def mae(actual: Sequence[float], forecast: Sequence[float]) -> float:
    """Mean absolute error of two equally long sequences.

    Args:
        actual: What was really sold, one value per month.
        forecast: What the model predicted for the same months, same order.

    Returns:
        The mean of ``abs(actual[i] - forecast[i])`` over all months, in
        units sold.

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
    before the holdout. Series with a missing month are skipped, and so are
    series not longer than ``holdout``.

    Args:
        make_model: A function without arguments that returns a new, unfitted
            model. A class works too: ``evaluate(NaiveForecaster, series)``.
        series: The demand series to evaluate on.
        holdout: Number of last months held back as the test period, a
            positive integer. Not validated: the caller passes a valid one.

    Returns:
        The mean over the evaluated series of the MAE of each series.

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
#| #
#| # Forecaster: a Protocol with fit(history) -> Self and
#| #   predict(horizon) -> list[float].
#| #
#| # mae(actual, forecast) -> float: mean of the absolute differences of two
#| #   sequences of floats. ValueError when the lengths differ or both are
#| #   empty.
#| #
#| # evaluate(make_model, series, holdout=6) -> float: make_model is a
#| #   function without arguments that returns a new model; holdout is a
#| #   positive integer (not validated); series is an
#| #   iterable of DemandSeries. For every complete series longer than
#| #   holdout: a new model from make_model(), fitted on all months but the
#| #   last holdout, forecasts holdout months; mae against those months.
#| #   Returns the mean of these MAE values. ValueError when no series
#| #   qualifies.
# <<< SOLUTION
