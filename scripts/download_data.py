#!/usr/bin/env python
"""Materialize the wine dataset to data/raw/wine.csv and record its checksum.

Idempotent: if the CSV already exists and its sha256 matches what's on record in
data/raw/CHECKSUMS.txt, nothing is re-downloaded or re-written. That file IS committed
to git (unlike the data itself) — it's how reproducibility gets checked without the
raw data ever being in version control: anyone can regenerate the CSV and confirm the
checksum matches.
"""
