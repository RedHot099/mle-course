"""Building and storing the processed dataset that later modules read."""

from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from freshcast.data.hourly import load_hourly, summarise_hours
from freshcast.data.load import load_sales
from freshcast.data.schema import (
    DATE,
    OOS_HOURS,
    PROCESSED_COLUMNS,
    RAW_OOS_HOURS,
    SERIES_KEY,
)
from freshcast.data.validate import check_panel, clean_discount

DAILY_FILE = "daily.parquet"


def prepare_daily(
    raw_path: Path, *, cities: Sequence[int] | None = None
) -> pd.DataFrame:
    """Build the processed daily dataset from a raw file.

    Steps: load the scalar columns, check the panel, clean the discount,
    summarise the hourly arrays and join the summary back, one to one.

    Args:
        raw_path: A raw FreshRetailNet parquet file.
        cities: City ids to keep. None keeps every city.

    Returns:
        A frame with exactly the columns of ``PROCESSED_COLUMNS``, in that
        order, sorted by series and date.

    Raises:
        ValueError: The raw data breaks a panel rule, or the raw stockout
            count disagrees with the hourly arrays.
    """
    # >>> SOLUTION 07.6
    daily = load_sales(raw_path, cities=cities)
    check_panel(daily)
    daily = clean_discount(daily)

    summary = summarise_hours(load_hourly(raw_path, cities=cities))
    daily = daily.merge(
        summary, on=[*SERIES_KEY, DATE], how="left", validate="one_to_one"
    )

    disagree = int((daily[RAW_OOS_HOURS] != daily[OOS_HOURS]).sum())
    if disagree:
        raise ValueError(
            f"{disagree} rows: {RAW_OOS_HOURS} differs from the hourly arrays."
        )
    return daily[PROCESSED_COLUMNS]
    # <<< SOLUTION


def save_processed(daily: pd.DataFrame, directory: Path) -> Path:
    """Write the processed dataset to ``directory`` and return the file path.

    Raises:
        ValueError: The frame's columns differ from ``PROCESSED_COLUMNS``.
    """
    # >>> SOLUTION 07.6
    if list(daily.columns) != PROCESSED_COLUMNS:
        raise ValueError("The frame does not match PROCESSED_COLUMNS.")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / DAILY_FILE
    daily.to_parquet(path, index=False)
    return path
    # <<< SOLUTION


def load_processed(directory: Path) -> pd.DataFrame:
    """Read the processed dataset written by ``save_processed``.

    Raises:
        FileNotFoundError: The dataset has not been built yet.
        ValueError: The file's columns differ from ``PROCESSED_COLUMNS``,
            which means it was written by an older version of the code.
    """
    # >>> SOLUTION 07.6
    path = directory / DAILY_FILE
    if not path.is_file():
        raise FileNotFoundError(f"{path} does not exist. Run prepare_daily first.")
    daily = pd.read_parquet(path)
    if list(daily.columns) != PROCESSED_COLUMNS:
        raise ValueError(f"{path} does not match PROCESSED_COLUMNS. Rebuild it.")
    return daily
    # <<< SOLUTION
