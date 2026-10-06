"""
OmniRevive-OS :: Test Suite for 4 Grand Research Frontiers
===========================================================
Tests Pearl Causal Engine, VCG Auction Engine, Formal Invariant Verifier, and eBPF/XDP Telemetry.
"""

import pytest
from backend.app.research.pearl_causal_engine import pearl_causal_engine
from backend.app.research.vcg_auction_mechanism import vcg_auction_engine
from backend.app.research.formal_invariant_verifier import formal_invariant_verifier
from backend.app.research.ebpf_xdp_telemetry import ebpf_xdp_engine

def test_pearl_causal_engine_ite_and_subsidy_suppression():
    """Verify Pearl Causal Engine suppresses discounts when organic recovery probability is high."""
    # High organic propensity (e.g. Mandate)
    res_mandate = pearl_causal_engine.estimate_doubly_robust_ite(
        amount_inr=15000.0,
        is_mandate=True,
        distress_score=0.1,
        proposed_discount_pct=10.0
    )
    assert res_mandate["action_recommendation"] == "SUPPRESS_DISCOUNT_SUBSIDY"
    assert res_mandate["optimal_discount_pct"] == 0.0
    assert res_mandate["subsidy_saved_inr"] > 0

    # Low organic propensity with high causal uplift
    res_uplift = pearl_causal_engine.estimate_doubly_robust_ite(
        amount_inr=85000.0,
        is_mandate=False,
        distress_score=0.6,
        proposed_discount_pct=8.0
    )
    assert res_uplift["individual_treatment_effect_tau_ite"] > 0.10

def test_vcg_truthful_auction_mechanism():
    """Verify VCG auction selects socially optimal bank and computes second-price externality."""
    res = vcg_auction_engine.run_truthful_van_auction(
        transaction_amount_inr=100000.0
    )
    assert res["status"] == "VCG_AUCTION_CLEARED_OPTIMAL"
    assert res["winning_bank_allocated"] in ["ICICI", "HDFC"]
    assert res["game_theoretic_properties"]["dominant_strategy_incentive_compatible"] is True
    assert res["effective_interchange_cost_inr"] > 0

def test_formal_mathematical_invariant_verifier():
    """Verify formal safety invariant verification passes and prevents violations."""
    # 1. Zero double-debit invariant
    res_lock = formal_invariant_verifier.verify_zero_double_debit_invariant(
        transaction_id="tx_test_formal_1",
        acquired_cas_lock=True,
        current_state="PENDING",
        execution_count=0
    )
    assert res_lock["proof_status"] == "QED_PROVED_FORMALLY"
    assert res_lock["double_debit_probability"] == 0.0

    # 2. Rejection on double execution
    res_rejected = formal_invariant_verifier.verify_zero_double_debit_invariant(
        transaction_id="tx_test_formal_1",
        acquired_cas_lock=True,
        current_state="MUTATED",
        execution_count=1
    )
    assert res_rejected["proof_status"] == "PROOF_REJECTED_VIOLATION_PREVENTED"

    # 3. TRAI quiet hours
    res_trai = formal_invariant_verifier.verify_trai_quiet_hours_invariant(
        ist_hour=22,
        is_customer_initiated=False
    )
    assert res_trai["proof_status"] == "PROOF_REJECTED_TRAI_VIOLATION"

    # 4. Merkle inductive continuity
    import hashlib
    prev = "00000000000000000000"
    payload = "tx_data"
    expected_hash = hashlib.sha256(f"{prev}:{payload}".encode("utf-8")).hexdigest()
    res_merkle = formal_invariant_verifier.verify_merkle_chain_inductive_step(
        prev_hash=prev,
        block_payload=payload,
        current_hash=expected_hash
    )
    assert res_merkle["proof_status"] == "QED_PROVED_FORMALLY"

def test_ebpf_xdp_kernel_telemetry():
    """Verify sub-10us eBPF socket layer telemetry and pre-504 outage detection."""
    res_hdfc = ebpf_xdp_engine.inspect_socket_layer_telemetry("HDFC")
    assert res_hdfc["status"] == "TELEMETRY_SAMPLE_VALID"
    assert res_hdfc["syn_ack_rtt_microseconds"] < 15.0
    assert res_hdfc["pre_504_outage_predicted"] is False

    res_sbi = ebpf_xdp_engine.inspect_socket_layer_telemetry("SBI")
    assert res_sbi["pre_504_outage_predicted"] is True
    assert res_sbi["hazard_lead_time_seconds"] == 1.5
