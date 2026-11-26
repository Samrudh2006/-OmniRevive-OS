from fastapi.testclient import TestClient
from backend.app.main import app

c = TestClient(app)


def test_stress_test_bounded():
    assert c.post("/agency/swarm/stress-test?total_transactions=100001").status_code == 422
    assert c.post("/agency/swarm/stress-test?total_transactions=0").status_code == 422
    assert c.post("/agency/swarm/stress-test?outage_severity=2").status_code == 422
    assert c.post("/agency/swarm/stress-test?total_transactions=1000").status_code == 200


def test_roi_bounded():
    assert c.get("/api/v1/roi/calculator?avg_ticket_size=0").status_code == 422
    assert c.get("/api/v1/roi/calculator?failure_rate_pct=1e308").status_code == 422
    assert c.get("/api/v1/roi/calculator?monthly_gmv=-5").status_code == 422
    assert c.get("/api/v1/roi/calculator").status_code == 200


def test_daily_report_email_validated():
    assert c.post("/agency/send_daily_report?email=notanemail").status_code == 422
    assert c.post("/agency/send_daily_report?email=" + "a" * 300 + "@x.com").status_code == 422
