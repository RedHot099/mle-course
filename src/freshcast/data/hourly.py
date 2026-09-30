"""Turning the 24-element hourly arrays into per-day numbers."""

from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd

from freshcast.data.schema import (
    CITY,
    DATE,
    HOURLY_COLUMNS,
    HOURLY_SALES,
    HOURLY_STOCKOUT,
    HOURS_PER_DAY,
    OOS_HOURS,
    OOS_HOURS_TOTAL,
    OOS_WINDOW,
    SALES_IN_STOCK,
    SALES_WHILE_OOS,
    SERIES_KEY,
)


def load_hourly(path: Path, *, cities: Sequence[int] | None = None) -> pd.DataFrame:
    """Load the series key, the date and the two hourly array columns.

    Args:
        path: A raw FreshRetailNet parquet file.
        cities: City ids to keep. None keeps every city, which needs
            several GB of memory for the full file.

    Returns:
        One row per series and day, sorted by series then date, with a fresh
        0..n-1 index and the date as ``datetime64``.
    """
    # >>> SOLUTION 07.4
    filters = None if cities is None else [(CITY, "in", list(cities))]
    df = pd.read_parquet(path, columns=HOURLY_COLUMNS, filters=filters)
    df = df.assign(**{DATE: pd.to_datetime(df[DATE], format="%Y-%m-%d")})
    return df.sort_values([*SERIES_KEY, DATE]).reset_index(drop=True)
    # <<< SOLUTION


def to_matrix(column: pd.Series) -> np.ndarray:
    """Stack a column of 24-element arrays into one ``(n, 24)`` array.

    Raises:
        ValueError: Some row does not hold exactly 24 values.
    """
    # >>> SOLUTION 07.4
    lengths = column.map(len)
    wrong = int((lengths != HOURS_PER_DAY).sum())
    if wrong:
        raise ValueError(f"{wrong} rows do not hold {HOURS_PER_DAY} hourly values.")
    return np.stack(column.tolist())
    # <<< SOLUTION


def summarise_hours(hourly: pd.DataFrame) -> pd.DataFrame:
    """Reduce the hourly arrays to four numbers per series and day.

    Args:
        hourly: Output of ``load_hourly``.

    Returns:
        A frame with the series key, the date and:

        - ``oos_hours``: hours out of stock between 06:00 and 22:00,
        - ``oos_hours_total``: hours out of stock in the whole day,
        - ``sales_in_stock``: sales in the hours with stock,
        - ``sales_while_oos``: sales recorded in hours flagged out of stock.

        Rows are in the order of the input. The two sales columns add up to
        the day's total sales.
    """
    # >>> SOLUTION 07.4
    sales = to_matrix(hourly[HOURLY_SALES])
    out_of_stock = to_matrix(hourly[HOURLY_STOCKOUT]).astype(bool)

    summary = hourly[[*SERIES_KEY, DATE]].copy()
    summary[OOS_HOURS] = out_of_stock[:, OOS_WINDOW].sum(axis=1)
    summary[OOS_HOURS_TOTAL] = out_of_stock.sum(axis=1)
    summary[SALES_IN_STOCK] = np.where(out_of_stock, 0.0, sales).sum(axis=1)
    summary[SALES_WHILE_OOS] = np.where(out_of_stock, sales, 0.0).sum(axis=1)
    return summary
    # <<< SOLUTION
