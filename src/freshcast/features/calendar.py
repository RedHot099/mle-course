"""Features that depend only on the date."""

import holidays
import numpy as np
import pandas as pd

from freshcast.data.schema import DATE

DAYS_IN_WEEK = 7
# Holidays further away than this are all "far": the model needs no more detail.
MAX_DAYS_TO_HOLIDAY = 14
COUNTRY = "CN"


def day_of_week(df: pd.DataFrame) -> pd.Series:
    """Return the day of week of every row: 0 for Monday, 6 for Sunday."""
    # >>> SOLUTION 09.1
    days: pd.Series = df[DATE].dt.dayofweek.astype("int8")
    return days
    # <<< SOLUTION


def cyclical(values: pd.Series, period: int) -> tuple[pd.Series, pd.Series]:
    """Encode a repeating quantity as a point on a circle.

    Day 6 and day 0 are neighbours in a week, but 6 and 0 are far apart as
    numbers. On the circle they sit next to each other.

    Args:
        values: Positions within the cycle, from 0 to ``period - 1``.
        period: Length of the cycle, for example 7 for days of the week.

    Returns:
        ``(sine, cosine)`` of the angle ``2 * pi * values / period``.
    """
    # >>> SOLUTION 09.1
    angle = 2 * np.pi * values / period
    return np.sin(angle), np.cos(angle)
    # <<< SOLUTION


def public_holidays(first: pd.Timestamp, last: pd.Timestamp) -> pd.DatetimeIndex:
    """Return the public holidays of the data's country between two dates.

    The dates come from the ``holidays`` package. The range is inclusive.
    Days off that were moved from a weekend count as holidays too.
    """
    # >>> SOLUTION 09.1
    years = range(first.year, last.year + 1)
    calendar = holidays.country_holidays(COUNTRY, years=years)
    days = pd.DatetimeIndex(sorted(calendar))
    return days[(days >= first) & (days <= last)]
    # <<< SOLUTION


def is_public_holiday(df: pd.DataFrame) -> pd.Series:
    """Return 1 on rows whose date is a public holiday, else 0."""
    # >>> SOLUTION 09.1
    days = public_holidays(df[DATE].min(), df[DATE].max())
    return df[DATE].isin(days).astype("int8")
    # <<< SOLUTION


def days_to_next_holiday(df: pd.DataFrame) -> pd.Series:
    """Return how many days remain until the next public holiday.

    0 on a holiday itself. Capped at ``MAX_DAYS_TO_HOLIDAY``, which is also
    the value when no holiday follows within the calendar that was looked up.
    """
    # >>> SOLUTION 09.1
    horizon = pd.Timedelta(days=MAX_DAYS_TO_HOLIDAY)
    days = public_holidays(df[DATE].min(), df[DATE].max() + horizon)
    dates = df[DATE].drop_duplicates().sort_values()
    positions = days.searchsorted(dates.to_numpy())
    has_next = positions < len(days)
    waits = np.full(len(dates), MAX_DAYS_TO_HOLIDAY, dtype="int64")
    upcoming = days[positions[has_next]]
    waits[has_next] = (upcoming - dates[has_next].to_numpy()).days
    wait_by_date = pd.Series(
        np.minimum(waits, MAX_DAYS_TO_HOLIDAY), index=dates.to_numpy()
    )
    return df[DATE].map(wait_by_date).astype("int8")
    # <<< SOLUTION
