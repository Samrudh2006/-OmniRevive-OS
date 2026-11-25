from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_valid_trace_id_echoed():
    r = client.get("/health", headers={"X-Trace-ID": "abc-123_x.y"})
    assert r.headers["X-Trace-ID"] == "abc-123_x.y"


def test_oversized_trace_id_replaced():
    r = client.get("/health", headers={"X-Trace-ID": "a" * 500})
    assert r.headers["X-Trace-ID"].startswith("tr_")


def test_odd_chars_trace_id_replaced():
    r = client.get("/health", headers={"X-Trace-ID": "x y<script>"})
    assert r.headers["X-Trace-ID"].startswith("tr_")
