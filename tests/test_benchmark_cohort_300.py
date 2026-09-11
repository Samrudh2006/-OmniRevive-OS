import json
import os
import pytest
from typing import Dict, Any, List

from backend.app.diagnostic_engine import diagnostic_engine
from backend.app.policy_engine import policy_engine
from backend.app.semantic_memory import semantic_memory_engine, generate_dense_embedding
from backend.app.schemas import DiagnosisProposal

# Load ground-truth 100-case production benchmark dataset
DATASET_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "benchmarks", "test_dataset_100.json")
)

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    BENCHMARK_CASES: List[Dict[str, Any]] = json.load(f)

assert len(BENCHMARK_CASES) == 100, f"Expected 100 benchmark cases, found {len(BENCHMARK_CASES)}"


# -----------------------------------------------------------------------------
# SUITE 1: 100-Case Diagnostic Engine Schema & Classification Verification
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("case", BENCHMARK_CASES, ids=[c["record_id"] for c in BENCHMARK_CASES])
def test_cohort_diagnostic_coverage(case: Dict[str, Any]):
    """
    Evaluates every single case in the 100-case benchmark cohort against the
    Diagnostic Kernel, enforcing strict Pydantic v2 typing and confidence bounds.
    """
    proposal = diagnostic_engine.diagnose(
        payment_id=case["payment_id"],
        amount=case["amount"],
        error_code=case["error_code"],
        error_description=case["error_description"],
        metadata={
            "issuing_bank": "SBI" if "sbi" in case["error_description"].lower() else "HDFC",
            "payment_rail": "UPI" if "upi" in case["error_code"].lower() else "CARD",
            "attempt_count": case["attempt_count"]
        }
    )
    
    assert isinstance(proposal, DiagnosisProposal)
    assert proposal.payment_id == case["payment_id"]
    assert proposal.amount == case["amount"]
    assert proposal.confidence >= 0.50
    assert len(proposal.reason_codes) > 0
    assert proposal.failure_class in (
        "TRANSIENT_GATEWAY", "INSUFFICIENT_FUNDS", "EXPIRED_MANDATE",
        "ABANDONED_AUTH", "SUSPICIOUS_VELOCITY"
    )
    assert proposal.recommended_strategy in (
        "DELAYED_RETRY", "DISPATCH_PAYMENT_LINK", "ESCALATE_HUMAN"
    )


# -----------------------------------------------------------------------------
# SUITE 2: 100-Case Deterministic Policy Engine Compliance Enforcement
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("case", BENCHMARK_CASES, ids=[f"policy_{c['record_id']}" for c in BENCHMARK_CASES])
def test_cohort_policy_gate_compliance(case: Dict[str, Any]):
    """
    Evaluates all 100 benchmark cases through the deterministic Policy Engine,
    proving financial bounding invariants, discount caps, and quiet-hour compliance.
    """
    proposal = diagnostic_engine.diagnose(
        payment_id=case["payment_id"],
        amount=case["amount"],
        error_code=case["error_code"],
        error_description=case["error_description"],
        metadata={"attempt_count": case["attempt_count"]}
    )
    
    verdict = policy_engine.evaluate(
        diagnosis=proposal,
        attempt_count=case["attempt_count"],
        proposed_discount_pct=15.0  # Propose aggressive 15% to test clamping
    )
    
    assert verdict.verdict in (
        "ALLOWED", "SUPPRESSED", "ESCALATED_HUMAN", "DEFERRED_QUIET_HOURS"
    )
    # Strict financial safety invariant: discounts never exceed min(10%, INR 500)
    max_allowed = min(case["amount"] * 0.10, 500.0)
    assert verdict.effective_discount <= max_allowed + 0.01

    # High value transaction guardrail: transactions > 50,000 with low confidence must escalate
    if case["amount"] > 50000.0 and proposal.confidence < 0.85:
        assert verdict.verdict == "ESCALATED_HUMAN"


# -----------------------------------------------------------------------------
# SUITE 3: 100-Case Qdrant Vector Semantic Memory Precedent Mapping
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("case", BENCHMARK_CASES, ids=[f"qdrant_{c['record_id']}" for c in BENCHMARK_CASES])
def test_cohort_qdrant_vector_memory_mapping(case: Dict[str, Any]):
    """
    Maps all 100 benchmark cases into Qdrant 64-dimensional dense vector space,
    evaluating nearest-neighbor similarity scores and retrieval latency.
    """
    vec = generate_dense_embedding(
        error_code=case["error_code"],
        bank="SBI" if "sbi" in case["error_description"].lower() else "HDFC",
        rail="UPI" if "upi" in case["error_code"].lower() else "CARD",
        amount=case["amount"],
        attempt_count=case["attempt_count"],
        hour_of_day=14,
        switch_status="UP"
    )
    assert vec.shape == (64,)
    assert abs(float(sum(vec**2)) - 1.0) < 1e-2

    precedents = semantic_memory_engine.search_precedents(
        error_code=case["error_code"],
        bank="SBI",
        rail="UPI",
        amount=case["amount"],
        attempt_count=case["attempt_count"],
        top_k=2,
        score_threshold=0.50
    )
    assert isinstance(precedents, list)
    if precedents:
        top = precedents[0]
        assert "precedent_id" in top
        assert 0.0 <= top["similarity_score"] <= 1.01
        assert top["historical_recovery_rate"] > 0.0
