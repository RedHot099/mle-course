import numpy as np
import pandas as pd

from shelfwise import features, model


def _frame(products: int = 5, weeks: int = 40) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for number in range(products):
        for week in pd.date_range("2010-01-04", periods=weeks, freq="7D"):
            rows.append((f"2{number:04d}", week, float(rng.poisson(5 + number))))
    return pd.DataFrame(rows, columns=["stock_code", "week", "units"])


def test_lags_stay_within_a_product():
    built = features.add_history(_frame(products=2, weeks=5))
    firsts = built.groupby("stock_code").head(1)
    assert firsts["units_lag_1"].isna().all()


def test_split_weeks_holds_out_the_last_weeks():
    train, valid = model.split_weeks(_frame(), validation_weeks=8)
    assert valid["week"].nunique() == 8
    assert train["week"].max() < valid["week"].min()


def test_train_and_validate_returns_forecasts():
    frame = features.build(_frame())
    fitted, valid = model.train_and_validate(frame, validation_weeks=8)
    assert (valid["forecast"] >= 0).all()
    assert len(model.predict_next(frame, fitted)) == 5


# >>> SOLUTION 17.4
def test_validation_targets_do_not_reach_the_training_features():
    frame = features.build(_frame())
    _, first = model.train_and_validate(frame, validation_weeks=8)
    shifted = frame.copy()
    last_weeks = shifted["week"] >= np.sort(shifted["week"].unique())[-8]
    shifted.loc[last_weeks, "units"] *= 100
    _, second = model.train_and_validate(shifted, validation_weeks=8)
    # Forecasts may use lags of validation weeks, but not a model fitted on them:
    # the first validation week has only training history.
    week = first["week"].min()
    assert np.allclose(
        first.loc[first["week"] == week, "forecast"], second.loc[second["week"] == week, "forecast"]
    )


# --- STUB
# <<< SOLUTION
# >>> SOLUTION 17.3
def test_season_flag_marks_october_to_december():
    frame = pd.DataFrame({"week": pd.to_datetime(["2010-09-27", "2010-10-04", "2010-12-27"])})
    assert features.add_season(frame)["is_season"].tolist() == [0, 1, 1]


def test_season_feature_is_used_only_when_enabled():
    assert "is_season" not in model.feature_columns(use_season=False)
    assert "is_season" in model.feature_columns(use_season=True)


# --- STUB
# <<< SOLUTION
