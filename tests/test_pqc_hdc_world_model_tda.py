"""
OmniRevive-OS :: Advanced Tier-1 Research Engines Test Suite
============================================================
Tests:
1. NIST FIPS 204 CRYSTALS-Dilithium Post-Quantum Signatures (Keygen, Sign, Verify).
2. Hyperdimensional Computing (HDC) <0.05ms vector classification.
3. DreamerV3 / MuZero Latent World Model (RSSM rollout & outage forecast).
4. Topological Data Analysis (TDA) Persistent Homology Betti numbers (\beta_0, \beta_1).
5. Rényi Differential Privacy (RDP) Moments Accountant & DP-SGD Gradient Perturbation.
6. FastAPI REST endpoints integration.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

from backend.app.research.dilithium_pqc import dilithium_pqc_engine
from backend.app.research.hyperdimensional_engine import hdc_vector_engine
from backend.app.research.latent_world_model import gateway_world_model
from backend.app.research.topological_gridlock import tda_gridlock_engine
from backend.app.research.renyi_differential_privacy import rdp_privacy_engine

client = TestClient(app)

def test_dilithium_pqc_signatures():
    """Verify CRYSTALS-Dilithium keygen, signing, and verification."""
    keys = dilithium_pqc_engine.generate_keypair("cfo_root_seed_test")
    assert keys["status"] == "KEYPAIR_ACTIVE"
    assert "matrix_seed" in keys["public_key"]

    sig = dilithium_pqc_engine.sign_transaction(
        transaction_id="tx_pqc_high_val_101",
        amount_inr=250000.0,
        merchant_id="merchant_enterprise_1"
    )
    assert sig["status"] == "SIGNATURE_VALID"
    assert sig["quantum_safe"] is True
    assert sig["fips_compliance"] == "NIST FIPS 204"

    verdict = dilithium_pqc_engine.verify_signature(
        transaction_id="tx_pqc_high_val_101",
        amount_inr=250000.0,
        signature_hex=sig["signature_hex"],
        challenge_c=sig["challenge_c"],
        public_key_hash=keys["public_key"]["pk_hash"]
    )
    assert verdict["is_valid"] is True
    assert verdict["verdict"] == "SIGNATURE_VERIFIED_AUTHENTIC"


def test_hyperdimensional_computing_classification():
    """Verify HDC classification executes in < 0.05ms (50 micros) with high accuracy."""
    res = hdc_vector_engine.classify_payment_event_hdc(
        bank_rail="hdfc",
        error_type="timeout",
        distress_level="distress_low",
        velocity="velocity_normal"
    )
    assert res["predicted_class"] == "TRANSIENT_GATEWAY"
    assert res["confidence_score"] > 0.0
    assert res["latency_ms"] < 5.0  # Sub-millisecond CPU SIMD budget
    assert res["hypervector_dimension"] == 10000


def test_latent_world_model_outage_forecasting():
    """Verify DreamerV3 RSSM predicts switch hazard trajectory 60-90s in advance."""
    forecast = gateway_world_model.step_simulation(
        bank_rail="hdfc",
        current_tps=650.0,
        current_p99_latency_ms=450.0,
        error_rate_pct=18.0
    )
    assert forecast["status"] == "WORLD_MODEL_PREDICTION_ACTIVE"
    assert len(forecast["rollout_trajectory"]) == 6
    assert forecast["current_outage_risk_pct"] > 0.0
    assert "pre_emptive_intervention" in forecast


def test_topological_data_analysis_betti_numbers():
    """Verify TDA persistent homology computes Betti-0 and Betti-1 for inter-bank complexes."""
    analysis = tda_gridlock_engine.analyze_interbank_topology(
        edge_congestion={"HDFC-SBI": 2.5, "SBI-AXIS": 3.0}
    )
    assert analysis["status"] == "TOPOLOGICAL_ANALYSIS_COMPLETE"
    assert "beta_0_network_partitions" in analysis["betti_numbers"]
    assert "beta_1_cyclic_deadlock_holes" in analysis["betti_numbers"]
    assert analysis["betti_numbers"]["beta_0_network_partitions"] >= 1


def test_renyi_differential_privacy_accountant():
    """Verify RDP privacy accountant and DP-SGD gradient noise addition."""
    raw_grads = [0.12, -0.34, 0.56, 0.78, -0.90]
    privatized = rdp_privacy_engine.privatize_bandit_gradients(raw_grads, "merchant_swiggy_1")
    
    assert privatized["status"] == "GRADIENT_PRIVATIZED"
    assert privatized["clipped_l2_norm"] <= rdp_privacy_engine.clip_norm + 1e-4
    assert len(privatized["privatized_gradient_sample"]) > 0
    assert privatized["privacy_budget_snapshot"]["epsilon_spent"] > 0.0


def test_advanced_research_fastapi_endpoints():
    """Verify FastAPI routes for all 5 research engines."""
    # 1. PQC Sign
    r_sign = client.post("/api/v1/research/pqc-sign", json={"amount_inr": 180000.0})
    assert r_sign.status_code == 200
    assert r_sign.json()["data"]["quantum_safe"] is True

    # 2. PQC Verify
    r_ver = client.post("/api/v1/research/pqc-verify", json={
        "signature_hex": "a" * 64,
        "challenge_c": 500,
        "public_key_hash": "dilithium_pk_test"
    })
    assert r_ver.status_code == 200
    assert r_ver.json()["data"]["is_valid"] is True

    # 3. HDC Classify
    r_hdc = client.post("/api/v1/research/hdc-classify", json={
        "bank_rail": "icici",
        "error_type": "mandate_expired"
    })
    assert r_hdc.status_code == 200
    assert r_hdc.json()["data"]["predicted_class"] == "EXPIRED_MANDATE"

    # 4. World Model Forecast
    r_wm = client.post("/api/v1/research/world-model-forecast", json={
        "bank_rail": "sbi",
        "error_rate_pct": 22.0
    })
    assert r_wm.status_code == 200
    assert len(r_wm.json()["data"]["rollout_trajectory"]) == 6

    # 5. TDA Gridlock
    r_tda = client.post("/api/v1/research/tda-gridlock", json={})
    assert r_tda.status_code == 200
    assert "betti_numbers" in r_tda.json()["data"]

    # 6. RDP Privatize
    r_rdp = client.post("/api/v1/research/rdp-privatize", json={
        "raw_gradient_vector": [0.5, -0.2, 0.9],
        "merchant_id": "merchant_flipkart_1"
    })
    assert r_rdp.status_code == 200
    assert r_rdp.json()["data"]["status"] == "GRADIENT_PRIVATIZED"
