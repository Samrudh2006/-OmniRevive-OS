from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_non_ascii_api_key_is_rejected_with_403_not_500():
    r = client.post(
        "/api/v1/invoices/inv_enterprise_998/mutate",
        headers={"X-API-Key": b"k\xe9y-\xfc"},
        json={"field": "amount", "new_value": 5},
    )
    assert r.status_code == 403, r.status_code
