"""
Comprehensive Test Suite for OmniRevive-OS Advanced Research Engines:
- Contextual Multi-Armed Bandits (LinUCB & Thompson Sampling)
- Causal Uplift & Double-ML Intervention Optimization
- Conformal Prediction Risk-Bounded Intervals
- Standalone RFC 6962 Merkle Proofs & Offline Cryptographic Verification
- Autonomous C-Suite Swarm Debate Protocol (Brahma Style)
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.contextual_bandit import contextual_bandit_router, ContextualMultiRailRouter
from backend.app.causal_uplift import causal_uplift_optimizer
from backend.app.conformal_predictor import conformal_predictor
from backend.app.merkle_proof import CompactMerkleTree, verify_merkle_inclusion_proof
from autonomous_ai_company_os.c_suite import c_suite_swarm_engine

client = TestClient(app)

def test_contextual_bandit_linucb_and_feedback():
    router = ContextualMultiRailRouter(alpha=0.5)
    decision = router.select_optimal_rail(amount_inr=5000.0, bank_issuer="HDFC", attempt_number=1, strategy="LINUCB")
    
    assert "selected_rail" in decision
    assert decision["selected_rail"] in ["RAZORPAY", "JUSPAY", "PHONEPE", "CASHFREE", "STRIPE"]
    assert decision["ucb_score"] > 0
    assert len(decision["fallback_rails"]) >= 2

    # Test feedback update
    router.record_feedback(
        rail=decision["selected_rail"],
        amount_inr=5000.0,
        bank_issuer="HDFC",
        attempt_number=1,
        success=True,
        latency_ms=85.0
    )
    assert router.linucb_arms[decision["selected_rail"]].total_trials >= 2

def test_contextual_bandit_thompson_sampling():
    router = ContextualMultiRailRouter()
    decision = router.select_optimal_rail(amount_inr=75000.0, bank_issuer="ICICI", attempt_number=1, strategy="THOMPSON")
    assert decision["strategy"] == "THOMPSON"
    assert "selected_rail" in decision
    assert decision["expected_success_rate"] > 0

def test_causal_uplift_optimization():
    res = causal_uplift_optimizer.select_optimal_intervention(
        amount_inr=3500.0,
        failure_class="USER_DROPOUT",
        attempt_count=1,
        bank_issuer="HDFC"
    )
    assert "optimal_intervention" in res
    assert res["optimal_intervention"] in ["NO_INTERVENTION", "WHATSAPP_QR", "DISCOUNT_5PCT", "DISCOUNT_10PCT", "AI_VOICE_CALL"]
    assert "all_evaluations" in res
    assert len(res["all_evaluations"]) == 5
    assert res["expected_incremental_gain_inr"] >= 0

def test_conformal_prediction_intervals():
    bounds = conformal_predictor.predict_recovery_interval(
        predicted_median_seconds=45.0,
        bank_issuer="HDFC",
        failure_class="TRANSIENT_GATEWAY",
        confidence_level=0.90
    )
    assert bounds["confidence_level"] == 0.90
    assert bounds["lower_bound_seconds"] < bounds["upper_bound_seconds"]
    assert bounds["margin_of_error_seconds"] > 0
    assert "Coverage >= 90%" in bounds["statistical_guarantee"]

    lower_bound_res = conformal_predictor.predict_success_rate_lower_bound(nominal_prob=0.88, confidence_level=0.95)
    assert lower_bound_res["guaranteed_lower_bound"] <= 0.88
    assert lower_bound_res["guaranteed_lower_bound"] > 0.50

def test_merkle_inclusion_proof_and_offline_verification():
    leaves = [
        "RECOVERY_RESOLVED:pay_101:1499.0",
        "RECOVERY_RESOLVED:pay_102:2499.0",
        "RECOVERY_RESOLVED:pay_103:999.0",
        "RECOVERY_RESOLVED:pay_104:45000.0"
    ]
    tree = CompactMerkleTree(leaves)
    assert len(tree.root_hash) == 64
    
    proof = tree.get_audit_proof(1)
    assert proof["leaf_index"] == 1
    assert proof["merkle_root"] == tree.root_hash

    # Valid proof verification
    is_valid, msg = verify_merkle_inclusion_proof(proof)
    assert is_valid is True
    assert "Cryptographic proof verified" in msg

    # Tampered proof verification
    tampered_proof = dict(proof)
    tampered_proof["leaf_hash"] = "0000000000000000000000000000000000000000000000000000000000000000"
    is_tampered_valid, tampered_msg = verify_merkle_inclusion_proof(tampered_proof)
    assert is_tampered_valid is False

def test_autonomous_c_suite_swarm_debate():
    tx_context = {
        "amount_inr": 25000.0,
        "bank_issuer": "HDFC",
        "preferred_language": "te-IN",
        "attempt_number": 2
    }
    debate = c_suite_swarm_engine.run_executive_debate(tx_context)
    assert debate["status"] == "CONSENSUS_REACHED"
    assert debate["consensus_score"] > 0.80
    assert len(debate["debate_rounds"][0]["executive_opinions"]) == 4
    assert debate["governance"]["aws_cedar_verified"] is True

def test_fastapi_endpoints_integration():
    # 1. Bandit Route
    res_b = client.post("/api/v1/gateways/bandit-route", json={
        "amount_inr": 12000.0,
        "bank_issuer": "ICICI",
        "attempt_number": 1,
        "strategy": "LINUCB"
    })
    assert res_b.status_code == 200
    assert res_b.json()["success"] is True

    # 2. Causal Uplift
    res_u = client.post("/api/v1/recovery/causal-uplift", json={
        "amount_inr": 4500.0,
        "failure_class": "USER_DROPOUT"
    })
    assert res_u.status_code == 200
    assert res_u.json()["success"] is True

    # 3. Conformal Predict
    res_c = client.post("/api/v1/recovery/conformal-predict", json={
        "predicted_median_seconds": 35.0,
        "bank_issuer": "HDFC",
        "confidence_level": 0.95
    })
    assert res_c.status_code == 200
    assert res_c.json()["success"] is True

    # 4. Merkle Proof
    res_p = client.get("/api/v1/audit/proof/pay_test_api_99")
    assert res_p.status_code == 200
    proof_data = res_p.json()["proof"]
    
    # 5. Merkle Verify
    res_v = client.post("/api/v1/audit/verify-proof", json=proof_data)
    assert res_v.status_code == 200
    assert res_v.json()["is_valid"] is True

    # 6. C-Suite Debate
    res_d = client.post("/agency/c-suite/debate?amount_inr=18000&bank_issuer=HDFC&preferred_language=te-IN")
    assert res_d.status_code == 200
    assert res_d.json()["success"] is True
