def mean_known(values: list[float | None]) -> float:
    """Return the mean of known non-negative values as a float.

    - Known values are the numbers in the list; None marks a missing value.
    - Include zeros.
    - Raise ValueError("no known values") for an empty list or only None.
    - Leave the input unchanged.
    """
    known = []
    for value in values:
        if value is not None and value >= 0:
            known.append(value)
    if len(values) == 0 or len(known) == 0:
        raise ValueError("no known values")
    else:
        return sum(known) / len(known)
    # Replace this placeholder with your implementation.
