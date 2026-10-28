"""Build reproducible starter bundles; --check compares committed downloads."""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "labs"


def bundle_bytes(lab: dict) -> bytes:
    output = io.BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name in sorted(lab["files"]):
            relative = Path(lab["id"]) / name
            assert not relative.is_absolute() and ".." not in relative.parts
            info = ZipInfo(relative.as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (LABS / relative).read_bytes())
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for lab in json.loads((LABS / "manifest.json").read_text())["labs"]:
        target = LABS / lab["bundle"]
        expected = bundle_bytes(lab)
        if args.check:
            assert target.read_bytes() == expected, f"Stale bundle: {target.name}"
        else:
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(expected)
        print(f"{'Checked' if args.check else 'Built'} {target.name}")


if __name__ == "__main__":
    main()
