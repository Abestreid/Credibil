from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Response

from credibil.config import get_settings

router = APIRouter(tags=["health"])


async def _check_database() -> dict[str, Any]:
    try:
        from credibil.core.database import get_engine

        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "healthy", "latency_ms": 0}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_redis() -> dict[str, Any]:
    try:
        from credibil.core.cache import get_redis

        r = await get_redis()
        await r.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_meilisearch() -> dict[str, Any]:
    try:
        import meilisearch_python_sdk as ms

        settings = get_settings()
        client = ms.AsyncClient(settings.meilisearch_url, settings.meilisearch_api_key or "")
        await client.health()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.get("/health")
async def health():
    return {"status": "healthy"}


@router.get("/health/ready")
async def readiness():
    checks = {}
    all_healthy = True

    db = await _check_database()
    checks["database"] = db
    if db["status"] != "healthy":
        all_healthy = False

    redis = await _check_redis()
    checks["redis"] = redis
    if redis["status"] != "healthy":
        all_healthy = False

    search = await _check_meilisearch()
    checks["meilisearch"] = search
    if search["status"] != "healthy":
        all_healthy = False

    status_code = 200 if all_healthy else 503
    return Response(
        content='{"status":"'
        + ("ready" if all_healthy else "not_ready")
        + '","checks":'
        + str(dict(checks)).replace("'", '"')
        + "}",
        status_code=status_code,
        media_type="application/json",
    )


@router.get("/health/live")
async def liveness():
    return {"status": "alive"}
