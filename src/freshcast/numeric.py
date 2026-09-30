"""Array helpers that need no pandas."""

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def row_shares(matrix: FloatArray) -> FloatArray:
    """Divide every row by its own sum, so each row adds up to 1.

    Used for hourly profiles: a row of 24 hourly sales becomes the share of
    the day's sales that fell in each hour.

    Args:
        matrix: Two-dimensional array of non-negative numbers.

    Returns:
        An array of the same shape. A row that sums to zero has no profile
        and becomes all NaN.

    Raises:
        ValueError: ``matrix`` is not two-dimensional or holds a negative
            value.
    """
    # >>> SOLUTION 05.4
    if matrix.ndim != 2:
        raise ValueError(f"Expected a 2-D array, got {matrix.ndim} dimensions.")
    negative = int((matrix < 0).sum())
    if negative:
        raise ValueError(f"{negative} values are negative.")

    totals = matrix.sum(axis=1, keepdims=True)
    safe_totals = np.where(totals == 0, np.nan, totals)
    shares: FloatArray = matrix / safe_totals
    return shares
    # <<< SOLUTION
