import time
import threading
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

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
        # Prioritize authenticated client ID / API key, then forward headers, then client IP
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key_{api_key[:12]}"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = request.client
        return client.host if client else "127.0.0.1"

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
