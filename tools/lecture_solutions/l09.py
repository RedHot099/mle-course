"""Reference solutions of the exercises in lecture 09."""

SOLUTIONS = {
    "e1": """
def horizon_lag(df, column, lag, horizon):
    if lag < horizon:
        raise ValueError(f"A lag of {lag} is not known {horizon} steps ahead.")
    return df.groupby("series")[column].shift(lag)
""",
    "e2": """
def target_encode(train, other, group, target):
    means = train.groupby(group)[target].mean()
    return other[group].map(means).fillna(train[target].mean())
""",
}
