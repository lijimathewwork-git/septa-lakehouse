"""Poll SEPTA TransitView and store the raw response untouched.

Design rule: ingestion does NOT clean or reshape data. It wraps the raw
payload in a small envelope (when/where it was fetched) and saves it.
All cleaning happens later in the silver layer, so you can always replay.
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import UTC, datetime
from pathlib import Path

import requests

log = logging.getLogger("transitview")

DEFAULT_URL = "https://www3.septa.org/api/TransitViewAll/index.php"


def fetch(url: str, retries: int = 3, timeout: float = 10.0) -> dict:
    """GET the feed with simple retry/backoff. Raises after the last attempt."""
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return {
                "http_status": resp.status_code,
                "payload": resp.json(),
            }
        except (requests.RequestException, ValueError) as err:
            last_err = err
            log.warning("attempt %d/%d failed: %s", attempt, retries, err)
            time.sleep(2**attempt)
    raise RuntimeError(f"fetch failed after {retries} attempts") from last_err


def build_envelope(url: str, result: dict, fetched_at: datetime) -> dict:
    return {
        "source": "septa_transitview",
        "source_url": url,
        "fetched_at": fetched_at.isoformat(),
        "http_status": result["http_status"],
        "payload": result["payload"],
    }


def partition_path(base: Path, fetched_at: datetime) -> Path:
    """Hive-style partitions: dt=YYYY-MM-DD/hr=HH/transitview_<ts>.json"""
    name = f"transitview_{fetched_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    return base / f"dt={fetched_at:%Y-%m-%d}" / f"hr={fetched_at:%H}" / name


def save_local(envelope: dict, base: Path, fetched_at: datetime) -> Path:
    path = partition_path(base, fetched_at)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(envelope), encoding="utf-8")
    return path


def upload_s3(local_path: Path, bucket: str, prefix: str, base: Path) -> str:
    import boto3  # imported here so week 1 works without AWS set up

    key = f"{prefix}/{local_path.relative_to(base).as_posix()}"
    boto3.client("s3").upload_file(str(local_path), bucket, key)
    return f"s3://{bucket}/{key}"


def run_once() -> Path:
    url = os.getenv("SEPTA_TRANSITVIEW_URL", DEFAULT_URL)
    base = Path(os.getenv("RAW_DATA_DIR", "data/raw")) / "transitview"
    bucket = os.getenv("S3_BUCKET", "").strip()
    prefix = os.getenv("S3_PREFIX", "raw/transitview").strip("/")

    fetched_at = datetime.now(UTC)
    result = fetch(url)
    envelope = build_envelope(url, result, fetched_at)
    path = save_local(envelope, base, fetched_at)
    log.info("saved %s", path)

    if bucket:
        dest = upload_s3(path, bucket, prefix, base)
        log.info("uploaded %s", dest)
    return path


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    run_once()
