"""Per-series computations on a sorted panel: lags, rolling means, profiles."""

import pandas as pd

from freshcast.data.schema import DATE, SERIES_KEY, TARGET


def is_sorted_panel(df: pd.DataFrame) -> bool:
    """Tell whether the rows are ordered by series, then by date.

    Lags and rolling windows read "the previous row of the same series", so
    they are only correct on a frame for which this returns True.
    """
    # >>> SOLUTION 07.5
    order = df[[*SERIES_KEY, DATE]]
    in_order = order.sort_values([*SERIES_KEY, DATE], kind="stable")
    return bool((order.index == in_order.index).all())
    # <<< SOLUTION


def add_lag(df: pd.DataFrame, column: str, lag: int) -> pd.DataFrame:
    """Add the value of ``column`` from ``lag`` days earlier in the same series.

    Args:
        df: A complete panel sorted by series and date.
        column: The column to look back in.
        lag: How many days back, at least 1.

    Returns:
        A new frame with the column ``{column}_lag_{lag}``. The first
        ``lag`` days of every series are NaN: there is no earlier value, and
        a value from another series must never fill the gap.

    Raises:
        ValueError: ``lag`` is below 1 or the frame is not sorted.
    """
    # >>> SOLUTION 07.5
    if lag < 1:
        raise ValueError(f"lag must be at least 1, got {lag}.")
    if not is_sorted_panel(df):
        raise ValueError("The frame must be sorted by series and date.")

    lagged = df.groupby(SERIES_KEY, sort=False)[column].shift(lag)
    return df.assign(**{f"{column}_lag_{lag}": lagged})
    # <<< SOLUTION


def add_rolling_mean(
    df: pd.DataFrame, column: str, window: int, lag: int = 1
) -> pd.DataFrame:
    """Add the mean of ``column`` over a window of past days of the same series.

    The window ends ``lag`` days before the row and spans ``window`` days.
    With the default ``lag=1`` it covers yesterday and the days before it,
    never the row's own day.

    Args:
        df: A complete panel sorted by series and date.
        column: The column to average.
        window: Number of days in the window, at least 1.
        lag: Distance in days between the row and the end of the window,
            at least 1.

    Returns:
        A new frame with the column ``{column}_mean_{window}_lag_{lag}``.
        Rows without ``window`` full past days are NaN.

    Raises:
        ValueError: ``window`` or ``lag`` is below 1, or the frame is not
            sorted.
    """
    # >>> SOLUTION 07.5
    if window < 1 or lag < 1:
        raise ValueError(f"window and lag must be at least 1, got {window}, {lag}.")
    if not is_sorted_panel(df):
        raise ValueError("The frame must be sorted by series and date.")

    past = df.groupby(SERIES_KEY, sort=False)[column].shift(lag)
    series_of_row = [df[key] for key in SERIES_KEY]
    mean = (
        past.groupby(series_of_row, sort=False)
        .rolling(window)
        .mean()
        .reset_index(level=SERIES_KEY, drop=True)
    )
    return df.assign(**{f"{column}_mean_{window}_lag_{lag}": mean})
    # <<< SOLUTION


def dow_profile(df: pd.DataFrame) -> pd.Series:
    """Return the typical shape of a week: relative sales by day of week.

    Each series is first divided by its own mean, so a big seller and a
    small one weigh the same. The result is the mean of those relative
    sales per weekday, over all series.

    Args:
        df: Daily sales with the series key, the date and the target.

    Returns:
        A Series indexed 0 (Monday) to 6 (Sunday), named ``dow_profile``.
        A value of 1.2 means sales 20% above the series average.

    Raises:
        ValueError: A series has zero mean sales, so its relative sales are
            undefined.
    """
    # >>> SOLUTION 07.5
    series_mean = df.groupby(SERIES_KEY, sort=False)[TARGET].transform("mean")
    dead = int((series_mean == 0).sum())
    if dead:
        raise ValueError(f"{dead} rows belong to series with zero mean sales.")

    relative = df[TARGET] / series_mean
    day_of_week = df[DATE].dt.dayofweek.rename("dow")
    return relative.groupby(day_of_week).mean().rename("dow_profile")
    # <<< SOLUTION
