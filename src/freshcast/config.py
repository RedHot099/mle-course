"""Run settings: one validated object instead of constants scattered in code.

Values come from three places, the later ones winning:

1. defaults written in the classes below,
2. a YAML file,
3. environment variables named ``FRESHCAST_<SECTION>__<FIELD>``, for
   example ``FRESHCAST_MODEL__ROUNDS=200``.

A misspelled key is an error, not a silently ignored line.
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class Section(BaseModel):
    """Base of every settings section: unknown keys are rejected."""

    model_config = ConfigDict(extra="forbid")


class DataSettings(Section):
    """Where the data lives and how much of it to use."""

    train_file: Path
    processed_dir: Path
    cities: list[int] | None = None

    @field_validator("cities")
    @classmethod
    def _cities_not_empty(cls, cities: list[int] | None) -> list[int] | None:
        # >>> SOLUTION 14.1
        if cities is not None and len(cities) == 0:
            raise ValueError("cities must list at least one city, or be omitted.")
        return cities
        # <<< SOLUTION


class ModelSettings(Section):
    """How the forecaster is trained."""

    params: dict[str, Any] = Field(default_factory=dict)
    rounds: int = Field(default=400, ge=1)
    in_stock_only: bool = True


class BacktestSettings(Section):
    """How the model is validated before the final fit."""

    folds: int = Field(default=4, ge=1)
    horizon: int = Field(default=7, ge=1)


class Settings(BaseSettings):
    """Everything one run of the pipeline needs to know."""

    model_config = SettingsConfigDict(
        env_prefix="FRESHCAST_", env_nested_delimiter="__", extra="forbid"
    )

    data: DataSettings
    model: ModelSettings = Field(default_factory=ModelSettings)
    backtest: BacktestSettings = Field(default_factory=BacktestSettings)
    artifacts_dir: Path = Path("artifacts")
    experiment: str = "freshcast"


def load_settings(path: Path) -> Settings:
    """Read settings from a YAML file, letting environment variables override it.

    Args:
        path: The YAML file.

    Raises:
        FileNotFoundError: The file does not exist.
        pydantic.ValidationError: A value has the wrong type or range, a
            required value is missing, or a key is not known.
    """
    # >>> SOLUTION 14.1
    if not path.is_file():
        raise FileNotFoundError(f"Settings file {path} does not exist.")

    class FromFile(Settings):
        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            # Earlier sources win: environment first, then the file.
            return env_settings, YamlConfigSettingsSource(settings_cls, yaml_file=path)

    return FromFile()
    # <<< SOLUTION
