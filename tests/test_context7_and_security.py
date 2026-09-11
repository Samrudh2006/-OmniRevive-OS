"""
Tests for RazorRevive-OS 7-D Context Telemetry Matrix and Zero-Trust Security Hardening.
Verifies Context7 endpoint, Security Headers (CSP, Permissions-Policy, nosniff),
and PCI-DSS/PII Masking utilities.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.utils.security_masking import (
    mask_pan,
    mask_phone,
    mask_upi_vpa,
    mask_aadhaar,
    sanitize_audit_payload
)

client = TestClient(app)

def test_context7_telemetry_endpoint_structure():
    """Verify that GET /api/v1/telemetry/context7 returns all 7 dimensions."""
    resp = client.get("/api/v1/telemetry/context7?bank_code=SBI")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "data" in data
    c7 = data["data"]
    assert c7["version"] == "context7_v2.4"
    assert "composite_recovery_score" in c7
    assert "dimensions" in c7

    dims = c7["dimensions"]
    assert "D1_switch_telemetry" in dims
    assert "D2_weibull_hazard" in dims
    assert "D3_enterprise_sla" in dims
    assert "D4_cedar_guardrails" in dims
    assert "D5_multi_rail_vector" in dims
    assert "D6_merkle_hash_chain" in dims
    assert "D7_multilingual_sentiment" in dims

    # Verify D2 Weibull hazard details
    assert dims["D2_weibull_hazard"]["shape_k"] == 2.1
    assert dims["D2_weibull_hazard"]["scale_lambda_mins"] == 45.0

    # Verify D7 Dialect details
    assert "te-IN (Telugu)" in dims["D7_multilingual_sentiment"]["active_detected_language"]

def test_security_headers_middleware():
    """Verify that all enterprise security headers (CSP, nosniff, DENY, Permissions-Policy) are present."""
    resp = client.get("/health")
    assert resp.status_code == 200
    headers = resp.headers

    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "max-age=31536000" in headers.get("Strict-Transport-Security", "")
    assert "strict-origin-when-cross-origin" in headers.get("Referrer-Policy", "")
    assert "Permissions-Policy" in headers
    assert "geolocation=()" in headers["Permissions-Policy"]
    assert "microphone=(self)" in headers["Permissions-Policy"]

    # Verify Content-Security-Policy
    csp = headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "script-src" in csp
    assert "object-src 'none'" in csp

def test_pci_dss_pan_masking():
    """Verify that 16-digit credit/debit card numbers are masked per PCI-DSS Requirement 3.4."""
    pan1 = "4111222233334444"
    masked1 = mask_pan(pan1)
    assert masked1 == "4111-XXXX-XXXX-4444"

    pan2 = "5200 8282 9191 0022"
    masked2 = mask_pan(pan2)
    assert masked2 == "5200-XXXX-XXXX-0022"

def test_pii_phone_masking():
    """Verify that mobile phone numbers are masked preserving prefix and last 3 digits."""
    phone1 = "+91 9876543210"
    masked1 = mask_phone(phone1)
    assert masked1 == "+91 98*** **210"

    phone2 = "9876543210"
    masked2 = mask_phone(phone2)
    assert masked2 == "98*** **210"

def test_upi_vpa_masking():
    """Verify that UPI VPAs are masked preserving initial characters and handle."""
    vpa = "rahul.verma@okaxis"
    masked = mask_upi_vpa(vpa)
    assert masked == "ra***@okaxis"

    short_vpa = "ab@sbi"
    masked_short = mask_upi_vpa(short_vpa)
    assert masked_short == "a***@sbi"

def test_aadhaar_masking():
    """Verify that 12-digit Aadhaar numbers are masked preserving only the last 4 digits."""
    aadhaar = "1234 5678 9012"
    masked = mask_aadhaar(aadhaar)
    assert masked == "XXXX-XXXX-9012"

def test_sanitize_audit_payload_recursive():
    """Verify recursive payload sanitization for cryptographic ledger storage."""
    raw_payload = {
        "event": "payment.failed",
        "customer_phone": "+91 9876543210",
        "card_pan": "4111222233334444",
        "upi_vpa": "merchant@okicici",
        "details": {
            "secondary_mobile": "9123456789",
            "aadhaar_uid": "998877665544"
        }
    }
    sanitized = sanitize_audit_payload(raw_payload)

    assert sanitized["customer_phone"] == "+91 98*** **210"
    assert sanitized["card_pan"] == "4111-XXXX-XXXX-4444"
    assert sanitized["upi_vpa"] == "me***@okicici"
    assert sanitized["details"]["secondary_mobile"] == "91*** **789"
    assert sanitized["details"]["aadhaar_uid"] == "XXXX-XXXX-5544"
