from fastapi.testclient import TestClient
from backend.app.main import app

c = TestClient(app)
BIG = "x" * 5000


def test_oversized_fields_rejected():
    assert c.post("/api/v1/telemetry/npci-switch/update", json={"bank_code": BIG}).status_code == 422
    assert c.post("/api/v1/b2b/voice/voxcpm-stream", json={"text_prompt": BIG}).status_code == 422
    assert c.post("/api/v1/invoices/inv_x/mutate", json={"field": BIG, "new_value": 1}).status_code == 422


def test_normal_payload_not_422():
    r = c.post("/api/v1/telemetry/npci-switch/update", json={"bank_code": "HDFC", "state": "DEGRADED"})
    assert r.status_code != 422
