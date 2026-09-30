"""Saving a trained model together with everything needed to trust it later."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib

from freshcast.models.panel import PanelForecaster

MODEL_FILE = "model.joblib"
METADATA_FILE = "metadata.json"


def model_signature(name: str, moment: datetime) -> str:
    """Return the directory name of a saved model: ``<name>_<YYYYmmdd-HHMMSS>``."""
    # >>> SOLUTION 14.2
    return f"{name}_{moment:%Y%m%d-%H%M%S}"
    # <<< SOLUTION


def save_model(
    model: PanelForecaster,
    directory: Path,
    name: str,
    metadata: dict[str, Any],
    *,
    moment: datetime | None = None,
) -> Path:
    """Write the model and its metadata to a new, uniquely named directory.

    Args:
        model: A fitted forecaster.
        directory: Parent directory of all saved models.
        name: What the model is, for example ``lightgbm``.
        metadata: Facts about the run: features, parameters, training
            period, scores. Must be JSON-serialisable.
        moment: Time stamp of the run. Defaults to now.

    Returns:
        The directory that was created: ``directory/<signature>``.

    Raises:
        FileExistsError: A model with the same signature already exists.
            Saved models are never overwritten.
    """
    # >>> SOLUTION 14.2
    signature = model_signature(name, moment or datetime.now())
    target = directory / signature
    target.mkdir(parents=True, exist_ok=False)
    joblib.dump(model, target / MODEL_FILE)
    document = {"signature": signature, "name": name, **metadata}
    (target / METADATA_FILE).write_text(
        json.dumps(document, indent=2, default=str) + "\n", encoding="utf-8"
    )
    return target
    # <<< SOLUTION


def load_model(model_dir: Path) -> tuple[PanelForecaster, dict[str, Any]]:
    """Read a saved model and its metadata.

    Only load models you saved yourself: ``joblib`` files can run arbitrary
    code when opened.

    Raises:
        FileNotFoundError: The directory lacks the model or the metadata.
    """
    # >>> SOLUTION 14.2
    model_path, metadata_path = model_dir / MODEL_FILE, model_dir / METADATA_FILE
    for path in (model_path, metadata_path):
        if not path.is_file():
            raise FileNotFoundError(f"{path} does not exist.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model: PanelForecaster = joblib.load(model_path)
    return model, metadata
    # <<< SOLUTION
