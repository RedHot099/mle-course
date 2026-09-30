"""Reference solutions of the exercises in lecture 19."""

SOLUTIONS = {
    "e1": """
import numpy as np
def drift_report(train, recent):
    shift = (recent.mean() - train.mean()) / train.std()
    outside = ((recent < train.min()) | (recent > train.max())).mean()
    return {"shift": float(shift), "outside": float(outside)}
""",
}
