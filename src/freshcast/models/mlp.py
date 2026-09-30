"""A small multilayer perceptron (MLP) in PyTorch, trained on the CPU.

The network, the training loop and the wrapper that plugs it into the panel
interface are written out in plain PyTorch. Nothing here needs a GPU: the
same loop moves to one in module 18.
"""

import copy
from collections.abc import Sequence
from typing import Self

import numpy as np
import pandas as pd
import torch
from numpy.typing import NDArray
from torch import Tensor, nn
from torch.utils.data import DataLoader, TensorDataset

from freshcast.models.panel import PanelForecaster
from freshcast.split import last_days_start, split_by_date

FloatArray = NDArray[np.float64]


class TabularMLP(nn.Module):
    """Fully connected network: a row of numbers in, one forecast out.

    Args:
        n_inputs: Number of input columns, at least 1.
        hidden: Width of every hidden layer, in order. Each hidden layer is a
            linear layer followed by a ReLU. An empty sequence gives no
            hidden layer, which is plain linear regression.

    Raises:
        ValueError: ``n_inputs`` is below 1 or some hidden width is.
    """

    def __init__(self, n_inputs: int, hidden: Sequence[int] = (64, 32)) -> None:
        # >>> SOLUTION 13.5
        if n_inputs < 1 or any(width < 1 for width in hidden):
            raise ValueError(f"Sizes must be at least 1: {n_inputs}, {list(hidden)}.")
        super().__init__()
        layers: list[nn.Module] = []
        width_in = n_inputs
        for width in hidden:
            layers.append(nn.Linear(width_in, width))
            layers.append(nn.ReLU())
            width_in = width
        layers.append(nn.Linear(width_in, 1))
        self.layers = nn.Sequential(*layers)
        # <<< SOLUTION

    def forward(self, x: Tensor) -> Tensor:
        """Forecast every row of ``x``.

        Args:
            x: Float tensor of shape ``(n, n_inputs)``.

        Returns:
            Tensor of shape ``(n,)``: one number per row, not ``(n, 1)``.
        """
        # >>> SOLUTION 13.5
        forecast: Tensor = self.layers(x).squeeze(-1)
        return forecast
        # <<< SOLUTION


def train_mlp(
    X_train: FloatArray,
    y_train: FloatArray,
    X_valid: FloatArray,
    y_valid: FloatArray,
    *,
    hidden: Sequence[int] = (64, 32),
    epochs: int = 100,
    batch_size: int = 256,
    learning_rate: float = 3e-3,
    patience: int = 10,
    seed: int = 0,
) -> tuple[TabularMLP, pd.DataFrame]:
    """Train a ``TabularMLP`` with mini-batches and early stopping.

    Every epoch shows the network the training rows once, in a new random
    order and in batches of ``batch_size``, and takes one Adam step on the
    mean squared error of each batch. After the epoch the loss on the
    validation rows is measured. Training stops when that loss has not
    improved for ``patience`` epochs in a row, or after ``epochs`` epochs.

    The seed fixes the initial weights and the order of the batches, so the
    same arguments always give the same network. It seeds PyTorch's global
    random generator.

    Args:
        X_train: Scaled inputs, shape ``(n, m)``, no NaN.
        y_train: Targets, shape ``(n,)``.
        X_valid: Validation inputs, shape ``(v, m)``. Used only to decide when
            to stop and which epoch to keep, never for a gradient step.
        y_valid: Validation targets, shape ``(v,)``.
        hidden: Widths of the hidden layers.
        epochs: Upper limit on the number of epochs, at least 1.
        batch_size: Rows per mini-batch, at least 1.
        learning_rate: Step size of Adam, above 0.
        patience: Epochs without a better validation loss before stopping,
            at least 1.
        seed: Seed for the initial weights and the batch order.

    Returns:
        ``(model, history)``. ``model`` holds the weights of the epoch with
        the lowest validation loss, not of the last epoch. ``history`` has
        one row per epoch that ran and the columns ``train_loss`` (mean over
        the batches of the epoch, while the weights were changing) and
        ``valid_loss``.

    Raises:
        ValueError: A number above is out of its range, ``X`` is not two-
            dimensional or ``y`` not one-dimensional, the row counts of an
            ``X`` and its ``y`` differ, the training or validation rows are
            empty, or any array holds NaN or infinite values.
    """
    # >>> SOLUTION 13.6
    if epochs < 1 or batch_size < 1 or patience < 1 or learning_rate <= 0:
        raise ValueError(
            "epochs, batch_size and patience must be at least 1 and "
            "learning_rate above 0."
        )
    for name, inputs, targets in [
        ("train", X_train, y_train),
        ("valid", X_valid, y_valid),
    ]:
        if inputs.ndim != 2 or targets.ndim != 1 or len(inputs) != len(targets):
            raise ValueError(
                f"{name}: X has shape {inputs.shape} and y has shape {targets.shape}."
            )
        if len(inputs) == 0:
            raise ValueError(f"{name}: there are no rows.")
        bad = int((~np.isfinite(inputs)).sum() + (~np.isfinite(targets)).sum())
        if bad:
            raise ValueError(f"{name}: {bad} values are NaN or infinite.")

    torch.manual_seed(seed)
    model = TabularMLP(X_train.shape[1], hidden)

    # torch.tensor copies, so the caller's arrays are never touched. PyTorch
    # layers work in float32; a float64 tensor would be an error.
    train_x = torch.tensor(X_train, dtype=torch.float32)
    train_y = torch.tensor(y_train, dtype=torch.float32)
    valid_x = torch.tensor(X_valid, dtype=torch.float32)
    valid_y = torch.tensor(y_valid, dtype=torch.float32)
    batches = DataLoader(
        TensorDataset(train_x, train_y), batch_size=batch_size, shuffle=True
    )
    loss_function = nn.MSELoss()
    optimiser = torch.optim.Adam(model.parameters(), lr=learning_rate)

    history = []
    best_loss = float("inf")
    best_weights = copy.deepcopy(model.state_dict())
    epochs_without_gain = 0
    for _ in range(epochs):
        model.train()
        loss_sum = 0.0
        for batch_x, batch_y in batches:
            optimiser.zero_grad()
            loss = loss_function(model(batch_x), batch_y)
            loss.backward()
            optimiser.step()
            # The last batch may be smaller, so weight by its size.
            loss_sum += loss.item() * len(batch_x)

        model.eval()
        with torch.no_grad():
            valid_loss = loss_function(model(valid_x), valid_y).item()
        history.append(
            {"train_loss": loss_sum / len(train_x), "valid_loss": valid_loss}
        )

        if valid_loss < best_loss:
            best_loss = valid_loss
            best_weights = copy.deepcopy(model.state_dict())
            epochs_without_gain = 0
        else:
            epochs_without_gain += 1
            if epochs_without_gain >= patience:
                break

    model.load_state_dict(best_weights)
    model.eval()
    return model, pd.DataFrame(history)
    # <<< SOLUTION


class MLPForecaster(PanelForecaster):
    """The MLP as a panel forecaster: scaling, missing values, early stopping.

    ``fit`` holds out the last ``valid_days`` days of the training rows to
    decide when to stop, so the network never trains on them, and it scales
    the inputs with statistics of the remaining training rows only.

    A missing feature value is replaced by the training mean of its column
    (zero after scaling) and flagged by an extra 0/1 input, so the network
    can tell "unknown" from "average". Only the columns that had a missing
    value in the training rows get a flag. A missing value in any other
    column, at ``fit`` or at ``predict``, is an error: the network has never
    seen one there.

    Args:
        features: Names of the numeric feature columns.
        hidden: Widths of the hidden layers.
        epochs: Upper limit on the number of epochs.
        batch_size: Rows per mini-batch.
        learning_rate: Step size of Adam.
        patience: Epochs without a better validation loss before stopping.
        valid_days: Length in days of the held-out final stretch.
        seed: Seed for the initial weights and the batch order.

    Attributes:
        history_: The loss history returned by ``train_mlp`` in the last
            ``fit``, None before the first one.
    """

    def __init__(
        self,
        features: Sequence[str],
        hidden: Sequence[int] = (64, 32),
        *,
        epochs: int = 100,
        batch_size: int = 256,
        learning_rate: float = 3e-3,
        patience: int = 10,
        valid_days: int = 7,
        seed: int = 0,
    ) -> None:
        # >>> SOLUTION 13.7
        self.features = list(features)
        self.hidden = list(hidden)
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.patience = patience
        self.valid_days = valid_days
        self.seed = seed
        self._mean: FloatArray | None = None
        self._scale: FloatArray | None = None
        self._flagged: NDArray[np.intp] = np.empty(0, dtype=np.intp)
        self._model: TabularMLP | None = None
        self.history_: pd.DataFrame | None = None
        # <<< SOLUTION

    def _inputs(self, X: pd.DataFrame) -> FloatArray:
        """Return the scaled network inputs of the rows of ``X``.

        Raises:
            RuntimeError: The statistics are not fitted yet.
            ValueError: ``X`` holds an infinite value, or a missing value in
                a column that had none in training.
        """
        # >>> SOLUTION 13.7
        if self._mean is None or self._scale is None:
            raise RuntimeError("Call fit first.")
        values = X[self.features].to_numpy(dtype=np.float64)
        infinite = int(np.isinf(values).sum())
        if infinite:
            raise ValueError(f"{infinite} infinite values in the feature columns.")
        missing = np.isnan(values)
        surprise = missing.copy()
        surprise[:, self._flagged] = False
        if surprise.any():
            columns = [self.features[i] for i in np.flatnonzero(surprise.any(axis=0))]
            raise ValueError(
                f"{int(surprise.sum())} missing values in columns {columns}, "
                "which had none in training."
            )
        scaled = (values - self._mean) / self._scale
        scaled[missing] = 0.0
        flags = missing[:, self._flagged].astype(np.float64)
        return np.hstack([scaled, flags])
        # <<< SOLUTION

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Self:
        """Scale the inputs and train the network with early stopping.

        Args:
            X: Training rows with the date and the feature columns.
            y: Their targets.

        Raises:
            ValueError: A feature column is all missing in the rows the
                network trains on, a feature holds an infinite value, or
                ``valid_days`` is below 1 or not shorter than the span of
                the dates in ``X``.
        """
        # >>> SOLUTION 13.7
        cutoff = last_days_start(X, self.valid_days)
        train, valid = split_by_date(X, cutoff)

        values = train[self.features].to_numpy(dtype=np.float64)
        all_missing = np.isnan(values).all(axis=0)
        empty = [
            name for name, gone in zip(self.features, all_missing, strict=True) if gone
        ]
        if empty:
            raise ValueError(f"No training row has a value for {empty}.")
        # Statistics from the training rows only, ignoring missing values.
        self._mean = np.nanmean(values, axis=0)
        spread = np.nanstd(values, axis=0)
        # A constant column has no spread. Dividing by 1 keeps it at zero.
        self._scale = np.where(spread > 0, spread, 1.0)
        self._flagged = np.flatnonzero(np.isnan(values).any(axis=0))

        self._model, self.history_ = train_mlp(
            self._inputs(train),
            y.loc[train.index].to_numpy(dtype=np.float64),
            self._inputs(valid),
            y.loc[valid.index].to_numpy(dtype=np.float64),
            hidden=self.hidden,
            epochs=self.epochs,
            batch_size=self.batch_size,
            learning_rate=self.learning_rate,
            patience=self.patience,
            seed=self.seed,
        )
        return self
        # <<< SOLUTION

    def predict(self, X: pd.DataFrame) -> FloatArray:
        """Forecast every row of ``X``, with negative outputs raised to zero.

        Raises:
            RuntimeError: ``fit`` has not been called.
            ValueError: A column that had no missing value in training has
                one in ``X``.
        """
        # >>> SOLUTION 13.7
        if self._model is None:
            raise RuntimeError("Call fit first.")
        inputs = torch.tensor(self._inputs(X), dtype=torch.float32)
        with torch.no_grad():
            raw = self._model(inputs).numpy().astype(np.float64)
        clipped: FloatArray = np.clip(raw, 0.0, None)
        return clipped
        # <<< SOLUTION
