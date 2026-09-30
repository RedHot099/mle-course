"""Reference solutions of the exercises in lecture 02."""

SOLUTIONS = {
    "e1": """
import functools
def counted(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper
""",
    "e2": """
def between(low, high):
    def test(value):
        return value is not None and low <= value <= high
    return test
""",
}
