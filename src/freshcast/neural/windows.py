"""Turning the panel into training windows for a sequence model.

A complete panel sorted by series and date is a rectangle in disguise:
every series has the same days. Reshaped, it becomes a cube of shape
``(series, days, channels)``, and a training example is a slice of it:
``past`` days of history followed by ``horizon`` days to forecast.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import torch
from numpy.typing import NDArray
from torch.utils.data import Dataset

from freshcast.data.schema import DATE, OOS_HOURS, SERIES_KEY, TARGET

FloatArray = NDArray[np.float32]


@dataclass(frozen=True)
class PanelCube:
    """A complete panel as arrays.

    Attributes:
        data: Shape ``(series, days, channels)``.
        stockout_hours: Shape ``(series, days)``: ``oos_hours`` per day,
            NaN where unknown (days being forecast).
        keys: One row per series, in the order of the first axis.
        dates: The days, in the order of the second axis.
        channels: Names of the last axis.
    """

    data: FloatArray
    stockout_hours: FloatArray
    keys: pd.DataFrame
    dates: pd.DatetimeIndex
    channels: list[str]


def panel_cube(panel: pd.DataFrame, channels: Sequence[str]) -> PanelCube:
    """Reshape a complete, sorted panel into a cube.

    Args:
        panel: One row per series and day, every series with the same days,
            sorted by series and date.
        channels: Numeric columns to keep, in this order.

    Raises:
        ValueError: The panel is not complete or not sorted, so a reshape
            would put values of one series into another.
    """
    # >>> SOLUTION 18.2
    dates = pd.DatetimeIndex(sorted(panel[DATE].unique()))
    days = len(dates)
    if len(panel) % days:
        raise ValueError("Series have different numbers of days.")
    series = len(panel) // days
    ordered = panel[[*SERIES_KEY, DATE]].sort_values([*SERIES_KEY, DATE])
    if not ordered.index.equals(panel.index):
        raise ValueError("The panel must be sorted by series and date.")
    if not (panel[DATE].to_numpy().reshape(series, days) == dates.to_numpy()).all():
        raise ValueError("Every series must cover the same days, in order.")

    data = panel[list(channels)].to_numpy(np.float32).reshape(series, days, -1)
    stockouts = panel[OOS_HOURS].to_numpy(np.float32).reshape(series, days)
    keys = panel[SERIES_KEY].iloc[::days].reset_index(drop=True)
    return PanelCube(data, stockouts, keys, dates, list(channels))
    # <<< SOLUTION


@dataclass(frozen=True)
class WindowSpec:
    """Which channels a window holds.

    Attributes:
        past: Days of history the model reads.
        horizon: Days it forecasts.
        past_channels: Channels read from the history days. The first one
            must be the target.
        future_channels: Channels known in advance for the forecast days.
    """

    past: int
    horizon: int
    past_channels: list[str]
    future_channels: list[str]


class WindowDataset(Dataset[dict[str, torch.Tensor]]):
    """Windows ``(series, start)`` of a cube as tensors for PyTorch.

    Each example is a dict with:

    - ``past``: ``(past, len(past_channels))``, the target divided by the
      series' mean over these days, so big and small sellers look alike,
    - ``future``: ``(horizon, len(future_channels))``,
    - ``target``: ``(horizon,)`` in original units, NaN if unknown,
    - ``in_stock``: ``(horizon,)``, 1.0 on days without a stockout hour,
    - ``scale``: the divisor applied to the past target,
    - ``series``: position of the series in the cube.

    ``__getitems__`` returns a whole batch at once with array indexing,
    which is much faster than building examples one by one. Use it with a
    ``DataLoader`` whose ``collate_fn`` passes the batch through unchanged.

    Raises:
        ValueError: A window does not fit inside the cube, or the first past
            channel is not the target.
    """

    def __init__(
        self, cube: PanelCube, spec: WindowSpec, windows: Sequence[tuple[int, int]]
    ) -> None:
        # >>> SOLUTION 18.3
        if spec.past_channels[0] != TARGET:
            raise ValueError(f"The first past channel must be {TARGET}.")
        self.spec = spec
        self.windows = np.asarray(windows, dtype=np.int64).reshape(-1, 2)
        span = spec.past + spec.horizon
        too_late = self.windows[:, 1] + span > cube.data.shape[1]
        if (self.windows[:, 1] < 0).any() or too_late.any():
            raise ValueError("Some windows do not fit inside the cube.")
        index = {name: position for position, name in enumerate(cube.channels)}
        self.data = cube.data
        self.stockouts = cube.stockout_hours
        self.past_idx = [index[name] for name in spec.past_channels]
        self.future_idx = [index[name] for name in spec.future_channels]
        # <<< SOLUTION

    def __len__(self) -> int:
        return len(self.windows)

    def __getitems__(self, positions: list[int]) -> dict[str, torch.Tensor]:
        """Return the batch of windows at ``positions``."""
        # >>> SOLUTION 18.3
        series, starts = self.windows[positions, 0], self.windows[positions, 1]
        past_days = starts[:, None] + np.arange(self.spec.past)
        future_days = starts[:, None] + self.spec.past + np.arange(self.spec.horizon)
        rows = series[:, None]

        past = self.data[rows, past_days][:, :, self.past_idx]
        scale = np.maximum(np.nanmean(past[:, :, 0], axis=1), 0.1)
        past[:, :, 0] = past[:, :, 0] / scale[:, None]
        future = self.data[rows, future_days][:, :, self.future_idx]
        target = self.data[rows, future_days][:, :, 0]
        in_stock = (self.stockouts[rows, future_days] == 0).astype(np.float32)
        return {
            "past": torch.from_numpy(np.ascontiguousarray(past)),
            "future": torch.from_numpy(np.ascontiguousarray(future)),
            "target": torch.from_numpy(np.ascontiguousarray(target)),
            "in_stock": torch.from_numpy(in_stock),
            "scale": torch.from_numpy(scale.astype(np.float32)),
            "series": torch.from_numpy(series),
        }
        # <<< SOLUTION

    def __getitem__(self, position: int) -> dict[str, torch.Tensor]:
        """Return one window, with the batch axis removed."""
        batch = self.__getitems__([position])
        return {name: tensor[0] for name, tensor in batch.items()}


def pass_through(batch: Any) -> Any:
    """``collate_fn`` for datasets whose ``__getitems__`` builds whole batches."""
    return batch
