"""
Tests for AWS Cedar Zero-Trust Enforcement in the Live Recovery Execution Path,
Multi-Tenant Idempotency Isolation, and Concurrent Duplicate Debit Prevention.
"""

import pytest
import time
import asyncio
import concurrent.futures
from aws.cedar.cedar_engine import get_cedar_engine, CedarPolicyEngine
from backend.app.security import DistributedIdempotencyStore
from backend.app.services.recovery_execution_service import execute_recovery_pipeline

@pytest.fixture
def cedar_engine():
    return get_cedar_engine()

@pytest.fixture
def temp_idempotency_store(tmp_path):
    db_file = str(tmp_path / "test_idempotency.db")
    return DistributedIdempotencyStore(db_path=db_file)

# --------------------------------------------------------------------------
# 1. AWS Cedar Zero-Trust Authorization in Live Execution Path
# --------------------------------------------------------------------------

def test_cedar_permits_fastloop_recovery_engine(cedar_engine):
    """Verifies Cedar Policy 5 permits FastLoopRecoveryEngine for valid recovery under INR 5,00,000."""
    result = cedar_engine.evaluate(
        principal='Agent::"FastLoopRecoveryEngine"',
        action="Action::ExecuteMandateRecovery",
        resource='RecoveryWorkflow::"pay_test_001"',
        context={"amount_inr": 25000.0, "cedar_kill_switch": False}
    )
    assert result.decision == "ALLOW"
    assert result.is_authorized is True
    assert result.policy_id == "policy_fastloop_recovery_permit"

def test_cedar_blocks_unauthorized_principal(cedar_engine):
    """Verifies Cedar blocks unknown/unauthorized principals from executing mandate recoveries."""
    result = cedar_engine.evaluate(
        principal='User::"AnonymousAttacker"',
        action="Action::ExecuteMandateRecovery",
        resource='RecoveryWorkflow::"pay_test_002"',
        context={"amount_inr": 1000.0, "cedar_kill_switch": False}
    )
    assert result.decision == "DENY"
    assert result.is_authorized is False

def test_cedar_blocks_amount_exceeding_ceiling(cedar_engine):
    """Verifies Cedar blocks transactions exceeding INR 5,00,000 without executive approval."""
    result = cedar_engine.evaluate(
        principal='Agent::"FastLoopRecoveryEngine"',
        action="Action::ExecuteMandateRecovery",
        resource='RecoveryWorkflow::"pay_test_003"',
        context={"amount_inr": 750000.0, "cedar_kill_switch": False}
    )
    assert result.decision == "DENY"
    assert "exceeds standard execution ceiling" in result.diagnostics["reason"]

def test_cedar_emergency_kill_switch(cedar_engine):
    """Verifies Cedar emergency kill-switch immediately halts all recovery actions."""
    result = cedar_engine.evaluate(
        principal='Agent::"FastLoopRecoveryEngine"',
        action="Action::ExecuteMandateRecovery",
        resource='RecoveryWorkflow::"pay_test_004"',
        context={"amount_inr": 10000.0, "cedar_kill_switch": True}
    )
    assert result.decision == "DENY"
    assert "kill-switch is active" in result.diagnostics["reason"]

def test_cedar_enforced_in_live_recovery_pipeline():
    """Verifies that execute_recovery_pipeline executes Cedar and logs trace steps."""
    trace_id = f"trace_cedar_{int(time.time())}"
    res = asyncio.run(execute_recovery_pipeline(
        trace_id=trace_id,
        payment_id=f"pay_live_cedar_{int(time.time())}",
        amount=14500.0,
        error_code="504",
        error_description="Gateway Timeout on SBI switch",
        customer_phone="+919876543210",
        customer_email="merchant@example.com",
        attempt_count=1,
        metadata={"merchant_id": "merch_acme_corp"}
    ))
    assert "decision_trace" in res
    cedar_step = next((s for s in res["decision_trace"] if s.get("step") == "Cedar Authorization"), None)
    assert cedar_step is not None
    assert "Cedar: ALLOW" in cedar_step["badge"]

# --------------------------------------------------------------------------
# 2. Multi-Tenant Idempotency Isolation
# --------------------------------------------------------------------------

def test_multi_tenant_idempotency_isolation(temp_idempotency_store):
    """Verifies two different merchants can safely use the exact same payment key without collision."""
    shared_key = "inv_shared_october_invoice"
    
    # Merchant A acquires lock
    acquired_a = temp_idempotency_store.acquire_lock(
        key=shared_key,
        payload_hash="hash_a",
        merchant_id="merchant_alpha"
    )
    assert acquired_a is True

    # Merchant B should also successfully acquire lock for their own isolated namespace
    acquired_b = temp_idempotency_store.acquire_lock(
        key=shared_key,
        payload_hash="hash_b",
        merchant_id="merchant_beta"
    )
    assert acquired_b is True

    # Merchant A tries again with same key -> rejected (idempotent)
    acquired_a_duplicate = temp_idempotency_store.acquire_lock(
        key=shared_key,
        payload_hash="hash_a_dup",
        merchant_id="merchant_alpha"
    )
    assert acquired_a_duplicate is False

    # Mark Merchant A completed
    temp_idempotency_store.mark_completed(
        key=shared_key,
        result_payload={"recovered": True, "amount": 5000},
        merchant_id="merchant_alpha"
    )
    assert temp_idempotency_store.is_execution_completed(shared_key, merchant_id="merchant_alpha") is True
    # Merchant B is NOT marked completed
    assert temp_idempotency_store.is_execution_completed(shared_key, merchant_id="merchant_beta") is False

# --------------------------------------------------------------------------
# 3. Concurrent Duplicate Debit Prevention
# --------------------------------------------------------------------------

def test_concurrent_duplicate_debit_prevention(temp_idempotency_store):
    """Verifies that 50 concurrent threads racing on the same key yield exactly 1 winner."""
    race_key = f"race_key_{int(time.time()*1000)}"
    num_threads = 50
    results = []

    def attempt_acquire(worker_id):
        return temp_idempotency_store.acquire_lock(
            key=race_key,
            payload_hash=f"hash_{worker_id}",
            merchant_id="merchant_speed_test"
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(attempt_acquire, i) for i in range(num_threads)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    # Exactly one thread acquires the lock
    winners = [r for r in results if r is True]
    losers = [r for r in results if r is False]
    assert len(winners) == 1
    assert len(losers) == num_threads - 1
