"""The weekly report: forecast, reorder suggestion and expected revenue per product."""

import math
from datetime import datetime

import pandas as pd

from shelfwise.model import wape


def report_title(now: datetime | None = None) -> str:
    # >>> SOLUTION 17.5
    moment = now or datetime.now()
    # --- STUB
    #| moment = datetime.now()
    # <<< SOLUTION
    return f"Raport zatowarowania, tydzień {moment.strftime('%V')}"


def build_report(
    weekly: pd.DataFrame,
    forecasts: pd.DataFrame,
    prices: pd.DataFrame,
    catalogue: pd.DataFrame,
    cover_weeks: int,
) -> pd.DataFrame:
    """One row per forecast product."""
    # >>> SOLUTION 17.7
    priced = forecasts.merge(prices, on="stock_code", how="left", validate="one_to_one")
    missing = int(priced["price"].isna().sum())
    if missing:
        raise ValueError(f"{missing} forecast products have no price.")
    # --- STUB
    #| priced = forecasts.merge(prices, on="stock_code", how="left")
    #| priced["price"] = priced["price"].fillna(0)
    # <<< SOLUTION
    # >>> SOLUTION 17.6
    last_week = weekly["week"].max()
    recent = weekly[weekly["week"] == last_week][["stock_code", "units"]]
    report = priced.merge(
        recent.rename(columns={"units": "last_week_units"}),
        on="stock_code",
        how="left",
        validate="one_to_one",
    )
    report["last_week_units"] = report["last_week_units"].fillna(0)  # no row: no sale
    report["order_units"] = (report["forecast"] * cover_weeks).apply(math.ceil)
    report["expected_revenue"] = report["forecast"] * report["price"]
    # --- STUB
    #| rows = []
    #| for _, row in priced.iterrows():
    #|     history = weekly[weekly["stock_code"] == row["stock_code"]].sort_values("week")
    #|     last = history[history["week"] == history["week"].max()]
    #|     last_units = float(last["units"].iloc[0]) if len(last) else 0.0
    #|     rows.append(
    #|         {
    #|             **row.to_dict(),
    #|             "last_week_units": last_units,
    #|             "order_units": math.ceil(row["forecast"] * cover_weeks),
    #|             "expected_revenue": row["forecast"] * row["price"],
    #|         }
    #|     )
    #| report = pd.DataFrame(rows)
    # <<< SOLUTION
    report = report.merge(catalogue, on="stock_code", how="left")
    return report.sort_values("expected_revenue", ascending=False).reset_index(drop=True)


# >>> SOLUTION 17.2
def wape_by_category(valid: pd.DataFrame) -> pd.DataFrame:
    """Validation error per product category.

    Args:
        valid: Validation rows with ``category``, ``units`` and ``forecast``.

    Returns:
        One row per category: ``category``, ``products``, ``units`` and
        ``wape``, sorted by ``units`` from the largest.
    """
    rows = []
    for category, group in valid.groupby("category"):
        rows.append(
            {
                "category": category,
                "products": group["stock_code"].nunique(),
                "units": float(group["units"].sum()),
                "wape": wape(group["units"], group["forecast"]),
            }
        )
    return pd.DataFrame(rows).sort_values("units", ascending=False).reset_index(drop=True)


# --- STUB
#| pass
# <<< SOLUTION
