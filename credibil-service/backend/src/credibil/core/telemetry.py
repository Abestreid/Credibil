from __future__ import annotations

from typing import TYPE_CHECKING

from credibil.config import get_settings

if TYPE_CHECKING:
    from fastapi import FastAPI


def setup_telemetry(app: FastAPI | None = None) -> None:
    """Initialize OpenTelemetry tracing. Skipped if no OTEL endpoint configured."""
    settings = get_settings()

    if not settings.otel_exporter_endpoint:
        return

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create(
        {
            "service.name": settings.app_name,
            "service.version": "0.1.0",
            "deployment.environment": "production" if not settings.debug else "development",
        }
    )

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_endpoint,
        insecure=True,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    if app is not None:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)

    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    HTTPXClientInstrumentor().instrument()

    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        from credibil.core.database import get_engine

        engine = get_engine()
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    except Exception:
        pass
