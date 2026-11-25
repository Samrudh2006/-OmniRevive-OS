import asyncio
import pytest
from backend.app.services.circuit_breaker import CircuitBreaker, CircuitOpenError, retry_async


class Clock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t


def run(c): return asyncio.run(c)


def test_opens_after_threshold_then_half_open_then_closes():
    clk = Clock()
    b = CircuitBreaker("t", failure_threshold=2, reset_seconds=10, clock=clk)

    async def bad(): raise ValueError("x")
    async def good(): return 1

    for _ in range(2):
        with pytest.raises(ValueError):
            run(b.call(bad))
    assert b.state == "open"
    with pytest.raises(CircuitOpenError):
        run(b.call(good))
    clk.t = 11
    assert b.state == "half_open"
    assert run(b.call(good)) == 1
    assert b.state == "closed"


def test_half_open_failure_reopens():
    clk = Clock()
    b = CircuitBreaker("t", failure_threshold=1, reset_seconds=5, clock=clk)

    async def bad(): raise ValueError("x")
    with pytest.raises(ValueError):
        run(b.call(bad))
    clk.t = 6
    with pytest.raises(ValueError):
        run(b.call(bad))
    assert b.state == "open"


def test_retry_succeeds_after_transient_failures():
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("blip")
        return "ok"

    assert run(retry_async(flaky, attempts=3, base_delay=0.001)) == "ok"
    assert calls["n"] == 3


def test_retry_gives_up_and_reraises():
    async def always(): raise ConnectionError("down")
    with pytest.raises(ConnectionError):
        run(retry_async(always, attempts=2, base_delay=0.001))
