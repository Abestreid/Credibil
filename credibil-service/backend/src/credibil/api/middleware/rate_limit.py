from __future__ import annotations

import time
from typing import Any

import redis.asyncio as aioredis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from credibil.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-based sliding window rate limiter.

    Headers returned:
        X-RateLimit-Limit     - Max requests per window
        X-RateLimit-Remaining - Remaining requests in window
        X-RateLimit-Reset     - Unix timestamp when window resets
    """

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ) -> None:
        super().__init__(app)
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self._redis: aioredis.Redis | None = None
        # Trusted service keys that bypass rate limiting entirely (all other
        # clients keep the limits). Loaded once from config.
        raw = get_settings().rate_limit_exempt_keys or ""
        self.exempt_keys = {k.strip() for k in raw.split(",") if k.strip()}

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            settings = get_settings()
            self._redis = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey:{api_key[:16]}"
        return f"ip:{ip}"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in (
            "/health",
            "/health/ready",
            "/health/live",
            "/docs",
            "/openapi.json",
        ):
            return await call_next(request)

        # Trusted service-to-service keys bypass the limiter (everyone else is
        # still limited). Matched on the full X-API-Key header value.
        if self.exempt_keys:
            api_key = request.headers.get("X-API-Key")
            if api_key and api_key in self.exempt_keys:
                return await call_next(request)

        client_id = self._get_client_id(request)
        try:
            r = await self._get_redis()
        except Exception:
            return await call_next(request)

        try:
            now = time.time()

            # Per-minute window
            minute_key = f"ratelimit:{client_id}:minute:{int(now // 60)}"
            minute_count = await r.incr(minute_key)
            if minute_count == 1:
                await r.expire(minute_key, 65)

            # Per-hour window
            hour_key = f"ratelimit:{client_id}:hour:{int(now // 3600)}"
            hour_count = await r.incr(hour_key)
            if hour_count == 1:
                await r.expire(hour_key, 3660)

            remaining_minute = max(0, self.rpm - minute_count)
            remaining_hour = max(0, self.rph - hour_count)
            remaining = min(remaining_minute, remaining_hour)

            reset_time = int((int(now // 60) + 1) * 60)

            if minute_count > self.rpm or hour_count > self.rph:
                return Response(
                    content='{"success":false,"error":{"code":"RATE_LIMITED","message":"Too many requests"}}',
                    status_code=429,
                    media_type="application/json",
                    headers={
                        "X-RateLimit-Limit": str(self.rpm),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_time),
                        "Retry-After": str(reset_time - int(now)),
                    },
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.rpm)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            return response
        except Exception:
            return await call_next(request)
