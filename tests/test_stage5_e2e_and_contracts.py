"""
Stage 5 End-to-End Financial Recovery Flow, B2B Cedar Fail-Closed Gate, and OpenAPI Contract Regression Tests
"""

import time
from fastapi.testclient import TestClient

from backend.app.config import settings
from backend.app.main import app

client = TestClient(app)


def test_openapi_schema_has_no_broken_routes_and_swagger_accessible():
    spec = app.openapi()
    paths = spec["paths"]
    assert "/agency/api/v1/agency/swarm/stress-test" not in paths
    for expected in (
        "/health",
        "/health/live",
        "/health/ready",
        "/api/v1/webhooks/razorpay",
        "/api/v1/simulate/failure",
        "/api/v1/b2b/voice/turn",
        "/api/v1/cfo/approve",
        "/api/v1/audit/verify",
        "/api/v1/audit/events",
        "/metrics",
    ):
        assert expected in paths, f"Missing expected API path: {expected}"

    # Ensure Swagger UI (/docs) is NOT shadowed by StaticFiles
    r_docs = client.get("/docs")
    assert r_docs.status_code == 200
    assert "SwaggerUIBundle" in r_docs.text


def test_structured_error_envelopes_omit_secrets_and_include_trace_id():
    r_404 = client.get("/api/v1/cfo/nonexistent_id_xyz")
    assert r_404.status_code == 404
    body = r_404.json()
    assert body["success"] is False
    assert "trace_id" in body and body["trace_id"]
    assert "API_AUTH_KEY" not in r_404.text
    assert settings.API_AUTH_KEY not in r_404.text


def test_b2b_voice_cedar_fail_closed_above_threshold():
    inv_id = f"inv_cedar_block_{int(time.time()*1000)}"
    r = client.post("/api/v1/b2b/voice/turn", json={
        "call_session_id": "call_hi_amt",
        "invoice_id": inv_id,
        "customer_speech_text": "Update GSTIN 29AABCU9603R1Z2 please",
        "invoice_amount": 750000.0,
    })
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["invoice_mutated"] is False
    assert data["action_taken"] == "ESCALATE_HUMAN"
    assert data["should_escalate_to_human"] is True
    assert data["cedar_evaluation"]["decision"] == "DENY"


def test_end_to_end_failure_cfo_escalation_approval_and_audit(monkeypatch):
    monkeypatch.setattr(settings, "SAFE_DEMO_MODE", False)
    sre_headers = {"X-API-Key": settings.API_AUTH_KEY}
    cfo_headers = {"X-API-Key": settings.CFO_AUTH_KEY}

    pid = f"pay_e2e_cfo_{int(time.time()*1000)}"
    # 1. Ingest high-risk suspicious velocity failure -> escalates to CFO queue + logs audit
    r_sim = client.post(
        "/api/v1/simulate/failure",
        json={
            "payment_id": pid,
            "amount": 125000.0,
            "error_code": "SUSPICIOUS_VELOCITY",
            "error_description": "Card testing anomaly",
        },
        headers=sre_headers,
    )
    assert r_sim.status_code == 200
    sim_data = r_sim.json()["data"]
    assert sim_data["action_taken"] == "ESCALATE_TO_CFO_QUEUE"
    cfo_id = sim_data["gateway_result"]["cfo_approval_id"]

    # 2. SRE key cannot self-approve CFO queue (must return 403!)
    r_forbid = client.post("/api/v1/cfo/approve", json={"approval_id": cfo_id}, headers=sre_headers)
    assert r_forbid.status_code == 403

    # 3. Genuine CFO key approves escalation -> EXECUTED + chained into audit ledger
    r_ok = client.post("/api/v1/cfo/approve", json={"approval_id": cfo_id, "notes": "Verified E2E"}, headers=cfo_headers)
    assert r_ok.status_code == 200
    assert r_ok.json()["data"]["status"] == "EXECUTED"

    # 4. Verify cryptographic Merkle audit ledger integrity remains unbroken
    r_audit = client.get("/api/v1/audit/verify")
    assert r_audit.status_code == 200
    assert r_audit.json()["data"]["valid"] is True
