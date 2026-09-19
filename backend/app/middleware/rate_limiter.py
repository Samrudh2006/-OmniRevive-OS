import time
import hmac
import hashlib
import threading
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from backend.app.config import settings

class SlidingWindowRateLimiter(BaseHTTPMiddleware):
    """
    Sliding-Window In-Memory Rate Limiting Middleware.
    Protects compute-intensive endpoints (simulation, copilot, batch upload, invoice mutation)
    from abuse, script storms, and accidental denial-of-service.
    """

    def __init__(self, app, default_rpm: int = 120, sensitive_rpm: int = 40):
        super().__init__(app)
        self.default_rpm = default_rpm
        self.sensitive_rpm = sensitive_rpm
        # In-memory request timestamp store: {client_id: [(timestamp, is_sensitive)]}
        self._clients: Dict[str, List[Tuple[float, bool]]] = {}
        self._lock = threading.Lock()

    def _get_client_id(self, request: Request) -> str:
        # Prioritize authenticated client ID / API key only if it matches configured secrets
        api_key = request.headers.get("X-API-Key")
        if api_key:
            api_key_clean = api_key.strip()
            sre_key = getattr(settings, "API_AUTH_KEY", "rzp_sec_live_recovery_agent_88")
            cfo_key = getattr(settings, "CFO_AUTH_KEY", "cfo_sec_live_recovery_key_99")
            if hmac.compare_digest(api_key_clean, sre_key) or hmac.compare_digest(api_key_clean, cfo_key):
                return f"key_{hashlib.sha256(api_key_clean.encode('utf-8')).hexdigest()[:12]}"

        client = request.client
        client_ip = client.host if client else "127.0.0.1"

        # Only trust X-Forwarded-For if request originates from trusted local/proxy interfaces
        trusted_proxies = {"127.0.0.1", "::1", "localhost"}
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded and (client_ip in trusted_proxies or client_ip.startswith("10.") or client_ip.startswith("172.") or client_ip.startswith("192.168.")):
            forwarded_ip = forwarded.split(",")[0].strip()
            if forwarded_ip:
                return f"fwd_{forwarded_ip}"

        return f"ip_{client_ip}"

    def _is_sensitive_route(self, path: str) -> bool:
        sensitive_prefixes = [
            "/api/v1/simulate/",
            "/api/v1/copilot/chat",
            "/api/v1/recovery/batch-",
            "/api/v1/b2b/voice/turn",
            "/api/v1/invoices/",
            "/api/v1/benchmark/run"
        ]
        return any(path.startswith(prefix) for prefix in sensitive_prefixes)

    async def dispatch(self, request: Request, call_next):
        # Exclude static assets and health checks from rate limiting
        path = request.url.path
        if path.startswith("/static") or path.startswith("/assets") or path in ["/health", "/api/v1/health", "/metrics", "/"]:
            return await call_next(request)

        client_id = self._get_client_id(request)
        is_sensitive = self._is_sensitive_route(path)
        limit = self.sensitive_rpm if is_sensitive else self.default_rpm
        now = time.time()
        window_start = now - 60.0  # 1-minute sliding window

        with self._lock:
            # Memory leak mitigation: prune stale client records if cache exceeds threshold
            if len(self._clients) > 1000:
                stale_keys = [k for k, h in self._clients.items() if not h or h[-1][0] <= window_start]
                for k in stale_keys:
                    del self._clients[k]

            history = self._clients.get(client_id, [])
            # Prune records older than 60s
            valid_history = [item for item in history if item[0] > window_start]

            # Count relevant requests in window
            relevant_count = sum(1 for item in valid_history if (not is_sensitive) or item[1])

            if relevant_count >= limit:
                retry_after = int(60.0 - (now - valid_history[0][0])) + 1
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={"Retry-After": str(max(1, retry_after))},
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Rate limit of {limit} requests/minute exceeded for route. Retry in {retry_after}s.",
                            "limit_rpm": limit
                        },
                        "timestamp": now
                    }
                )

            valid_history.append((now, is_sensitive))
            self._clients[client_id] = valid_history

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - (relevant_count + 1)))
        return response
