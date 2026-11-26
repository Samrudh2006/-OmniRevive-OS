from fastapi.testclient import TestClient
from backend.app.config import Settings, settings
from backend.app.main import app

c = TestClient(app)


def test_safe_demo_mode_default_unchanged():
    assert Settings.model_fields["SAFE_DEMO_MODE"].default is True


def test_daily_report_requires_key_even_in_demo_mode():
    assert settings.SAFE_DEMO_MODE is True
    assert c.post("/agency/send_daily_report?email=a@b.co").status_code == 401
    assert c.post("/agency/send_daily_report?email=a@b.co", headers={"X-API-Key": "wrong"}).status_code == 403
    r = c.post("/agency/send_daily_report?email=a@b.co", headers={"X-API-Key": settings.API_AUTH_KEY})
    assert r.status_code == 200


def test_other_demo_endpoints_still_open_in_demo_mode():
    r = c.post("/api/v1/telemetry/npci-switch/update", json={"bank_code": "HDFC", "status": "DEGRADED"})
    assert r.status_code != 401
