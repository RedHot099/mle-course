"""How a regression tree picks a split, in NumPy.

LightGBM does this millions of times with many refinements. The core is
small: try every threshold on a feature and keep the one after which the
two halves are each as uniform as possible.
"""

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def sum_of_squares(values: FloatArray) -> float:
    """Return the sum of squared distances of ``values`` from their mean.

    This is the error of predicting the mean for every row: the quantity a
    regression tree tries to shrink. An empty array has error 0.
    """
    # >>> SOLUTION 10.1
    if values.size == 0:
        return 0.0
    return float(np.sum((values - values.mean()) ** 2))
    # <<< SOLUTION


def best_split(feature: FloatArray, target: FloatArray) -> tuple[float, float]:
    """Find the threshold on one feature that reduces the error the most.

    Rows with ``feature <= threshold`` go left, the rest go right. Candidate
    thresholds are the midpoints between consecutive distinct values of the
    feature.

    Args:
        feature: Values of one feature, shape ``(n,)``.
        target: Target of the same rows.

    Returns:
        ``(threshold, gain)`` where ``gain`` is the error before the split
        minus the summed error of the two sides. With several equally good
        thresholds the lowest one is returned.

    Raises:
        ValueError: The feature has a single distinct value, so no split
            exists.
    """
    # >>> SOLUTION 10.1
    order = np.argsort(feature, kind="stable")
    x, y = feature[order], target[order]
    boundaries = np.flatnonzero(x[1:] != x[:-1])
    if boundaries.size == 0:
        raise ValueError("The feature is constant: there is nothing to split on.")

    # Error of a group = sum(y^2) - sum(y)^2 / n, from running sums.
    total, total_squares, rows = y.sum(), np.square(y).sum(), y.size
    left_sum = np.cumsum(y)[boundaries]
    left_squares = np.cumsum(np.square(y))[boundaries]
    left_rows = boundaries + 1
    right_rows = rows - left_rows

    left_error = left_squares - left_sum**2 / left_rows
    right_error = (total_squares - left_squares) - (total - left_sum) ** 2 / right_rows
    parent_error = total_squares - total**2 / rows
    gains = parent_error - left_error - right_error

    best = int(np.argmax(gains))
    at = boundaries[best]
    return float((x[at] + x[at + 1]) / 2), float(gains[best])
    # <<< SOLUTION
