import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.gateways.juspay_adapter import JuspayHyperSDKAdapter
from backend.app.gateways.phonepe_adapter import PhonePeSwitchAdapter
from backend.app.gateways.cred_adapter import CredPayAdapter
from backend.app.gateways.cashfree_adapter import CashfreeAdapter
from backend.app.gateways.neobank_adapter import NeobankMandateAdapter
from backend.app.gateways.stripe_adapter import StripeAdapter
from backend.app.gateways.multi_rail_router import MultiRailRouter

client = TestClient(app)

def test_juspay_adapter_link_and_switch():
    adapter = JuspayHyperSDKAdapter()
    res = adapter.create_recovery_link(
        payment_id="pay_jus_99182",
        amount=30000.0,
        customer_name="Aarav Mehta",
        customer_email="aarav@techcorp.in",
        customer_phone="+919876543210",
        discount_amount=500.0
    )
    assert res["success"] is True
    assert res["provider"] == "JUSPAY"
    assert res["selected_switch"] == "ICICI_SWITCH"
    assert "upi_intent_url" in res
    assert "sdk_payload" in res
    assert res["final_amount"] == 29500.0

def test_phonepe_adapter_qr_and_checksum():
    adapter = PhonePeSwitchAdapter()
    res = adapter.create_recovery_link(
        payment_id="pay_phpe_11223",
        amount=1200.0,
        customer_name="Priya Sharma",
        customer_email="priya@gmail.com",
        customer_phone="+919812345678"
    )
    assert res["success"] is True
    assert res["provider"] == "PHONEPE"
    assert res["upi_rail"] == "PHONEPE_YES_BANK_SWITCH"
    assert res["phonepe_intent_url"].startswith("phonepe://pay?")
    assert "x_verify_checksum" in res
    assert res["final_amount"] == 1200.0

def test_cred_pay_adapter_high_ticket_mutex():
    adapter = CredPayAdapter()
    res = adapter.create_recovery_link(
        payment_id="pay_cred_88319",
        amount=75000.0,
        customer_name="Rohan Varma",
        customer_email="rohan@clubcred.in",
        customer_phone="+919988776655",
        discount_amount=500.0
    )
    assert res["success"] is True
    assert res["provider"] == "CRED"
    assert res["member_tier"] == "CRED_BLACK_ELITE"
    assert res["concurrency_guarantee"] == "ATOMIC_CAS_MUTEX_0_DOUBLE_DEBIT"
    assert res["cred_intent_url"].startswith("cred://pay/collect?")
    assert res["final_amount"] == 74500.0

def test_cashfree_adapter_auto_collect_van():
    adapter = CashfreeAdapter()
    res = adapter.create_recovery_link(
        payment_id="pay_cf_55443",
        amount=45000.0,
        customer_name="Enterprise Client",
        customer_email="finance@enterprise.com",
        customer_phone="+919711223344"
    )
    assert res["success"] is True
    assert res["provider"] == "CASHFREE"
    assert res["auto_collect_status"] == "VIRTUAL_ACCOUNT_ACTIVE"
    assert res["virtual_account_number"].startswith("CFVAN")
    assert "payments.cashfree.com/links/" in res["short_url"]

def test_neobank_adapter_salary_cycle_heuristic():
    adapter = NeobankMandateAdapter()
    res = adapter.schedule_mandate_retry(
        mandate_id="man_sip_9901",
        amount=5000.0,
        scheduled_epoch=1727740800.0  # Approx late in the month
    )
    assert res["success"] is True
    assert res["provider"] == "GROWW_JUPITER_FI"
    assert "SALARY_CREDIT_WINDOW_SURPLUS" in res["recovery_heuristic"]
    assert res["optimized_salary_cycle_epoch"] >= res["original_scheduled_epoch"]

def test_stripe_adapter_multi_currency():
    adapter = StripeAdapter()
    res = adapter.create_recovery_link(
        payment_id="pay_strp_88776",
        amount=8650.0,
        customer_name="Global Client",
        customer_email="cfo@uscorp.com",
        customer_phone="+14155552671"
    )
    assert res["success"] is True
    assert res["provider"] == "STRIPE"
    assert res["currency"] == "USD"
    assert res["amount_usd"] == 100.0  # 8650 / 86.50
    assert "checkout.stripe.com" in res["short_url"]
    assert res["rbi_purpose_code"] == "P0802_SOFTWARE_CONSULTING_EXPORTS"

def test_multi_rail_router_adaptive_selection():
    router = MultiRailRouter(default_mode="universal_auto")
    
    # 1. High-ticket > ₹50,000 -> CRED Pay
    cred_res = router.create_recovery_link(
        payment_id="pay_test_high_ticket",
        amount=65000.0,
        customer_name="VIP",
        customer_email="vip@india.in",
        customer_phone="+919876543210"
    )
    assert cred_res["provider"] == "CRED"

    # 2. International email -> Stripe
    stripe_res = router.create_recovery_link(
        payment_id="pay_test_intl",
        amount=10000.0,
        customer_name="Alex",
        customer_email="alex@globaltech.io",
        customer_phone="+14155550199"
    )
    assert stripe_res["provider"] == "STRIPE"

    # 3. Explicit switch to PhonePe
    router.set_active_rail("phonepe")
    phpe_res = router.create_recovery_link(
        payment_id="pay_test_switch",
        amount=500.0,
        customer_name="User",
        customer_email="user@gmail.com",
        customer_phone="+919800000000"
    )
    assert phpe_res["provider"] == "PHONEPE"

def test_gateway_rest_endpoints():
    # 1. GET /api/v1/gateways/rails
    resp = client.get("/api/v1/gateways/rails")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_supported_rails"] >= 7
    rail_ids = [r["id"] for r in data["rails"]]
    assert "juspay" in rail_ids
    assert "phonepe" in rail_ids
    assert "cred" in rail_ids
    assert "cashfree" in rail_ids
    assert "neobank" in rail_ids
    assert "stripe" in rail_ids

    # 2. POST /api/v1/gateways/select
    resp_select = client.post("/api/v1/gateways/select", json={"rail_id": "juspay"})
    assert resp_select.status_code == 200
    assert resp_select.json()["active_rail"] == "juspay"

    # 3. POST /api/v1/gateways/simulate
    resp_sim = client.post("/api/v1/gateways/simulate", json={
        "rail_id": "cred",
        "amount": 90000.0,
        "customer_name": "Deepak Parekh",
        "customer_email": "deepak@finance.in"
    })
    assert resp_sim.status_code == 200
    sim_data = resp_sim.json()["data"]
    assert sim_data["provider"] == "CRED"
    assert sim_data["concurrency_guarantee"] == "ATOMIC_CAS_MUTEX_0_DOUBLE_DEBIT"

    # Restore to universal_auto
    client.post("/api/v1/gateways/select", json={"rail_id": "universal_auto"})
