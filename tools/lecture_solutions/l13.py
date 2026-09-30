"""Reference solutions of the exercises in lecture 13."""

SOLUTIONS = {
    "e1": """
import numpy as np
def kmeans_step(points, centres):
    distances = ((points[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)
    assigned = distances.argmin(axis=1)
    new = centres.copy()
    for k in range(len(centres)):
        if (assigned == k).any():
            new[k] = points[assigned == k].mean(axis=0)
    return new, assigned
""",
    "e2": """
import numpy as np
def first_component_share(matrix):
    centred = matrix - matrix.mean(axis=0)
    s = np.linalg.svd(centred, compute_uv=False)
    return float(s[0] ** 2 / (s ** 2).sum())
""",
}
