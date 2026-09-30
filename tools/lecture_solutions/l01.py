"""Reference solutions of the exercises in lecture 01."""

SOLUTIONS = {
    "e1": """
def apply_discount(prices, rate):
    return [round(p * (1 - rate), 2) for p in prices]
""",
    "e2": """
def known(values):
    for v in values:
        if v is not None:
            yield v
""",
}
