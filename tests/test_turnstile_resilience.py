import asyncio
import httpx
import pytest
from fastapi import HTTPException
from backend.app.config import settings
from backend.app.services import cloudflare_turnstile as ct

V = ct.CloudflareTurnstileVerifier


def _patch(monkeypatch, handler, demo=False):
    real = httpx.AsyncClient
    monkeypatch.setattr(ct.httpx, "AsyncClient", lambda **k: real(transport=httpx.MockTransport(handler), **k))
    monkeypatch.setattr(settings, "SAFE_DEMO_MODE", demo, raising=False)
    monkeypatch.setenv("CLOUDFLARE_TURNSTILE_SECRET_KEY", "real-secret")


def test_retry_then_success(monkeypatch):
    calls = []

    def h(req):
        calls.append(1)
        return httpx.Response(503) if len(calls) == 1 else httpx.Response(200, json={"success": True})

    _patch(monkeypatch, h)
    assert asyncio.run(V.verify_token("tok"))["success"] is True
    assert len(calls) == 2


def test_non_json_is_502_not_500(monkeypatch):
    _patch(monkeypatch, lambda r: httpx.Response(200, text="<html>"))
    with pytest.raises(HTTPException) as e:
        asyncio.run(V.verify_token("tok"))
    assert e.value.status_code == 502


def test_definitive_failure_not_retried(monkeypatch):
    calls = []

    def h(req):
        calls.append(1)
        return httpx.Response(200, json={"success": False, "error-codes": ["x"]})

    _patch(monkeypatch, h)
    with pytest.raises(HTTPException) as e:
        asyncio.run(V.verify_token("tok"))
    assert e.value.status_code == 403 and len(calls) == 1


def test_strict_mode_without_real_secret_fails_closed(monkeypatch):
    monkeypatch.delenv("CLOUDFLARE_TURNSTILE_SECRET_KEY", raising=False)
    monkeypatch.setattr(settings, "SAFE_DEMO_MODE", False, raising=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(V.verify_token("tok"))
    assert e.value.status_code == 503
