import pandas as pd

from shelfwise import calendar


def test_week_range_steps_by_seven_days():
    weeks = calendar.week_range(pd.Timestamp("2011-01-03"), pd.Timestamp("2011-01-24"))
    assert len(weeks) == 4
    assert (weeks[1:] - weeks[:-1]).days.tolist() == [7, 7, 7]


# >>> SOLUTION 17.9
def test_week_starts_on_monday_for_every_day_of_the_week():
    days = pd.Series(pd.date_range("2011-03-07 13:00", periods=7, freq="D"))
    starts = calendar.week_start(days)
    assert starts.nunique() == 1
    assert starts.iloc[0] == pd.Timestamp("2011-03-07")


def test_sunday_closes_the_week():
    sunday = pd.Series(pd.to_datetime(["2011-03-13 18:00"]))
    assert calendar.week_start(sunday).iloc[0] == pd.Timestamp("2011-03-07")


# --- STUB
# <<< SOLUTION
