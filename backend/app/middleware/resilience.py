"""Request timeout and HTTP error-rate metrics.

- Requests that exceed REQUEST_TIMEOUT_SECONDS return a 504 JSON error instead of hanging a worker.
- Prometheus counters/histogram expose request volume, 4xx/5xx/429/504 counts and latency per route template,
  so an error rate can be graphed as rate(omnirevive_http_errors_total[5m]) / rate(omnirevive_http_requests_total[5m]).
"""
import asyncio
import time
import uuid
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.app.config import settings

HTTP_REQUESTS_TOTAL = Counter(
    "omnirevive_http_requests_total", "HTTP requests handled", ["method", "route", "status_class"]
)
HTTP_ERRORS_TOTAL = Counter(
    "omnirevive_http_errors_total", "HTTP responses with status >= 500", ["route", "status"]
)
HTTP_RATE_LIMITED_TOTAL = Counter(
    "omnirevive_http_rate_limited_total", "HTTP 429 responses", ["route"]
)
HTTP_TIMEOUTS_TOTAL = Counter(
    "omnirevive_http_timeouts_total", "Requests aborted by the request timeout", ["route"]
)
HTTP_LATENCY_SECONDS = Histogram(
    "omnirevive_http_request_duration_seconds", "HTTP request latency", ["route"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
)

# Long-lived streaming endpoints must not be cut off by the request timeout.
_NO_TIMEOUT_MARKERS = ("/stream", "-stream", "/events", "/ws")


def _route_label(request) -> str:
    """Use the route template (e.g. /api/v1/invoices/{id}) to keep metric cardinality bounded."""
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    if path:
        return path
    return "unmatched"


class RequestResilienceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout_seconds: float | None = None):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else settings.REQUEST_TIMEOUT_SECONDS

    async def dispatch(self, request, call_next):
        path = request.url.path
        started = time.perf_counter()
        use_timeout = self.timeout_seconds > 0 and not any(m in path for m in _NO_TIMEOUT_MARKERS)
        try:
            if use_timeout:
                response = await asyncio.wait_for(call_next(request), timeout=self.timeout_seconds)
            else:
                response = await call_next(request)
        except asyncio.TimeoutError:
            HTTP_TIMEOUTS_TOTAL.labels(route=_route_label(request)).inc()
            trace_id = getattr(request.state, "trace_id", f"tr_{uuid.uuid4().hex[:12]}")
            response = JSONResponse(
                status_code=504,
                content={
                    "success": False,
                    "error": {"code": "REQUEST_TIMEOUT", "message": f"Request exceeded {self.timeout_seconds:g}s and was cancelled."},
                    "trace_id": trace_id,
                    "timestamp": time.time(),
                },
            )
        route = _route_label(request)
        status = response.status_code
        if status == 429 and route == "unmatched":
            route = "rate_limited_pre_routing"  # limiter answers before routing, so no route template exists
        HTTP_REQUESTS_TOTAL.labels(method=request.method, route=route, status_class=f"{status // 100}xx").inc()
        HTTP_LATENCY_SECONDS.labels(route=route).observe(time.perf_counter() - started)
        if status >= 500:
            HTTP_ERRORS_TOTAL.labels(route=route, status=str(status)).inc()
        if status == 429:
            HTTP_RATE_LIMITED_TOTAL.labels(route=route).inc()
        return response
