"""Reference solutions of the exercises in lecture 12."""

SOLUTIONS = {
    "e1": """
import numpy as np
def precision_recall(y, alarm):
    tp = int(((alarm == 1) & (y == 1)).sum())
    alarms, events = int(alarm.sum()), int(y.sum())
    return (tp / alarms if alarms else 0.0, tp / events if events else 0.0)
""",
    "e2": """
import numpy as np
def cheapest_threshold(y, scores, cost_false, cost_missed):
    best, best_cost = float("inf"), y.sum() * cost_missed
    for threshold in sorted(set(scores.tolist()), reverse=True):
        alarm = scores >= threshold
        cost = (alarm & (y == 0)).sum() * cost_false + (~alarm & (y == 1)).sum() * cost_missed
        if cost < best_cost:
            best, best_cost = threshold, cost
    return best
""",
}
