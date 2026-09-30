"""Choosing where tensors live, and making runs repeatable."""

import logging
import random

import numpy as np
import torch

logger = logging.getLogger(__name__)


def pick_device(prefer_gpu: bool = True) -> torch.device:
    """Return the CUDA device when one is usable and wanted, else the CPU.

    The choice is logged, so a run that silently fell back to the CPU is
    visible in the output instead of just being slow.
    """
    # >>> SOLUTION 18.1
    if prefer_gpu and torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info("Using GPU: %s", torch.cuda.get_device_name(device))
    else:
        device = torch.device("cpu")
        logger.info("Using CPU")
    return device
    # <<< SOLUTION


def seed_everything(seed: int) -> None:
    """Seed Python, NumPy and PyTorch (CPU and every GPU).

    Seeds make runs repeatable on the same machine. Some GPU kernels are
    not deterministic, so two GPU runs can still differ in the last digits.
    """
    # >>> SOLUTION 18.1
    random.seed(seed)
    np.random.seed(seed)  # noqa: NPY002 - seeds the legacy global generator
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # <<< SOLUTION
