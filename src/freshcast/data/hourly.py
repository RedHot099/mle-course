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

    Each cell of ``hours_sale`` holds 24 sales figures, one per hour of the
    day (position 0 is 00:00-00:59). Each cell of ``hours_stock_status``
    holds 24 flags, where 1 means the product was out of stock in that hour.

    Args:
        path: A raw FreshRetailNet parquet file, e.g. ``paths.FRN_TRAIN``.
        cities: ``city_id`` values to keep. None keeps every city, which
            needs several GB of memory for the full file.

    Returns:
        One row per series and day with exactly the columns of
        ``HOURLY_COLUMNS`` (``store_id``, ``product_id``, ``dt``,
        ``hours_sale``, ``hours_stock_status``), sorted by ``store_id``,
        ``product_id``, then ``dt``, with a fresh 0..n-1 index and ``dt`` as
        ``datetime64``. The rows line up with ``load_sales`` for the same
        file and cities.
    """
    # >>> SOLUTION 07.4
    filters = None if cities is None else [(CITY, "in", list(cities))]
    df = pd.read_parquet(path, columns=HOURLY_COLUMNS, filters=filters)
    df = df.assign(**{DATE: pd.to_datetime(df[DATE], format="%Y-%m-%d")})
    return df.sort_values([*SERIES_KEY, DATE]).reset_index(drop=True)
    # <<< SOLUTION


def to_matrix(column: pd.Series) -> np.ndarray:
    """Stack a column of 24-element arrays into one ``(n, 24)`` array.

    Args:
        column: A Series whose every cell is a 1-D array of hourly values,
            e.g. ``hourly["hours_sale"]``.

    Returns:
        A NumPy array of shape ``(len(column), 24)``: row ``i`` holds the
        values of the ``i``-th cell, column ``h`` the hour starting at
        ``h``:00. The element type is that of the arrays (float for sales,
        integer for stock status).

    Raises:
        ValueError: Some row does not hold exactly 24 values. The message
            gives the number of such rows.
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
        hourly: Output of ``load_hourly``: the series key, ``dt``,
            ``hours_sale`` and ``hours_stock_status``.

    Returns:
        A new frame with ``store_id``, ``product_id``, ``dt`` and these four
        columns, in this order:

        - ``oos_hours``: integer, hours out of stock between 06:00 and 22:00
          (array positions 6 to 21, ``OOS_WINDOW``), from 0 to 16,
        - ``oos_hours_total``: integer, hours out of stock in the whole day,
          from 0 to 24,
        - ``sales_in_stock``: float, sales in the hours with stock,
        - ``sales_while_oos``: float, sales recorded in hours flagged out of
          stock.

        Rows are in the order of the input, with the same index. The two
        sales columns add up to the day's total sales (``sale_amount``).
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
