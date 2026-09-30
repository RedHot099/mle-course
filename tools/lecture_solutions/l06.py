"""Reference solutions of the exercises in lecture 06."""

SOLUTIONS = {
    "e1": """
import pandas as pd
def missing_report(df):
    count = df.isna().sum()
    report = pd.DataFrame({"count": count, "share": count / len(df)})
    return report.loc[report["count"] > 0].sort_values("count", ascending=False)
""",
    "e2": """
def check_unique_key(df, key):
    repeated = df.duplicated(subset=key, keep=False)
    if repeated.any():
        example = df.loc[repeated, key].iloc[0].to_dict()
        raise ValueError(f"{int(repeated.sum())} rows repeat the key {key}, e.g. {example}")
""",
}
