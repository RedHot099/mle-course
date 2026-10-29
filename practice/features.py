import pandas as pd


def lag_within_series(
    table: pd.DataFrame, key: str, column: str, periods: int
) -> pd.Series:
    """Return `column` shifted by `periods` rows inside each `key` series.

    The table must already be sorted by key and day. Leave the table unchanged
    and keep its index. The first `periods` rows of every series are missing.
    """
    # Replace this placeholder with your implementation.
    return pd.Series(dtype=float)
