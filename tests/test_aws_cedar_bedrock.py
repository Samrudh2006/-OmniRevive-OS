"""
Automated Verification Suite for AWS Cedar Zero-Trust and Amazon Bedrock Engine.
Validates formal policy evaluation, role-based boundary enforcement, and Bedrock inference.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from aws.cedar.cedar_engine import get_cedar_engine
from aws.bedrock.bedrock_client import get_bedrock_agent

client = TestClient(app)


def test_cedar_engine_loads_policies():
    engine = get_cedar_engine()
    raw = engine.load_policies()
    assert len(raw) > 50
    assert len(engine.policy_hash) == 64
    assert "SRE_Admin" in raw
    assert "DeleteAuditRecord" in raw


def test_cedar_sre_circuit_breaker_allow():
    engine = get_cedar_engine()
    res = engine.evaluate(
        principal="Role::SRE_Admin",
        action="Action::TripCircuitBreaker",
        resource="BankingSwitch::SBI",
        context={"mfa_verified": True, "system_risk_score": 40}
    )
    assert res.decision == "ALLOW"
    assert res.policy_id == "policy_sre_circuit_breaker_permit"
    assert res.policy_sha256 == engine.policy_hash


def test_cedar_sre_circuit_breaker_deny_unauthorized():
    engine = get_cedar_engine()
    res = engine.evaluate(
        principal="Role::Junior_Dev",
        action="Action::TripCircuitBreaker",
        resource="BankingSwitch::SBI",
        context={"mfa_verified": True, "system_risk_score": 40}
    )
    assert res.decision == "DENY"


def test_cedar_b2b_gstin_mutation_allow():
    engine = get_cedar_engine()
    res = engine.evaluate(
        principal="Agent::BedrockVoiceAgent",
        action="Action::MutateInvoiceGSTIN",
        resource="B2BInvoice::inv_test_99",
        context={
            "proposed_gstin": "29AABCU9603R1Z2",
            "invoice_amount": 125000,
            "regulatory_compliance": "GST_RULE_46"
        }
    )
    assert res.decision == "ALLOW"
    assert res.policy_id == "policy_b2b_gstin_mutation_permit"


def test_cedar_audit_log_immutability_forbid():
    engine = get_cedar_engine()
    res = engine.evaluate(
        principal="Role::SuperAdmin",
        action="Action::DeleteAuditRecord",
        resource="AuditLog::recovery_audit"
    )
    assert res.decision == "DENY"
    assert "forbid" in res.policy_id.lower()


def test_bedrock_agent_synthesize_turn():
    agent = get_bedrock_agent()
    res = agent.synthesize_turn(
        customer_speech="Invoice mein hamara GST galat hai, correct GSTIN 29AABCU9603R1Z2 daal kar bhejo",
        invoice_context={"invoice_id": "inv_123", "amount": 85000}
    )
    assert res.intent == "GSTIN_DISPUTE"
    assert res.detected_entities["proposed_gstin"] == "29AABCU9603R1Z2"
    assert len(res.response_text) > 20
    assert "29AABCU9603R1Z2" in res.response_text


def test_api_aws_cedar_policies_endpoint():
    response = client.get("/aws/cedar/policies")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "policy_sha256" in data["data"]
    assert data["data"]["rule_count"] == 4


def test_api_aws_cedar_evaluate_endpoint():
    payload = {
        "principal": "Role::SRE_Admin",
        "action": "Action::TripCircuitBreaker",
        "resource": "BankingSwitch::HDFC",
        "context": {"mfa_verified": True, "system_risk_score": 30}
    }
    response = client.post("/aws/cedar/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["decision"] == "ALLOW"


def test_api_aws_bedrock_status_endpoint():
    response = client.get("/aws/bedrock/status")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "claude-3-5" in data["data"]["foundation_model"]
    assert "ap-south-1" in data["data"]["target_region"]
