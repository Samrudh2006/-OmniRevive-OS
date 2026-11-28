"""
Stage 7: SRE Health Probes, Configuration Validation, and Deployment Smoke Tests.
"""

from fastapi.testclient import TestClient

from backend.app.config import Settings, settings
from backend.app.main import app
from backend.app.routes import system as system_routes
from deployment.verify_deployment import run_verification

client = TestClient(app)


def test_liveness_readiness_and_metrics_endpoints():
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["data"]["version"] == settings.APP_VERSION

    live_resp = client.get("/health/live")
    assert live_resp.status_code == 200
    assert live_resp.json()["data"]["status"] == "alive"

    live_alias = client.get("/api/v1/health/live")
    assert live_alias.status_code == 200
    assert live_alias.json()["data"]["status"] == "alive"

    ready_resp = client.get("/health/ready")
    assert ready_resp.status_code == 200
    ready_data = ready_resp.json()["data"]
    assert ready_data["checks"]["database"]["status"] == "up"
    assert ready_data["checks"]["audit_chain"]["status"] == "up"

    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == 200
    assert "# HELP" in metrics_resp.text


def test_readiness_degrades_on_redis_failure_and_503_on_db_failure(monkeypatch):
    # Redis is optional: failing Redis marks response degraded while staying HTTP 200
    monkeypatch.setattr(system_routes, "_check_redis", lambda: {"status": "degraded", "error": "ConnectionError"})
    degraded_resp = client.get("/health/ready")
    assert degraded_resp.status_code == 200
    assert degraded_resp.json()["data"]["status"] == "degraded"

    # Required SQLite DB down returns HTTP 503 not_ready
    monkeypatch.setattr(system_routes, "_check_database", lambda: {"status": "down", "error": "OperationalError"})
    down_resp = client.get("/health/ready")
    assert down_resp.status_code == 503
    assert down_resp.json()["success"] is False
    assert down_resp.json()["data"]["status"] == "not_ready"


def test_production_readiness_guardrails_require_explicit_secrets_when_strict(monkeypatch):
    # SAFE_DEMO_MODE=True must never block demo startup
    assert Settings(SAFE_DEMO_MODE=True).validate_production_readiness() == []

    # Disabling SAFE_DEMO_MODE without explicit env secrets must return 3 blockers
    monkeypatch.delenv("API_AUTH_KEY", raising=False)
    monkeypatch.delenv("CFO_AUTH_KEY", raising=False)
    monkeypatch.delenv("RAZORPAY_WEBHOOK_SECRET", raising=False)

    issues = Settings(SAFE_DEMO_MODE=False).validate_production_readiness()
    assert len(issues) == 3
    joined = " ".join(issues)
    assert "API_AUTH_KEY" in joined
    assert "CFO_AUTH_KEY" in joined
    assert "RAZORPAY_WEBHOOK_SECRET" in joined


def test_deployment_smoke_verification_suite():
    report = run_verification()
    assert report["all_passed"] is True, f"Failed deployment smoke checks: {report}"
    names = {c["check"] for c in report["checks"]}
    assert {"health", "liveness_probe", "readiness_probe", "prometheus_metrics", "swagger_docs", "openapi_schema", "merkle_audit_verify", "cedar_policies"}.issubset(names)
