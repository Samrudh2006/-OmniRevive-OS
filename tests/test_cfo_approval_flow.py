import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.cfo_service import CFOApprovalService
from backend.app.audit_store import CryptographicAuditLedger

client = TestClient(app)

def test_cfo_approval_state_machine_flow(tmp_path):
    db_file = str(tmp_path / f"test_cfo_{uuid.uuid4().hex[:8]}.db")
    service = CFOApprovalService(db_path=db_file)

    # 1. Create approval request -> PENDING_APPROVAL
    item = service.create_request(
        entity_id="pay_test_high_01",
        amount=150000.0,
        reason="High-value anomaly above 50,000 INR",
        request_type="HIGH_VALUE_RECOVERY_ANOMALY"
    )
    assert item.status == "PENDING_APPROVAL"
    assert item.amount == 150000.0

    # 2. List queue -> item must be present
    pending_items = service.list_queue(status="PENDING_APPROVAL")
    assert any(q.approval_id == item.approval_id for q in pending_items)

    # 3. Approve item as CFO -> transitions to EXECUTED
    approved_item = service.process_decision(
        approval_id=item.approval_id,
        action="APPROVE",
        actor="Role::CFO",
        notes="Verified legitimate enterprise renewal."
    )
    assert approved_item.status == "EXECUTED"
    assert approved_item.decided_by == "Role::CFO"

    # 4. Attempting to transition terminal EXECUTED state again must raise ValueError
    with pytest.raises(ValueError, match="Invalid transition"):
        service.process_decision(
            approval_id=item.approval_id,
            action="REJECT",
            actor="Role::CFO"
        )

def test_cfo_rejection_flow(tmp_path):
    db_file = str(tmp_path / f"test_cfo_rej_{uuid.uuid4().hex[:8]}.db")
    service = CFOApprovalService(db_path=db_file)

    item = service.create_request(
        entity_id="pay_test_suspicious_02",
        amount=250000.0,
        reason="Unverified velocity pattern",
        request_type="HIGH_VALUE_RECOVERY_ANOMALY"
    )

    rejected_item = service.process_decision(
        approval_id=item.approval_id,
        action="REJECT",
        actor="Role::CFO",
        notes="Suspected fraud cluster. Reroute to legal."
    )
    assert rejected_item.status == "REJECTED"

def test_cfo_unauthorized_role_rejection(tmp_path):
    db_file = str(tmp_path / f"test_cfo_unauth_{uuid.uuid4().hex[:8]}.db")
    service = CFOApprovalService(db_path=db_file)

    item = service.create_request(
        entity_id="pay_test_unauth_03",
        amount=75000.0,
        reason="Test unauthorized approval attempt"
    )

    # Junior Dev lacks Role::CFO -> Cedar denies -> PermissionError
    with pytest.raises(PermissionError, match="Cedar Zero-Trust Policy DENY"):
        service.process_decision(
            approval_id=item.approval_id,
            action="APPROVE",
            actor="Role::Junior_Dev"
        )

def test_cfo_api_endpoints():
    # 1. GET /api/v1/cfo/queue
    resp = client.get("/api/v1/cfo/queue")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "queue" in data["data"]
    assert len(data["data"]["queue"]) >= 1

    # Grab first pending item
    first_item = data["data"]["queue"][0]
    app_id = first_item["approval_id"]

    # 2. GET /api/v1/cfo/{approval_id}
    detail_resp = client.get(f"/api/v1/cfo/{app_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["data"]["approval_id"] == app_id

    # 3. POST /api/v1/cfo/approve
    if first_item["status"] == "PENDING_APPROVAL":
        approve_resp = client.post("/api/v1/cfo/approve", json={
            "approval_id": app_id,
            "notes": "Automated test executive approval"
        })
        assert approve_resp.status_code == 200
        assert approve_resp.json()["data"]["status"] == "EXECUTED"
