"""Reference solutions of the exercises in lecture 08."""

SOLUTIONS = {
    "e1": """
import numpy as np
def gd_step(w, b, x, y, rate):
    r = w * x + b - y
    return w - rate * 2 * np.mean(r * x), b - rate * 2 * np.mean(r)
""",
    "e2": """
import numpy as np
def time_split(days, valid_days, test_days):
    last = days.max()
    test = days > last - test_days
    valid = ~test & (days > last - test_days - valid_days)
    return ~test & ~valid, valid, test
""",
}
