"""Reference solutions of the exercises in lecture 15."""

SOLUTIONS = {
    "e1": """
def delays(attempts, base, factor, cap):
    return [min(base * factor ** k, cap) for k in range(attempts - 1)]
""",
    "e2": """
QUERY = '''
SELECT series, day,
       AVG(units) OVER (PARTITION BY series ORDER BY day ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING)
FROM s
ORDER BY series, day
'''
""",
}
