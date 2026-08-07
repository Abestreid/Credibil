from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from credibil.api.public.routes import router as public_router

_STATIC_DIR = Path(__file__).parent / "static"
# Mount base path (the sub-app is mounted at /api/public on the main app).
_BASE = "/api/public"

API_DESCRIPTION = """
## Credibil Public API

Programmatic access to Moldovan counterparty data — companies, enforcement
proceedings, court cases and corporate relationships — matched by **fiscal code
(IDNO)**.

### Authentication
Every request must include your API key in the **`X-API-Key`** header:

```
curl https://api.credibil.md/api/public/v1/companies/1013600012345 \\
     -H "X-API-Key: cb_your_key_here"
```

Click **Authorize** below and paste your key to try the endpoints from this page.

### Scopes
Keys are granted scopes (`companies`, `enforcement`, `court`, `relationships`,
or `*` for all). A request to an endpoint outside your scopes returns `403`.

### Rate limits
Each key has an hourly request budget (`rate_limit`). Check yours at `GET /v1/me`.
Exceeding it returns `429 Too Many Requests`.

### Conventions
* All company lookups are keyed by the 13-digit **IDNO**.
* Enforcement proceedings carry a `role` (`debtor` / `creditor`) relative to the
  queried company, and a `state` (`active` — currently on unej.md, or `archived`
  — previously seen, since removed).
""".strip()

TAGS_METADATA = [
    {"name": "Account", "description": "Information about the authenticated API key."},
    {"name": "Companies", "description": "Company registry data by fiscal code (IDNO)."},
    {"name": "Enforcement", "description": "Enforcement proceedings (unej.md), debtor/creditor."},
    {"name": "Court", "description": "Court cases where the company is a party."},
    {"name": "Relationships", "description": "Founders, directors and related persons."},
]

_PUBLIC_PATHS = {"/health", "/", "/openapi.json"}


def create_public_app() -> FastAPI:
    app = FastAPI(
        title="Credibil Public API",
        version="1.0.0",
        description=API_DESCRIPTION,
        # Default docs are disabled; we serve self-hosted Swagger UI below so it
        # works under the app's strict Content-Security-Policy (no external CDN).
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json",
        openapi_tags=TAGS_METADATA,
        servers=[{"url": "/api/public", "description": "Public API base path"}],
    )

    if _STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/docs", include_in_schema=False)
    async def swagger_docs():  # noqa: ANN202
        return get_swagger_ui_html(
            openapi_url=f"{_BASE}/openapi.json",
            title="Credibil Public API — Swagger",
            swagger_js_url=f"{_BASE}/static/swagger-ui-bundle.js",
            swagger_css_url=f"{_BASE}/static/swagger-ui.css",
            swagger_ui_parameters={
                "persistAuthorization": True,
                "docExpansion": "list",
                "filter": True,
                "tryItOutEnabled": True,
            },
        )

    app.include_router(public_router)

    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=TAGS_METADATA,
            servers=app.servers,
        )
        schema.setdefault("components", {})["securitySchemes"] = {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "Your Credibil API key (starts with `cb_`).",
            }
        }
        # Lock every operation except the public ones.
        for path, item in schema.get("paths", {}).items():
            for operation in item.values():
                if isinstance(operation, dict) and path not in _PUBLIC_PATHS:
                    operation["security"] = [{"ApiKeyAuth": []}]
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
    return app
