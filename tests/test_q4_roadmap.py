"""Tests for Q4 2026 roadmap modules: WhatsApp Flow 2.0, Ed25519 CFO signing, Multi-Region CAS."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from backend.app.services.cfo_ed25519_signer import CFOEd25519Signer, SignedCFOApproval
from backend.app.services.multiregion_cas_lock import MultiRegionCASCoordinator
from backend.app.services.whatsapp_flow_service import (
    build_whatsapp_flow_upi_payload,
    clamp_cedar_discount,
)


def test_whatsapp_flow_cedar_discount_clamp():
    assert clamp_cedar_discount(1000.0, 25.0) == 100.0
    assert clamp_cedar_discount(50000.0, 10.0) == 500.0
    assert clamp_cedar_discount(1000.0, -5.0) == 0.0

    payload = build_whatsapp_flow_upi_payload(
        recipient_phone="+919876543210",
        invoice_id="inv_9001",
        amount_inr=10000.0,
        proposed_discount_pct=15.0,
    )
    assert payload.discount_applied_inr == 500.0
    assert payload.payable_amount_inr == 9500.0
    assert "am=9500.00" in payload.upi_intent_uri
    assert payload.flow_message["interactive"]["type"] == "flow"


def test_cfo_ed25519_sign_and_tamper_detection():
    signer = CFOEd25519Signer()
    env = signer.sign_approval(
        approval_id="cfo_app_01",
        entity_id="inv_ent_998",
        amount_inr=125000.0,
        decision="APPROVED",
        approver_id="cfo@omnirevive.io",
        signed_at=1795674000.0,
    )
    assert CFOEd25519Signer.verify_approval(env) is True

    tampered = SignedCFOApproval(
        approval_id=env.approval_id,
        entity_id=env.entity_id,
        amount_inr=999999.0,
        decision=env.decision,
        approver_id=env.approver_id,
        signed_at=env.signed_at,
        signature_b64=env.signature_b64,
        public_key_b64=env.public_key_b64,
    )
    assert CFOEd25519Signer.verify_approval(tampered) is False


def test_multiregion_cas_lock_storm_and_expiry():
    coord = MultiRegionCASCoordinator(default_ttl_seconds=60.0)

    def attempt(idx: int):
        return coord.acquire_quorum_lock("pay_storm_001", f"worker_{idx}")[0]

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(attempt, range(50)))

    assert results.count(True) == 1
    assert results.count(False) == 49

    # Wrong owner cannot release
    assert coord.release_quorum_lock("pay_storm_001", "intruder") is False
    # Correct owner releases
    # Find winning worker or test TTL expiry directly
    acquired_after_ttl, token2 = coord.acquire_quorum_lock(
        "pay_storm_001", "worker_recovery", now=time_future()
    )
    assert acquired_after_ttl is True
    assert token2 == 2


def time_future() -> float:
    import time

    return time.monotonic() + 120.0
