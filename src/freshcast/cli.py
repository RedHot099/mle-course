"""Command line of the project: ``freshcast train`` and ``freshcast forecast``."""

import argparse
import logging
import sys
from pathlib import Path

from pydantic import ValidationError

from freshcast import pipeline
from freshcast.config import load_settings

logger = logging.getLogger("freshcast")


def build_parser() -> argparse.ArgumentParser:
    """Build the parser with the two commands and their arguments."""
    # >>> SOLUTION 14.5
    parser = argparse.ArgumentParser(
        prog="freshcast", description="Daily demand forecasts for fresh retail."
    )
    parser.add_argument("--verbose", action="store_true", help="log debug messages")
    commands = parser.add_subparsers(dest="command", required=True)

    train = commands.add_parser("train", help="backtest, fit and save a model")
    train.add_argument("--config", type=Path, required=True)

    forecast = commands.add_parser("forecast", help="forecast with a saved model")
    forecast.add_argument("--config", type=Path, required=True)
    forecast.add_argument("--model", type=Path, required=True, help="model directory")
    forecast.add_argument("--future", type=Path, required=True, help="raw file")
    return parser
    # <<< SOLUTION


def main(argv: list[str] | None = None) -> int:
    """Run a command and return the process exit code.

    0 means success. 2 means the run could not start because the settings
    file is missing or invalid. Any other failure is a bug or bad data: it
    is logged with its traceback and the exit code is 1.
    """
    # >>> SOLUTION 14.5
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        settings = load_settings(args.config)
    except (FileNotFoundError, ValidationError) as error:
        logger.error("Cannot load settings: %s", error)
        return 2

    try:
        if args.command == "train":
            result = pipeline.train(settings)
            print(result.model_dir)
        else:
            forecasts = pipeline.forecast(settings, args.model, args.future)
            print(f"{len(forecasts)} forecasts written to {args.model}")
    except Exception:
        # The one deliberate error boundary: log everything, fail the process.
        logger.exception("The %s command failed", args.command)
        return 1
    return 0
    # <<< SOLUTION


if __name__ == "__main__":
    sys.exit(main())
