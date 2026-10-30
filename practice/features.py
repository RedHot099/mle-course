import pandas as pd


def lag_within_series(
    table: pd.DataFrame, key: str, column: str, periods: int
) -> pd.Series:
    """Return `column` shifted by `periods` rows inside each `key` series.

    - The table is already sorted by key and day.
    - The result keeps the index of the table.
    - The first `periods` rows of every series are missing.
    - Leave the table unchanged.
    """
    # Replace this placeholder with your implementation.
    return pd.Series(dtype=float)
