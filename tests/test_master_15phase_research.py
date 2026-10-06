"""
OmniRevive-OS :: Unified 15-Phase Master Research Pipeline Test Suite
=====================================================================
Tests the complete unified 15-phase research diagnostic & recovery lifecycle.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.research.master_orchestrator import master_research_orchestrator

client = TestClient(app)

def test_master_15phase_orchestrator_execution():
    """Verify master orchestrator executes all 15 phases cleanly."""
    res = master_research_orchestrator.run_unified_15phase_cycle(
        transaction_id="tx_master_test_100",
        amount_inr=125000.0,
        bank_rail="HDFC",
        error_type="timeout",
        merchant_id="merchant_enterprise_test"
    )
    assert res["overall_status"] == "ALL_15_PHASES_VERIFIED_OPTIMAL"
    assert res["amount_inr"] == 125000.0
    assert len(res["phases_summary"]) == 15
    assert res["phases_summary"]["phase_01_pqc"]["quantum_safe"] is True
    assert res["phases_summary"]["phase_04_zk_snark"]["status"] == "VALID_SNARK_PROOF"
    assert res["phases_summary"]["phase_05_safe_rl"]["selected_action"] is not None
    assert res["phases_summary"]["phase_13_cbdc_escrow"]["offline_state"] == "LOCKED_IN_ENCLAVE"


def test_master_15phase_fastapi_endpoint():
    """Verify POST /api/v1/research/master-15phase-cycle returns full 15-phase envelope."""
    payload = {
        "transaction_id": "tx_api_master_1",
        "amount_inr": 95000.0,
        "bank_rail": "ICICI",
        "error_type": "mandate_expired",
        "merchant_id": "merchant_flipkart_1"
    }
    resp = client.post("/api/v1/research/master-15phase-cycle", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["overall_status"] == "ALL_15_PHASES_VERIFIED_OPTIMAL"
    assert len(data["data"]["phases_summary"]) == 15
