"""Hyperparameter search with Optuna, every trial logged to MLflow."""

from collections.abc import Sequence
from typing import Any

import mlflow
import optuna
import pandas as pd

from freshcast.evaluation.backtest import backtest
from freshcast.models.gbm import LightGBMForecaster
from freshcast.split import Fold

# The score the search minimises: error on days without a stockout.
OBJECTIVE_METRIC = "wape_in_stock"
LOGGED_METRICS = ["wape", "mae", "bias", "wape_in_stock", "bias_in_stock"]


def suggest_params(trial: optuna.Trial) -> dict[str, Any]:
    """Draw one set of LightGBM parameters from the search space.

    | Parameter | Range | Scale |
    |---|---|---|
    | ``learning_rate`` | 0.02 to 0.2 | log |
    | ``num_leaves`` | 15 to 255 | log |
    | ``min_child_samples`` | 5 to 200 | log |
    | ``feature_fraction`` | 0.5 to 1.0 | linear |
    | ``lambda_l2`` | 0.001 to 10 | log |
    """
    # >>> SOLUTION 11.3
    return {
        "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.2, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 15, 255, log=True),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 200, log=True),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.5, 1.0),
        "lambda_l2": trial.suggest_float("lambda_l2", 1e-3, 10.0, log=True),
    }
    # <<< SOLUTION


def tune(
    table: pd.DataFrame,
    folds: Sequence[Fold],
    features: Sequence[str],
    categorical: Sequence[str],
    *,
    n_trials: int,
    fit_mask: pd.Series | None = None,
    rounds: int = 400,
    experiment: str = "freshcast-tuning",
    seed: int = 0,
) -> optuna.Study:
    """Search LightGBM parameters by backtest and log each trial to MLflow.

    Every trial runs a full backtest with parameters from
    ``suggest_params``. Its MLflow run holds the parameters, the mean of
    each metric over the folds, and the per-fold table as an artifact named
    ``backtest.json``. The study minimises the mean ``wape_in_stock``.

    Args:
        table: The panel with features, the target and ``oos_hours``.
        folds: Validation windows.
        features: Feature columns, categorical ones included.
        categorical: The categorical features.
        n_trials: Number of parameter sets to try.
        fit_mask: Rows allowed in training, see ``backtest``.
        rounds: Trees per model.
        experiment: MLflow experiment name.
        seed: Seed of the sampler, so the search can be repeated.

    Returns:
        The finished study. ``study.best_params`` holds the winner.
    """
    # >>> SOLUTION 11.3
    mlflow.set_experiment(experiment)

    def objective(trial: optuna.Trial) -> float:
        params = suggest_params(trial)

        def make_model() -> LightGBMForecaster:
            return LightGBMForecaster(features, categorical, params, rounds=rounds)

        with mlflow.start_run(run_name=f"trial-{trial.number}"):
            results = backtest(make_model, table, folds, fit_mask=fit_mask)
            means = {name: float(results[name].mean()) for name in LOGGED_METRICS}
            mlflow.log_params({**params, "rounds": rounds, "folds": len(folds)})
            mlflow.log_metrics(means)
            per_fold = results.astype({"valid_start": str, "valid_end": str})
            mlflow.log_table(per_fold, "backtest.json")
        return means[OBJECTIVE_METRIC]

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(
        direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed)
    )
    study.optimize(objective, n_trials=n_trials)
    return study
    # <<< SOLUTION
