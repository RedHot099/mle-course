"""Demand statistics for the Monash Car Parts series.

The parsing and statistics come from lab 01, now typed. The decorators and
the registry come from lab 02.
"""

import functools
import json
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from pathlib import Path

MISSING = "?"

type Values = Sequence[float | None]
type Stats = dict[str, float | None]
type Statistic = Callable[[Values], float | None]

# >>> SOLUTION 02.1


def parse_value(text: str) -> float | None:
    """Turn one value of a .tsf series into a float, or None for a missing month."""
    text = text.strip()
    if text == MISSING:
        return None
    try:
        value = float(text)
    except ValueError as error:
        raise ValueError(f"Not a number: {text!r}") from error
    if value < 0:
        raise ValueError(f"Demand cannot be negative: {text!r}")
    return value


def parse_series_line(line: str) -> tuple[str, str, list[float | None]]:
    """Split one data line into (name, start date, list of values)."""
    parts = line.strip().split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"Expected name:start:values, got {line.strip()[:40]!r}")
    name, start, values = parts
    return name, start.split(" ")[0], [parse_value(text) for text in values.split(",")]


def read_series(path: str | Path) -> Iterator[tuple[str, str, list[float | None]]]:
    """Yield (name, start, values) for every series of a .tsf file."""
    in_data = False
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if in_data:
                yield parse_series_line(line)
            elif line.lower() == "@data":
                in_data = True


def demand_stats(values: Values) -> Stats:
    """Summarise one series: known months, missing months, total, zero share, ADI."""
    known = [value for value in values if value is not None]
    demand = [value for value in known if value > 0]
    return {
        "months": len(known),
        "missing": len(values) - len(known),
        "total": sum(known),
        "zero_share": (len(known) - len(demand)) / len(known) if known else None,
        "adi": len(known) / len(demand) if demand else None,
    }


def top_series(stats: Mapping[str, Stats], key: str, n: int) -> list[tuple[str, float]]:
    """Return the n (name, value) pairs with the largest `key`, ties by name."""
    rows = [
        (name, value)
        for name, row in stats.items()
        if (value := row.get(key)) is not None
    ]
    return sorted(rows, key=lambda row: (-row[1], row[0]))[:n]


def save_summary(stats: Mapping[str, Stats], path: str | Path) -> Path:
    """Write the statistics as sorted, indented JSON and return the file path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stats, indent=2, sort_keys=True), encoding="utf-8")
    return path


# --- STUB
#| # 02.1: paste your six functions from lab 01 here and give them type hints.
# <<< SOLUTION


def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Print how long each call of `func` took, then return its result.

    The line reads ``<function name>: <seconds> s``. It is printed even when
    the call raises.
    """

    # >>> SOLUTION 02.2
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__}: {time.perf_counter() - start:.3f} s")

    return wrapper
    # <<< SOLUTION


def requires_history(min_months: int) -> Callable[[Statistic], Statistic]:
    """Make a statistic return None for series with fewer than `min_months` known.

    Raises:
        ValueError: `min_months` is below 1. This happens when the decorator
            is applied, not when the statistic is called.
    """
    # >>> SOLUTION 02.3
    if min_months < 1:
        raise ValueError(f"min_months must be at least 1, got {min_months}")

    def decorator(statistic: Statistic) -> Statistic:
        @functools.wraps(statistic)
        def wrapper(values: Values) -> float | None:
            known = sum(value is not None for value in values)
            if known < min_months:
                return None
            return statistic(values)

        return wrapper

    return decorator
    # <<< SOLUTION


STATISTICS: dict[str, Statistic] = {}


def register(name: str) -> Callable[[Statistic], Statistic]:
    """Add a statistic to STATISTICS under `name` and return it unchanged.

    Raises:
        ValueError: Another statistic already uses `name`.
    """

    # >>> SOLUTION 02.4
    def decorator(statistic: Statistic) -> Statistic:
        if name in STATISTICS:
            raise ValueError(f"A statistic named {name!r} is already registered")
        STATISTICS[name] = statistic
        return statistic

    return decorator
    # <<< SOLUTION


# >>> SOLUTION 02.4
@register("months")
def known_months(values: Values) -> float | None:
    """Number of months with a known value."""
    return sum(value is not None for value in values)


@register("missing")
def missing_months(values: Values) -> float | None:
    """Number of months without a value."""
    return sum(value is None for value in values)


@register("total")
def total(values: Values) -> float | None:
    """Sum of the known values."""
    return sum(value for value in values if value is not None)


@register("zero_share")
def zero_share(values: Values) -> float | None:
    """Share of known months with zero demand; None without known months."""
    known = [value for value in values if value is not None]
    return sum(value == 0 for value in known) / len(known) if known else None


@register("adi")
def adi(values: Values) -> float | None:
    """Average demand interval; None when there was no demand."""
    known = [value for value in values if value is not None]
    demand = sum(value > 0 for value in known)
    return len(known) / demand if demand else None


@register("cv2")
@requires_history(12)
def cv2(values: Values) -> float | None:
    """Squared coefficient of variation of the non-zero demand sizes."""
    sizes = [value for value in values if value is not None and value > 0]
    if len(sizes) < 2:
        return None
    mean = sum(sizes) / len(sizes)
    variance = sum((size - mean) ** 2 for size in sizes) / len(sizes)
    return variance / mean**2


# --- STUB
#| # 02.4: register the statistics here: months, missing, total, zero_share,
#| # adi and cv2.
# <<< SOLUTION


def summarise(values: Values, names: Sequence[str] | None = None) -> Stats:
    """Compute the registered statistics `names` (all when None) for one series.

    Raises:
        ValueError: A name is not registered. The message lists the known ones.
    """
    # >>> SOLUTION 02.4
    names = list(STATISTICS) if names is None else names
    unknown = [name for name in names if name not in STATISTICS]
    if unknown:
        raise ValueError(f"Unknown statistics {unknown}; known: {sorted(STATISTICS)}")
    return {name: STATISTICS[name](values) for name in names}
    # <<< SOLUTION


def at_least(key: str, threshold: float) -> Callable[[Stats], bool]:
    """Return a test that passes when a series' `key` is known and >= `threshold`."""

    # >>> SOLUTION 02.5
    def passes(stats: Stats) -> bool:
        value = stats.get(key)
        return value is not None and value >= threshold

    return passes
    # <<< SOLUTION


def select(stats: Mapping[str, Stats], *tests: Callable[[Stats], bool]) -> list[str]:
    """Return the sorted names of the series that pass every test."""
    # >>> SOLUTION 02.5
    return sorted(name for name, row in stats.items() if all(t(row) for t in tests))
    # <<< SOLUTION
