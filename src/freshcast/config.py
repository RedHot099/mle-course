"""Run settings: one validated object instead of constants scattered in code.

Values come from three places, the later ones winning:

1. defaults written in the classes below,
2. a YAML file,
3. environment variables named ``FRESHCAST_<SECTION>__<FIELD>``, for
   example ``FRESHCAST_MODEL__ROUNDS=200``.

A misspelled key is an error, not a silently ignored line.
"""

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

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


# Amazon S3 names buckets this way. Dots are legal there but break the
# certificates of virtual-hosted addresses, so they are not accepted here.
BUCKET_NAME = re.compile(r"[a-z0-9][a-z0-9-]{1,61}[a-z0-9]")
URL_SCHEMES = ("http", "https")
DEFAULT_REGION = "us-east-1"


class ModelSettings(Section):
    """How the forecaster is trained."""

    params: dict[str, Any] = Field(default_factory=dict)
    rounds: int = Field(default=400, ge=1)
    in_stock_only: bool = True


class BacktestSettings(Section):
    """How the model is validated before the final fit."""

    folds: int = Field(default=4, ge=1)
    horizon: int = Field(default=7, ge=1)


class StorageSettings(Section):
    """Where finished models are published: a bucket on an S3-compatible server.

    Leave the whole section out and nothing is published. Credentials are not
    part of the settings: boto3 reads them from ``AWS_ACCESS_KEY_ID`` and
    ``AWS_SECRET_ACCESS_KEY``, so they never reach a file that is committed.
    """

    bucket: str
    prefix: str = "models"
    endpoint_url: str | None = None
    region: str = DEFAULT_REGION

    @field_validator("bucket")
    @classmethod
    def _valid_bucket(cls, bucket: str) -> str:
        # >>> SOLUTION 15.1
        if BUCKET_NAME.fullmatch(bucket) is None:
            raise ValueError(
                f"bucket {bucket!r} is not a valid name: use 3 to 63 lowercase "
                "letters, digits and hyphens, starting and ending with a letter "
                "or a digit."
            )
        return bucket
        # <<< SOLUTION

    @field_validator("prefix")
    @classmethod
    def _clean_prefix(cls, prefix: str) -> str:
        # >>> SOLUTION 15.1
        # Keys are built as prefix/signature/file, so the prefix carries no
        # slashes at its ends. Empty means the root of the bucket.
        cleaned = prefix.strip("/")
        parts = cleaned.split("/") if cleaned else []
        if any(part in ("", ".", "..") for part in parts):
            raise ValueError(
                f"prefix {prefix!r} has an empty, '.' or '..' part between slashes."
            )
        return cleaned
        # <<< SOLUTION

    @field_validator("endpoint_url")
    @classmethod
    def _valid_endpoint(cls, endpoint_url: str | None) -> str | None:
        # >>> SOLUTION 15.1
        if endpoint_url is None:
            return None
        parsed = urlparse(endpoint_url)
        if parsed.scheme not in URL_SCHEMES or not parsed.netloc:
            raise ValueError(
                f"endpoint_url {endpoint_url!r} must look like "
                "http://localhost:9000 (scheme, host and port)."
            )
        return endpoint_url
        # <<< SOLUTION


class Settings(BaseSettings):
    """Everything one run of the pipeline needs to know."""

    model_config = SettingsConfigDict(
        env_prefix="FRESHCAST_", env_nested_delimiter="__", extra="forbid"
    )

    data: DataSettings
    model: ModelSettings = Field(default_factory=ModelSettings)
    backtest: BacktestSettings = Field(default_factory=BacktestSettings)
    storage: StorageSettings | None = None
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
