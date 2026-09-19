import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["DEMO_MODE"] = "1"

from fastapi.testclient import TestClient

from app.ergonomics.measurements import ErgonomicMeasurements
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["demo_mode"] is True


def test_posture_current(client):
    r = client.get("/api/posture/current")
    assert r.status_code == 200
    data = r.json()
    assert "score" in data
    assert "status" in data
    assert "measurements" in data
    assert 0 <= data["score"] <= 100


def test_session_stats(client):
    r = client.get("/api/session/stats")
    assert r.status_code == 200
    data = r.json()
    assert "session_duration_seconds" in data
    assert "good_percentage" in data
    assert "average_score" in data


def test_config(client):
    r = client.get("/api/config")
    assert r.status_code == 200
    data = r.json()
    assert "head_tilt_warning_degrees" in data
    assert "score_good_threshold" in data
    assert data["demo_mode"] is True


def test_stream_returns_data(client):
    r = client.get("/api/stream/frame")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/jpeg")
    assert len(r.content) > 1000


def test_websocket_posture_updates(client):
    with client.websocket_connect("/ws/posture") as ws:
        data = ws.receive_json()
        assert "score" in data
        assert "status" in data
        assert "measurements" in data
        assert 0 <= data["score"] <= 100