from __future__ import annotations

import secrets
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "CREDIBIL_", "env_file": ".env", "extra": "ignore"}

    app_name: str = "credibil"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://credibil:credibil@localhost:5432/credibil"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_recycle: int = 1800
    database_pool_pre_ping: bool = True

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_ttl: int = 900
    jwt_refresh_token_ttl: int = 604800

    default_page_size: int = 25
    max_page_size: int = 100

    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = ""

    cors_origins: list[str] = ["http://localhost:5173"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    rate_limit_rpm: int = 60
    rate_limit_rph: int = 1000
    # Comma-separated API keys exempt from rate limiting (trusted service-to-
    # service integrations, e.g. the SDN Sanctions Intelligence sync). All other
    # clients keep the per-minute/hour limits above. Set via
    # CREDIBIL_RATE_LIMIT_EXEMPT_KEYS.
    rate_limit_exempt_keys: str = ""

    otel_exporter_endpoint: str | None = None

    backup_retention_days: int = 30
    backup_s3_bucket: str = ""

    sdn_api_key: str = ""
    sdn_api_url: str = "http://compliance.dazor.by/api/v1"

    log_level: str = "INFO"
    log_format: str = "json"

    @field_validator("jwt_secret")
    @classmethod
    def _validate_jwt_secret(cls, v: str) -> str:
        if not v:
            return secrets.token_urlsafe(32)
        if v == "change-me-in-production":
            import warnings

            warnings.warn(
                "Using default JWT secret! Set CREDIBIL_JWT_SECRET in production.",
                stacklevel=2,
            )
        return v

    @property
    def is_production(self) -> bool:
        return not self.debug


@lru_cache
def get_settings() -> Settings:
    return Settings()
