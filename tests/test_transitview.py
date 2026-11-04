import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.ingest import transitview as tv

T = datetime(2026, 11, 2, 14, 5, 9, tzinfo=UTC)


def test_partition_path_layout():
    p = tv.partition_path(Path("data/raw/transitview"), T)
    assert p.as_posix() == (
        "data/raw/transitview/dt=2026-11-02/hr=14/transitview_20261102T140509Z.json"
    )


def test_envelope_keeps_payload_untouched():
    payload = {"routes": [{"23": [{"VehicleID": "1"}]}]}
    env = tv.build_envelope("http://x", {"http_status": 200, "payload": payload}, T)
    assert env["payload"] == payload
    assert env["fetched_at"] == T.isoformat()
    assert env["source"] == "septa_transitview"


def test_save_local_roundtrip(tmp_path):
    env = tv.build_envelope("http://x", {"http_status": 200, "payload": {"a": 1}}, T)
    path = tv.save_local(env, tmp_path, T)
    assert path.exists()
    assert json.loads(path.read_text())["payload"] == {"a": 1}


def test_fetch_retries_then_raises(monkeypatch):
    calls = {"n": 0}

    def boom(*args, **kwargs):
        calls["n"] += 1
        raise tv.requests.ConnectionError("down")

    monkeypatch.setattr(tv.requests, "get", boom)
    monkeypatch.setattr(tv.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeError):
        tv.fetch("http://x", retries=3)
    assert calls["n"] == 3
