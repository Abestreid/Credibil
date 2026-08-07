from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from credibil.api.admin.routes import router as admin_router
from credibil.api.apikey.routes import router as apikey_router
from credibil.api.auth.routes import router as auth_router
from credibil.api.health import router as health_router
from credibil.api.middleware import (
    AuditLogMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from credibil.api.monitoring.routes import router as monitoring_router
from credibil.api.public.app import create_public_app
from credibil.api.v1.router import v1_router
from credibil.config import get_settings
from credibil.core.cache import close_redis
from credibil.core.database import close_engine
from credibil.core.exceptions import register_error_handlers

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from credibil.core.metrics import APP_INFO

    APP_INFO.info({"version": "0.1.0"})
    yield
    await close_redis()
    await close_engine()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Credibil API",
        description="Company due diligence SaaS platform",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(AuditLogMiddleware)

    try:
        from credibil.core.metrics import PrometheusMiddleware

        app.add_middleware(PrometheusMiddleware)
    except ImportError:
        pass

    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_rpm,
        requests_per_hour=settings.rate_limit_rph,
    )

    register_error_handlers(app)

    app.include_router(health_router)
    app.include_router(v1_router, prefix="/api")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api/v1")
    app.include_router(monitoring_router, prefix="/api/v1")
    app.include_router(apikey_router, prefix="/api/v1")

    # Public client-facing API — separate contour with its own Swagger at
    # /api/public/docs and X-API-Key authentication.
    app.mount("/api/public", create_public_app())

    @app.get("/metrics")
    async def metrics() -> Response:
        from prometheus_client import generate_latest as _generate_latest

        return Response(
            content=_generate_latest(),
            media_type="text/plain",
        )

    if not settings.debug:
        try:
            from credibil.core.telemetry import setup_telemetry

            setup_telemetry(app)
        except ImportError:
            pass

    return app


app = create_app()
