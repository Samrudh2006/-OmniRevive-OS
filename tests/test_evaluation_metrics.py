"""
Tests for OmniRevive-OS AI Evaluation Metrics Suite
Validates:
- Ragas (Faithfulness, Answer Relevancy, Context Precision/Recall)
- DeepEval (G-Eval, Zero-Hallucination, RBI/TRAI Compliance)
- LangGraph / CrewAI (Tool Precision, FSM Transition Fidelity, Token Efficiency)
- API endpoints (/api/v1/eval/metrics, /api/v1/eval/run-suite, /api/v1/eval/traces)
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.evaluation.eval_engine import (
    eval_engine,
    calculate_faithfulness,
    calculate_answer_relevancy,
    calculate_context_precision_recall,
    evaluate_g_eval,
    evaluate_zero_hallucination,
    evaluate_rbi_tone_compliance,
    evaluate_tool_calling_accuracy,
    evaluate_graph_state_transitions,
    calculate_token_efficiency
)

@pytest.fixture
def client():
    return TestClient(app)

# =========================================================================
# 1. Ragas Metrics Tests
# =========================================================================
def test_ragas_faithfulness_grounded():
    """Checks that claims with facts from context score high faithfulness."""
    context = "Invoice ID: inv_998, Amount: 85,000 INR, GSTIN: 29AABCU9603R1Z2"
    claim = "Mawa, updating invoice inv_998 with GSTIN 29AABCU9603R1Z2 and amount 85,000 INR."
    score = calculate_faithfulness(claim, context)
    assert score >= 0.85

def test_ragas_faithfulness_discount_clamp():
    """Checks that valid <=10% discount calculations are deemed faithful."""
    context = "Invoice ID: inv_100, Amount: 1,000 INR"
    claim = "Applying 5% discount of 50 INR on invoice 1000."
    score = calculate_faithfulness(claim, context)
    assert score >= 0.80

def test_ragas_answer_relevancy_domain_keywords():
    """Validates answer relevancy detects fintech domain intent matching."""
    query = "GST number thappu undi, change cheyyandi"
    response = "Sure, we will update the GST number on your B2B invoice."
    score = calculate_answer_relevancy(query, response)
    assert score >= 0.90

def test_ragas_context_precision_recall():
    """Tests vector memory precision and recall calculations."""
    retrieved = ["doc_gst_998", "doc_upi_200", "doc_irrelevant_1"]
    relevant = ["doc_gst_998", "doc_upi_200"]
    res = calculate_context_precision_recall(retrieved, relevant)
    assert res["context_precision"] == pytest.approx(0.6667, 0.01)
    assert res["context_recall"] == 1.0

# =========================================================================
# 2. DeepEval Metrics Tests
# =========================================================================
def test_deepeval_zero_hallucination_valid():
    """Legitimate discount <= 10% passes zero-hallucination rate."""
    text = "We can apply a 5% discount on this invoice as per policy."
    score = evaluate_zero_hallucination(text)
    assert score >= 0.95

def test_deepeval_zero_hallucination_violation():
    """Excessive discount > 10% drops zero-hallucination rate."""
    text = "I will grant you a 50% discount right now to settle."
    score = evaluate_zero_hallucination(text)
    assert score <= 0.30

def test_deepeval_rbi_tone_compliance_polite():
    """Polite professional tone passes RBI compliance."""
    text = "Namaskaram mawa, your payment of INR 85,000 is pending. We can arrange a payment link."
    score = evaluate_rbi_tone_compliance(text)
    assert score == 1.0

def test_deepeval_rbi_tone_compliance_prohibited_terms():
    """Harassing or predatory language fails RBI compliance."""
    text = "If you don't pay we will send police and take legal action immediately to seize property."
    score = evaluate_rbi_tone_compliance(text)
    assert score <= 0.20

def test_deepeval_g_eval_score():
    """Tests 0-100 rubric scoring for goal completion."""
    trace_success = "Customer requested PTP. PTP confirmed and locked for Friday 11:00 AM IST. Reminders suppressed."
    score = evaluate_g_eval("Book PTP calendar lock", trace_success)
    assert score >= 85.0

# =========================================================================
# 3. LangGraph / CrewAI Agentic Metrics Tests
# =========================================================================
def test_langgraph_tool_calling_accuracy():
    """Tests tool precision & recall matching."""
    invoked = ["MUTATE_RAZORPAY_INVOICE", "DISPATCH_LINK"]
    expected = ["MUTATE_RAZORPAY_INVOICE", "DISPATCH_LINK"]
    f1 = evaluate_tool_calling_accuracy(invoked, expected)
    assert f1 == 1.0

    invoked_partial = ["MUTATE_RAZORPAY_INVOICE"]
    f1_partial = evaluate_tool_calling_accuracy(invoked_partial, expected)
    assert 0.4 <= f1_partial <= 0.8

def test_langgraph_state_transition_fidelity():
    """Tests deterministic FSM state transition validation."""
    valid_seq = ["IDLE", "INITIATED", "GREETING", "OBJECTION_PARSING", "PTP_PROPOSAL", "PTP_LOCKED", "CLOSING", "COMPLETED"]
    score = evaluate_graph_state_transitions(valid_seq)
    assert score == 1.0

def test_token_efficiency_calculation():
    """Calculates tokens used per 1,000 INR GMV recovered."""
    tokens = 1500
    gmv = 75000.0  # 1500 / 75 = 20 tokens per 1k
    eff = calculate_token_efficiency(tokens, gmv)
    assert eff == 20.0

# =========================================================================
# 4. Evaluation API Endpoint Tests
# =========================================================================
def test_api_get_eval_metrics(client):
    """Verifies GET /api/v1/eval/metrics returns full evaluation suite."""
    resp = client.get("/api/v1/eval/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "ragas_suite" in data["data"]
    assert "deepeval_suite" in data["data"]
    assert "langgraph_crewai_suite" in data["data"]
    assert data["data"]["ragas_suite"]["faithfulness"] >= 0.80
    assert data["data"]["deepeval_suite"]["zero_hallucination_rate"] >= 0.90

def test_api_run_eval_suite(client):
    """Verifies POST /api/v1/eval/run-suite executes synthetic evaluation benchmark."""
    payload = {"sample_size": 10, "domain": "ALL_RAILS"}
    resp = client.post("/api/v1/eval/run-suite", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["data"]["recent_traces"]) > 0
    assert "execution_duration_ms" in data

def test_api_get_eval_traces(client):
    """Verifies GET /api/v1/eval/traces returns itemized evaluation traces."""
    resp = client.get("/api/v1/eval/traces?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["data"]["traces"]) > 0
    trace = data["data"]["traces"][0]
    assert "ragas" in trace
    assert "deepeval" in trace
    assert "agent_graph" in trace
