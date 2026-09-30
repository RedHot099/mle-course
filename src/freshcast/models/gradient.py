"""Linear regression trained by gradient descent, written out in NumPy.

Nothing here is used in production: scikit-learn does the same job better.
It exists so that "the model learns" stops being a figure of speech.
"""

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def predict_linear(X: FloatArray, weights: FloatArray, intercept: float) -> FloatArray:
    """Return ``X @ weights + intercept``: one prediction per row of ``X``."""
    # >>> SOLUTION 08.3
    predictions: FloatArray = X @ weights + intercept
    return predictions
    # <<< SOLUTION


def mse(actual: FloatArray, predicted: FloatArray) -> float:
    """Mean squared error: the loss that gradient descent minimises here."""
    # >>> SOLUTION 08.3
    return float(np.mean((predicted - actual) ** 2))
    # <<< SOLUTION


def mse_gradient(
    X: FloatArray, y: FloatArray, weights: FloatArray, intercept: float
) -> tuple[FloatArray, float]:
    """Return the gradient of the MSE with respect to weights and intercept.

    With ``error = prediction - y`` and ``n`` rows:

    - for the weights: ``2 / n * X.T @ error``,
    - for the intercept: ``2 / n * error.sum()``.

    Returns:
        ``(gradient_of_weights, gradient_of_intercept)``.
    """
    # >>> SOLUTION 08.3
    error = predict_linear(X, weights, intercept) - y
    rows = len(y)
    weight_gradient: FloatArray = 2.0 / rows * (X.T @ error)
    return weight_gradient, float(2.0 / rows * error.sum())
    # <<< SOLUTION


def fit_linear_gd(
    X: FloatArray, y: FloatArray, *, learning_rate: float, steps: int
) -> tuple[FloatArray, float, list[float]]:
    """Fit a linear model by gradient descent, starting from all zeros.

    Every step moves the parameters against the gradient, by
    ``learning_rate`` times the gradient.

    Args:
        X: Features, shape ``(n, k)``. Scale them first: columns on very
            different scales make one learning rate fit none of them.
        y: Target, shape ``(n,)``.
        learning_rate: Size of each step, above 0.
        steps: Number of steps, at least 1.

    Returns:
        ``(weights, intercept, losses)`` where ``losses[i]`` is the MSE
        before step ``i``, so ``losses[0]`` is the loss of the all-zero model.

    Raises:
        ValueError: ``learning_rate`` is not positive, ``steps`` is below 1,
            or the loss stopped being finite, which means the learning rate
            is too large.
    """
    # >>> SOLUTION 08.3
    if learning_rate <= 0 or steps < 1:
        raise ValueError("learning_rate must be positive and steps at least 1.")

    weights: FloatArray = np.zeros(X.shape[1])
    intercept = 0.0
    losses = []
    # A diverging run overflows before it is detected; the check below reports it.
    with np.errstate(over="ignore", invalid="ignore"):
        for _ in range(steps):
            loss = mse(y, predict_linear(X, weights, intercept))
            if not np.isfinite(loss):
                raise ValueError("The loss diverged. Lower the learning rate.")
            losses.append(loss)
            weight_gradient, intercept_gradient = mse_gradient(X, y, weights, intercept)
            weights = weights - learning_rate * weight_gradient
            intercept = intercept - learning_rate * intercept_gradient
    return weights, intercept, losses
    # <<< SOLUTION
