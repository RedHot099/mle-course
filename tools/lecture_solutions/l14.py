"""Reference solutions of the exercises in lecture 14."""

SOLUTIONS = {
    "e1": """
from pydantic import BaseModel, ConfigDict, Field
class BacktestSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    folds: int = Field(default=4, ge=1)
    horizon: int = Field(default=7, ge=1)
""",
    "e2": """
import logging
logger = logging.getLogger("freshcast")
def run(load, execute):
    try:
        settings = load()
    except (FileNotFoundError, ValueError):
        return 2
    try:
        execute(settings)
    except Exception:
        logger.exception("The command failed")
        return 1
    return 0
""",
}
