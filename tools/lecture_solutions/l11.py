"""Reference solutions of the exercises in lecture 11."""

SOLUTIONS = {
    "e1": """
def rolling_folds(last_day, n_folds, horizon):
    if n_folds < 1 or horizon < 1:
        raise ValueError("n_folds and horizon must be at least 1")
    folds = []
    for back in range(n_folds - 1, -1, -1):
        end = last_day - back * horizon
        folds.append((end - horizon + 1, end))
    return folds
""",
    "e2": """
def compare(a, b):
    differences = [x - y for x, y in zip(a, b)]
    return sum(differences) / len(differences), sum(x < y for x, y in zip(a, b))
""",
}
