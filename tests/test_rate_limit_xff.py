from types import SimpleNamespace
from backend.app.middleware.rate_limiter import SlidingWindowRateLimiter


def _req(xff, host="10.0.0.5"):
    return SimpleNamespace(headers={"X-Forwarded-For": xff} if xff else {}, client=SimpleNamespace(host=host))


def _limiter():
    return SlidingWindowRateLimiter(app=lambda *a, **k: None)


def test_spoofed_left_xff_entries_do_not_change_client_identity():
    lim = _limiter()
    ids = {lim._get_client_id(_req(f"1.2.3.{i}, 198.51.100.7")) for i in range(50)}
    assert ids == {"fwd_198.51.100.7"}


def test_untrusted_direct_client_ignores_xff():
    lim = _limiter()
    assert lim._get_client_id(_req("9.9.9.9", host="198.51.100.20")) == "ip_198.51.100.20"
