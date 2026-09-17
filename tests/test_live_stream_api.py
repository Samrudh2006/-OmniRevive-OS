import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_live_forex_rates_contract():
    response = client.get("/api/v1/telemetry/forex-rates")
    assert response.status_code == 200
    data = response.json()
    assert "rates" in data
    rates = data["rates"]
    assert "USD_INR" in rates
    assert rates["USD_INR"] > 0
    assert "EUR_INR" in rates
    assert "timestamp" in data

def test_live_bank_pings_contract():
    response = client.get("/api/v1/telemetry/bank-pings")
    assert response.status_code == 200
    data = response.json()
    assert "rails" in data
    assert len(data["rails"]) >= 4
    for rail in data["rails"]:
        assert "rail" in rail
        assert "latency_ms" in rail
        assert "status" in rail
