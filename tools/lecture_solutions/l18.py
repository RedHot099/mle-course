"""Reference solutions of the exercises in lecture 18."""

SOLUTIONS = {
    "e1": """
def window_starts(days, past, horizon):
    return list(range(days - past - horizon + 1))
""",
    "e2": """
import numpy as np
def masked_mae(forecast, target, in_stock):
    weights = in_stock * np.isfinite(target)
    if weights.sum() == 0:
        raise ValueError("no in-stock day with a known target")
    return float((np.abs(forecast - np.nan_to_num(target)) * weights).sum() / weights.sum())
""",
}
