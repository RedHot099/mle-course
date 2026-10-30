from collections.abc import Sequence


def error_summary(
    actual: Sequence[float], forecast: Sequence[float]
) -> dict[str, float | None]:
    """Return MAE, RMSE, WAPE and summed bias of a forecast on aligned days.

    - Both sequences have the same length and order; raise ValueError otherwise.
    - bias is sum(forecast - actual).
    - wape is sum(|forecast - actual|) / sum(actual).
    - wape is None when the actual sum is zero.
    - Leave the inputs unchanged.
    """
    # Replace this placeholder with your implementation.
    return {"mae": None, "rmse": None, "wape": None, "bias": None}
