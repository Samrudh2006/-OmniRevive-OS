from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.routes import copilot

client = TestClient(app)


def test_query_length_bounded():
    r = client.post("/api/v1/copilot/chat", json={"query": "a" * 2001})
    assert r.status_code == 422


def test_breaker_opens_after_failures_and_fallback_still_answers():
    copilot.local_ai_breaker.record_success()
    for _ in range(2):
        r = client.post("/api/v1/copilot/chat", json={"query": "what is the CAS mutex"})
        assert r.status_code == 200 and r.json()["success"] is True
    assert copilot.local_ai_breaker.state == "open"
    r = client.post("/api/v1/copilot/chat", json={"query": "what is the CAS mutex"})
    assert r.status_code == 200
    copilot.local_ai_breaker.record_success()
