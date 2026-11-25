import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY
from backend.app.middleware.resilience import RequestResilienceMiddleware


def _app(timeout):
    app = FastAPI()
    app.add_middleware(RequestResilienceMiddleware, timeout_seconds=timeout)

    @app.get("/slow")
    async def slow():
        await asyncio.sleep(2)
        return {"ok": True}

    @app.get("/fast")
    async def fast():
        return {"ok": True}

    @app.get("/boom")
    async def boom():
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="down")

    return app


def _val(name, labels):
    return REGISTRY.get_sample_value(name, labels) or 0.0


def test_slow_request_gets_504_and_is_counted():
    before = _val("omnirevive_http_timeouts_total", {"route": "/slow"})
    r = TestClient(_app(0.2)).get("/slow")
    assert r.status_code == 504
    assert r.json()["error"]["code"] == "REQUEST_TIMEOUT"
    assert _val("omnirevive_http_timeouts_total", {"route": "/slow"}) == before + 1


def test_fast_request_passes_and_5xx_counted_as_error():
    c = TestClient(_app(5))
    assert c.get("/fast").status_code == 200
    before = _val("omnirevive_http_errors_total", {"route": "/boom", "status": "503"})
    assert c.get("/boom").status_code == 503
    assert _val("omnirevive_http_errors_total", {"route": "/boom", "status": "503"}) == before + 1


def test_live_stream_path_is_exempt_from_timeout():
    from backend.app.middleware import resilience
    assert any(m in "/api/v1/live-stream" for m in resilience._NO_TIMEOUT_MARKERS)
