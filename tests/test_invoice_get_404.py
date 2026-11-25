from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_unknown_invoice_returns_404_not_another_invoice():
    r = client.get("/api/v1/invoices/does_not_exist_123")
    assert r.status_code == 404


def test_demo_invoice_still_served():
    r = client.get("/api/v1/invoices/inv_enterprise_998")
    assert r.status_code == 200
    assert r.json()["data"]["invoice_id"] == "inv_enterprise_998"


def test_mutate_unknown_invoice_returns_404_and_creates_nothing():
    r = client.post("/api/v1/invoices/ghost_invoice_42/mutate", json={"field": "amount", "new_value": 5})
    assert r.status_code in (401, 403, 404)
    assert client.get("/api/v1/invoices/ghost_invoice_42").status_code == 404
