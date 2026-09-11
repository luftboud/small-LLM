#!/usr/bin/env python
"""Materialize the wine dataset to data/raw/wine.csv and record its checksum.

Idempotent: if the CSV already exists and its sha256 matches what's on record in
data/raw/CHECKSUMS.txt, nothing is re-downloaded or re-written. That file IS committed
to git (unlike the data itself) — it's how reproducibility gets checked without the
raw data ever being in version control: anyone can regenerate the CSV and confirm the
checksum matches.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
from pathlib import Path

from wine_origin.data import materialize_raw_csv

logger = logging.getLogger(__name__)

RAW_CSV = Path("data/raw/wine.csv")
CHECKSUMS_FILE = Path("data/raw/CHECKSUMS.txt")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_recorded_checksum(checksums_file: Path, filename: str) -> str | None:
    if not checksums_file.exists():
        return None
    for line in checksums_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, recorded_name = line.split(maxsplit=1)
        if recorded_name == filename:
            return digest
    return None


def write_checksum(checksums_file: Path, filename: str, digest: str) -> None:
    checksums_file.parent.mkdir(parents=True, exist_ok=True)
    checksums_file.write_text(
        "# sha256 checksums for files in data/raw/, so reproducibility can be checked\n"
        "# without the data itself being committed. Regenerate by rerunning this "
        "script.\n"
        f"{digest}  {filename}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="Re-materialize even if checksums already match"
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    recorded = read_recorded_checksum(CHECKSUMS_FILE, RAW_CSV.name)
    if not args.force and RAW_CSV.exists() and recorded is not None:
        if sha256_of(RAW_CSV) == recorded:
            logger.info("%s already up to date (sha256 matches CHECKSUMS.txt), skipping", RAW_CSV)
            return
        logger.warning("%s exists but checksum doesn't match — re-materializing", RAW_CSV)

    materialize_raw_csv(RAW_CSV)
    digest = sha256_of(RAW_CSV)
    write_checksum(CHECKSUMS_FILE, RAW_CSV.name, digest)
    logger.info("Wrote %s (sha256 %s)", RAW_CSV, digest)


if __name__ == "__main__":
    main()
