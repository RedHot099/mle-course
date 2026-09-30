"""Reference solutions of the exercises in lecture 17."""

SOLUTIONS = {
    "e1": """
def first_bad(n, is_bad):
    low, high = 0, n
    while low < high:
        middle = (low + high) // 2
        if is_bad(middle):
            high = middle
        else:
            low = middle + 1
    return low
""",
    "e2": """
from datetime import date
def week_label(now=None):
    iso = (now or date.today()).isocalendar()
    return f"{iso.year}-W{iso.week:02d}"
""",
}
