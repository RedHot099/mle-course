"""Reading the raw parquet files without loading more than needed."""

from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from freshcast.data.schema import CITY, DAILY_COLUMNS, DATE, SERIES_KEY


def shrink_integers(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with every integer column in its smallest fitting type.

    Floats are left alone: halving their precision changes values, halving
    an integer's width does not.

    Args:
        df: Any frame.

    Returns:
        A new frame with the same values and column order.
    """
    # >>> SOLUTION 07.1
    integer_columns = df.select_dtypes("integer").columns
    shrunk = {
        column: pd.to_numeric(df[column], downcast="integer")
        for column in integer_columns
    }
    return df.assign(**shrunk)
    # <<< SOLUTION


def load_sales(
    path: Path,
    *,
    cities: Sequence[int] | None = None,
    columns: Sequence[str] = DAILY_COLUMNS,
) -> pd.DataFrame:
    """Load daily sales rows for the chosen cities.

    Only the requested columns are read from disk, and rows of other cities
    are dropped while reading, so memory use follows the result, not the file.

    Args:
        path: A raw FreshRetailNet parquet file.
        cities: City ids to keep. None keeps every city.
        columns: Columns to read. Must include the series key and the date.

    Returns:
        One row per series and day, sorted by series then date, with a fresh
        0..n-1 index, the date as ``datetime64`` and integers shrunk.
    """
    # >>> SOLUTION 07.1
    filters = None if cities is None else [(CITY, "in", list(cities))]
    df = pd.read_parquet(path, columns=list(columns), filters=filters)
    df = df.assign(**{DATE: pd.to_datetime(df[DATE], format="%Y-%m-%d")})
    df = shrink_integers(df)
    return df.sort_values([*SERIES_KEY, DATE]).reset_index(drop=True)
    # <<< SOLUTION
