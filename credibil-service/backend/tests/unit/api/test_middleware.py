from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from credibil.api.middleware.audit import AuditLogMiddleware
from credibil.api.middleware.rate_limit import RateLimitMiddleware
from credibil.api.middleware.security import SecurityHeadersMiddleware


def _make_request(path: str = "/api/test", method: str = "GET", headers: dict | None = None):
    request = MagicMock()
    request.url.path = path
    request.method = method
    request.headers = headers or {}
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.body = AsyncMock(return_value=b"")
    request.state = MagicMock()
    return request


def _make_response(status_code: int = 200):
    response = MagicMock()
    response.status_code = status_code
    response.headers = {}
    return response


@pytest.mark.asyncio
class TestSecurityHeadersMiddleware:
    async def test_adds_security_headers(self):
        middleware = SecurityHeadersMiddleware(app=MagicMock())
        request = _make_request()
        call_next = AsyncMock(return_value=_make_response())

        response = await middleware.dispatch(request, call_next)

        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]

    async def test_adds_hsts_for_non_docs(self):
        middleware = SecurityHeadersMiddleware(app=MagicMock())
        request = _make_request(path="/api/companies")
        call_next = AsyncMock(return_value=_make_response())

        response = await middleware.dispatch(request, call_next)
        assert "Strict-Transport-Security" in response.headers

    async def test_no_hsts_for_docs(self):
        middleware = SecurityHeadersMiddleware(app=MagicMock())
        request = _make_request(path="/docs")
        call_next = AsyncMock(return_value=_make_response())

        response = await middleware.dispatch(request, call_next)
        assert "Strict-Transport-Security" not in response.headers


@pytest.mark.asyncio
class TestRateLimitMiddleware:
    async def test_allows_request_under_limit(self):
        middleware = RateLimitMiddleware(
            app=MagicMock(), requests_per_minute=60, requests_per_hour=1000
        )
        request = _make_request()
        call_next = AsyncMock(return_value=_make_response())

        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(return_value=1)
        mock_redis.expire = AsyncMock()
        middleware._redis = mock_redis

        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers

    async def test_blocks_over_limit(self):
        middleware = RateLimitMiddleware(
            app=MagicMock(), requests_per_minute=60, requests_per_hour=1000
        )
        request = _make_request()
        call_next = AsyncMock(return_value=_make_response())

        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(return_value=61)
        mock_redis.expire = AsyncMock()
        middleware._redis = mock_redis

        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 429
        assert "RATE_LIMITED" in response.body.decode()

    async def test_skips_health_endpoints(self):
        middleware = RateLimitMiddleware(app=MagicMock())
        request = _make_request(path="/health")
        call_next = AsyncMock(return_value=_make_response())

        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200


@pytest.mark.asyncio
class TestAuditLogMiddleware:
    async def test_logs_request(self):
        middleware = AuditLogMiddleware(app=MagicMock())
        request = _make_request(path="/api/companies")
        call_next = AsyncMock(return_value=_make_response(200))

        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    async def test_skips_health_endpoints(self):
        middleware = AuditLogMiddleware(app=MagicMock())
        request = _make_request(path="/health")
        call_next = AsyncMock(return_value=_make_response())

        response = await middleware.dispatch(request, call_next)
        assert "X-Request-ID" not in response.headers
