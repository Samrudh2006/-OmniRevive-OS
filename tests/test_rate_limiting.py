import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.app.middleware.rate_limiter import SlidingWindowRateLimiter

def test_sliding_window_rate_limiter_enforcement():
    test_app = FastAPI()
    test_app.add_middleware(SlidingWindowRateLimiter, default_rpm=5, sensitive_rpm=3)

    @test_app.get("/normal")
    def normal_endpoint():
        return {"ok": True}

    @test_app.post("/api/v1/simulate/failure")
    def sensitive_endpoint():
        return {"simulated": True}

    client = TestClient(test_app)

    # 1. Sensitive route limit = 3
    for i in range(3):
        res = client.post("/api/v1/simulate/failure")
        assert res.status_code == 200
        assert "X-RateLimit-Limit" in res.headers
        assert "X-RateLimit-Remaining" in res.headers

    # 4th request must trigger HTTP 429
    blocked_res = client.post("/api/v1/simulate/failure")
    assert blocked_res.status_code == 429
    assert blocked_res.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "Retry-After" in blocked_res.headers

def test_unthrottled_health_routes():
    test_app = FastAPI()
    test_app.add_middleware(SlidingWindowRateLimiter, default_rpm=2, sensitive_rpm=1)

    @test_app.get("/health")
    def health_endpoint():
        return {"status": "healthy"}

    client = TestClient(test_app)

    # Health check is never throttled
    for _ in range(10):
        res = client.get("/health")
        assert res.status_code == 200
