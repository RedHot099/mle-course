"""Estimating demand on days when a stockout capped the sales.

The idea: if a product usually sells 30% of its day between 6 and 10, and
today it was in stock only then, today's sales are about 30% of what would
have sold. Dividing by that share gives an estimate of the full day.
"""

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from freshcast.data.hourly import to_matrix
from freshcast.data.schema import HOURLY_SALES, HOURLY_STOCKOUT
from freshcast.numeric import row_shares

FloatArray = NDArray[np.float64]


def hourly_profile(hourly: pd.DataFrame) -> FloatArray:
    """Return the typical share of a day's sales that falls in each hour.

    Only days without any out-of-stock hour and with some sales are used:
    on other days the hourly shape is distorted by the very thing being
    corrected.

    Args:
        hourly: Output of ``load_hourly``.

    Returns:
        24 shares that add up to 1.

    Raises:
        ValueError: No day qualifies.
    """
    # >>> SOLUTION 09.3
    sales = to_matrix(hourly[HOURLY_SALES])
    out_of_stock = to_matrix(hourly[HOURLY_STOCKOUT]).astype(bool)
    usable = ~out_of_stock.any(axis=1) & (sales.sum(axis=1) > 0)
    if not usable.any():
        raise ValueError("No fully stocked day with sales to build a profile from.")
    profile: FloatArray = row_shares(sales[usable]).mean(axis=0)
    return profile
    # <<< SOLUTION


def coverage(hourly: pd.DataFrame, profile: FloatArray) -> FloatArray:
    """Return, per row, the share of a typical day's sales that was in stock.

    1.0 means the product was available in every hour that matters; 0.4
    means the in-stock hours usually account for 40% of a day's sales.
    """
    # >>> SOLUTION 09.3
    out_of_stock = to_matrix(hourly[HOURLY_STOCKOUT]).astype(bool)
    covered: FloatArray = np.where(out_of_stock, 0.0, profile).sum(axis=1)
    return covered
    # <<< SOLUTION


def corrected_demand(
    sales_in_stock: FloatArray, covered: FloatArray, *, min_coverage: float = 0.2
) -> FloatArray:
    """Scale in-stock sales up to a full-day demand estimate.

    Args:
        sales_in_stock: Sales in the hours with stock.
        covered: Output of ``coverage`` for the same rows.
        min_coverage: Below this share the estimate would be built on too
            few hours, so the result is NaN: demand unknown.

    Returns:
        ``sales_in_stock / covered``, or NaN where ``covered`` is below
        ``min_coverage``.

    Raises:
        ValueError: ``min_coverage`` is not between 0 (exclusive) and 1.
    """
    # >>> SOLUTION 09.3
    if not 0 < min_coverage <= 1:
        raise ValueError(f"min_coverage must be in (0, 1], got {min_coverage}.")
    enough = covered >= min_coverage
    safe = np.where(enough, covered, 1.0)
    demand: FloatArray = np.where(enough, sales_in_stock / safe, np.nan)
    return demand
    # <<< SOLUTION
