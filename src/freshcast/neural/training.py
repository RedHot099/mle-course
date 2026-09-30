"""A training loop for the window model, written out in plain PyTorch."""

import copy
import logging
import time
from dataclasses import dataclass, field

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

from freshcast.neural.windows import WindowDataset, pass_through

logger = logging.getLogger(__name__)


@dataclass
class TrainingLog:
    """What happened during training, epoch by epoch."""

    train_loss: list[float] = field(default_factory=list)
    valid_loss: list[float] = field(default_factory=list)
    seconds: list[float] = field(default_factory=list)
    best_epoch: int = -1


def masked_mae(
    forecast: torch.Tensor, target: torch.Tensor, in_stock: torch.Tensor
) -> torch.Tensor:
    """Mean absolute error over the forecast days that had no stockout.

    Days with a stockout have sales capped by supply; scoring the model on
    them would teach it to forecast shortages instead of demand.

    Raises:
        ValueError: No day in the batch is in stock.
    """
    # >>> SOLUTION 18.5
    weights = in_stock * torch.isfinite(target)
    days = weights.sum()
    if days == 0:
        raise ValueError("No in-stock day in the batch to compute the loss on.")
    errors = (forecast - torch.nan_to_num(target)).abs() * weights
    return errors.sum() / days
    # <<< SOLUTION


def loader(dataset: WindowDataset, batch_size: int, *, shuffle: bool) -> DataLoader:
    """Return a DataLoader that asks the dataset for whole batches at once."""
    return DataLoader(
        dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=pass_through
    )


def _forecast(
    net: nn.Module,
    batch: dict[str, torch.Tensor],
    codes: tuple[torch.Tensor, torch.Tensor],
    device: torch.device,
) -> torch.Tensor:
    """Run the network on a batch and return forecasts in original units."""
    series = batch["series"].to(device)
    scaled = net(
        batch["past"].to(device),
        batch["future"].to(device),
        codes[0][series],
        codes[1][series],
    )
    forecast: torch.Tensor = scaled.float() * batch["scale"].to(device)[:, None]
    return forecast


def fit_windows(
    net: nn.Module,
    train: WindowDataset,
    valid: WindowDataset | None,
    codes: tuple[torch.Tensor, torch.Tensor],
    *,
    device: torch.device,
    epochs: int = 15,
    batch_size: int = 1024,
    learning_rate: float = 2e-3,
    patience: int = 3,
) -> TrainingLog:
    """Train with AdamW, mixed precision on GPU, and early stopping.

    After every epoch the loss on ``valid`` is computed without gradients.
    When it has not improved for ``patience`` epochs, training stops and the
    weights of the best epoch are put back into ``net``. Without ``valid``
    all ``epochs`` run and the last weights are kept.

    Args:
        net: The model, already on ``device``.
        train: Training windows.
        valid: Validation windows, later in time than every training window,
            or None to train for exactly ``epochs`` epochs.
        codes: Store and product code of every series in the cube, as
            tensors on ``device``, indexed by series position.
        device: Where to compute.
        epochs: Upper limit of passes over the training windows.
        batch_size: Windows per step.
        learning_rate: Peak learning rate of the one-cycle schedule.
        patience: Epochs without improvement before stopping.

    Returns:
        Losses and times per epoch, and the index of the best epoch.
    """
    # >>> SOLUTION 18.5
    use_amp = device.type == "cuda"
    batches = loader(train, batch_size, shuffle=True)
    optimiser = torch.optim.AdamW(net.parameters(), lr=learning_rate)
    schedule = torch.optim.lr_scheduler.OneCycleLR(
        optimiser, max_lr=learning_rate, total_steps=epochs * len(batches)
    )
    scaler = torch.amp.GradScaler(enabled=use_amp)
    log = TrainingLog()
    best_loss, best_state, waited = np.inf, copy.deepcopy(net.state_dict()), 0

    for epoch in range(epochs):
        started = time.perf_counter()
        net.train()
        losses = []
        for batch in batches:
            with torch.autocast(device_type=device.type, enabled=use_amp):
                forecast = _forecast(net, batch, codes, device)
            loss = masked_mae(
                forecast, batch["target"].to(device), batch["in_stock"].to(device)
            )
            optimiser.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(optimiser)
            scaler.update()
            schedule.step()
            losses.append(loss.item())

        log.train_loss.append(float(np.mean(losses)))
        log.seconds.append(time.perf_counter() - started)
        if valid is None:
            log.best_epoch = epoch
            logger.info("Epoch %d: train %.4f", epoch, log.train_loss[-1])
            continue
        valid_loss = evaluate_windows(net, valid, codes, device=device)
        log.valid_loss.append(valid_loss)
        logger.info(
            "Epoch %d: train %.4f, valid %.4f", epoch, log.train_loss[-1], valid_loss
        )
        if valid_loss < best_loss:
            best_loss, best_state, waited = (
                valid_loss,
                copy.deepcopy(net.state_dict()),
                0,
            )
            log.best_epoch = epoch
        else:
            waited += 1
            if waited >= patience:
                break

    if valid is not None:
        net.load_state_dict(best_state)
    return log
    # <<< SOLUTION


def evaluate_windows(
    net: nn.Module,
    windows: WindowDataset,
    codes: tuple[torch.Tensor, torch.Tensor],
    *,
    device: torch.device,
    batch_size: int = 8192,
) -> float:
    """Return the masked MAE of ``net`` on ``windows``, without gradients."""
    # >>> SOLUTION 18.5
    net.eval()
    total, days = 0.0, 0.0
    with torch.no_grad():
        for batch in loader(windows, batch_size, shuffle=False):
            forecast = _forecast(net, batch, codes, device)
            in_stock = batch["in_stock"].to(device)
            weights = in_stock * torch.isfinite(batch["target"].to(device))
            errors = (forecast - torch.nan_to_num(batch["target"].to(device))).abs()
            total += float((errors * weights).sum())
            days += float(weights.sum())
    return total / max(days, 1.0)
    # <<< SOLUTION


def predict_windows(
    net: nn.Module,
    windows: WindowDataset,
    codes: tuple[torch.Tensor, torch.Tensor],
    *,
    device: torch.device,
    batch_size: int = 8192,
) -> np.ndarray:
    """Return forecasts of shape ``(windows, horizon)``, never below zero."""
    # >>> SOLUTION 18.5
    net.eval()
    parts = []
    with torch.no_grad():
        for batch in loader(windows, batch_size, shuffle=False):
            forecast = _forecast(net, batch, codes, device).clamp_min(0.0)
            parts.append(forecast.cpu().numpy())
    return np.concatenate(parts)
    # <<< SOLUTION
