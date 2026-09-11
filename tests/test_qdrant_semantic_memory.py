import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.semantic_memory import (
    SemanticMemoryEngine,
    generate_dense_embedding,
    VECTOR_DIMENSION,
    COLLECTION_NAME
)
from backend.app.diagnostic_engine import diagnostic_engine

client = TestClient(app)

def test_semantic_memory_initialization_and_telemetry():
    engine = SemanticMemoryEngine()
    telemetry = engine.get_memory_telemetry()
    assert telemetry["collection_name"] == COLLECTION_NAME
    assert telemetry["vector_dimension"] == VECTOR_DIMENSION
    assert telemetry["distance_metric"] == "Cosine"
    assert telemetry["indexed_precedents_count"] >= 8
    assert telemetry["status"] == "HEALTHY"
    assert "SBI" in telemetry["supported_banks"]
    assert "UPI" in telemetry["supported_rails"]

def test_dense_embedding_vector_properties():
    vec1 = generate_dense_embedding("GATEWAY_TIMEOUT", "SBI", "UPI", 2500.0, 1, 14, "DOWN")
    vec2 = generate_dense_embedding("INSUFFICIENT_FUNDS", "HDFC", "CARD", 500.0, 1, 10, "UP")
    
    assert vec1.shape == (VECTOR_DIMENSION,)
    assert vec2.shape == (VECTOR_DIMENSION,)
    assert np.isclose(np.linalg.norm(vec1), 1.0, atol=1e-3)
    assert np.isclose(np.linalg.norm(vec2), 1.0, atol=1e-3)
    
    # Dissimilar vectors should have low cosine similarity
    cos_sim = float(np.dot(vec1, vec2))
    assert cos_sim < 0.70

def test_precedent_seeding_and_retrieval():
    engine = SemanticMemoryEngine()
    results = engine.search_precedents(
        error_code="GATEWAY_TIMEOUT",
        bank="SBI",
        rail="UPI",
        amount=2500.0,
        switch_status="DOWN",
        top_k=3
    )
    assert len(results) > 0
    top = results[0]
    assert top["similarity_score"] >= 0.70
    assert "DEFER_WEIBULL" in top["strategy"] or "GATEWAY" in top["matched_error"]
    assert top["historical_recovery_rate"] > 0.80

def test_mandate_expiry_vector_retrieval():
    engine = SemanticMemoryEngine()
    results = engine.search_precedents(
        error_code="U30_MANDATE_EXPIRED",
        bank="HDFC",
        rail="UPI",
        amount=4999.0,
        switch_status="UP",
        top_k=1
    )
    assert len(results) >= 1
    top = results[0]
    assert "mandate" in top["precedent_id"].lower() or "mandate" in top["strategy"].lower()

def test_insufficient_funds_nach_retrieval():
    engine = SemanticMemoryEngine()
    results = engine.search_precedents(
        error_code="INSUFFICIENT_FUNDS",
        bank="AXIS",
        rail="NACH",
        amount=12500.0,
        top_k=1
    )
    assert len(results) >= 1
    assert "SALARY" in results[0]["strategy"] or "NACH" in results[0]["precedent_id"]

def test_closed_loop_feedback_upsert():
    engine = SemanticMemoryEngine()
    test_case_id = "test_feedback_case_999"
    success = engine.record_recovery_feedback(
        case_id=test_case_id,
        error_code="CARD_CRYPTOGRAM_INVALID",
        bank="ICICI",
        rail="CARD",
        amount=3500.0,
        strategy_applied="REQUEST_FRESH_CARD_TOKEN_CRYPTOGRAM",
        recovered=True,
        recovery_latency_sec=42,
        tenant_id="tenant_alpha"
    )
    assert success is True
    
    # Search for this newly learned outcome
    matches = engine.search_precedents(
        error_code="CARD_CRYPTOGRAM_INVALID",
        bank="ICICI",
        rail="CARD",
        amount=3500.0,
        top_k=5,
        tenant_id="tenant_alpha"
    )
    found = any(m["precedent_id"] == f"outcome_{test_case_id}_1" for m in matches)
    assert found is True

def test_tenant_isolation_in_semantic_memory():
    engine = SemanticMemoryEngine()
    # Insert private precedent for Tenant X
    engine.record_recovery_feedback(
        case_id="case_private_tenant_x",
        error_code="VELOCITY_BLOCKED",
        bank="YES",
        rail="UPI",
        amount=99000.0,
        strategy_applied="CUSTOM_TENANT_X_STRATEGY",
        recovered=True,
        recovery_latency_sec=100,
        tenant_id="tenant_secret_x"
    )
    
    # Tenant Y searches - should NOT see Tenant X's private precedent
    matches_y = engine.search_precedents(
        error_code="VELOCITY_BLOCKED",
        bank="YES",
        rail="UPI",
        amount=99000.0,
        top_k=5,
        tenant_id="tenant_secret_y"
    )
    for m in matches_y:
        assert m["precedent_id"] != "outcome_case_private_tenant_x_1"

def test_memory_api_telemetry_endpoint():
    response = client.get("/api/v1/memory/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["collection_name"] == COLLECTION_NAME
    assert data["vector_dimension"] == 64

def test_memory_api_search_endpoint():
    response = client.get(
        "/api/v1/memory/precedents",
        params={
            "error_code": "GATEWAY_TIMEOUT",
            "bank": "SBI",
            "rail": "UPI",
            "amount": 2500.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["matches_count"] > 0
    assert len(data["precedents"]) > 0

def test_memory_api_feedback_post_endpoint():
    payload = {
        "case_id": "api_test_case_123",
        "error_code": "GATEWAY_TIMEOUT",
        "bank": "SBI",
        "rail": "UPI",
        "amount": 1500.0,
        "strategy_applied": "DEFER_WEIBULL_45M_AND_WHATSAPP_UPI",
        "recovered": True,
        "recovery_latency_sec": 1200,
        "tenant_id": "test_tenant"
    }
    response = client.post("/api/v1/memory/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RECORDED"
    assert data["vector_memory_updated"] is True

def test_diagnostic_engine_integration_with_qdrant():
    proposal = diagnostic_engine.diagnose(
        payment_id="pay_qdrant_test_01",
        amount=2500.0,
        error_code="GATEWAY_TIMEOUT",
        error_description="SBI switch timed out on core debit",
        metadata={"issuing_bank": "SBI", "payment_rail": "UPI"}
    )
    assert proposal.payment_id == "pay_qdrant_test_01"
    assert proposal.confidence >= 0.85
    # Verification that Qdrant precedent was queried and matched
    has_qdrant_reason = any("QDRANT_PRECEDENT_MATCH" in r for r in proposal.reason_codes)
    assert has_qdrant_reason or "Qdrant Advisory" in proposal.diagnostic_summary

# -----------------------------------------------------------------------------
# ADVERSARIAL & NEGATIVE SAFETY TESTS (Grounded in Financial Guardrail Principles)
# -----------------------------------------------------------------------------
def test_negative_qdrant_does_not_inflate_confidence():
    """
    CRITICAL FINANCIAL SAFETY TEST:
    A high historical recovery rate in Qdrant memory MUST NOT artificially
    inflate the Diagnostic Engine's confidence for a new transaction.
    """
    proposal = diagnostic_engine.diagnose(
        payment_id="pay_conf_test_01",
        amount=1200.0,
        error_code="INSUFFICIENT_FUNDS",
        error_description="Soft balance decline on customer card",
        metadata={"issuing_bank": "HDFC", "payment_rail": "CARD"}
    )
    # The baseline confidence for INSUFFICIENT_FUNDS in ERROR_CODE_MAP is 0.92.
    # It must NOT be inflated to 0.98 just because historical recovery was high.
    assert proposal.confidence == 0.92

def test_negative_low_similarity_rejection():
    """
    An obscure, completely unseen error code must NOT falsely match
    unrelated historical banking precedents.
    """
    engine = SemanticMemoryEngine()
    evidence = engine.aggregate_precedent_evidence(
        error_code="ERR_QUANTUM_COHERENCE_LOST",
        bank="NON_EXISTENT_BANK",
        rail="SATELLITE_RAIL",
        amount=500.0,
        min_similarity=0.85
    )
    assert evidence["evidence_available"] is False
    assert evidence["matches_count"] == 0
    assert evidence["evidence_strength"] == "NONE"

def test_negative_amount_scale_disparity_warning():
    """
    If a transaction is high-value (>₹50,000), the system must flag an
    AMOUNT_SCALE_DISPARITY_WARNING rather than blindly trusting micro-ticket recovery actions.
    """
    proposal = diagnostic_engine.diagnose(
        payment_id="pay_high_value_scale_01",
        amount=85000.0,
        error_code="GATEWAY_TIMEOUT",
        error_description="SBI gateway timeout on high value transfer",
        metadata={"issuing_bank": "SBI", "payment_rail": "UPI"}
    )
    has_warning = any("QDRANT_AMOUNT_SCALE_DISPARITY_WARNING" in r for r in proposal.reason_codes)
    assert has_warning is True

def test_negative_qdrant_failure_graceful_degradation(monkeypatch):
    """
    If Qdrant cluster fails or raises a socket error, the diagnostic pipeline
    MUST degrade gracefully without crashing or interrupting payment flow.
    """
    from backend.app import semantic_memory
    def mock_fail(*args, **kwargs):
        raise RuntimeError("Simulated Qdrant cluster socket termination")

    monkeypatch.setattr(semantic_memory.semantic_memory_engine, "aggregate_precedent_evidence", mock_fail)
    
    proposal = diagnostic_engine.diagnose(
        payment_id="pay_fallback_01",
        amount=1500.0,
        error_code="GATEWAY_TIMEOUT",
        error_description="SBI timeout during network fault"
    )
    assert proposal.payment_id == "pay_fallback_01"
    assert proposal.failure_class == "TRANSIENT_GATEWAY"
    assert proposal.confidence >= 0.50

def test_negative_precedent_cannot_override_policy_quiet_hours():
    """
    Even if Qdrant precedent suggests instant messaging, TRAI quiet hours
    (21:00 to 09:00 IST) MUST unconditionally defer communication.
    """
    from backend.app.policy_engine import policy_engine
    
    proposal = diagnostic_engine.diagnose(
        payment_id="pay_trai_test_01",
        amount=1500.0,
        error_code="OTP_EXPIRED",
        error_description="User dropped off during OTP"
    )
    # Test during quiet hours: 23:00 IST
    # 23:00 IST = 17:30 UTC
    import time
    fake_epoch = 1787333400.0 # corresponds to 23:00 IST
    verdict = policy_engine.evaluate(
        diagnosis=proposal,
        attempt_count=1,
        channel="WHATSAPP",
        current_epoch=fake_epoch
    )
    assert verdict.verdict == "DEFERRED_QUIET_HOURS"
    assert verdict.scheduled_epoch is not None

def test_negative_precedent_cannot_override_max_retries():
    """
    Even if Qdrant precedent indicates high historical recovery rate,
    exceeding 3 retries MUST unconditionally suppress execution.
    """
    from backend.app.policy_engine import policy_engine
    
    proposal = diagnostic_engine.diagnose(
        payment_id="pay_retry_limit_01",
        amount=1500.0,
        error_code="GATEWAY_TIMEOUT",
        error_description="SBI core gateway timeout"
    )
    verdict = policy_engine.evaluate(
        diagnosis=proposal,
        attempt_count=4 # Exceeds limit of 3
    )
    assert verdict.verdict == "SUPPRESSED"
    assert any("MAX_RETRIES_EXCEEDED" in r for r in verdict.violated_rules)

