from __future__ import annotations

import hashlib
import json
from functools import wraps
from typing import TYPE_CHECKING, Any

import redis.asyncio as aioredis

from credibil.config import get_settings

if TYPE_CHECKING:
    from collections.abc import Callable

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def _make_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    h = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"credibil:{prefix}:{h}"


async def cache_get(key: str) -> Any | None:
    r = await get_redis()
    val = await r.get(key)
    if val is not None:
        return json.loads(val)
    return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    r = await get_redis()
    await r.set(key, json.dumps(value, default=str), ex=ttl)


async def cache_delete(pattern: str) -> int:
    r = await get_redis()
    keys = []
    async for key in r.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        return await r.delete(*keys)
    return 0


def cached(prefix: str, ttl: int = 300) -> Callable:
    """Decorator that caches async function results in Redis."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _make_cache_key(prefix, *args, **kwargs)
            result = await cache_get(key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            if result is not None:
                await cache_set(key, result, ttl=ttl)
            return result

        wrapper.invalidate = lambda *a, **kw: cache_delete(  # type: ignore
            _make_cache_key(prefix, *a, **kw)
        )
        wrapper.invalidate_all = lambda: cache_delete(f"credibil:{prefix}:*")  # type: ignore
        return wrapper

    return decorator
