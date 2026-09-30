"""Reference solutions of the exercises in lecture 04."""

SOLUTIONS = {
    "e1": """
def moving_average(history, window):
    recent = history[-window:]
    return sum(recent) / len(recent)
def test_moving_average_uses_only_the_last_values():
    assert moving_average([100.0, 1.0, 2.0, 3.0], 3) == 2.0
""",
    "e2": """
from datetime import date
def report_title(today=None):
    week = (today or date.today()).isocalendar().week
    return f'Raport za tydzień {week}'
""",
}
