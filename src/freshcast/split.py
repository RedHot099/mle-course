"""Splitting a panel in time: the past trains, the future validates."""

from dataclasses import dataclass

import pandas as pd

from freshcast.data.schema import DATE


def last_days_start(df: pd.DataFrame, days: int) -> pd.Timestamp:
    """Return the first date of the final ``days`` days of the frame.

    The span of the frame is counted in calendar days from its earliest to
    its latest date, both included. Rows may come in any order and a date
    may repeat (one row per series per day); only the earliest and the
    latest date matter. Example: for data from 2024-04-01 to 2024-04-10
    and ``days=3`` the result is 2024-04-08, so 04-08, 04-09 and 04-10 are
    the final three days.

    Args:
        df: A frame with the date column ``DATE`` (``"dt"``, dtype
            ``datetime64``), for example the processed panel of module 07.
            Other columns are ignored.
        days: Length of the final period in days, at least 1.

    Returns:
        The first day of the final period, as a ``pd.Timestamp``. It is a
        valid ``cutoff`` for ``split_by_date``.

    Raises:
        ValueError: ``days`` is below 1 or not shorter than the frame's span,
            so nothing would be left before the final period.
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
        df: A frame with the date column ``DATE`` (``"dt"``, dtype
            ``datetime64``). All columns are kept in both parts.
        cutoff: First date of the second part, e.g. the result of
            ``last_days_start``.

    Returns:
        ``(before, after)``: the rows with a date earlier than ``cutoff``,
        and the rows with ``cutoff`` or a later date. Together they hold
        every row of ``df`` exactly once. Both keep the columns, the row
        order and the index of ``df`` (no reset), so predictions made for
        one part can be aligned with the original frame. ``df`` is not
        modified.

    Raises:
        ValueError: One of the parts would be empty, i.e. ``cutoff`` is on
            or before the first date or after the last date.
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
