import pytest
from summary import mean_known


def test_includes_zero() -> None:
    # Use mean_known with a small input and an independent expected value.
    values = [0, 5, 3, 0]
    assert mean_known(values) == 2


def test_empty_input() -> None:
    values = []

    with pytest.raises(ValueError, match="no known"):
        mean_known(values)


def test_only_missing() -> None:
    values = [None, None]

    with pytest.raises(ValueError, match="no known"):
        mean_known(values)


def test_fractional_result() -> None:
    values = [1, 2]

    assert mean_known(values) == pytest.approx(1.5)


def test_preserves_input() -> None:
    values = [None, 0, 5, 3]
    original = values.copy()

    mean_known(values)

    assert values == original
