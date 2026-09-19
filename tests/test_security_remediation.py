import hmac
import hashlib
import json
import time
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)

def test_webhook_missing_signature_rejected():
    """Verify that omitting X-Razorpay-Signature header returns 401 Unauthorized."""
    payload = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_unauthorized_99",
                    "amount": 250000,
                    "currency": "INR",
                    "error_code": "BAD_REQUEST_ERROR"
                }
            }
        }
    }
    # No signature header sent
    res = client.post("/api/v1/webhooks/razorpay", json=payload)
    assert res.status_code == 401
    err = res.json().get("error", {})
    assert "Missing or invalid cryptographic HMAC signature" in err.get("message", "")

def test_webhook_invalid_signature_rejected():
    """Verify that sending a forged/invalid X-Razorpay-Signature returns 401."""
    payload = {"event": "payment.failed", "payload": {"payment": {"entity": {"id": "pay_fake_1"}}}}
    res = client.post(
        "/api/v1/webhooks/razorpay",
        json=payload,
        headers={"X-Razorpay-Signature": "forged_invalid_hmac_hex_9999"}
    )
    assert res.status_code == 401
    err = res.json().get("error", {})
    assert "Missing or invalid cryptographic HMAC signature" in err.get("message", "")

def test_webhook_valid_signature_accepted():
    """Verify that a cryptographically authentic HMAC signature succeeds with 202."""
    raw_body = json.dumps({
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_auth_test_{int(time.time())}",
                    "amount": 199900,
                    "currency": "INR",
                    "error_code": "GATEWAY_ERROR",
                    "error_description": "Bank node timeout"
                }
            }
        }
    }).encode("utf-8")
    
    valid_sig = hmac.new(
        key=settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    res = client.post(
        "/api/v1/webhooks/razorpay",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": valid_sig,
            "X-Razorpay-Event-Time": str(int(time.time()))
        }
    )
    assert res.status_code == 202
    data = res.json()
    assert data["success"] is True
    assert data["data"]["status"] == "accepted_for_recovery"

def test_http_security_headers_enforced():
    """Verify essential security response headers are present on all HTTP responses."""
    res = client.get("/health")
    assert res.status_code == 200
    headers = res.headers
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "max-age=31536000" in headers.get("Strict-Transport-Security", "")
    assert "camera=()" in headers.get("Permissions-Policy", "")

def test_rate_limiter_spoofed_forwarded_for_handled():
    """Verify rate limiter does not trust untrusted spoofed forward headers from external hosts."""
    from backend.app.middleware.rate_limiter import SlidingWindowRateLimiter

    limiter = SlidingWindowRateLimiter(app)
    # Mock external client request
    class MockRequest:
        def __init__(self, host, forwarded=None, api_key=None):
            self.headers = {}
            if forwarded:
                self.headers["X-Forwarded-For"] = forwarded
            if api_key:
                self.headers["X-API-Key"] = api_key
            self.client = type("Client", (), {"host": host})()

    # External IP attempting to spoof X-Forwarded-For
    req_external = MockRequest(host="203.0.113.42", forwarded="8.8.8.8, 1.1.1.1")
    client_id = limiter._get_client_id(req_external)
    # Must bind to client IP, not the spoofed 8.8.8.8!
    assert client_id == "ip_203.0.113.42"

    # Local trusted proxy forwarding legitimate client IP
    req_local_proxy = MockRequest(host="127.0.0.1", forwarded="198.51.100.25")
    proxy_client_id = limiter._get_client_id(req_local_proxy)
    assert proxy_client_id == "fwd_198.51.100.25"

def test_copilot_mutation_requires_auth_in_strict_mode(monkeypatch):
    """Verify that in non-demo mode, mutating financial actions via Copilot require authorization."""
    monkeypatch.setattr(settings, "SAFE_DEMO_MODE", False)
    
    # Attempt mutation without auth headers
    res = client.post(
        "/api/v1/copilot/chat",
        json={"query": "Change GST to 29AABCU9603R1Z2 on active invoice"}
    )
    # Should be rejected with 401 before any mutation occurs
    assert res.status_code == 401
    err = res.json().get("error", {})
    assert "Authentication required" in err.get("message", "")

def test_gateway_selection_auth_in_strict_mode(monkeypatch):
    """Verify that in strict mode, switching payment rails requires SRE_Admin auth."""
    monkeypatch.setattr(settings, "SAFE_DEMO_MODE", False)
    
    # Without auth -> 401
    res = client.post("/api/v1/gateways/select", json={"rail_id": "juspay"})
    assert res.status_code == 401

    # With authentic SRE auth -> 200
    res_auth = client.post(
        "/api/v1/gateways/select",
        json={"rail_id": "juspay"},
        headers={"X-API-Key": settings.API_AUTH_KEY}
    )
    assert res_auth.status_code == 200
    assert res_auth.json()["success"] is True

def test_audit_events_auth_and_tenant_isolation(monkeypatch):
    """Verify audit events endpoint requires auth in strict mode and filters by merchant."""
    from backend.app.audit_store import audit_store
    
    # Record events for two different merchants
    audit_store.record_event(
        trace_id="tr_tenant_a",
        merchant_id="merch_alpha",
        payment_id="pay_alpha_1",
        event_type="test.event",
        failure_class="TEST",
        decision={"test": True},
        policy_verdict="ALLOWED",
        action_taken="TEST_ALPHA"
    )
    audit_store.record_event(
        trace_id="tr_tenant_b",
        merchant_id="merch_beta",
        payment_id="pay_beta_1",
        event_type="test.event",
        failure_class="TEST",
        decision={"test": True},
        policy_verdict="ALLOWED",
        action_taken="TEST_BETA"
    )

    monkeypatch.setattr(settings, "SAFE_DEMO_MODE", False)
    # 1. Unauthenticated -> 401
    res = client.get("/api/v1/audit/events")
    assert res.status_code == 401

    # 2. Authenticated with merchant_id filter
    res_auth = client.get(
        "/api/v1/audit/events?merchant_id=merch_alpha",
        headers={"X-API-Key": settings.API_AUTH_KEY}
    )
    assert res_auth.status_code == 200
    events = res_auth.json()["data"]["events"]
    assert len(events) >= 1
    assert all(e["merchant_id"] == "merch_alpha" for e in events)

def test_rate_limiter_ignores_forged_api_key():
    """Verify rate limiter does not key on unrecognized/forged API keys."""
    from backend.app.middleware.rate_limiter import SlidingWindowRateLimiter

    limiter = SlidingWindowRateLimiter(app)
    class MockRequest:
        def __init__(self, host, api_key=None):
            self.headers = {"X-API-Key": api_key} if api_key else {}
            self.client = type("Client", (), {"host": host})()

    # Forged API key -> must NOT use fake key, must fall back to IP
    req_forged = MockRequest(host="198.51.100.99", api_key="fake_attacker_key_xyz")
    client_id = limiter._get_client_id(req_forged)
    assert client_id == "ip_198.51.100.99"

    # Authentic SRE API key -> recognized
    req_legit = MockRequest(host="198.51.100.99", api_key=settings.API_AUTH_KEY)
    legit_id = limiter._get_client_id(req_legit)
    assert legit_id.startswith("key_")

def test_bulk_csv_upload_size_limit():
    """Verify bulk CSV upload rejects files exceeding 10MB."""
    oversized_data = b"payment_id,amount\n" + (b"0" * (10 * 1024 * 1024 + 1024))
    files = {"file": ("oversized.csv", oversized_data, "text/csv")}
    res = client.post("/api/v1/recovery/batch-upload", files=files)
    assert res.status_code == 413
    err = res.json().get("error", {})
    assert "10MB" in err.get("message", "")

