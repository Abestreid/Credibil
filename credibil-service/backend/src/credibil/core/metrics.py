from __future__ import annotations

import time
from typing import TYPE_CHECKING

from prometheus_client import Counter, Gauge, Histogram, Info
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

if TYPE_CHECKING:
    from fastapi import Request, Response

APP_INFO = Info("credibil", "Credibil application info")
REQUEST_COUNT = Counter(
    "credibil_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "credibil_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)
ACTIVE_REQUESTS = Gauge(
    "credibil_http_active_requests",
    "Number of active HTTP requests",
)
DB_QUERY_LATENCY = Histogram(
    "credibil_db_query_duration_seconds",
    "Database query latency",
    ["operation"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)
CACHE_HITS = Counter("credibil_cache_hits_total", "Cache hit count", ["prefix"])
CACHE_MISSES = Counter("credibil_cache_misses_total", "Cache miss count", ["prefix"])
SEARCH_LATENCY = Histogram(
    "credibil_search_duration_seconds",
    "Search query latency",
    ["index"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)
SYNC_OPERATIONS = Counter(
    "credibil_sync_operations_total",
    "Data sync operations",
    ["provider", "status"],
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Collects Prometheus metrics for every HTTP request."""

    SKIP_PATHS = {"/health", "/health/ready", "/health/live", "/metrics"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        ACTIVE_REQUESTS.inc()
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            REQUEST_COUNT.labels(
                method=request.method,
                path=request.url.path,
                status_code=500,
            ).inc()
            raise
        finally:
            ACTIVE_REQUESTS.dec()

        duration = time.perf_counter() - start
        REQUEST_COUNT.labels(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            path=request.url.path,
        ).observe(duration)

        return response
