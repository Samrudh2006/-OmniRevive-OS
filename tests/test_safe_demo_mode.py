import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)

def test_safe_demo_mode_allows_unauthenticated_mutation():
    # In default SAFE_DEMO_MODE=True, mutation succeeds
    orig_mode = settings.SAFE_DEMO_MODE
    try:
        settings.SAFE_DEMO_MODE = True
        resp = client.post("/api/v1/invoices/inv_enterprise_998/mutate", json={
            "field": "customer_name",
            "new_value": "Acme Global Solutions Pvt Ltd",
            "reason": "Demo mode company rename"
        })
        assert resp.status_code == 200
        assert resp.json()["success"] is True
    finally:
        settings.SAFE_DEMO_MODE = orig_mode

def test_strict_production_mode_rejects_unauthenticated_mutation():
    orig_mode = settings.SAFE_DEMO_MODE
    try:
        settings.SAFE_DEMO_MODE = False
        
        # 1. Unauthenticated request -> HTTP 401
        resp = client.post("/api/v1/invoices/inv_enterprise_998/mutate", json={
            "field": "customer_name",
            "new_value": "Hacked Without Auth"
        })
        assert resp.status_code == 401
        assert "Authentication required" in resp.json()["error"]["message"]

        # 2. Authenticated request with valid key -> HTTP 200
        auth_resp = client.post(
            "/api/v1/invoices/inv_enterprise_998/mutate",
            json={
                "field": "customer_name",
                "new_value": "Acme Authorized Rename"
            },
            headers={"X-API-Key": settings.API_AUTH_KEY}
        )
        assert auth_resp.status_code == 200
        assert auth_resp.json()["success"] is True
    finally:
        settings.SAFE_DEMO_MODE = orig_mode
