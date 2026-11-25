from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.routes import system

client = TestClient(app)


def test_readiness_ready_with_dependency_checks():
    r = client.get("/api/v1/health/ready")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["checks"]["database"]["status"] == "up"
    assert data["checks"]["audit_chain"]["status"] == "up"
    assert data["checks"]["redis"]["status"] in ("up", "not_configured")


def test_readiness_503_when_database_down(monkeypatch):
    monkeypatch.setattr(system, "_check_database", lambda: {"status": "down", "error": "OperationalError"})
    r = client.get("/health/ready")
    assert r.status_code == 503
    assert r.json()["data"]["status"] == "not_ready"


def test_readiness_degraded_not_503_when_redis_down(monkeypatch):
    monkeypatch.setattr(system, "_check_redis", lambda: {"status": "degraded", "error": "ConnectionError"})
    r = client.get("/health/ready")
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "degraded"
