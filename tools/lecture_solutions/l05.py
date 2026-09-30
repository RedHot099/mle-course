"""Reference solutions of the exercises in lecture 05."""

SOLUTIONS = {
    "e1": """
import numpy as np
def in_stock_share(stockouts):
    return (stockouts == 0).mean(axis=1)
""",
    "e2": """
import numpy as np
def standardise(matrix):
    std = matrix.std(axis=0)
    return (matrix - matrix.mean(axis=0)) / np.where(std == 0, 1.0, std)
""",
}
