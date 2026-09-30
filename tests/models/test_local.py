"""Tests of the local forecasters.

The first test is given as a pattern. The rest is yours: `uv run course
check 04.2` runs your tests against deliberately broken forecasters and
tells you which bugs they would let through.
"""

import pytest

from freshcast.models.local import (
    LocalForecaster,
    MovingAverageForecaster,
    NaiveForecaster,
    SeasonalNaiveForecaster,
)


def test_naive_repeats_the_last_value() -> None:
    forecast = NaiveForecaster().fit([3.0, 5.0, 4.0]).predict(horizon=2)

    assert forecast == [4.0, 4.0]


# >>> SOLUTION 04.2
def test_naive_ignores_everything_but_the_last_value() -> None:
    forecast = NaiveForecaster().fit([9.0, 1.0]).predict(horizon=1)

    assert forecast == [1.0]


def test_seasonal_naive_repeats_the_last_season() -> None:
    history = [1.0, 2.0, 3.0, 10.0, 20.0, 30.0]

    forecast = SeasonalNaiveForecaster(season=3).fit(history).predict(horizon=3)

    assert forecast == [10.0, 20.0, 30.0]


def test_seasonal_naive_wraps_around_for_long_horizons() -> None:
    history = [10.0, 20.0, 30.0]

    forecast = SeasonalNaiveForecaster(season=3).fit(history).predict(horizon=5)

    assert forecast == [10.0, 20.0, 30.0, 10.0, 20.0]


def test_moving_average_uses_only_the_window() -> None:
    history = [100.0, 1.0, 2.0, 3.0]

    forecast = MovingAverageForecaster(window=3).fit(history).predict(horizon=2)

    assert forecast == pytest.approx([2.0, 2.0])


def test_moving_average_of_a_short_history_uses_all_of_it() -> None:
    forecast = MovingAverageForecaster(window=7).fit([2.0, 4.0]).predict(horizon=1)

    assert forecast == pytest.approx([3.0])


@pytest.mark.parametrize(
    "forecaster",
    [NaiveForecaster(), SeasonalNaiveForecaster(season=2), MovingAverageForecaster()],
)
@pytest.mark.parametrize("horizon", [1, 4])
def test_forecast_has_one_value_per_step(
    forecaster: LocalForecaster, horizon: int
) -> None:
    forecast = forecaster.fit([1.0, 2.0, 3.0]).predict(horizon=horizon)

    assert len(forecast) == horizon


def test_fit_rejects_an_empty_history() -> None:
    with pytest.raises(ValueError, match="empty"):
        NaiveForecaster().fit([])


def test_seasonal_naive_rejects_a_history_shorter_than_a_season() -> None:
    with pytest.raises(ValueError, match="shorter"):
        SeasonalNaiveForecaster(season=7).fit([1.0, 2.0])


@pytest.mark.parametrize("horizon", [0, -1])
def test_predict_rejects_a_horizon_below_one(horizon: int) -> None:
    forecaster = NaiveForecaster().fit([1.0])

    with pytest.raises(ValueError, match="horizon"):
        forecaster.predict(horizon=horizon)


def test_predict_before_fit_is_an_error() -> None:
    with pytest.raises(RuntimeError, match="fit"):
        NaiveForecaster().predict(horizon=1)


# --- STUB
#| # Your tests go here.
# <<< SOLUTION
