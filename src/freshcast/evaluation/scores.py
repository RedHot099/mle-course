"""One scoring function for every model of the course."""

from numpy.typing import ArrayLike

from freshcast import metrics


def score_forecast(
    actual: ArrayLike, predicted: ArrayLike, in_stock: ArrayLike
) -> dict[str, float]:
    """Score a forecast on all rows and on the rows without a stockout.

    Sales on a stockout day are capped by supply, so they say little about
    how well demand was forecast. The in-stock rows are the honest test.

    Args:
        actual: Observed sales.
        predicted: Forecasts for the same rows.
        in_stock: Booleans, True where the day had no stockout hour.

    Returns:
        ``wape``, ``mae`` and ``bias`` on all rows, then ``wape_in_stock``
        and ``bias_in_stock`` on the in-stock rows.
    """
    # >>> SOLUTION 08.5
    return {
        "wape": metrics.wape(actual, predicted),
        "mae": metrics.mae(actual, predicted),
        "bias": metrics.bias(actual, predicted),
        "wape_in_stock": metrics.wape(actual, predicted, in_stock),
        "bias_in_stock": metrics.bias(actual, predicted, in_stock),
    }
    # <<< SOLUTION
