"""Hand-rolled metrics middleware — educational alternative to
prometheus-fastapi-instrumentator (see app/core/metrics.py).

NOT wired into main.py. If you want to experiment with it, add
`app.add_middleware(MetricsMiddleware)` in create_app() — the metric names
are prefixed with `manual_` so they don't collide with the instrumentator's.
"""

import time

from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

REQUEST_COUNT = Counter(
    "manual_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "manual_http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "path"],
)
IN_PROGRESS = Gauge(
    "manual_http_requests_in_progress",
    "Requests currently being processed",
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        IN_PROGRESS.inc()
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            IN_PROGRESS.dec()

        duration = time.perf_counter() - start
        path = request.url.path
        REQUEST_LATENCY.labels(method=request.method, path=path).observe(duration)
        REQUEST_COUNT.labels(
            method=request.method, path=path, status_code=response.status_code
        ).inc()
        return response