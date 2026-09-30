"""Splitting a panel in time: the past trains, the future validates."""

from dataclasses import dataclass

import pandas as pd

from freshcast.data.schema import DATE


def last_days_start(df: pd.DataFrame, days: int) -> pd.Timestamp:
    """Return the first date of the final ``days`` days of the frame.

    Args:
        df: A frame with the date column.
        days: Length of the final period, at least 1.

    Raises:
        ValueError: ``days`` is below 1 or not shorter than the frame's span.
    """
    # >>> SOLUTION 08.1
    first, last = df[DATE].min(), df[DATE].max()
    span = (last - first).days + 1
    if not 1 <= days < span:
        raise ValueError(f"days must be between 1 and {span - 1}, got {days}.")
    start: pd.Timestamp = last - pd.Timedelta(days=days - 1)
    return start
    # <<< SOLUTION


def split_by_date(
    df: pd.DataFrame, cutoff: pd.Timestamp
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a frame into the rows before ``cutoff`` and the rows from it on.

    Rows are never shuffled: everything the model trains on happened before
    everything it is validated on.

    Args:
        df: A frame with the date column.
        cutoff: First date of the second part.

    Returns:
        ``(before, after)``. Both keep the index of ``df``, so predictions
        made for one part can be aligned with the original frame.

    Raises:
        ValueError: One of the parts would be empty.
    """
    # >>> SOLUTION 08.1
    is_before = df[DATE] < cutoff
    if is_before.all() or not is_before.any():
        raise ValueError(f"Cutoff {cutoff} leaves one side of the split empty.")
    return df.loc[is_before], df.loc[~is_before]
    # <<< SOLUTION


@dataclass(frozen=True)
class Fold:
    """One step of a rolling-origin backtest.

    The model trains on every day before ``valid_start`` and is scored on
    the days from ``valid_start`` to ``valid_end``, inclusive.
    """

    valid_start: pd.Timestamp
    valid_end: pd.Timestamp

    def split(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return ``(train, valid)`` for this fold, keeping the index of ``df``."""
        # >>> SOLUTION 11.1
        is_train = df[DATE] < self.valid_start
        is_valid = (df[DATE] >= self.valid_start) & (df[DATE] <= self.valid_end)
        return df.loc[is_train], df.loc[is_valid]
        # <<< SOLUTION


def rolling_origin_folds(
    last_date: pd.Timestamp, n_folds: int, horizon: int
) -> list[Fold]:
    """Build folds whose validation windows are the last weeks of the data.

    The last fold validates on the final ``horizon`` days, the one before it
    on the ``horizon`` days preceding those, and so on. Windows do not
    overlap, and each fold trains on everything before its own window.

    Args:
        last_date: Last date of the data.
        n_folds: Number of folds, at least 1.
        horizon: Length of each validation window in days, at least 1.

    Returns:
        The folds, oldest validation window first.

    Raises:
        ValueError: ``n_folds`` or ``horizon`` is below 1.
    """
    # >>> SOLUTION 11.1
    if n_folds < 1 or horizon < 1:
        raise ValueError(
            f"n_folds and horizon must be at least 1, got {n_folds}, {horizon}."
        )
    folds = []
    for steps_back in range(n_folds - 1, -1, -1):
        valid_end = last_date - pd.Timedelta(days=steps_back * horizon)
        valid_start = valid_end - pd.Timedelta(days=horizon - 1)
        folds.append(Fold(valid_start, valid_end))
    return folds
    # <<< SOLUTION
