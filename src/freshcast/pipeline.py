"""The two jobs of the project: train a model, and forecast with a saved one."""

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from freshcast.artifacts import load_model, save_model
from freshcast.config import Settings
from freshcast.data.prepare import prepare_daily
from freshcast.data.schema import DATE, OOS_HOURS, OUTCOME_COLUMNS, SERIES_KEY, TARGET
from freshcast.evaluation.backtest import backtest
from freshcast.features import catalog
from freshcast.forecast import FORECAST, forecast_direct
from freshcast.models.gbm import LightGBMForecaster
from freshcast.split import rolling_origin_folds

logger = logging.getLogger(__name__)

SCORE_COLUMNS = ["wape", "mae", "bias", "wape_in_stock", "bias_in_stock"]
# The longest look-back of any feature. Earlier rows have incomplete features.
WARM_UP_FEATURE = f"{TARGET}_lag_{max(catalog.LAGS)}"


@dataclass(frozen=True)
class TrainResult:
    """What a training run produced."""

    model_dir: Path
    backtest: pd.DataFrame


def cities_in(raw_path: Path) -> list[int]:
    """Return the city ids present in a raw file, in ascending order.

    Only one small column is read, so this is cheap even for the full file.
    """
    # >>> SOLUTION 14.3
    cities = pd.read_parquet(raw_path, columns=["city_id"])["city_id"].unique()
    return sorted(int(city) for city in cities)
    # <<< SOLUTION


def prepare_in_chunks(raw_path: Path, cities: list[int] | None) -> pd.DataFrame:
    """Build the processed panel one city at a time.

    The hourly arrays of the whole file do not fit in the memory of a
    laptop. Each city's arrays are reduced to a few numbers per row before
    the next city is read, so the peak is the largest city, not the file.

    Args:
        raw_path: A raw FreshRetailNet parquet file.
        cities: City ids to keep. None means every city in the file.

    Returns:
        The same frame ``prepare_daily`` would return for all the cities at
        once, sorted by series and date.
    """
    # >>> SOLUTION 14.3
    chosen = cities_in(raw_path) if cities is None else cities
    parts = []
    for number, city in enumerate(chosen, start=1):
        logger.info("Preparing city %d (%d of %d)", city, number, len(chosen))
        parts.append(prepare_daily(raw_path, cities=[city]))
    panel = pd.concat(parts, ignore_index=True)
    return panel.sort_values([*SERIES_KEY, DATE]).reset_index(drop=True)
    # <<< SOLUTION


def training_mask(table: pd.DataFrame, *, in_stock_only: bool) -> pd.Series:
    """Return which rows of the feature table may be trained on.

    Rows from the first weeks of a series are out: their lag features are
    incomplete. With ``in_stock_only`` the days with a stockout are out too,
    because their sales are capped by supply and teach the model to
    under-forecast.
    """
    # >>> SOLUTION 14.3
    mask = table[WARM_UP_FEATURE].notna()
    if in_stock_only:
        mask &= table[OOS_HOURS] == 0
    return mask
    # <<< SOLUTION


def train(settings: Settings) -> TrainResult:
    """Prepare the data, backtest, fit on everything and save the model.

    Returns:
        Where the model was saved and the per-fold backtest scores.
    """
    # >>> SOLUTION 14.4
    data = settings.data
    daily = prepare_in_chunks(data.train_file, data.cities)
    logger.info("Prepared %d rows, %d days", len(daily), daily[DATE].nunique())

    table = catalog.build_feature_table(daily)
    mask = training_mask(table, in_stock_only=settings.model.in_stock_only)
    logger.info("Training rows after the mask: %d of %d", int(mask.sum()), len(table))

    def make_model() -> LightGBMForecaster:
        return LightGBMForecaster(
            catalog.MODEL_FEATURES,
            catalog.CATEGORICAL_FEATURES,
            settings.model.params,
            rounds=settings.model.rounds,
        )

    folds = rolling_origin_folds(
        table[DATE].max(), settings.backtest.folds, settings.backtest.horizon
    )
    scores = backtest(make_model, table, folds, fit_mask=mask)
    means = {name: float(scores[name].mean()) for name in SCORE_COLUMNS}
    logger.info("Backtest over %d folds: %s", len(folds), means)

    final = make_model().fit(table.loc[mask], table.loc[mask, TARGET])
    metadata = {
        "features": catalog.MODEL_FEATURES,
        "categorical": catalog.CATEGORICAL_FEATURES,
        "params": final.params,
        "rounds": final.rounds_used,
        "train_rows": int(mask.sum()),
        "train_first_day": daily[DATE].min(),
        "train_last_day": daily[DATE].max(),
        "cities": data.cities,
        "backtest": means,
    }
    model_dir = save_model(final, settings.artifacts_dir, "lightgbm", metadata)
    daily.to_parquet(model_dir / "history.parquet", index=False)
    scores.to_csv(model_dir / "backtest.csv", index=False)
    logger.info("Saved model to %s", model_dir)
    return TrainResult(model_dir, scores)
    # <<< SOLUTION


def forecast(settings: Settings, model_dir: Path, future_file: Path) -> pd.DataFrame:
    """Forecast the days in ``future_file`` with a saved model.

    The future file has the raw layout. Whatever outcomes it holds are
    dropped before forecasting, so the same function serves real use, where
    they do not exist, and evaluation, where they do.

    Returns:
        One row per series and future day: the series key, the date and
        ``forecast``. Also written to ``model_dir/forecast.parquet``.
    """
    # >>> SOLUTION 14.4
    model, metadata = load_model(model_dir)
    history = pd.read_parquet(model_dir / "history.parquet")
    data = settings.data
    future = prepare_in_chunks(future_file, data.cities)
    known = future.drop(columns=OUTCOME_COLUMNS)
    logger.info("Forecasting %d rows with model %s", len(known), metadata["signature"])

    predicted = forecast_direct(model, history, known, catalog.build_feature_table)
    result = known[[*SERIES_KEY, DATE]].assign(**{FORECAST: predicted})
    result.to_parquet(model_dir / "forecast.parquet", index=False)
    return result
    # <<< SOLUTION
