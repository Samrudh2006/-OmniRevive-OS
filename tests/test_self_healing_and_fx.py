"""
Test Suite for Autonomous Self-Healing Code Synthesizer & Cross-Border FX Arbitrage
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from autonomous_ai_company_os.self_healing import self_healing_synthesizer
from backend.app.gateways.fx_arbitrage_engine import fx_arbitrage_engine

client = TestClient(app)

def test_self_healing_synthesizer_drift_and_patch():
    # 1. Detect schema anomaly
    anomaly = self_healing_synthesizer.detect_schema_drift(
        gateway_name="RAZORPAY",
        sent_payload={"charge_id": "ch_mock_101", "amount": 5000.0},
        received_response={"error": "Deprecated parameter: charge_id is missing required parameter payment_intent_id"},
        http_status=422
    )
    assert anomaly is not None
    assert anomaly["drift_type"] == "FIELD_NAME_DRIFT"

    # 2. Synthesize and apply patch
    repair = self_healing_synthesizer.synthesize_and_apply_remediation(anomaly, dry_run=False)
    assert repair["status"] == "PATCH_DEPLOYED_LIVE"
    assert "patched_payload_transformer" in repair["synthesized_code"]
    assert repair["sandbox_verification"]["status"] == "PASSED"
    
    patch_id = repair["patch_id"]
    assert patch_id in self_healing_synthesizer.registry.active_patches

    # 3. Test rollback
    rolled_back = self_healing_synthesizer.registry.rollback_patch(patch_id)
    assert rolled_back is True
    assert patch_id not in self_healing_synthesizer.registry.active_patches

def test_fx_arbitrage_engine_spot_and_van():
    # 1. Spot FX and 7d forward rate
    usd_rate = fx_arbitrage_engine.get_spot_fx_rate("USD")
    assert usd_rate["currency"] == "USD"
    assert usd_rate["spot_rate_inr"] > 80.0
    assert usd_rate["hedged_7d_forward_inr"] >= usd_rate["spot_rate_inr"]

    # 2. Localized VAN Generation for USD
    van_usd = fx_arbitrage_engine.generate_localized_van("USD", "Acme Enterprise Corp", 500.0)
    assert van_usd["currency"] == "USD"
    assert "routing_number_aba" in van_usd["virtual_account"]
    assert van_usd["virtual_account"]["rail"] == "US_ACH_FEDNOW"

    # 3. Localized VAN Generation for EUR
    van_eur = fx_arbitrage_engine.generate_localized_van("EUR", "Berlin Fintech GmbH", 1200.0)
    assert van_eur["currency"] == "EUR"
    assert "iban" in van_eur["virtual_account"]
    assert van_eur["virtual_account"]["rail"] == "SEPA_INSTANT"

def test_fx_arbitrage_comparison_and_savings():
    arbitrage = fx_arbitrage_engine.evaluate_cross_border_arbitrage(
        amount_foreign=1000.0,
        currency="USD",
        customer_name="Global Enterprise Client"
    )
    assert arbitrage["currency"] == "USD"
    assert arbitrage["gross_equivalent_inr"] > 80000.0
    assert arbitrage["optimal_rail_selected"] == "WISE_VAN_B2B"
    assert arbitrage["arbitrage_savings_inr"] > 0
    assert len(arbitrage["all_rail_comparisons"]) == 4

def test_fx_and_self_healing_fastapi_endpoints():
    # 1. FX Arbitrage endpoint
    res_fx = client.post("/api/v1/gateways/fx-arbitrage", json={
        "amount_foreign": 250.0,
        "currency": "EUR",
        "customer_name": "Zurich Global Client"
    })
    assert res_fx.status_code == 200
    assert res_fx.json()["success"] is True
    assert "optimal_rail_selected" in res_fx.json()["data"]

    # 2. FX Rates endpoint
    res_rates = client.get("/api/v1/gateways/fx-rates")
    assert res_rates.status_code == 200
    assert "USD" in res_rates.json()["data"]
    assert "EUR" in res_rates.json()["data"]

    # 3. Self-healing remediation endpoint
    res_heal = client.post("/api/v1/gateways/self-healing/remediate", json={
        "gateway_name": "STRIPE",
        "http_status": 422,
        "error_message": "Deprecated field charge_id"
    })
    assert res_heal.status_code == 200
    assert res_heal.json()["success"] is True

    # 4. Self-healing active patches endpoint
    res_patches = client.get("/api/v1/gateways/self-healing/patches")
    assert res_patches.status_code == 200
    assert "active_patches" in res_patches.json()
