"""One classifier interface over two very different models."""

from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Any, Literal, Self

import lightgbm as lgb
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from freshcast.classify.metrics import binary_array

FloatArray = NDArray[np.float64]

# Regularisation of the linear model is left at scikit-learn's default, C=1.
MAX_LOGISTIC_ITERATIONS = 1000

DEFAULT_LIGHTGBM_PARAMS: dict[str, Any] = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "num_leaves": 15,
    "min_child_samples": 20,
    "random_state": 0,
    "verbose": -1,
}


class ModelKind(StrEnum):
    """The models ``StockoutClassifier`` can wrap."""

    LOGISTIC = "logistic"
    LIGHTGBM = "lightgbm"


class StockoutClassifier:
    """Predicts the probability of the positive class with one of two models.

    Args:
        features: Names of the feature columns. They may hold NaN.
        kind: ``"logistic"`` is scaling plus logistic regression, with missing
            values replaced by the training median and an indicator column for
            every feature that had any. ``"lightgbm"`` is a boosted-trees
            classifier that takes missing values as they are.
        class_weight: None counts every row equally. ``"balanced"`` makes a
            row of the rare class weigh as much in total as all rows of the
            common one, which raises the predicted probabilities: they stop
            being frequencies.
        params: Model parameters that override the defaults: ``C`` and the like
            for the logistic regression, ``DEFAULT_LIGHTGBM_PARAMS`` entries for
            LightGBM.

    Raises:
        ValueError: ``kind`` is not one of ``ModelKind``, or ``features`` is
            empty.
    """

    def __init__(
        self,
        features: Sequence[str],
        kind: ModelKind | str = ModelKind.LOGISTIC,
        *,
        class_weight: Literal["balanced"] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> None:
        if not features:
            raise ValueError("At least one feature is needed.")
        self.features = list(features)
        self.kind = ModelKind(kind)
        self.class_weight = class_weight
        self.params = dict(params or {})
        self._model: Any = None

    def _make_model(self) -> Any:
        """Return a new, unfitted scikit-learn model of the chosen kind."""
        # >>> SOLUTION 12.7
        if self.kind is ModelKind.LIGHTGBM:
            # Trees split on thresholds, so they need neither scaling nor a
            # stand-in for NaN: LightGBM sends missing values down the branch
            # that fits the training rows best.
            params = {**DEFAULT_LIGHTGBM_PARAMS, **self.params}
            return lgb.LGBMClassifier(class_weight=self.class_weight, **params)
        # A linear model cannot read NaN. The median of the training rows
        # stands in, and the indicator columns say which rows were filled,
        # because "no history yet" is information in itself. Both steps are
        # fitted inside the pipeline, so only on the rows passed to ``fit``.
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True),
            StandardScaler(),
            LogisticRegression(
                class_weight=self.class_weight,
                max_iter=MAX_LOGISTIC_ITERATIONS,
                **self.params,
            ),
        )
        # <<< SOLUTION

    def _columns(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return the feature columns of ``X``.

        Raises:
            ValueError: A feature column is missing.
        """
        # >>> SOLUTION 12.7
        missing = [name for name in self.features if name not in X.columns]
        if missing:
            raise ValueError(f"Feature columns missing from X: {missing}.")
        return X[self.features]
        # <<< SOLUTION

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Self:
        """Train on the rows of ``X`` and their labels ``y``.

        Args:
            X: Training rows. Only the feature columns are used.
            y: Labels of the same rows, 0 or 1, none missing.

        Raises:
            ValueError: A feature column is missing, a label is NaN or not 0
                or 1, ``X`` and ``y`` differ in length, or ``y`` holds only one
                class.
        """
        # >>> SOLUTION 12.7
        labels = binary_array("y", y)
        features = self._columns(X)
        if len(labels) != len(features):
            raise ValueError(f"X has {len(features)} rows, y has {len(labels)}.")
        if labels.min() == labels.max():
            raise ValueError(f"y holds only the class {labels[0]}.")
        self._model = self._make_model().fit(features, labels)
        return self
        # <<< SOLUTION

    def predict_proba(self, X: pd.DataFrame) -> FloatArray:
        """Return the probability of the positive class for every row of ``X``.

        Whatever was learned in ``fit`` (medians, scale, trees) is applied as
        it is. Nothing is re-estimated on ``X``, so a row gets the same
        probability alone and in a batch.

        Returns:
            A one-dimensional array of numbers in [0, 1], in the order of ``X``.

        Raises:
            RuntimeError: ``fit`` has not been called.
            ValueError: A feature column is missing.
        """
        # >>> SOLUTION 12.7
        if self._model is None:
            raise RuntimeError("Call fit before predict_proba.")
        positive: FloatArray = self._model.predict_proba(self._columns(X))[:, 1]
        return positive
        # <<< SOLUTION
