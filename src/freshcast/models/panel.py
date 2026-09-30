"""Panel forecasters: one model object for all series at once."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Hashable, Sequence
from typing import Self

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

from freshcast.data.schema import DATE, SERIES_KEY
from freshcast.models.local import LocalForecaster

FloatArray = NDArray[np.float64]


class PanelForecaster(ABC):
    """Common interface of every model from module 08 on.

    ``X`` is a slice of the panel: the series key, the date and whatever
    feature columns the model uses. ``y`` is the target of the same rows.
    ``predict`` returns one number per row of ``X``, in the order of ``X``.
    """

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> Self:
        """Learn from the rows of ``X`` and their targets ``y``."""

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> FloatArray:
        """Return a forecast for every row of ``X``."""


class PerSeriesForecaster(PanelForecaster):
    """Runs a local forecaster separately on every series of the panel.

    This adapter is how the baselines of module 04 take part in every later
    comparison through the same interface as the real models.

    Args:
        make_local: Called once per series to get a fresh local forecaster,
            for example ``lambda: SeasonalNaiveForecaster(season=7)``.
    """

    def __init__(self, make_local: Callable[[], LocalForecaster]) -> None:
        self._make_local = make_local
        self._histories: dict[tuple[Hashable, ...], list[float]] = {}

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Self:
        """Store the history of every series, oldest day first.

        Args:
            X: Rows with the series key and the date.
            y: Target of the same rows.
        """
        # >>> SOLUTION 08.2
        frame = X[[*SERIES_KEY, DATE]].assign(target=y.to_numpy())
        frame = frame.sort_values([*SERIES_KEY, DATE])
        self._histories = {
            key: group["target"].tolist()
            for key, group in frame.groupby(SERIES_KEY, sort=False)
        }
        return self
        # <<< SOLUTION

    def predict(self, X: pd.DataFrame) -> FloatArray:
        """Forecast the days in ``X``, series by series.

        For each series the rows of ``X`` are taken as the next consecutive
        days after its history: the earliest row gets the first step of the
        local forecast, the next one the second step, and so on.

        Raises:
            ValueError: ``X`` holds a series that ``fit`` has not seen.
        """
        # >>> SOLUTION 08.2
        rows = X[[*SERIES_KEY, DATE]].reset_index(drop=True)
        forecast = np.empty(len(rows), dtype=np.float64)
        for key, group in rows.groupby(SERIES_KEY, sort=False):
            if key not in self._histories:
                raise ValueError(f"Series {key} was not in the training data.")
            positions = group.sort_values(DATE).index.to_numpy()
            local = self._make_local().fit(self._histories[key])
            forecast[positions] = local.predict(len(positions))
        return forecast
        # <<< SOLUTION


class LinearForecaster(PanelForecaster):
    """Ridge regression on standardised features, never below zero.

    Args:
        features: Names of the feature columns. They must be numeric and
            free of NaN: a linear model has no way to use a missing value,
            and guessing one here would hide the problem.
        alpha: Strength of the L2 penalty. 0 is plain least squares.
    """

    def __init__(self, features: Sequence[str], alpha: float = 1.0) -> None:
        self.features = list(features)
        self.alpha = alpha
        self._pipeline: Pipeline | None = None

    def _checked(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return the feature columns, or raise if any of them holds NaN."""
        # >>> SOLUTION 08.4
        selected = X[self.features]
        missing = int(selected.isna().any(axis=1).sum())
        if missing:
            raise ValueError(f"{missing} rows have a NaN in the feature columns.")
        return selected
        # <<< SOLUTION

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Self:
        """Fit the scaler and the regression on the training rows only."""
        # >>> SOLUTION 08.4
        self._pipeline = make_pipeline(StandardScaler(), Ridge(alpha=self.alpha))
        self._pipeline.fit(self._checked(X), y)
        return self
        # <<< SOLUTION

    def predict(self, X: pd.DataFrame) -> FloatArray:
        """Forecast, with negative outputs raised to zero.

        Raises:
            RuntimeError: ``fit`` has not been called.
        """
        # >>> SOLUTION 08.4
        if self._pipeline is None:
            raise RuntimeError("Call fit before predict.")
        raw = self._pipeline.predict(self._checked(X))
        clipped: FloatArray = np.clip(raw, 0.0, None)
        return clipped
        # <<< SOLUTION

    def coefficients(self) -> pd.Series:
        """Return the fitted weights by feature name, on the standardised scale.

        Raises:
            RuntimeError: ``fit`` has not been called.
        """
        if self._pipeline is None:
            raise RuntimeError("Call fit before reading coefficients.")
        ridge = self._pipeline.named_steps["ridge"]
        return pd.Series(ridge.coef_, index=self.features, name="coefficient")
