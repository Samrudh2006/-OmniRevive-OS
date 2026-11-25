from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_surge_stream_rejects_unbounded_rate_and_duration():
    assert client.get("/api/v1/streaming/surge-stream?rate_tps=2000000&duration_sec=1").status_code == 422
    assert client.get("/api/v1/streaming/surge-stream?rate_tps=1000&duration_sec=600").status_code == 422
    assert client.get("/api/v1/streaming/surge-stream?rate_tps=1000&duration_sec=0.5").status_code == 200


def test_list_endpoints_reject_negative_and_huge_limits():
    for path in ("/api/v1/eval/traces", "/api/v1/logs/recent"):
        assert client.get(f"{path}?limit=-5").status_code == 422
        assert client.get(f"{path}?limit=100000000").status_code == 422
        assert client.get(f"{path}?limit=5").status_code == 200


def test_voice_synthesis_rejects_oversized_text():
    r = client.post("/api/v1/b2b/voice/synthesize", json={"text": "a" * 5001})
    assert r.status_code == 413
