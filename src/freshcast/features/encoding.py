"""Target encoding: replacing a category with the mean target of its group."""

from collections.abc import Sequence
from typing import Self

import pandas as pd


class TargetEncoder:
    """Encodes groups of rows by their mean target, learned from training data.

    The encoder has state: the group means. That state must come from the
    training rows only. Fitting it on rows the model is later scored on puts
    their targets into a feature.

    Args:
        columns: Columns whose combination defines a group.
        smoothing: Weight of the overall mean, in rows. A group with ``n``
            rows is encoded as
            ``(n * group_mean + smoothing * overall_mean) / (n + smoothing)``,
            so small groups are pulled toward the overall mean. 0 turns it off.

    Raises:
        ValueError: ``columns`` is empty or ``smoothing`` is negative.
    """

    def __init__(self, columns: Sequence[str], smoothing: float = 0.0) -> None:
        # >>> SOLUTION 09.4
        if not columns:
            raise ValueError("At least one column is needed to define groups.")
        if smoothing < 0:
            raise ValueError(f"smoothing must not be negative, got {smoothing}.")
        self.columns = list(columns)
        self.smoothing = smoothing
        self._encoding: pd.DataFrame | None = None
        self._overall = float("nan")
        # <<< SOLUTION

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Self:
        """Learn the mean target of every group in ``X``."""
        # >>> SOLUTION 09.4
        self._overall = float(y.mean())
        stats = (
            X[self.columns]
            .assign(target=y.to_numpy())
            .groupby(self.columns, as_index=False)
            .agg(total=("target", "sum"), rows=("target", "size"))
        )
        smoothed = (stats["total"] + self.smoothing * self._overall) / (
            stats["rows"] + self.smoothing
        )
        self._encoding = stats[self.columns].assign(encoded=smoothed)
        return self
        # <<< SOLUTION

    def transform(self, X: pd.DataFrame) -> pd.Series:
        """Return the learned mean for every row of ``X``.

        Groups that ``fit`` has not seen get the overall training mean.

        Returns:
            A Series aligned with ``X``, named after the columns joined by
            underscores plus ``_target_mean``.

        Raises:
            RuntimeError: ``fit`` has not been called.
        """
        # >>> SOLUTION 09.4
        if self._encoding is None:
            raise RuntimeError("Call fit before transform.")
        merged = X[self.columns].merge(
            self._encoding, on=self.columns, how="left", validate="many_to_one"
        )
        name = "_".join(self.columns) + "_target_mean"
        encoded = merged["encoded"].fillna(self._overall)  # unseen groups
        return pd.Series(encoded.to_numpy(), index=X.index, name=name)
        # <<< SOLUTION
