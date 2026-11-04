"""Download the SEPTA static GTFS schedule zip.

Get the feed URL from SEPTA's GTFS repo releases (github.com/septadev/GTFS)
and put it in GTFS_URL. Not hard-coded because release URLs change.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


def download(url: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    dest = dest_dir / f"gtfs_{stamp}.zip"
    with requests.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                fh.write(chunk)
    return dest


if __name__ == "__main__":
    url = os.getenv("GTFS_URL")
    if not url:
        sys.exit("Set GTFS_URL (see module docstring).")
    out = download(url, Path(os.getenv("RAW_DATA_DIR", "data/raw")) / "gtfs_static")
    print(f"saved {out}")
