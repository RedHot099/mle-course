"""Tests of the forecast error metrics.

The first test is given as a pattern. The rest is yours: `uv run course
check 05.5` tells you which bugs your tests would let through.
"""

from collections.abc import Callable

import numpy as np
import pytest

from freshcast.metrics import bias, mae, rmse, wape

Metric = Callable[..., float]


def test_mae_is_the_mean_absolute_difference() -> None:
    actual = np.array([1.0, 2.0, 3.0])
    predicted = np.array([2.0, 2.0, 5.0])

    assert mae(actual, predicted) == pytest.approx(1.0)


# >>> SOLUTION 05.5
def test_rmse_weighs_large_misses_more_than_mae() -> None:
    actual = np.array([0.0, 0.0, 0.0, 0.0])
    predicted = np.array([0.0, 0.0, 0.0, 4.0])

    assert mae(actual, predicted) == pytest.approx(1.0)
    assert rmse(actual, predicted) == pytest.approx(2.0)


def test_wape_is_total_miss_over_total_actual() -> None:
    actual = np.array([0.0, 10.0, 10.0])
    predicted = np.array([1.0, 8.0, 13.0])

    assert wape(actual, predicted) == pytest.approx(6 / 20)


def test_bias_is_positive_when_forecasting_too_much() -> None:
    actual = np.array([10.0, 10.0])

    assert bias(actual, np.array([12.0, 11.0])) == pytest.approx(0.15)
    assert bias(actual, np.array([8.0, 9.0])) == pytest.approx(-0.15)


def test_mask_selects_the_rows_to_score() -> None:
    actual = np.array([1.0, 100.0, 3.0])
    predicted = np.array([2.0, 0.0, 3.0])
    keep = np.array([True, False, True])

    assert mae(actual, predicted, keep) == pytest.approx(0.5)
    assert rmse(actual, predicted, keep) == pytest.approx(np.sqrt(0.5))
    assert wape(actual, predicted, keep) == pytest.approx(0.25)
    assert bias(actual, predicted, keep) == pytest.approx(0.25)


@pytest.mark.parametrize("metric", [mae, rmse, wape, bias])
def test_nan_is_an_error(metric: Metric) -> None:
    with pytest.raises(ValueError, match="NaN"):
        metric(np.array([1.0, np.nan]), np.array([1.0, 2.0]))


@pytest.mark.parametrize("metric", [mae, rmse, wape, bias])
def test_different_lengths_are_an_error(metric: Metric) -> None:
    with pytest.raises(ValueError, match="[Ss]hape"):
        metric(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0]))


@pytest.mark.parametrize("metric", [wape, bias])
def test_zero_total_is_an_error(metric: Metric) -> None:
    with pytest.raises(ValueError, match="zero"):
        metric(np.zeros(3), np.ones(3))


# --- STUB
#| # Your tests go here.
# <<< SOLUTION
