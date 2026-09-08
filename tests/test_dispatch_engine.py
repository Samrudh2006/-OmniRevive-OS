import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.b2b.invoice_store import invoice_store
from backend.app.communication.dispatch_engine import dispatch_engine
from backend.app.copilot.action_agent import action_router

client = TestClient(app)

def test_invoice_store_mutation():
    """Verify invoice field mutation actually persists in the store."""
    inv = invoice_store.get_invoice("inv_enterprise_998")
    assert inv is not None

    updated = invoice_store.mutate_invoice_field(
        invoice_id="inv_enterprise_998",
        field="gstin",
        new_value="29AABCU9603R1Z2",
        reason="Customer dispute resolution"
    )
    assert updated.gstin == "29AABCU9603R1Z2"
    assert updated.status == "MUTATED"
    assert len(updated.mutations) > 0

def test_dispatch_engine_email_generation():
    """Verify authentic MIME RFC-822 email generation with HTML body."""
    dispatch = dispatch_engine.dispatch_email(
        to_email="finance@acmepvt.com",
        invoice_id="inv_enterprise_998",
        subject="Test Tax Invoice Delivery",
        custom_note="Verification test run"
    )
    assert dispatch.dispatch_id.startswith("disp_em_")
    assert dispatch.delivery_status == "DELIVERED"
    assert "Tax Invoice" in dispatch.rendered_html
    assert "upi://pay?" in dispatch.rendered_html
    assert "29AABCU9603R1Z2" in dispatch.rendered_html
    assert "Message-ID" in dispatch.headers

def test_b2b_voice_turn_real_mutation_and_dispatch():
    """Verify B2B voice turn actually executes invoice mutation and email dispatch."""
    payload = {
        "call_session_id": "call_test_8819",
        "invoice_id": "inv_enterprise_998",
        "customer_speech_text": "Invoice mein hamara GST galat hai, correct GSTIN 36AAACB9876Q1Z1 daal kar bhejo",
        "invoice_amount": 85000.0
    }
    resp = client.post("/api/v1/b2b/voice/turn", json=payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    
    assert data["invoice_mutated"] is True
    assert data["dispatch_id"] is not None
    assert data["dispatch_id"].startswith("disp_em_")
    assert data["mutated_invoice_summary"]["gstin"] == "36AAACB9876Q1Z1"

    # Verify state in invoice store was updated
    inv = invoice_store.get_invoice("inv_enterprise_998")
    assert inv.gstin == "36AAACB9876Q1Z1"

def test_copilot_action_router_email_dispatch():
    """Verify Copilot chat detects action intent and dispatches email."""
    query = "Please send invoice email to cfo@acme.com"
    resp = client.post("/api/v1/copilot/chat", json={"query": query})
    assert resp.status_code == 200
    data = resp.json()["data"]
    
    assert data.get("action_executed") is True
    assert data.get("tool_name") == "tool_send_invoice_email"
    assert data.get("dispatch_id") is not None
    assert "cfo@acme.com" in data.get("response")

def test_communication_dispatch_endpoints():
    """Verify REST endpoints for communication preview and raw HTML."""
    # 1. Send on-demand email
    resp = client.post("/api/v1/communication/email/send", json={
        "invoice_id": "inv_enterprise_998",
        "recipient_email": "accounts@client.com",
        "subject": "On-Demand Settlement Advice"
    })
    assert resp.status_code == 200
    disp_id = resp.json()["data"]["dispatch_id"]

    # 2. Get dispatch details
    resp_details = client.get(f"/api/v1/communication/{disp_id}")
    assert resp_details.status_code == 200
    assert resp_details.json()["data"]["recipient"] == "accounts@client.com"

    # 3. Get raw HTML email rendering
    resp_html = client.get(f"/api/v1/communication/{disp_id}/html")
    assert resp_html.status_code == 200
    assert "Tax Invoice & Settlement Advice" in resp_html.text
