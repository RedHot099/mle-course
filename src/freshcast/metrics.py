"""Forecast error metrics on NumPy arrays.

All four share the same rules, applied by ``prepare``: the two inputs must
have the same shape and hold no NaN, and an optional boolean ``mask`` picks
the elements to score. The mask is how later modules evaluate "only the days
without a stockout". Inputs may be lists, 1-D or 2-D arrays or pandas
columns; a (series, day) matrix is scored element by element, as if it were
flattened. Every metric returns a plain Python ``float``.
"""

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


def prepare(
    actual: ArrayLike, predicted: ArrayLike, mask: ArrayLike | None = None
) -> tuple[FloatArray, FloatArray]:
    """Validate the inputs of a metric and apply the mask.

    Args:
        actual: Observed values, for example the daily sales of the test
            week: a list, or an array of any number of dimensions.
        predicted: Forecasts of the same values, same shape as ``actual``,
            element for element.
        mask: Booleans of the same shape. True keeps the element, False
            leaves it out of the score. None keeps all.

    Returns:
        A pair ``(actual, predicted)`` of one-dimensional ``float64`` arrays
        of equal length: the inputs flattened, without the elements the mask
        leaves out, in their original order.

    Raises:
        ValueError: ``actual`` and ``predicted`` differ in shape (a (2, 3)
            and a (3, 2) input are an error too), the mask has a different
            shape, nothing is left after masking, or a kept value is NaN. A
            NaN in an element the mask leaves out is not an error.
    """
    # >>> SOLUTION 05.1
    actual_array = np.asarray(actual, dtype=np.float64)
    predicted_array = np.asarray(predicted, dtype=np.float64)
    if actual_array.shape != predicted_array.shape:
        raise ValueError(
            f"Shapes differ: actual {actual_array.shape}, "
            f"predicted {predicted_array.shape}."
        )
    actual_array, predicted_array = actual_array.ravel(), predicted_array.ravel()
    if mask is not None:
        keep = np.asarray(mask, dtype=bool)
        if keep.shape != np.shape(actual):
            raise ValueError(f"Mask shape {keep.shape} differs from the data.")
        keep = keep.ravel()
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
    """Mean absolute error: the average size of a miss, in units of the data.

    ``mean(|actual - predicted|)`` over the elements kept by ``mask``.

    Args:
        actual: Observed values.
        predicted: Forecasts, same shape as ``actual``.
        mask: Booleans of the same shape, True keeps the element; None keeps
            all.

    Returns:
        The error as a ``float``, in units of the data (units sold).

    Raises:
        ValueError: The inputs break a rule of ``prepare``.
    """
    # >>> SOLUTION 05.2
    a, p = prepare(actual, predicted, mask)
    return float(np.abs(a - p).mean())
    # <<< SOLUTION


def rmse(
    actual: ArrayLike, predicted: ArrayLike, mask: ArrayLike | None = None
) -> float:
    """Root mean squared error: like MAE, but large misses weigh more.

    ``sqrt(mean((actual - predicted) ** 2))`` over the elements kept by
    ``mask``.

    Args:
        actual: Observed values.
        predicted: Forecasts, same shape as ``actual``.
        mask: Booleans of the same shape, True keeps the element; None keeps
            all.

    Returns:
        The error as a ``float``, in units of the data (units sold).

    Raises:
        ValueError: The inputs break a rule of ``prepare``.
    """
    # >>> SOLUTION 05.2
    a, p = prepare(actual, predicted, mask)
    return float(np.sqrt(np.square(a - p).mean()))
    # <<< SOLUTION


def wape(
    actual: ArrayLike, predicted: ArrayLike, mask: ArrayLike | None = None
) -> float:
    """Weighted absolute percentage error: total miss over total actual.

    ``sum(|actual - predicted|) / sum(|actual|)`` over the elements kept by
    ``mask``. Unlike a mean of per-row percentages, it stays defined when
    single rows are zero, which daily sales often are.

    Args:
        actual: Observed values.
        predicted: Forecasts, same shape as ``actual``.
        mask: Booleans of the same shape, True keeps the element; None keeps
            all.

    Returns:
        A ``float`` without unit: 0.3 means the misses add up to 30% of the
        actual total.

    Raises:
        ValueError: The inputs break a rule of ``prepare``, or the absolute values
            of the kept actual values sum to zero (the denominator of the formula
            above).
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

    ``(sum(predicted) - sum(actual)) / sum(actual)`` over the elements kept
    by ``mask``. Positive means the forecast is too high overall, negative
    too low. A forecast can have zero bias and a large WAPE: the misses
    cancel out.

    Args:
        actual: Observed values.
        predicted: Forecasts, same shape as ``actual``.
        mask: Booleans of the same shape, True keeps the element; None keeps
            all.

    Returns:
        A ``float`` without unit: -0.1 means the forecast total is 10% below
        the actual total.

    Raises:
        ValueError: The inputs break a rule of ``prepare``, or the kept
            actual values sum to zero.
    """
    # >>> SOLUTION 05.3
    a, p = prepare(actual, predicted, mask)
    total = float(a.sum())
    if total == 0:
        raise ValueError("Bias is undefined when the actual values sum to zero.")
    return float((p - a).sum() / total)
    # <<< SOLUTION
