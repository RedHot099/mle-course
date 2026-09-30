"""The capstone's two questions: which model, and how good on unseen days."""

from collections.abc import Callable, Mapping

import pandas as pd

from freshcast.data.schema import DATE, OOS_HOURS, SERIES_KEY, TARGET
from freshcast.evaluation.backtest import backtest
from freshcast.evaluation.scores import score_forecast
from freshcast.models.panel import PanelForecaster
from freshcast.split import Fold


def compare_models(
    candidates: Mapping[str, Callable[[], PanelForecaster]],
    table: pd.DataFrame,
    folds: list[Fold],
    fit_masks: Mapping[str, pd.Series | None],
) -> pd.DataFrame:
    """Backtest every candidate on the same folds and put the results side by side.

    Args:
        candidates: Model name to a function returning a new, unfitted model.
        table: The panel with features, the target and ``oos_hours``.
        folds: Validation windows, the same for every model.
        fit_masks: Model name to the rows it may train on (see ``backtest``).
            A model missing here trains on every row.

    Returns:
        One row per model and fold: ``model`` followed by the columns of
        ``backtest``.

    Raises:
        ValueError: ``candidates`` is empty, or ``fit_masks`` names a model
            that is not a candidate, which is most likely a typo.
    """
    # >>> SOLUTION 19.1
    if not candidates:
        raise ValueError("Give at least one model to compare.")
    unknown = set(fit_masks) - set(candidates)
    if unknown:
        raise ValueError(
            f"fit_masks names models that are not candidates: {sorted(unknown)}."
        )
    parts = [
        backtest(make, table, folds, fit_mask=fit_masks.get(name)).assign(model=name)
        for name, make in candidates.items()
    ]
    results = pd.concat(parts, ignore_index=True)
    return results[["model", *results.columns.drop("model")]]
    # <<< SOLUTION


def seasonal_naive_forecast(history: pd.DataFrame, days: pd.DataFrame) -> pd.Series:
    """Forecast each day with the sales of the same series seven days earlier.

    Args:
        history: The panel up to the last known day, with the target.
        days: Rows of the days to forecast (series key and date), at most
            seven days after the history.

    Returns:
        A Series named ``seasonal_naive`` with the index of ``days``.

    Raises:
        ValueError: A day is more than seven days after the history, or a
            series has no value a week earlier.
    """
    # >>> SOLUTION 19.2
    last = history[DATE].max()
    too_far = int((days[DATE] > last + pd.Timedelta(days=7)).sum())
    if too_far:
        raise ValueError(f"{too_far} rows are more than 7 days after the history.")
    week_ago = history[[*SERIES_KEY, DATE, TARGET]].assign(
        **{DATE: history[DATE] + pd.Timedelta(days=7)}
    )
    merged = days[[*SERIES_KEY, DATE]].merge(
        week_ago, on=[*SERIES_KEY, DATE], how="left", validate="one_to_one"
    )
    missing = int(merged[TARGET].isna().sum())
    if missing:
        raise ValueError(f"{missing} rows have no sales a week earlier.")
    return pd.Series(merged[TARGET].to_numpy(), index=days.index, name="seasonal_naive")
    # <<< SOLUTION


def test_scores(
    forecasts: pd.DataFrame, actuals: pd.DataFrame, history: pd.DataFrame
) -> pd.DataFrame:
    """Score the model and the seasonal naive baseline on the same test rows.

    Args:
        forecasts: Series key, date and ``forecast``, as written by
            ``pipeline.forecast``.
        actuals: The processed test days, with the target and ``oos_hours``.
        history: The panel the model was trained on.

    Returns:
        Two rows, ``model`` and ``seasonal_naive``, with the columns of
        ``score_forecast``.

    Raises:
        ValueError: Forecasts and actuals do not cover the same series and days.
    """
    # >>> SOLUTION 19.2
    rows = actuals.merge(
        forecasts,
        on=[*SERIES_KEY, DATE],
        how="outer",
        validate="one_to_one",
        indicator=True,
    )
    unmatched = int((rows["_merge"] != "both").sum())
    if unmatched:
        raise ValueError(f"{unmatched} rows are in only one of forecasts and actuals.")
    in_stock = rows[OOS_HOURS] == 0
    naive = seasonal_naive_forecast(history, rows)
    scores = {
        "model": score_forecast(rows[TARGET], rows["forecast"], in_stock),
        "seasonal_naive": score_forecast(rows[TARGET], naive, in_stock),
    }
    return pd.DataFrame.from_dict(scores, orient="index")
    # <<< SOLUTION
