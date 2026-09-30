import pandas as pd

from shelfwise import report


def _inputs():
    weekly = pd.DataFrame(
        {
            "stock_code": ["A", "A", "B"],
            "week": pd.to_datetime(["2011-03-07", "2011-03-14", "2011-03-14"]),
            "units": [4.0, 6.0, 2.0],
        }
    )
    forecasts = pd.DataFrame({"stock_code": ["A", "B"], "forecast": [5.0, 1.2]})
    prices = pd.DataFrame({"stock_code": ["A", "B"], "price": [2.0, 10.0]})
    catalogue = pd.DataFrame(
        {"stock_code": ["A", "B"], "description": ["a", "b"], "category": ["X", "Y"]}
    )
    return weekly, forecasts, prices, catalogue


def test_report_orders_by_expected_revenue():
    table = report.build_report(*_inputs(), cover_weeks=2)
    assert table["stock_code"].tolist() == ["B", "A"]
    assert table["order_units"].tolist() == [3, 10]
    assert table["last_week_units"].tolist() == [2.0, 6.0]


# >>> SOLUTION 17.5
def test_report_title_uses_the_iso_week():
    from datetime import datetime

    assert report.report_title(datetime(2026, 1, 5)).endswith("tydzień 02")
    assert report.report_title(datetime(2026, 9, 30)).endswith("tydzień 40")


# --- STUB
#| def test_report_title_uses_the_iso_week():
#|     from datetime import date
#|
#|     week = date.today().isocalendar().week
#|     assert report.report_title() == f"Raport zatowarowania, tydzień {week}"
# <<< SOLUTION
# >>> SOLUTION 17.2
def test_wape_by_category():
    valid = pd.DataFrame(
        {
            "stock_code": ["A", "A", "B"],
            "category": ["X", "X", "Y"],
            "units": [10.0, 10.0, 5.0],
            "forecast": [8.0, 12.0, 5.0],
        }
    )
    table = report.wape_by_category(valid)
    assert table["category"].tolist() == ["X", "Y"]
    assert table["wape"].tolist() == [0.2, 0.0]


# --- STUB
# <<< SOLUTION
# >>> SOLUTION 17.7
def test_missing_price_is_an_error():
    weekly, forecasts, prices, catalogue = _inputs()
    try:
        report.build_report(weekly, forecasts, prices.iloc[:1], catalogue, cover_weeks=1)
    except ValueError:
        return
    raise AssertionError("a product without a price must stop the report")


# --- STUB
# <<< SOLUTION
