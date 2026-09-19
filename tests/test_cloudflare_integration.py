import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings
from backend.app.services.r2_storage import r2_storage

client = TestClient(app)

def test_cloudflare_all_25_capabilities():
    """Verify that all 25 Cloudflare free-tier capabilities are enumerated and configured."""
    res = client.get("/api/v1/cloudflare/capabilities")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["total_capabilities"] == 25
    assert "$0.00" in data["cost"]
    
    caps = data["capabilities"]
    assert len(caps) == 25
    
    cap_names = [c["name"] for c in caps]
    # Verify core items from user reference image
    assert "Host Your Websites" in cap_names
    assert "Store Files" in cap_names
    assert "Get free SSL" in cap_names
    assert "Speed up your site worldwide" in cap_names
    assert "Get DDoS protection" in cap_names
    assert "Run an API" in cap_names
    assert "Store Backups" in cap_names
    assert "Block bots" in cap_names
    assert "Run serverless functions" in cap_names
    assert "Use a SQL database" in cap_names
    assert "Cache your pages" in cap_names
    assert "Add CAPTCHA" in cap_names
    assert "Run cron jobs" in cap_names
    assert "Hide your home server" in cap_names
    assert "Lock an admin page behind login" in cap_names
    assert "Receive webhooks" in cap_names
    assert "Use key-value storage" in cap_names
    assert "Track your traffic" in cap_names

def test_cloudflare_turnstile_demo_verification():
    """Verify that Turnstile CAPTCHA verification passes cleanly in demo/testing mode."""
    res = client.post(
        "/api/v1/cloudflare/verify-turnstile",
        json={"token": "test_turnstile_dummy_token"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["success"] is True

def test_cloudflare_r2_storage_and_backup():
    """Verify that Cloudflare R2 backup service generates correct manifest and zero-egress URL."""
    res = client.post("/api/v1/cloudflare/backup-to-r2")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    backup_data = data["data"]
    assert backup_data["provider"] == "Cloudflare R2 (Zero Egress)"
    assert backup_data["bucket"] == "omnirevive-backups"
    assert "backups/sqlite_" in backup_data["key"]

def test_cloudflare_r2_public_url_builder():
    url = r2_storage.get_public_url("invoices/inv_998.pdf")
    assert url.endswith("invoices/inv_998.pdf")
