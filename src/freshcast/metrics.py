"""Forecast error metrics on NumPy arrays.

All four share the same rules: the two inputs must have the same shape and
hold no NaN, and an optional boolean ``mask`` picks the rows to score.
The mask is how later modules evaluate "only the days without a stockout".
"""

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


def prepare(
    actual: ArrayLike, predicted: ArrayLike, mask: ArrayLike | None = None
) -> tuple[FloatArray, FloatArray]:
    """Validate the inputs of a metric and apply the mask.

    Args:
        actual: Observed values.
        predicted: Forecasts, same shape as ``actual``.
        mask: Booleans of the same shape. True keeps the row. None keeps all.

    Returns:
        The two inputs as one-dimensional float arrays, masked.

    Raises:
        ValueError: The shapes differ, a kept value is NaN, or nothing is
            left after masking.
    """
    # >>> SOLUTION 05.1
    actual_array = np.asarray(actual, dtype=np.float64).ravel()
    predicted_array = np.asarray(predicted, dtype=np.float64).ravel()
    if actual_array.shape != predicted_array.shape:
        raise ValueError(
            f"Shapes differ: actual {actual_array.shape}, "
            f"predicted {predicted_array.shape}."
        )
    if mask is not None:
        keep = np.asarray(mask, dtype=bool).ravel()
        if keep.shape != actual_array.shape:
            raise ValueError(f"Mask shape {keep.shape} differs from the data.")
        actual_array, predicted_array = actual_array[keep], predicted_array[keep]
    if actual_array.size == 0:
        raise ValueError("No values to score.")
    missing = int(np.isnan(actual_array).sum() + np.isnan(predicted_array).sum())
    if missing:
        raise ValueError(f"{missing} values are NaN.")
    return actual_array, predicted_array
    # <<< SOLUTION


def mae(
    actual: ArrayLike, predicted: ArrayLike, mask: ArrayLike | None = None
) -> float:
    """Mean absolute error: the average size of a miss, in units of the data."""
    # >>> SOLUTION 05.2
    a, p = prepare(actual, predicted, mask)
    return float(np.abs(a - p).mean())
    # <<< SOLUTION


def rmse(
    actual: ArrayLike, predicted: ArrayLike, mask: ArrayLike | None = None
) -> float:
    """Root mean squared error: like MAE, but large misses weigh more."""
    # >>> SOLUTION 05.2
    a, p = prepare(actual, predicted, mask)
    return float(np.sqrt(np.square(a - p).mean()))
    # <<< SOLUTION


def wape(
    actual: ArrayLike, predicted: ArrayLike, mask: ArrayLike | None = None
) -> float:
    """Weighted absolute percentage error: total miss over total actual.

    Unlike a mean of per-row percentages, it stays defined when single rows
    are zero, which daily sales often are.

    Raises:
        ValueError: The actual values sum to zero.
    """
    # >>> SOLUTION 05.3
    a, p = prepare(actual, predicted, mask)
    total = float(np.abs(a).sum())
    if total == 0:
        raise ValueError("WAPE is undefined when the actual values sum to zero.")
    return float(np.abs(a - p).sum() / total)
    # <<< SOLUTION


def bias(
    actual: ArrayLike, predicted: ArrayLike, mask: ArrayLike | None = None
) -> float:
    """Relative bias: total forecast minus total actual, over total actual.

    Positive means the forecast is too high overall, negative too low.
    A forecast can have zero bias and a large WAPE: the misses cancel out.

    Raises:
        ValueError: The actual values sum to zero.
    """
    # >>> SOLUTION 05.3
    a, p = prepare(actual, predicted, mask)
    total = float(a.sum())
    if total == 0:
        raise ValueError("Bias is undefined when the actual values sum to zero.")
    return float((p - a).sum() / total)
    # <<< SOLUTION
