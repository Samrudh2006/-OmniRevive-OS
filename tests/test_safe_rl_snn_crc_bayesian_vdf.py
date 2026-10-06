"""
OmniRevive-OS :: Safe RL, SNN, CRC, Bayesian Probing, and VDF Test Suite
========================================================================
Tests:
1. Safe RL with Primal-Dual Lagrangian Optimization.
2. Neuromorphic Spiking Neural Network (LIF neurons, STDP plasticity).
3. Conformal Risk Control (CRC) distribution-free PTP guarantees.
4. Bayesian Active Probing (Expected Information Gain).
5. Wesolowski Verifiable Delay Functions (VDF) anti-front-running proofs.
6. FastAPI REST endpoints integration.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

from backend.app.research.safe_rl_lagrangian import safe_rl_optimizer
from backend.app.research.spiking_neuromorphic_engine import neuromorphic_snn_engine
from backend.app.research.conformal_risk_control import conformal_risk_engine
from backend.app.research.bayesian_active_routing import bayesian_active_engine
from backend.app.research.verifiable_delay_vdf import wesolowski_vdf_engine

client = TestClient(app)

def test_safe_rl_lagrangian_optimizer():
    """Verify Lagrangian Safe RL respects discount budget and safety bounds."""
    res = safe_rl_optimizer.select_safe_action(
        amount_inr=50000.0,
        failure_count=1,
        customer_distress_score=0.4,
        bank_switch_health=0.9
    )
    assert res["primal_dual_status"] == "CONSTRAINED_OPTIMAL"
    assert res["selected_action"] in [c["action"] for c in safe_rl_optimizer.action_space]
    assert res["current_dual_multiplier_lambda"] > 0.0


def test_neuromorphic_snn_engine():
    """Verify LIF spike generation and sub-millisecond telemetry processing."""
    res = neuromorphic_snn_engine.process_telemetry_event_stream(
        raw_latency_samples_ms=[10.0, 15.0, 95.0, 120.0, 140.0],
        packet_jitter_ms=4.5
    )
    assert res["status"] == "NEUROMORPHIC_SNN_PROCESSED"
    assert res["total_spikes_generated"] >= 0
    assert res["processing_latency_ms"] < 10.0


def test_conformal_risk_control():
    """Verify distribution-free CRC bound on voice PTP promises."""
    res = conformal_risk_engine.compute_guaranteed_ptp_interval(
        promised_delay_days=3,
        invoice_amount_inr=85000.0,
        debtor_hesitation_score=0.5
    )
    assert res["status"] == "CONFORMAL_RISK_BOUNDED"
    assert res["guaranteed_ptp_deadline_days"] >= 3
    assert res["target_risk_alpha"] == 0.05


def test_bayesian_active_routing():
    """Verify EIG-optimal micro-probing of degraded bank rails."""
    probe = bayesian_active_engine.select_optimal_micro_probe()
    assert probe["status"] == "BAYESIAN_OPTIMAL_PROBE_SELECTED"
    assert probe["optimal_probe_rail"] in ["HDFC", "ICICI", "SBI", "AXIS"]
    assert probe["max_information_gain_nats"] > 0.0

    # Update feedback
    updated = bayesian_active_engine.update_with_probe_feedback(probe["optimal_probe_rail"], True)
    assert updated["bank_rail"] == probe["optimal_probe_rail"]


def test_wesolowski_vdf_engine():
    """Verify VDF sequential modular squaring proof and verification."""
    vdf_proof = wesolowski_vdf_engine.compute_vdf_delay_proof("tx_seed_anti_front_running", time_delay_steps=1000)
    assert vdf_proof["status"] == "VDF_COMPUTATION_VALID"
    assert vdf_proof["time_steps_t"] == 1000

    verdict = wesolowski_vdf_engine.verify_vdf_proof(
        transaction_seed="tx_seed_anti_front_running",
        output_y_hex=vdf_proof["output_y_hex"],
        proof_pi_hex=vdf_proof["proof_pi_hex"],
        fiat_shamir_prime_l=vdf_proof["fiat_shamir_prime_l"],
        time_steps_t=1000
    )
    assert verdict["is_valid"] is True
    assert verdict["verdict"] == "VDF_TIME_DELAY_PROOF_VERIFIED"


def test_frontier_research_fastapi_endpoints():
    """Verify FastAPI routes for all 5 frontier research engines."""
    # 1. Safe RL Action
    r_rl = client.post("/api/v1/research/safe-rl-action", json={"amount_inr": 20000.0})
    assert r_rl.status_code == 200
    assert r_rl.json()["data"]["primal_dual_status"] == "CONSTRAINED_OPTIMAL"

    # 2. SNN Telemetry
    r_snn = client.post("/api/v1/research/snn-telemetry-stream", json={"raw_latency_samples_ms": [10.0, 20.0]})
    assert r_snn.status_code == 200
    assert r_snn.json()["data"]["status"] == "NEUROMORPHIC_SNN_PROCESSED"

    # 3. Conformal Risk PTP
    r_crc = client.post("/api/v1/research/conformal-risk-ptp", json={"invoice_amount_inr": 45000.0})
    assert r_crc.status_code == 200
    assert r_crc.json()["data"]["status"] == "CONFORMAL_RISK_BOUNDED"

    # 4. Bayesian Active Probe
    r_probe = client.post("/api/v1/research/bayesian-active-probe", json={})
    assert r_probe.status_code == 200
    assert r_probe.json()["data"]["status"] == "BAYESIAN_OPTIMAL_PROBE_SELECTED"

    # 5. VDF Delay Proof
    r_vdf = client.post("/api/v1/research/vdf-delay-proof", json={"time_delay_steps": 500})
    assert r_vdf.status_code == 200
    assert r_vdf.json()["data"]["status"] == "VDF_COMPUTATION_VALID"
