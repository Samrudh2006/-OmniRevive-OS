"""
Stage 3 Financial Safety & Zero-Trust Verification Suite:
- Webhook size limits, replay timestamp=0 / strict timestamp enforcement, secret rotation ring, schema validation
- Redis & SQLite CAS atomic locking with fencing owner tokens, release ownership, expiration, Redis failover, 100-thread race
- AWS Cedar fail-closed evaluation, Rule 3 principal verification, quiet-hours gate, cross-tenant deny, live pipeline DENY
- Multi-tenant API key scoping and strict-mode endpoint authentication across all financial routes
"""

import asyncio
import concurrent.futures
import hashlib
import hmac
import json
import time
import pytest
from fastapi.testclient import TestClient

from aws.cedar.cedar_engine import get_cedar_engine
from backend.app.config import settings
from backend.app.main import app
from backend.app.security import DistributedIdempotencyStore, verify_razorpay_signature
from backend.app.services.recovery_execution_service import execute_recovery_pipeline

client = TestClient(app)


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# A & B. Webhook Security: Size Limit, Replay (=0 & missing), Secret Rotation
# ---------------------------------------------------------------------------

def test_webhook_rejects_zero_timestamp_replay():
    body = b'{"event":"payment.failed","payload":{}}'
    sig = _sign(body, settings.RAZORPAY_WEBHOOK_SECRET)
    assert verify_razorpay_signature(body, sig, timestamp=0) is False


def test_webhook_requires_timestamp_when_strict(monkeypatch):
    monkeypatch.setattr(settings, "SAFE_DEMO_MODE", False)
    payload = json.dumps({"event": "payment.failed", "payload": {"payment": {"entity": {"id": "pay_req_ts"}}}}).encode()
    sig = _sign(payload, settings.RAZORPAY_WEBHOOK_SECRET)
    res = client.post(
        "/api/v1/webhooks/razorpay",
        content=payload,
        headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig},
    )
    assert res.status_code == 401


def test_webhook_secret_rotation_accepts_previous_secret(monkeypatch):
    old_secret = "whsec_old_rotated_secret_key_123456"
    monkeypatch.setattr(settings, "RAZORPAY_WEBHOOK_SECRET_PREVIOUS", old_secret)
    body = json.dumps({
        "event": "payment.failed",
        "payload": {"payment": {"entity": {"id": f"pay_rot_{int(time.time()*1000)}", "amount": 150000}}},
    }).encode()
    sig = _sign(body, old_secret)
    res = client.post(
        "/api/v1/webhooks/razorpay",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": sig,
            "X-Razorpay-Event-Time": str(int(time.time())),
        },
    )
    assert res.status_code == 202
    assert res.json()["data"]["status"] == "accepted_for_recovery"


def test_webhook_rejects_oversized_payload(monkeypatch):
    monkeypatch.setattr(settings, "MAX_WEBHOOK_BYTES", 64)
    body = b'{"event":"payment.failed","payload":{"padding":"' + (b"x" * 100) + b'"}}'
    sig = _sign(body, settings.RAZORPAY_WEBHOOK_SECRET)
    res = client.post(
        "/api/v1/webhooks/razorpay",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": sig,
            "X-Razorpay-Event-Time": str(int(time.time())),
        },
    )
    assert res.status_code == 413


def test_webhook_rejects_invalid_schema():
    body = json.dumps({"event": "payment.failed", "payload": {"payment": {"entity": "not_an_object"}}}).encode()
    sig = _sign(body, settings.RAZORPAY_WEBHOOK_SECRET)
    res = client.post(
        "/api/v1/webhooks/razorpay",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": sig,
            "X-Razorpay-Event-Time": str(int(time.time())),
        },
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# C. AWS Cedar Hardening: Rule 3 Principal, Quiet Hours, Cross-Tenant, Fail-Closed
# ---------------------------------------------------------------------------

def test_cedar_rule3_denies_unauthorized_principal():
    eng = get_cedar_engine()
    res = eng.evaluate(
        principal='User::"ExternalAttacker"',
        action="Action::ExecuteVoiceDialogueTurn",
        resource='B2BInvoice::"inv_998"',
    )
    assert res.decision == "DENY"
    assert res.is_authorized is False


def test_cedar_rule5_denies_quiet_hours_dispatch():
    eng = get_cedar_engine()
    res = eng.evaluate(
        principal='Agent::"FastLoopRecoveryEngine"',
        action="Action::DispatchRecoveryLink",
        resource='RecoveryWorkflow::"pay_qh_1"',
        context={"amount_inr": 2500.0, "quiet_hours_blocked": True},
    )
    assert res.decision == "DENY"
    assert "Quiet Hours" in res.diagnostics["reason"]


def test_cedar_denies_cross_tenant_resource():
    eng = get_cedar_engine()
    res = eng.evaluate(
        principal='Agent::"FastLoopRecoveryEngine"',
        action="Action::ExecuteMandateRecovery",
        resource='RecoveryWorkflow::"pay_t1"',
        context={"amount_inr": 1000.0, "merchant_id": "merch_a", "resource_tenant_id": "merch_b"},
    )
    assert res.decision == "DENY"
    assert res.policy_id == "policy_tenant_isolation_forbid"


def test_cedar_fails_closed_on_malformed_context():
    eng = get_cedar_engine()
    res = eng.evaluate(
        principal='Agent::"FastLoopRecoveryEngine"',
        action="Action::ExecuteMandateRecovery",
        resource='RecoveryWorkflow::"pay_err"',
        context={"amount_inr": "not_a_number"},
    )
    assert res.decision == "DENY"
    assert res.policy_id == "fail_closed_evaluation_error"


def test_live_pipeline_blocks_on_cedar_kill_switch():
    trace_id = f"trace_ks_{int(time.time()*1000)}"
    res = asyncio.run(execute_recovery_pipeline(
        trace_id=trace_id,
        payment_id=f"pay_ks_{int(time.time()*1000)}",
        amount=5000.0,
        error_code="GATEWAY_ERROR",
        error_description="Timeout",
        customer_phone="+919876543210",
        customer_email="u@example.com",
        attempt_count=1,
        metadata={"cedar_kill_switch": True, "merchant_id": "merch_ks"},
    ))
    assert res["policy_result"] == "DENIED_BY_CEDAR"
    assert res["action_taken"] == "SUPPRESS_ACTION"
    assert res["cedar_evaluation"]["decision"] == "DENY"


# ---------------------------------------------------------------------------
# D. Redis & SQLite CAS Concurrency: 100 Threads, Fencing Owner, Redis Failover
# ---------------------------------------------------------------------------

def test_idempotency_owner_fencing_and_expiry(tmp_path):
    store = DistributedIdempotencyStore(db_path=str(tmp_path / "fencing.db"))
    acq1, tok1 = store.acquire_lock_with_token("key_fence", payload_hash="h1", ttl_seconds=60, merchant_id="m1")
    assert acq1 is True and tok1 is not None

    # Wrong owner cannot release or complete
    assert store.release_lock("key_fence", merchant_id="m1", owner_token="forged_owner") is False
    assert store.mark_completed("key_fence", merchant_id="m1", owner_token="forged_owner") is False

    # Right owner releases
    assert store.release_lock("key_fence", merchant_id="m1", owner_token=tok1) is True

    # Expired lock can be reclaimed
    acq2, tok2 = store.acquire_lock_with_token("key_exp", payload_hash="h2", ttl_seconds=0, merchant_id="m1")
    assert acq2 is True and tok2 is not None
    time.sleep(0.02)
    acq3, tok3 = store.acquire_lock_with_token("key_exp", payload_hash="h2b", ttl_seconds=0, merchant_id="m1")
    assert acq3 is True and tok3 != tok2


def test_redis_cas_mock_and_connection_failure_fallback(tmp_path):
    class FakeRedis:
        def __init__(self, fail=False):
            self.kv = {}
            self.fail = fail

        def ping(self):
            if self.fail:
                raise ConnectionError("redis down")
            return True

        def set(self, k, v, nx=False, ex=None):
            if self.fail:
                raise ConnectionError("redis down")
            if nx and k in self.kv:
                return False
            self.kv[k] = v
            return True

        def eval(self, script, numkeys, k, expected):
            if self.fail:
                raise ConnectionError("redis down")
            if self.kv.get(k) == expected:
                del self.kv[k]
                return 1
            return 0

        def close(self):
            pass

    store = DistributedIdempotencyStore(db_path=str(tmp_path / "redis_mock.db"))
    fake = FakeRedis(fail=False)
    store.redis_client = fake

    acq1, tok1 = store.acquire_lock_with_token("rk_1", merchant_id="m_redis")
    assert acq1 is True
    # Concurrent attempt rejected by Redis NX
    acq2, _ = store.acquire_lock_with_token("rk_1", merchant_id="m_redis")
    assert acq2 is False
    # Wrong owner Lua CAS release denied
    assert store.release_lock("rk_1", merchant_id="m_redis", owner_token="wrong") is False
    # Correct owner Lua CAS release succeeds and cleans both Redis and SQLite
    assert store.release_lock("rk_1", merchant_id="m_redis", owner_token=tok1) is True
    assert f"idempotency:m_redis:rk_1" not in fake.kv

    # Redis outages degrade cleanly into SQLite WAL atomic CAS
    fake.fail = True
    assert store.acquire_lock("rk_failover", merchant_id="m_redis") is True
    assert store.acquire_lock("rk_failover", merchant_id="m_redis") is False


def test_100_thread_concurrent_storm(tmp_path):
    store = DistributedIdempotencyStore(db_path=str(tmp_path / "storm100.db"))
    key = f"storm_100_{int(time.time()*1000)}"

    def hit(idx):
        return store.acquire_lock(key, payload_hash=f"p_{idx}", merchant_id="merch_100")

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
        results = list(ex.map(hit, range(100)))

    assert results.count(True) == 1
    assert results.count(False) == 99


# ---------------------------------------------------------------------------
# E. Multi-Tenant API Authorization & Strict-Mode Endpoint Gating
# ---------------------------------------------------------------------------

def test_strict_mode_gates_mutating_endpoints_and_tenant_isolation(monkeypatch):
    monkeypatch.setattr(settings, "SAFE_DEMO_MODE", False)
    monkeypatch.setattr(settings, "MERCHANT_TENANT_KEYS", {"key_tenant_alpha_secret": "merch_alpha"})

    # 1. Previously open mutating routes must require auth in strict mode
    assert client.post("/api/v1/b2b/voice/turn", json={"call_session_id": "c1", "invoice_id": "inv_998", "customer_speech_text": "hello"}).status_code == 401
    assert client.post("/api/v1/system/rebalance-traffic", json={"action": "OPTIMIZE"}).status_code == 401
    assert client.post("/api/v1/simulate/failure", json={"payment_id": "pay_x", "amount": 500}).status_code == 401
    assert client.post("/api/v1/cfo/sign-approval", json={"approval_id": "a1", "entity_id": "e1", "amount_inr": 1000, "decision": "APPROVED", "approver_id": "cfo"}).status_code == 401
    assert client.post("/api/v1/gateways/simulate", json={"amount": 500}).status_code == 401

    # 2. Tenant-scoped key can query own tenant's audit ledger, blocked from reading another tenant
    res_own = client.get("/api/v1/audit/events?merchant_id=merch_alpha", headers={"X-API-Key": "key_tenant_alpha_secret"})
    assert res_own.status_code == 200
    assert all(ev["merchant_id"] == "merch_alpha" for ev in res_own.json()["data"]["events"])

    res_cross = client.get("/api/v1/audit/events?merchant_id=merch_beta", headers={"X-API-Key": "key_tenant_alpha_secret"})
    assert res_cross.status_code == 403

    # 3. Tenant key cannot access platform SRE_Admin / CFO routes
    assert client.post("/api/v1/system/rebalance-traffic", json={"action": "OPTIMIZE"}, headers={"X-API-Key": "key_tenant_alpha_secret"}).status_code == 403
