"""Reference solutions of the exercises in lecture 10."""

SOLUTIONS = {
    "e1": """
import numpy as np
def split_gain(x, y, threshold):
    def sse(values):
        return float(((values - values.mean()) ** 2).sum()) if values.size else 0.0
    left, right = y[x <= threshold], y[x > threshold]
    return sse(y) - sse(left) - sse(right)
""",
    "e2": """
import numpy as np
def knn_predict(X, y, point, k):
    distances = np.sqrt(((X - point) ** 2).sum(axis=1))
    return float(y[np.argsort(distances)[:k]].mean())
""",
}
