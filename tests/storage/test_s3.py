"""Tests of the S3 service class, against a fake S3 from moto.

The first test is given as a pattern. The rest is yours: `uv run course
check 15.6` runs your tests against deliberately broken versions of the
service and tells you which bugs they would let through.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError, EndpointConnectionError
from moto import mock_aws

from freshcast.storage.s3 import S3Storage

BUCKET = "test-bucket"


@pytest.fixture(name="storage")
def fixture_storage(tmp_path: Path) -> Iterator[S3Storage]:
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        yield S3Storage(
            client, BUCKET, cache_dir=tmp_path / "cache", sleep=lambda _: None
        )


def test_uploaded_file_comes_back_unchanged(storage: S3Storage, tmp_path: Path) -> None:
    source = tmp_path / "in.txt"
    source.write_text("hello", encoding="utf-8")

    storage.upload_file(source, "folder/in.txt")
    storage.download_file("folder/in.txt", tmp_path / "out.txt")

    assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "hello"


# >>> SOLUTION 15.6
def test_exists_sees_only_whole_keys(storage: S3Storage, tmp_path: Path) -> None:
    source = tmp_path / "a.txt"
    source.write_text("a", encoding="utf-8")
    storage.upload_file(source, "models/a.txt")

    assert storage.exists("models/a.txt")
    assert not storage.exists("models")
    assert not storage.exists("models/b.txt")


def test_list_keys_filters_by_prefix_and_sorts(
    storage: S3Storage, tmp_path: Path
) -> None:
    source = tmp_path / "x.txt"
    source.write_text("x", encoding="utf-8")
    for key in ("b/2.txt", "a/1.txt", "b/1.txt"):
        storage.upload_file(source, key)

    assert storage.list_keys("b/") == ["b/1.txt", "b/2.txt"]
    assert storage.list_keys() == ["a/1.txt", "b/1.txt", "b/2.txt"]
    assert storage.list_keys("zzz/") == []


def test_download_of_a_missing_key_is_file_not_found(
    storage: S3Storage, tmp_path: Path
) -> None:
    with pytest.raises(FileNotFoundError, match="does not exist"):
        storage.download_file("nothing.txt", tmp_path / "out.txt")


def test_upload_of_a_missing_file_is_file_not_found(
    storage: S3Storage, tmp_path: Path
) -> None:
    with pytest.raises(FileNotFoundError):
        storage.upload_file(tmp_path / "nope.txt", "nope.txt")


def test_delete_removes_and_tolerates_missing_keys(
    storage: S3Storage, tmp_path: Path
) -> None:
    source = tmp_path / "a.txt"
    source.write_text("a", encoding="utf-8")
    storage.upload_file(source, "a.txt")

    storage.delete("a.txt")
    storage.delete("a.txt")

    assert not storage.exists("a.txt")


def test_fetch_downloads_once_and_sees_replacements(
    storage: S3Storage, tmp_path: Path
) -> None:
    source = tmp_path / "data.txt"
    source.write_text("first", encoding="utf-8")
    storage.upload_file(source, "data.txt")

    first = storage.fetch("data.txt")
    again = storage.fetch("data.txt")
    source.write_text("second", encoding="utf-8")
    storage.upload_file(source, "data.txt")
    replaced = storage.fetch("data.txt")

    assert first == again
    assert first.read_text(encoding="utf-8") == "first"
    assert replaced.read_text(encoding="utf-8") == "second"


def test_transient_failures_are_retried(tmp_path: Path) -> None:
    calls: list[str] = []
    waits: list[float] = []

    class Flaky:
        def head_object(self, **_: object) -> dict[str, str]:
            calls.append("head")
            if len(calls) < 3:
                raise EndpointConnectionError(endpoint_url="http://localhost:9000")
            return {}

    storage = S3Storage(Flaky(), BUCKET, attempts=3, sleep=waits.append)  # type: ignore[arg-type]

    assert storage.exists("a.txt")
    assert len(calls) == 3
    assert len(waits) == 2


def test_permanent_failures_are_not_retried() -> None:
    calls: list[str] = []

    class Denied:
        def head_object(self, **_: object) -> None:
            calls.append("head")
            response: Any = {
                "Error": {"Code": "AccessDenied"},
                "ResponseMetadata": {"HTTPStatusCode": 403},
            }
            raise ClientError(response, "HeadObject")

    storage = S3Storage(Denied(), BUCKET, attempts=3, sleep=lambda _: None)  # type: ignore[arg-type]

    with pytest.raises(ClientError):
        storage.exists("a.txt")
    assert len(calls) == 1


# --- STUB
#| # Your tests go here.
# <<< SOLUTION
