"""The same training, handed to PyTorch Lightning.

``fit_windows`` spells out every step: device moves, mixed precision,
early stopping, keeping the best weights. Lightning does those steps for
you once you describe three things: what a training step computes, what a
validation step computes, and which optimiser to use.
"""

from pathlib import Path
from typing import Any

import lightning as L
import torch
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint
from torch import nn

from freshcast.neural.training import loader, masked_mae
from freshcast.neural.windows import WindowDataset


class WindowModule(L.LightningModule):
    """Wraps a window network with its loss and optimiser.

    Args:
        net: A network with the signature of ``GRUForecastNet.forward``.
        codes: Store and product code of every series, indexed by series
            position. Registered as buffers, so Lightning moves them to the
            same device as the network.
        learning_rate: Peak learning rate of the one-cycle schedule.
    """

    net: nn.Module
    learning_rate: float
    stores: torch.Tensor
    products: torch.Tensor

    def __init__(
        self,
        net: nn.Module,
        codes: tuple[torch.Tensor, torch.Tensor],
        learning_rate: float = 2e-3,
    ) -> None:
        # >>> SOLUTION 18.7
        super().__init__()
        self.net = net
        self.learning_rate = learning_rate
        self.register_buffer("stores", codes[0])
        self.register_buffer("products", codes[1])
        # <<< SOLUTION

    def _forecast(self, batch: dict[str, torch.Tensor]) -> torch.Tensor:
        series = batch["series"]
        scaled = self.net(
            batch["past"], batch["future"], self.stores[series], self.products[series]
        )
        forecast: torch.Tensor = scaled.float() * batch["scale"][:, None]
        return forecast

    def training_step(self, batch: dict[str, torch.Tensor], _: int) -> torch.Tensor:
        """Return the loss of one batch; Lightning runs the backward pass."""
        # >>> SOLUTION 18.7
        loss = masked_mae(self._forecast(batch), batch["target"], batch["in_stock"])
        self.log("train_loss", loss, prog_bar=True)
        return loss
        # <<< SOLUTION

    def validation_step(self, batch: dict[str, torch.Tensor], _: int) -> None:
        """Log the loss of one validation batch, weighted by its in-stock days."""
        # >>> SOLUTION 18.7
        loss = masked_mae(self._forecast(batch), batch["target"], batch["in_stock"])
        days = int(batch["in_stock"].sum())
        self.log("valid_loss", loss, batch_size=days, prog_bar=True)
        # <<< SOLUTION

    def configure_optimizers(self) -> Any:
        """AdamW with a one-cycle schedule stepped after every batch."""
        # >>> SOLUTION 18.7
        optimiser = torch.optim.AdamW(self.parameters(), lr=self.learning_rate)
        schedule = torch.optim.lr_scheduler.OneCycleLR(
            optimiser,
            max_lr=self.learning_rate,
            total_steps=int(self.trainer.estimated_stepping_batches),
        )
        return {
            "optimizer": optimiser,
            "lr_scheduler": {"scheduler": schedule, "interval": "step"},
        }
        # <<< SOLUTION


def fit_with_lightning(
    module: WindowModule,
    train: WindowDataset,
    valid: WindowDataset,
    *,
    checkpoint_dir: Path,
    max_epochs: int = 15,
    batch_size: int = 1024,
    patience: int = 3,
) -> tuple[WindowModule, float]:
    """Train with early stopping and keep the checkpoint of the best epoch.

    Mixed precision is used on a GPU and plain 32-bit floats on the CPU.

    Returns:
        The module with the best weights loaded, and its validation loss.
    """
    # >>> SOLUTION 18.7
    on_gpu = torch.cuda.is_available()
    if on_gpu:
        # Let matrix products use tensor cores; the loss does not need more.
        torch.set_float32_matmul_precision("high")
    best = ModelCheckpoint(dirpath=checkpoint_dir, monitor="valid_loss", save_top_k=1)
    trainer = L.Trainer(
        accelerator="auto",
        devices=1,
        precision="16-mixed" if on_gpu else "32-true",
        max_epochs=max_epochs,
        callbacks=[EarlyStopping(monitor="valid_loss", patience=patience), best],
        logger=False,
        enable_progress_bar=False,
        enable_model_summary=False,
    )
    trainer.fit(
        module,
        loader(train, batch_size, shuffle=True),
        loader(valid, 8192, shuffle=False),
    )
    state = torch.load(best.best_model_path, weights_only=True)["state_dict"]
    module.load_state_dict(state)
    if best.best_model_score is None:
        raise RuntimeError("Training ended before any validation score was logged.")
    return module, float(best.best_model_score)
    # <<< SOLUTION
