"""Rules the data must satisfy before anything is computed from it."""

import pandas as pd

from freshcast.data.schema import DATE, DISCOUNT, DISCOUNT_IS_ZERO, SERIES_KEY, TARGET


def check_panel(df: pd.DataFrame) -> None:
    """Raise unless ``df`` is a complete daily panel.

    The rules, in the order they are checked:

    1. No missing value in the series key, the date or the target.
    2. At most one row per series and day.
    3. Every series has a row for every day between the first and the last
       date of the frame.
    4. The target is never negative.

    Args:
        df: Daily sales with the series key, the date and the target.

    Raises:
        ValueError: A rule is broken. The message names the rule and says
            how many rows or series break it.
    """
    # >>> SOLUTION 07.2
    row_key = [*SERIES_KEY, DATE]

    missing = int(df[[*row_key, TARGET]].isna().any(axis=1).sum())
    if missing:
        raise ValueError(f"{missing} rows have a missing key, date or target.")

    duplicated = int(df.duplicated(row_key).sum())
    if duplicated:
        raise ValueError(f"{duplicated} rows repeat a (series, day) pair.")

    expected_days = (df[DATE].max() - df[DATE].min()).days + 1
    days_per_series = df.groupby(SERIES_KEY, sort=False).size()
    incomplete = int((days_per_series != expected_days).sum())
    if incomplete:
        raise ValueError(
            f"{incomplete} series do not cover all {expected_days} days of the panel."
        )

    negative = int((df[TARGET] < 0).sum())
    if negative:
        raise ValueError(f"{negative} rows have a negative {TARGET}.")
    # <<< SOLUTION


def clean_discount(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy in which a zero discount is off the numeric scale.

    ``discount`` is a price multiplier: 1.0 is the regular price, 0.8 is 20%
    off. The documentation does not say what exactly 0 means. It may be a
    product given away for free or a placeholder for "not recorded". Either
    way it does not behave like the low end of the same scale, so:

    - rows with a discount of exactly 0 get ``discount_is_zero`` True and
      their ``discount`` becomes NaN,
    - every other value, including the few above 1, stays as it is.

    No information is lost: the flag says where the zeros were.

    Args:
        df: Daily sales with a ``discount`` column.

    Returns:
        A new frame with ``discount`` cleaned and a boolean
        ``discount_is_zero`` column added. The input is not modified.

    Raises:
        ValueError: A discount is negative or missing on input. Neither can
            be explained, so neither is handled.
    """
    # >>> SOLUTION 07.2
    discount = df[DISCOUNT]
    unexpected = int((discount.isna() | (discount < 0)).sum())
    if unexpected:
        raise ValueError(f"{unexpected} rows have a negative or missing {DISCOUNT}.")

    is_zero = discount == 0
    return df.assign(**{DISCOUNT: discount.mask(is_zero), DISCOUNT_IS_ZERO: is_zero})
    # <<< SOLUTION
