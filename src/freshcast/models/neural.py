"""The GRU as a panel forecaster, so it runs through the same backtest."""

from typing import Self

import numpy as np
import pandas as pd
import torch
from numpy.typing import NDArray

from freshcast.data.schema import DATE, OOS_HOURS, SERIES_KEY, TARGET
from freshcast.models.panel import PanelForecaster
from freshcast.neural.device import pick_device, seed_everything
from freshcast.neural.gru import GRUForecastNet
from freshcast.neural.training import TrainingLog, fit_windows, predict_windows
from freshcast.neural.windows import PanelCube, WindowDataset, WindowSpec, panel_cube

FloatArray = NDArray[np.float64]

PAST_CHANNELS = [
    TARGET,
    "discount_filled",
    "zero_discount",
    "activity_flag",
    "holiday_flag",
    "dow_sin",
    "dow_cos",
    OOS_HOURS,
    "avg_temperature",
    "precpt",
]
FUTURE_CHANNELS = [
    "discount_filled",
    "zero_discount",
    "activity_flag",
    "holiday_flag",
    "dow_sin",
    "dow_cos",
    "avg_temperature",
    "precpt",
]
# Rough scaling so every channel is of order 1; the target is scaled per window.
_SCALES = {OOS_HOURS: 16.0, "avg_temperature": 30.0, "precpt": 10.0}


class GRUForecaster(PanelForecaster):
    """Train the window model on a history and forecast the days after it.

    ``fit`` takes every row of the history, stockout days included: they
    are needed as input, and the loss ignores them as targets. It trains
    twice. The first run holds out the last ``valid_days`` days and stops
    early to find the best number of epochs. The second run trains a fresh
    network on all windows for that many epochs, so the most recent week,
    the most informative one, is not lost to validation.

    ``predict`` takes the rows of the days right after the history, with
    the columns known in advance; their outcome columns are never read.

    Args:
        past: History days per window.
        horizon: Forecast days per window; ``predict`` must get exactly
            this many days per series.
        epochs, batch_size, learning_rate, patience: See ``fit_windows``.
        valid_days: Days at the end of the history held out for early stopping.
        seed: Seed for weights and batch order.
        prefer_gpu: Use CUDA when available.
    """

    def __init__(
        self,
        past: int = 28,
        horizon: int = 7,
        *,
        epochs: int = 15,
        batch_size: int = 1024,
        learning_rate: float = 2e-3,
        patience: int = 3,
        valid_days: int = 7,
        seed: int = 0,
        prefer_gpu: bool = True,
    ) -> None:
        self.spec = WindowSpec(past, horizon, PAST_CHANNELS, FUTURE_CHANNELS)
        self.epochs, self.batch_size = epochs, batch_size
        self.learning_rate, self.patience = learning_rate, patience
        self.valid_days, self.seed = valid_days, seed
        self.device = pick_device(prefer_gpu)
        self.log = TrainingLog()
        self._history: pd.DataFrame | None = None
        self._net: GRUForecastNet | None = None
        self._codes: tuple[torch.Tensor, torch.Tensor] | None = None

    @staticmethod
    def _scaled(panel: pd.DataFrame) -> pd.DataFrame:
        return panel.assign(
            **{name: panel[name] / div for name, div in _SCALES.items()}
        )

    def _cube(self, panel: pd.DataFrame) -> PanelCube:
        columns = [*SERIES_KEY, DATE, *dict.fromkeys(PAST_CHANNELS + FUTURE_CHANNELS)]
        ordered = panel[columns].sort_values([*SERIES_KEY, DATE]).reset_index(drop=True)
        return panel_cube(
            self._scaled(ordered), list(dict.fromkeys(PAST_CHANNELS + FUTURE_CHANNELS))
        )

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Self:
        """Train on every window that ends inside the history."""
        # >>> SOLUTION 18.6
        seed_everything(self.seed)
        history = X.assign(**{TARGET: y.to_numpy()})
        cube = self._cube(history)
        days = cube.data.shape[1]
        span = self.spec.past + self.spec.horizon
        last_valid_start = days - span
        first_valid_start = last_valid_start - self.valid_days + 1
        if first_valid_start < 1:
            raise ValueError(f"A history of {days} days is too short to train on.")

        series = range(cube.data.shape[0])

        def windows(starts: range) -> list[tuple[int, int]]:
            return [(s, t) for s in series for t in starts]

        train = WindowDataset(
            cube,
            self.spec,
            windows(range(0, first_valid_start - self.spec.horizon + 1)),
        )
        valid = WindowDataset(
            cube, self.spec, windows(range(first_valid_start, last_valid_start + 1))
        )

        everything = WindowDataset(
            cube, self.spec, windows(range(last_valid_start + 1))
        )

        stores = torch.tensor(
            pd.factorize(cube.keys["store_id"])[0], device=self.device
        )
        products = torch.tensor(
            pd.factorize(cube.keys["product_id"])[0], device=self.device
        )
        self._codes = (stores, products)

        def fresh_net() -> GRUForecastNet:
            seed_everything(self.seed)
            return GRUForecastNet(
                len(PAST_CHANNELS),
                len(FUTURE_CHANNELS),
                self.spec.horizon,
                int(stores.max()) + 1,
                int(products.max()) + 1,
            ).to(self.device)

        # First run: find how many epochs help, on a held-out last week.
        self.log = fit_windows(
            fresh_net(),
            train,
            valid,
            self._codes,
            device=self.device,
            epochs=self.epochs,
            batch_size=self.batch_size,
            learning_rate=self.learning_rate,
            patience=self.patience,
        )
        # Second run: that many epochs on every window, the last week included.
        self._net = fresh_net()
        fit_windows(
            self._net,
            everything,
            None,
            self._codes,
            device=self.device,
            epochs=self.log.best_epoch + 1,
            batch_size=self.batch_size,
            learning_rate=self.learning_rate,
            patience=self.patience,
        )
        self._history = history
        return self
        # <<< SOLUTION

    def predict(self, X: pd.DataFrame) -> FloatArray:
        """Forecast the ``horizon`` days in ``X`` right after the history.

        Raises:
            RuntimeError: ``fit`` has not been called.
            ValueError: ``X`` is not exactly the next ``horizon`` days of the
                series seen in ``fit``.
        """
        # >>> SOLUTION 18.6
        if self._history is None or self._net is None or self._codes is None:
            raise RuntimeError("Call fit before predict.")
        last = self._history[DATE].max()
        expected = pd.date_range(last + pd.Timedelta(days=1), periods=self.spec.horizon)
        if (
            not X[DATE]
            .drop_duplicates()
            .sort_values()
            .reset_index(drop=True)
            .equals(pd.Series(expected, name=DATE))
        ):
            raise ValueError(
                f"X must hold exactly the {self.spec.horizon} days after {last.date()}."
            )

        recent = self._history[
            self._history[DATE] > last - pd.Timedelta(days=self.spec.past)
        ]
        unknown = {column: np.nan for column in (TARGET, OOS_HOURS)}
        future = X.assign(**unknown)[recent.columns]
        cube = self._cube(pd.concat([recent, future], ignore_index=True))
        if not cube.keys.equals(self._cube(recent).keys):
            raise ValueError("X holds different series than the history.")

        series = range(cube.data.shape[0])
        windows = WindowDataset(cube, self.spec, [(s, 0) for s in series])
        forecast = predict_windows(self._net, windows, self._codes, device=self.device)

        rows = cube.keys.loc[cube.keys.index.repeat(self.spec.horizon)].reset_index(
            drop=True
        )
        rows[DATE] = np.tile(expected, cube.data.shape[0])
        rows["forecast"] = forecast.reshape(-1)
        aligned = X[[*SERIES_KEY, DATE]].merge(
            rows, on=[*SERIES_KEY, DATE], how="left", validate="one_to_one"
        )
        return aligned["forecast"].to_numpy(np.float64)
        # <<< SOLUTION
