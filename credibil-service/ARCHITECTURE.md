# Credibil — System Architecture

> Production-grade SaaS platform for company due diligence.
> Initial market: Moldova. Designed for multi-country expansion.

---

## Table of Contents

1. [Tech Stack](#1-tech-stack)
2. [Architecture Principles](#2-architecture-principles)
3. [High-Level Architecture](#3-high-level-architecture)
4. [Repository Layout](#4-repository-layout)
5. [Domain Model & Entities](#5-domain-model--entities)
6. [Database Schema](#6-database-schema)
7. [Country Isolation & Provider Pattern](#7-country-isolation--provider-pattern)
8. [Internal Services Layer](#8-internal-services-layer)
9. [API Structure](#9-api-structure)
10. [Authentication & Authorization](#10-authentication--authorization)
11. [Multi-Tenancy](#11-multi-tenancy)
12. [Subscriptions & Billing](#12-subscriptions--billing)
13. [Background Workers & Task Queue](#13-background-workers--task-queue)
14. [ETL Pipeline](#14-etl-pipeline)
15. [Synchronization Architecture](#15-synchronization-architecture)
16. [Cache Layer](#16-cache-layer)
17. [Search Architecture](#17-search-architecture)
18. [Audit Logs](#18-audit-logs)
19. [Analytics & Statistics](#19-analytics--statistics)
20. [Frontend Architecture](#20-frontend-architecture)
21. [Admin Panel Architecture](#21-admin-panel-architecture)
22. [Deployment Architecture](#22-deployment-architecture)
23. [Observability](#23-observability)
24. [Security](#24-security)

---

## 1. Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Language** | Python 3.11+ | Ecosystem, data libraries, team expertise |
| **Web Framework** | FastAPI | Async, OpenAPI auto-gen, performance |
| **ORM** | SQLAlchemy 2.0 | Mature, async support, complex queries |
| **Migrations** | Alembic | Standard with SQLAlchemy |
| **Validation** | Pydantic v2 | FastAPI native, serialization, settings |
| **Task Queue** | Celery 5.x + Redis broker | Proven, monitoring, retry logic |
| **Database** | PostgreSQL 15+ | JSONB, full-text search, row-level security |
| **Cache** | Redis 7+ | Pub/sub, TTL, streams for task queue |
| **Search** | Meilisearch | Fast, typo-tolerant, simple operations |
| **Object Storage** | S3-compatible (MinIO dev) | Reports, documents, exports |
| **Containerization** | Docker + docker-compose | Reproducible environments |
| **Dependency Mgmt** | UV | Fast, modern Python packaging |
| **Testing** | pytest + factory_boy + httpx | Unit, integration, API tests |
| **Linting** | Ruff + mypy | Speed + type safety |
| **API Docs** | OpenAPI 3.1 (auto from FastAPI) | Interactive docs |

### Future Swaps

| Concern | Current | Alternative |
|---|---|---|
| Search | Meilisearch | Elasticsearch, Typesense |
| Task Queue | Celery | Dramatiq, ARQ |
| Cache | Redis | DragonflyDB |
| Database | PostgreSQL | CockroachDB (distributed) |

---

## 2. Architecture Principles

### Hexagonal Architecture (Ports & Adapters)

Every module follows the hexagonal pattern:

```
module/
  domain/        # Entities, value objects, domain errors (pure Python)
  ports/         # Abstract interfaces (Input/Output ports)
  application/   # Use cases, orchestration (depends only on domain + ports)
  infrastructure/# Concrete implementations of ports (DB, HTTP, cache)
  api/           # HTTP routes, schemas, dependencies
```

**Dependency rule:** Inner layers never import from outer layers. Dependencies point inward.

```
api → application → domain ← ports ← infrastructure
```

### Additional Principles

- **Country isolation:** Country-specific code lives in isolated packages. Adding a country never modifies core code.
- **Provider uniformity:** Every external data source is accessed through a Provider implementing a common interface.
- **Idempotent synchronization:** All sync operations can be safely retried.
- **Event-driven core:** State changes emit domain events for loose coupling.
- **Configuration over convention:** Country adapters are registered via configuration, not hardcoded.

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTS                                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│   │ Web App  │  │Admin App │  │ API (v1) │  │ Webhooks │      │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└────────┼──────────────┼──────────────┼──────────────┼───────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY / LOAD BALANCER                 │
│                     (Nginx / Traefik / Caddy)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│  API Server  │  │ Admin Server │  │  WebSocket Server    │
│  (FastAPI)   │  │  (FastAPI)   │  │  (FastAPI + WS)      │
└──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘
       │                 │                      │
       ▼                 ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION SERVICES                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Company  │ │  Court   │ │ Financial│ │    Search        │   │
│  │ Service  │ │ Service  │ │ Service  │ │    Service       │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Tender   │ │ Sanction │ │   Auth   │ │  Subscription    │   │
│  │ Service  │ │ Service  │ │ Service  │ │    Service       │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │  Audit   │ │Analytics │ │   Sync   │ │    Tenant        │   │
│  │ Service  │ │ Service  │ │ Service  │ │    Service       │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│  PostgreSQL  │  │    Redis     │  │   Meilisearch        │
│  (Primary)   │  │  (Cache +    │  │   (Full-text)        │
│              │  │   Broker)    │  │                      │
└──────────────┘  └──────────────┘  └──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   CELERY WORKER POOL                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │  ETL     │ │   Sync   │ │  Report  │ │   Notification   │   │
│  │ Workers  │ │ Workers  │ │ Workers  │ │    Workers       │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 EXTERNAL DATA PROVIDERS                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Company  │ │  Court   │ │Statistics│ │     Tender       │   │
│  │ Provider │ │ Provider │ │ Provider │ │    Provider      │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
│  ┌──────────┐ ┌──────────┐                                    │
│  │Certifice │ │ Sanction │  ← Each country implements these   │
│  │ Provider │ │ Provider │                                     │
│  └──────────┘ └──────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Repository Layout

```
credibil/
├── ARCHITECTURE.md
├── pyproject.toml
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── alembic.ini
│
├── alembic/                          # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── src/
│   └── credibil/
│       ├── __init__.py
│       ├── config.py                 # Pydantic Settings (all config)
│       ├── main.py                   # FastAPI app factory
│       ├── dependencies.py           # Global DI wiring
│       ├── events.py                 # Domain event bus
│       │
│       ├── core/                     # Cross-cutting concerns
│       │   ├── __init__.py
│       │   ├── database.py           # SQLAlchemy engine, session, base model
│       │   ├── cache.py              # Redis connection + cache decorators
│       │   ├── search.py             # Meilisearch client wrapper
│       │   ├── storage.py            # S3/MinIO abstraction
│       │   ├── security.py           # JWT, password hashing, encryption
│       │   ├── exceptions.py         # Global exception hierarchy
│       │   ├── middleware.py          # Request ID, tenant context, timing
│       │   ├── pagination.py         # Cursor/offset pagination utilities
│       │   ├── telemetry.py          # Structured logging + tracing
│       │   └── id.py                 # ULID/UUID generation
│       │
│       ├── domain/                   # Pure domain (no imports from infra)
│       │   ├── __init__.py
│       │   ├── company/
│       │   │   ├── __init__.py
│       │   │   ├── entities.py       # Company, CompanyRelation
│       │   │   ├── value_objects.py  # RegistrationNumber, TaxId, etc.
│       │   │   ├── events.py         # CompanyCreated, CompanyUpdated
│       │   │   └── errors.py         # DomainError subclasses
│       │   ├── financial/
│       │   │   ├── entities.py       # FinancialReport, BalanceSheet
│       │   │   ├── value_objects.py
│       │   │   └── errors.py
│       │   ├── court/
│       │   │   ├── entities.py       # CourtCase, CourtCaseParty
│       │   │   └── errors.py
│       │   ├── procurement/
│       │   │   ├── entities.py       # Tender, TenderItem, TenderAward
│       │   │   └── errors.py
│       │   ├── certification/
│       │   │   ├── entities.py       # Certification
│       │   │   └── errors.py
│       │   ├── sanctions/
│       │   │   ├── entities.py       # Sanction, SanctionList
│       │   │   └── errors.py
│       │   ├── statistics/
│       │   │   └── entities.py       # CompanyStatistic
│       │   ├── auth/
│       │   │   ├── entities.py       # User, Role, Permission
│       │   │   └── value_objects.py  # Email, UserRole
│       │   ├── tenant/
│       │   │   ├── entities.py       # Tenant, TenantConfig
│       │   │   └── value_objects.py  # TenantId, Plan
│       │   ├── subscription/
│       │   │   ├── entities.py       # Subscription, Plan, Invoice
│       │   │   └── value_objects.py
│       │   ├── audit/
│       │   │   └── entities.py       # AuditLog
│       │   └── search/
│       │       └── entities.py       # SearchQuery, SearchResult
│       │
│       ├── ports/                    # Abstract interfaces
│       │   ├── __init__.py
│       │   ├── providers/            # Country data provider interfaces
│       │   │   ├── __init__.py
│       │   │   ├── base.py           # BaseProvider ABC
│       │   │   ├── company.py        # CompanyProvider ABC
│       │   │   ├── court.py          # CourtProvider ABC
│       │   │   ├── financial.py      # FinancialProvider ABC
│       │   │   ├── procurement.py    # TenderProvider ABC
│       │   │   ├── certification.py  # CertificationProvider ABC
│       │   │   ├── sanctions.py      # SanctionProvider ABC
│       │   │   └── statistics.py     # StatisticsProvider ABC
│       │   ├── repositories/         # Data access interfaces
│       │   │   ├── __init__.py
│       │   │   ├── company.py        # CompanyRepository ABC
│       │   │   ├── financial.py
│       │   │   ├── court.py
│       │   │   ├── procurement.py
│       │   │   ├── certification.py
│       │   │   ├── sanctions.py
│       │   │   ├── statistics.py
│       │   │   ├── audit.py
│       │   │   ├── tenant.py
│       │   │   ├── user.py
│       │   │   └── subscription.py
│       │   └── services/             # Infrastructure service interfaces
│       │       ├── __init__.py
│       │       ├── email.py          # EmailSender ABC
│       │       ├── notification.py   # NotificationService ABC
│       │       ├── export.py         # ReportExporter ABC
│       │       └── webhook.py        # WebhookDispatcher ABC
│       │
│       ├── application/              # Use cases / application services
│       │   ├── __init__.py
│       │   ├── company/
│       │   │   ├── __init__.py
│       │   │   ├── commands.py       # CreateCompany, UpdateCompany
│       │   │   ├── queries.py        # GetCompany, ListCompanies, SearchCompanies
│       │   │   ├── handlers.py       # Command/Query handlers
│       │   │   └── dto.py            # Data transfer objects
│       │   ├── financial/
│       │   │   ├── commands.py
│       │   │   ├── queries.py
│       │   │   └── handlers.py
│       │   ├── court/
│       │   │   ├── commands.py
│       │   │   ├── queries.py
│       │   │   └── handlers.py
│       │   ├── procurement/
│       │   │   ├── commands.py
│       │   │   ├── queries.py
│       │   │   └── handlers.py
│       │   ├── certification/
│       │   │   ├── commands.py
│       │   │   ├── queries.py
│       │   │   └── handlers.py
│       │   ├── sanctions/
│       │   │   ├── commands.py
│       │   │   ├── queries.py
│       │   │   └── handlers.py
│       │   ├── statistics/
│       │   │   └── queries.py
│       │   ├── search/
│       │   │   ├── commands.py       # IndexCompany, ReindexAll
│       │   │   ├── queries.py        # FullTextSearch, FacetedSearch
│       │   │   └── handlers.py
│       │   ├── auth/
│       │   │   ├── commands.py       # Register, Login, RefreshToken
│       │   │   ├── queries.py        # GetCurrentUser, GetPermissions
│       │   │   └── handlers.py
│       │   ├── tenant/
│       │   │   ├── commands.py       # CreateTenant, ConfigureTenant
│       │   │   ├── queries.py
│       │   │   └── handlers.py
│       │   ├── subscription/
│       │   │   ├── commands.py       # Subscribe, Upgrade, Cancel
│       │   │   ├── queries.py
│       │   │   └── handlers.py
│       │   ├── audit/
│       │   │   ├── commands.py       # LogAuditEvent
│       │   │   └── handlers.py
│       │   ├── sync/
│       │   │   ├── commands.py       # TriggerSync, SyncCompany
│       │   │   └── handlers.py       # Orchestrates provider calls
│       │   └── analytics/
│       │       └── queries.py        # Dashboard, Reports, Trends
│       │
│       ├── infrastructure/           # Concrete implementations
│       │   ├── __init__.py
│       │   ├── database/
│       │   │   ├── __init__.py
│       │   │   ├── models.py         # SQLAlchemy declarative models
│       │   │   ├── session.py        # Async session factory
│       │   │   └── repositories/     # Repository implementations
│       │   │       ├── __init__.py
│       │   │       ├── company.py
│       │   │       ├── financial.py
│       │   │       ├── court.py
│       │   │       ├── procurement.py
│       │   │       ├── certification.py
│       │   │       ├── sanctions.py
│       │   │       ├── statistics.py
│       │   │       ├── audit.py
│       │   │       ├── tenant.py
│       │   │       ├── user.py
│       │   │       └── subscription.py
│       │   ├── cache/
│       │   │   ├── __init__.py
│       │   │   ├── redis.py          # Redis client + connection pool
│       │   │   └── strategies.py     # Cache-aside, write-through, etc.
│       │   ├── search/
│       │   │   ├── __init__.py
│       │   │   ├── meilisearch.py    # Meilisearch client
│       │   │   └── indexers.py       # Entity → search document mapping
│       │   ├── email/
│       │   │   ├── __init__.py
│       │   │   └── smtp.py           # SMTP email sender
│       │   ├── storage/
│       │   │   ├── __init__.py
│       │   │   └── s3.py             # S3/MinIO storage
│       │   └── webhook/
│       │       ├── __init__.py
│       │       └── dispatcher.py     # Outgoing webhook dispatcher
│       │
│       ├── countries/                # Country-specific adapters
│       │   ├── __init__.py
│       │   ├── registry.py           # Country provider registry
│       │   ├── base.py               # Base country adapter
│       │   │
│       │   └── moldova/              # Moldova-specific implementation
│       │       ├── __init__.py
│       │       ├── config.py         # Moldova-specific config
│       │       ├── providers/
│       │       │   ├── __init__.py
│       │       │   ├── company.py    # CompanyProvider → Moldovan registry
│       │       │   ├── court.py      # CourtProvider → Moldovan courts
│       │       │   ├── financial.py  # FinancialProvider → Moldovan financial data
│       │       │   ├── procurement.py# TenderProvider → MTender.gov.md
│       │       │   ├── certification.py # CertificationProvider
│       │       │   ├── sanctions.py  # SanctionProvider → UN/EU lists
│       │       │   └── statistics.py # StatisticsProvider → National Bureau
│       │       ├── mappings/
│       │       │   ├── __init__.py
│       │       │   ├── company.py    # External → domain entity mapping
│       │       │   ├── court.py
│       │       │   ├── financial.py
│       │       │   ├── procurement.py
│       │       │   ├── certification.py
│       │       │   └── sanctions.py
│       │       └── parsers/
│       │           ├── __init__.py
│       │           ├── xml.py        # XML response parsers
│       │           ├── csv.py        # CSV parsers
│       │           └── json_api.py   # JSON API parsers
│       │
│       │   # Future countries follow same structure:
│       │   # └── romania/
│       │   #     ├── providers/
│       │   #     ├── mappings/
│       │   #     └── parsers/
│       │
│       ├── api/                      # HTTP layer
│       │   ├── __init__.py
│       │   ├── deps.py               # Dependency injection
│       │   ├── middleware.py          # Request middleware
│       │   │
│       │   ├── v1/                   # API version 1
│       │   │   ├── __init__.py
│       │   │   ├── router.py         # Aggregated v1 router
│       │   │   ├── companies/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── routes.py     # FastAPI route handlers
│       │   │   │   ├── schemas.py    # Request/Response Pydantic models
│       │   │   │   └── dependencies.py
│       │   │   ├── financial/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── court/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── procurement/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── certifications/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── sanctions/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── search/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── relationships/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── analytics/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── auth/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── users/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── tenants/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── subscriptions/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   ├── sync/
│       │   │   │   ├── routes.py
│       │   │   │   └── schemas.py
│       │   │   └── webhooks/
│       │   │       ├── routes.py
│       │   │       └── schemas.py
│       │   └── admin/               # Admin API (separate router)
│       │       ├── __init__.py
│       │       ├── router.py
│       │       ├── tenants/
│       │       │   ├── routes.py
│       │       │   └── schemas.py
│       │       ├── users/
│       │       │   ├── routes.py
│       │       │   └── schemas.py
│       │       ├── subscriptions/
│       │       │   ├── routes.py
│       │       │   └── schemas.py
│       │       ├── sync/
│       │       │   ├── routes.py
│       │       │   └── schemas.py
│       │       ├── audit/
│       │       │   ├── routes.py
│       │       │   └── schemas.py
│       │       ├── analytics/
│       │       │   ├── routes.py
│       │       │   └── schemas.py
│       │       └── system/
│       │           ├── routes.py
│       │           └── schemas.py
│       │
│       ├── workers/                  # Celery workers
│       │   ├── __init__.py
│       │   ├── app.py                # Celery app factory
│       │   ├── config.py             # Worker configuration
│       │   │
│       │   ├── tasks/                # Task definitions
│       │   │   ├── __init__.py
│       │   │   ├── etl/              # ETL tasks
│       │   │   │   ├── __init__.py
│       │   │   │   ├── company.py    # extract_company_data
│       │   │   │   ├── financial.py
│       │   │   │   ├── court.py
│       │   │   │   ├── procurement.py
│       │   │   │   ├── certification.py
│       │   │   │   └── sanctions.py
│       │   │   ├── sync/             # Synchronization tasks
│       │   │   │   ├── __init__.py
│       │   │   │   ├── scheduled.py  # Periodic sync triggers
│       │   │   │   └── on_demand.py  # User-triggered sync
│       │   │   ├── search/           # Search index tasks
│       │   │   │   ├── __init__.py
│       │   │   │   ├── index.py      # index_company, reindex_all
│       │   │   │   └── maintain.py   # index maintenance
│       │   │   ├── analytics/        # Analytics computation tasks
│       │   │   │   ├── __init__.py
│       │   │   │   └── compute.py
│       │   │   ├── notifications/    # Notification tasks
│       │   │   │   ├── __init__.py
│       │   │   │   └── send.py
│       │   │   └── reports/          # Report generation tasks
│       │   │       ├── __init__.py
│       │   │       └── generate.py
│       │   └── schedules/            # Celery Beat schedules
│       │       ├── __init__.py
│       │       └── periodic.py       # Periodic task definitions
│       │
│       └── webhooks/                 # Webhook handling
│           ├── __init__.py
│           ├── dispatcher.py         # Outgoing webhooks
│           └── receiver.py           # Incoming webhooks
│
├── frontend/                         # Web application
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/                      # API client layer
│       │   ├── client.ts             # Axios/fetch wrapper
│       │   ├── hooks/                # React Query hooks
│       │   │   ├── useCompanies.ts
│       │   │   ├── useSearch.ts
│       │   │   └── ...
│       │   └── types/                # Generated API types
│       ├── components/
│       │   ├── ui/                   # Shared UI components
│       │   ├── company/              # Company-related components
│       │   ├── financial/
│       │   ├── court/
│       │   ├── search/
│       │   └── layout/
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── Companies/
│       │   │   ├── List.tsx
│       │   │   ├── Detail.tsx
│       │   │   └── Search.tsx
│       │   ├── Financial/
│       │   ├── Court/
│       │   ├── Procurement/
│       │   ├── Sanctions/
│       │   ├── Analytics/
│       │   ├── Settings/
│       │   └── Auth/
│       ├── store/                    # Client state (Zustand)
│       ├── lib/                      # Utilities
│       └── styles/                   # Global styles / Tailwind
│
├── admin/                            # Admin panel (separate SPA)
│   ├── package.json
│   └── src/
│       ├── pages/
│       │   ├── Tenants/
│       │   ├── Users/
│       │   ├── Subscriptions/
│       │   ├── Sync/
│       │   ├── Audit/
│       │   ├── Analytics/
│       │   └── System/
│       └── ...
│
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── domain/
    │   ├── application/
    │   └── infrastructure/
    ├── integration/
    │   ├── api/
    │   ├── database/
    │   └── workers/
    └── e2e/
```

---

## 5. Domain Model & Entities

### Core Entities

```
┌─────────────────────────────────────────────────────────────┐
│                        TENANT                                │
│  id, name, slug, plan, config, country_code, status        │
└───────────────────┬─────────────────────────────────────────┘
                    │ owns
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
│  id, tenant_id, email, name, role, permissions, mfa        │
└───────────────────┬─────────────────────────────────────────┘
                    │ searches
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                       COMPANY                               │
│  id, tenant_id, name, registration_number, tax_id,         │
│  country_code, legal_form, status, address,成立_date,      │
│  directors[], shareholders[], metadata, source,             │
│  last_synced_at, data_freshness_score                       │
│                                                             │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Relations:                                       │       │
│  │  company_id, related_company_id, relation_type,  │       │
│  │  strength, metadata                              │       │
│  └──────────────────────────────────────────────────┘       │
└───────────────────┬─────────────────────────────────────────┘
                    │ has many
     ┌──────────────┼──────────────┬──────────────┐
     ▼              ▼              ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Financial │ │  Court   │ │ Tender   │ │Certifice │
│ Reports  │ │  Cases   │ │  Bids    │ │   ates   │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
                    │
                    ▼
            ┌──────────┐
            │ Sanctions│
            └──────────┘
```

### Entity Definitions

**Company** — The central entity.
- Fields: `id`, `tenant_id`, `name`, `name_normalized`, `registration_number`, `tax_id` (VAT), `country_code`, `legal_form`, `status` (active/liquidated/dissolved), `address`, `city`, `region`, `postal_code`, `phone`, `email`, `website`, `founded_date`, `industry_codes` (NACE), `employee_count_range`, `metadata` (JSONB), `source`, `external_ids` (JSONB), `last_synced_at`, `data_freshness_score`, `created_at`, `updated_at`

**CompanyRelation** — Directed graph of company relationships.
- Fields: `id`, `company_id`, `related_company_id`, `relation_type` (subsidiary/parent/partner/branch/subsidiary_of), `strength` (0.0–1.0), `start_date`, `end_date`, `metadata`, `created_at`

**FinancialReport** — Annual financial statements.
- Fields: `id`, `company_id`, `year`, `period`, `currency`, `revenue`, `profit_loss`, `total_assets`, `total_liabilities`, `equity`, `cash_flow`, `employees_count`, `report_url`, `source`, `raw_data` (JSONB), `created_at`

**CourtCase** — Legal proceedings involving a company.
- Fields: `id`, `company_id`, `case_number`, `court_name`, `court_type` (commercial/civil/criminal/administrative), `filing_date`, `status` (filed/open/closed/dismissed), `plaintiff`, `defendant`, `amount_disputed`, `currency`, `verdict`, `verdict_date`, `source`, `metadata`, `created_at`

**Tender** — Public procurement opportunity.
- Fields: `id`, `company_id` (winner/issuer), `external_id`, `title`, `description`, `procuring_entity`, `tender_type` (open/negotiated/direct), `status` (planned/published/evaluated/awarded/cancelled), `publication_date`, `deadline`, `estimated_value`, `currency`, `awarded_value`, `winner_name`, `winner_id`, `cpv_codes`, `source`, `metadata`, `created_at`

**Certification** — Licenses, permits, professional certifications.
- Fields: `id`, `company_id`, `certification_type`, `name`, `issuing_body`, `certificate_number`, `issue_date`, `expiry_date`, `status` (active/expired/suspended/revoked), `scope`, `source`, `metadata`, `created_at`

**Sanction** — Sanctions list entries.
- Fields: `id`, `company_id`, `person_name`, `sanction_list` (UN/EU/OFAC/other), `sanction_type`, `program`, `listed_date`, `delisted_date`, `reason`, `source_reference`, `metadata`, `created_at`

**CompanyStatistic** — Aggregated statistics per company per year.
- Fields: `id`, `company_id`, `year`, `metric_type`, `value`, `source`, `created_at`

### Auth Entities

**Tenant** — Organization using the platform.
- Fields: `id`, `name`, `slug`, `plan` (free/starter/pro/enterprise), `country_code`, `status` (active/suspended/cancelled), `config` (JSONB — per-tenant settings), `max_users`, `max_searches_per_month`, `data_retention_days`, `created_at`, `updated_at`

**User** — Platform user within a tenant.
- Fields: `id`, `tenant_id`, `email`, `name`, `password_hash`, `role` (owner/admin/viewer), `is_active`, `mfa_enabled`, `mfa_secret`, `last_login_at`, `created_at`, `updated_at`

**Subscription** — Tenant's billing subscription.
- Fields: `id`, `tenant_id`, `plan`, `status`, `current_period_start`, `current_period_end`, `stripe_subscription_id`, `stripe_customer_id`, `created_at`, `updated_at`

**AuditLog** — Immutable audit trail.
- Fields: `id`, `tenant_id`, `user_id`, `action`, `resource_type`, `resource_id`, `changes` (JSONB), `ip_address`, `user_agent`, `created_at`

---

## 6. Database Schema

### Schema Design Decisions

- **Row-level multi-tenancy:** `tenant_id` on all business tables with PostgreSQL RLS policies.
- **Soft deletes:** `deleted_at` timestamp on all mutable entities.
- **Immutable audit log:** Append-only, partitioned by month.
- **JSONB for flexibility:** `metadata` columns for country-specific data without schema changes.
- **ULID for primary keys:** Time-sortable, globally unique.

### Tables

```sql
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- TENANTS
-- ============================================================
CREATE TABLE tenants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    plan            VARCHAR(50) NOT NULL DEFAULT 'free',
    country_code    VARCHAR(2) NOT NULL,  -- ISO 3166-1 alpha-2
    status          VARCHAR(50) NOT NULL DEFAULT 'active',
    config          JSONB NOT NULL DEFAULT '{}',
    max_users       INTEGER NOT NULL DEFAULT 5,
    max_searches_per_month INTEGER NOT NULL DEFAULT 1000,
    data_retention_days INTEGER NOT NULL DEFAULT 365,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_country ON tenants(country_code);

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    email           VARCHAR(255) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(50) NOT NULL DEFAULT 'viewer',
    is_active       BOOLEAN NOT NULL DEFAULT true,
    mfa_enabled     BOOLEAN NOT NULL DEFAULT false,
    mfa_secret      VARCHAR(255),
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    UNIQUE(tenant_id, email)
);
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);

-- ============================================================
-- SUBSCRIPTIONS
-- ============================================================
CREATE TABLE subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    plan            VARCHAR(50) NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'active',
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end   TIMESTAMPTZ NOT NULL,
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id    VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_subscriptions_tenant ON subscriptions(tenant_id);

-- ============================================================
-- COMPANIES
-- ============================================================
CREATE TABLE companies (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL REFERENCES tenants(id),
    name                    VARCHAR(500) NOT NULL,
    name_normalized         VARCHAR(500) NOT NULL,
    registration_number     VARCHAR(100),
    tax_id                  VARCHAR(100),
    country_code            VARCHAR(2) NOT NULL,
    legal_form              VARCHAR(100),
    status                  VARCHAR(50) NOT NULL DEFAULT 'active',
    address                 TEXT,
    city                    VARCHAR(255),
    region                  VARCHAR(255),
    postal_code             VARCHAR(20),
    phone                   VARCHAR(50),
    email                   VARCHAR(255),
    website                 VARCHAR(500),
    founded_date            DATE,
    dissolution_date        DATE,
    industry_codes          TEXT[],              -- NACE codes
    employee_count_range    VARCHAR(50),
    metadata                JSONB NOT NULL DEFAULT '{}',
    source                  VARCHAR(100),       -- 'registry', 'manual', 'provider'
    external_ids            JSONB NOT NULL DEFAULT '{}',  -- {"moldova_registry": "..."}
    last_synced_at          TIMESTAMPTZ,
    data_freshness_score    DECIMAL(3,2),       -- 0.00 to 1.00
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at              TIMESTAMPTZ
);
CREATE INDEX idx_companies_tenant ON companies(tenant_id);
CREATE INDEX idx_companies_registration ON companies(tenant_id, registration_number);
CREATE INDEX idx_companies_tax ON companies(tenant_id, tax_id);
CREATE INDEX idx_companies_country ON companies(country_code);
CREATE INDEX idx_companies_name_search ON companies USING gin(to_tsvector('simple', name_normalized));
CREATE INDEX idx_companies_status ON companies(tenant_id, status);
CREATE INDEX idx_companies_external_ids ON companies USING gin(external_ids);
CREATE INDEX idx_companies_synced ON companies(last_synced_at);

-- ============================================================
-- COMPANY RELATIONSHIPS
-- ============================================================
CREATE TABLE company_relations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    company_id          UUID NOT NULL REFERENCES companies(id),
    related_company_id  UUID NOT NULL REFERENCES companies(id),
    relation_type       VARCHAR(50) NOT NULL,  -- subsidiary/parent/partner/branch
    strength            DECIMAL(3,2) DEFAULT 1.0,
    start_date          DATE,
    end_date            DATE,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ,
    UNIQUE(tenant_id, company_id, related_company_id, relation_type)
);
CREATE INDEX idx_relations_company ON company_relations(company_id);
CREATE INDEX idx_relations_related ON company_relations(related_company_id);
CREATE INDEX idx_relations_tenant ON company_relations(tenant_id);

-- ============================================================
-- FINANCIAL REPORTS
-- ============================================================
CREATE TABLE financial_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    company_id      UUID NOT NULL REFERENCES companies(id),
    year            INTEGER NOT NULL,
    period          VARCHAR(20) NOT NULL DEFAULT 'annual',  -- annual/quarterly
    currency        VARCHAR(3) NOT NULL DEFAULT 'MDL',
    revenue         DECIMAL(18,2),
    profit_loss     DECIMAL(18,2),
    total_assets    DECIMAL(18,2),
    total_liabilities DECIMAL(18,2),
    equity          DECIMAL(18,2),
    cash_flow       DECIMAL(18,2),
    employees_count INTEGER,
    report_url      VARCHAR(1000),
    source          VARCHAR(100),
    raw_data        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    UNIQUE(tenant_id, company_id, year, period)
);
CREATE INDEX idx_financial_company ON financial_reports(company_id);
CREATE INDEX idx_financial_tenant ON financial_reports(tenant_id);
CREATE INDEX idx_financial_year ON financial_reports(company_id, year);

-- ============================================================
-- COURT CASES
-- ============================================================
CREATE TABLE court_cases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    company_id      UUID NOT NULL REFERENCES companies(id),
    case_number     VARCHAR(200) NOT NULL,
    court_name      VARCHAR(500),
    court_type      VARCHAR(50),  -- commercial/civil/criminal/administrative
    filing_date     DATE,
    status          VARCHAR(50) NOT NULL DEFAULT 'filed',
    plaintiff       VARCHAR(500),
    defendant       VARCHAR(500),
    amount_disputed DECIMAL(18,2),
    currency        VARCHAR(3),
    verdict         TEXT,
    verdict_date    DATE,
    source          VARCHAR(100),
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_court_company ON court_cases(company_id);
CREATE INDEX idx_court_tenant ON court_cases(tenant_id);
CREATE INDEX idx_court_status ON court_cases(status);
CREATE INDEX idx_court_filing ON court_cases(filing_date);

-- ============================================================
-- TENDERS (Public Procurement)
-- ============================================================
CREATE TABLE tenders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    company_id          UUID REFERENCES companies(id),  -- nullable: issuer or winner
    external_id         VARCHAR(200),
    title               VARCHAR(1000) NOT NULL,
    description         TEXT,
    procuring_entity    VARCHAR(500),
    tender_type         VARCHAR(50),
    status              VARCHAR(50) NOT NULL DEFAULT 'published',
    publication_date    DATE,
    deadline            DATE,
    estimated_value     DECIMAL(18,2),
    awarded_value       DECIMAL(18,2),
    currency            VARCHAR(3) DEFAULT 'MDL',
    winner_name         VARCHAR(500),
    winner_id           UUID REFERENCES companies(id),
    cpv_codes           TEXT[],
    source              VARCHAR(100),
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ,
    UNIQUE(tenant_id, external_id)
);
CREATE INDEX idx_tenders_company ON tenders(company_id);
CREATE INDEX idx_tenders_winner ON tenders(winner_id);
CREATE INDEX idx_tenders_tenant ON tenders(tenant_id);
CREATE INDEX idx_tenders_status ON tenders(status);
CREATE INDEX idx_tenders_date ON tenders(publication_date);

-- ============================================================
-- CERTIFICATIONS
-- ============================================================
CREATE TABLE certifications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    company_id          UUID NOT NULL REFERENCES companies(id),
    certification_type  VARCHAR(100) NOT NULL,
    name                VARCHAR(500) NOT NULL,
    issuing_body        VARCHAR(500),
    certificate_number  VARCHAR(200),
    issue_date          DATE,
    expiry_date         DATE,
    status              VARCHAR(50) NOT NULL DEFAULT 'active',
    scope               TEXT,
    source              VARCHAR(100),
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);
CREATE INDEX idx_certs_company ON certifications(company_id);
CREATE INDEX idx_certs_tenant ON certifications(tenant_id);
CREATE INDEX idx_certs_status ON certifications(status);

-- ============================================================
-- SANCTIONS
-- ============================================================
CREATE TABLE sanctions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    company_id      UUID REFERENCES companies(id),  -- nullable: may match by name
    person_name     VARCHAR(500),
    entity_name     VARCHAR(500),
    sanction_list   VARCHAR(50) NOT NULL,  -- UN/EU/OFAC/other
    sanction_type   VARCHAR(100),
    program         VARCHAR(200),
    listed_date     DATE,
    delisted_date   DATE,
    reason          TEXT,
    source_reference VARCHAR(500),
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_sanctions_company ON sanctions(company_id);
CREATE INDEX idx_sanctions_tenant ON sanctions(tenant_id);
CREATE INDEX idx_sanctions_list ON sanctions(sanction_list);
CREATE INDEX idx_sanctions_entity ON sanctions USING gin(to_tsvector('simple', coalesce(entity_name, '') || ' ' || coalesce(person_name, '')));

-- ============================================================
-- COMPANY STATISTICS
-- ============================================================
CREATE TABLE company_statistics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id),
    company_id  UUID NOT NULL REFERENCES companies(id),
    year        INTEGER NOT NULL,
    metric_type VARCHAR(100) NOT NULL,
    value       DECIMAL(18,4),
    source      VARCHAR(100),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(tenant_id, company_id, year, metric_type)
);
CREATE INDEX idx_stats_company ON company_statistics(company_id);
CREATE INDEX idx_stats_tenant ON company_statistics(tenant_id);
CREATE INDEX idx_stats_metric ON company_statistics(metric_type);

-- ============================================================
-- SYNC LOGS
-- ============================================================
CREATE TABLE sync_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    provider_type   VARCHAR(100) NOT NULL,
    country_code    VARCHAR(2) NOT NULL,
    status          VARCHAR(50) NOT NULL,  -- running/success/failed/partial
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    records_fetched INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed  INTEGER DEFAULT 0,
    error_message   TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX idx_sync_logs_tenant ON sync_logs(tenant_id);
CREATE INDEX idx_sync_logs_provider ON sync_logs(provider_type);
CREATE INDEX idx_sync_logs_status ON sync_logs(status);
CREATE INDEX idx_sync_logs_started ON sync_logs(started_at);

-- ============================================================
-- AUDIT LOGS (append-only, partitioned by month)
-- ============================================================
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(100) NOT NULL,
    resource_id     UUID,
    changes         JSONB,
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);

-- Monthly partitions (created by maintenance job)
-- CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs
--     FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- ============================================================
-- WEBHOOKS (outgoing webhook registrations)
-- ============================================================
CREATE TABLE webhook_registrations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    url             VARCHAR(1000) NOT NULL,
    secret          VARCHAR(255) NOT NULL,
    events          TEXT[] NOT NULL,  -- ['company.created', 'sync.completed']
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_webhooks_tenant ON webhook_registrations(tenant_id);

-- ============================================================
-- ROW-LEVEL SECURITY POLICIES
-- ============================================================
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_relations ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE court_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenders ENABLE ROW LEVEL SECURITY;
ALTER TABLE certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE sanctions ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Example policy (applied via session variable)
CREATE POLICY tenant_isolation ON companies
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## 7. Country Isolation & Provider Pattern

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    COUNTRY REGISTRY                              │
│                                                                 │
│  country_code → {providers: {...}, config: {...}}               │
│                                                                 │
│  "MD" → MoldovaAdapter                                         │
│  "RO" → RomaniaAdapter (future)                                │
│  "UA" → UkraineAdapter (future)                                │
└─────────────────────────────────────────────────────────────────┘
```

### Provider Interface (Port)

Every provider implements a base protocol:

```python
# src/credibil/ports/providers/base.py

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")  # Domain entity type


class BaseProvider(ABC, Generic[T]):
    """Base interface for all external data providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier for this provider (e.g., 'moldova_registry')."""
        ...

    @property
    @abstractmethod
    def country_code(self) -> str:
        """ISO 3166-1 alpha-2 country code."""
        ...

    @property
    @abstractmethod
    def data_source_name(self) -> str:
        """Human-readable name of the data source."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the external data source is reachable."""
        ...

    @abstractmethod
    async def fetch_by_identifier(
        self, identifier: str, id_type: str = "registration_number"
    ) -> T | None:
        """Fetch a single entity by known identifier."""
        ...

    @abstractmethod
    async def fetch_batch(
        self,
        identifiers: list[str],
        id_type: str = "registration_number",
    ) -> list[T]:
        """Fetch multiple entities by identifiers."""
        ...

    @abstractmethod
    async def fetch_all(
        self,
        since: datetime | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[T]:
        """Fetch all entities, optionally since a timestamp."""
        ...

    @abstractmethod
    async def search(
        self, query: str, filters: dict[str, Any] | None = None
    ) -> list[T]:
        """Search the external data source."""
        ...

    @abstractmethod
    def get_last_updated(self) -> datetime | None:
        """Return the last known update time of the external source."""
        ...
```

### Specific Provider Ports

```python
# src/credibil/ports/providers/company.py

class CompanyProvider(BaseProvider["CompanyEntity"]):
    """Provider for company registry data."""

    @abstractmethod
    async def fetch_by_registration_number(
        self, registration_number: str, country_code: str
    ) -> CompanyEntity | None:
        ...

    @abstractmethod
    async def fetch_directors(
        self, company_id: str
    ) -> list[DirectorEntity]:
        ...

    @abstractmethod
    async def fetch_shareholders(
        self, company_id: str
    ) -> list[ShareholderEntity]:
        ...

    @abstractmethod
    async def fetch_company_relations(
        self, company_id: str
    ) -> list[RelationEntity]:
        ...
```

```python
# src/credibil/ports/providers/court.py

class CourtProvider(BaseProvider["CourtCaseEntity"]):
    """Provider for court case data."""

    @abstractmethod
    async def fetch_cases_by_company(
        self, registration_number: str
    ) -> list[CourtCaseEntity]:
        ...

    @abstractmethod
    async def fetch_case_details(
        self, case_number: str
    ) -> CourtCaseEntity | None:
        ...
```

```python
# src/credibil/ports/providers/financial.py

class FinancialProvider(BaseProvider["FinancialReportEntity"]):
    """Provider for financial report data."""

    @abstractmethod
    async def fetch_reports(
        self,
        registration_number: str,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[FinancialReportEntity]:
        ...
```

```python
# src/credibil/ports/providers/procurement.py

class TenderProvider(BaseProvider["TenderEntity"]):
    """Provider for public procurement data."""

    @abstractmethod
    async def fetch_tenders_by_company(
        self, registration_number: str
    ) -> list[TenderEntity]:
        ...

    @abstractmethod
    async def fetch_active_tenders(
        self, filters: dict[str, Any] | None = None
    ) -> list[TenderEntity]:
        ...
```

```python
# src/credibil/ports/providers/certification.py

class CertificationProvider(BaseProvider["CertificationEntity"]):
    """Provider for certification/license data."""

    @abstractmethod
    async def fetch_certifications(
        self, registration_number: str
    ) -> list[CertificationEntity]:
        ...
```

```python
# src/credibil/ports/providers/sanctions.py

class SanctionProvider(BaseProvider["SanctionEntity"]):
    """Provider for sanctions list data."""

    @abstractmethod
    async def fetch_sanctions_by_name(
        self, name: str, match_threshold: float = 0.8
    ) -> list[SanctionEntity]:
        ...

    @abstractmethod
    async def fetch_sanctions_by_entity(
        self, registration_number: str
    ) -> list[SanctionEntity]:
        ...

    @abstractmethod
    async def get_lists(self) -> list[str]:
        """Return available sanction lists (UN, EU, OFAC, etc.)."""
        ...
```

```python
# src/credibil/ports/providers/statistics.py

class StatisticsProvider(BaseProvider["StatisticEntity"]):
    """Provider for company statistics data."""

    @abstractmethod
    async def fetch_statistics(
        self, registration_number: str, years: list[int] | None = None
    ) -> list[StatisticEntity]:
        ...
```

### Country Adapter Registration

```python
# src/credibil/countries/registry.py

from typing import Dict, Type
from credibil.ports.providers.base import BaseProvider


class CountryRegistry:
    """Registry of country-specific provider implementations."""

    _providers: Dict[str, Dict[str, Type[BaseProvider]]] = {}

    @classmethod
    def register(
        cls,
        country_code: str,
        provider_type: str,
        provider_class: Type[BaseProvider],
    ) -> None:
        if country_code not in cls._providers:
            cls._providers[country_code] = {}
        cls._providers[country_code][provider_type] = provider_class

    @classmethod
    def get_provider(
        cls, country_code: str, provider_type: str
    ) -> Type[BaseProvider] | None:
        return cls._providers.get(country_code, {}).get(provider_type)

    @classmethod
    def get_all_providers(
        cls, country_code: str
    ) -> Dict[str, Type[BaseProvider]]:
        return cls._providers.get(country_code, {})

    @classmethod
    def supported_countries(cls) -> list[str]:
        return list(cls._providers.keys())


# Decorator for easy registration
def provider(country_code: str, provider_type: str):
    def decorator(cls):
        CountryRegistry.register(country_code, provider_type, cls)
        return cls
    return decorator
```

### Moldova Implementation Example

```python
# src/credibil/countries/moldova/providers/company.py

import httpx
from credibil.ports.providers.company import CompanyProvider
from credibil.countries.registry import provider
from credibil.countries.moldova.config import MoldovaConfig
from credibil.countries.moldova.mappings.company import (
    map_external_to_domain,
)


@provider("MD", "company")
class MoldovaCompanyProvider(CompanyProvider):
    """Company data from Moldovan Public Services Agency (APS)."""

    def __init__(self, config: MoldovaConfig):
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.registry_base_url,
            timeout=30.0,
        )

    @property
    def provider_id(self) -> str:
        return "moldova_aps_registry"

    @property
    def country_code(self) -> str:
        return "MD"

    @property
    def data_source_name(self) -> str:
        return "Moldovan Agency of Public Services - Company Registry"

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get("/health")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def fetch_by_registration_number(
        self, registration_number: str, id_type: str = "registration_number"
    ) -> "CompanyEntity | None":
        resp = await self._client.get(
            f"/api/v1/companies/{registration_number}"
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return map_external_to_domain(resp.json())

    # ... other methods
```

### Adding a New Country

To add Romania (example):

1. Create `src/credibil/countries/romania/` directory
2. Create `config.py` with Romania-specific settings
3. Implement each provider: `providers/company.py`, `providers/court.py`, etc.
4. Create mappings: `mappings/company.py`, etc.
5. Create parsers if needed: `parsers/xml.py`, etc.
6. Register providers in `__init__.py`
7. Add `RO` to supported countries configuration

**Zero changes to core code.**

---

## 8. Internal Services Layer

### Service Architecture

Services are thin orchestration layers. They:
1. Accept commands/queries from the API layer
2. Coordinate between repositories, providers, and infrastructure
3. Emit domain events
4. Enforce business rules

```
┌──────────┐     ┌─────────────────┐     ┌──────────┐
│   API    │────▶│   Application   │────▶│   Domain │
│  Routes  │     │    Services     │     │  Events  │
└──────────┘     └────────┬────────┘     └──────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         ┌─────────┐ ┌─────────┐ ┌─────────┐
         │   Repo  │ │Provider │ │  Cache  │
         │   Port  │ │  Port   │ │  Port   │
         └─────────┘ └─────────┘ └─────────┘
```

### Company Service (Example)

```python
# src/credibil/application/company/handlers.py

class CompanyHandlers:
    def __init__(
        self,
        company_repo: CompanyRepository,
        relation_repo: RelationRepository,
        search_service: SearchService,
        cache: CacheService,
        event_bus: EventBus,
    ):
        self._repo = company_repo
        self._relations = relation_repo
        self._search = search_service
        self._cache = cache
        self._events = event_bus

    async def handle_create_company(
        self, cmd: CreateCompanyCommand
    ) -> CompanyDTO:
        company = Company.create(
            tenant_id=cmd.tenant_id,
            name=cmd.name,
            registration_number=cmd.registration_number,
            country_code=cmd.country_code,
            # ...
        )
        await self._repo.save(company)
        await self._search.index(company)
        await self._events.emit(CompanyCreated(company_id=company.id))
        return CompanyDTO.from_entity(company)

    async def handle_get_company(
        self, query: GetCompanyQuery
    ) -> CompanyDTO:
        cache_key = f"company:{query.tenant_id}:{query.company_id}"
        cached = await self._cache.get(cache_key)
        if cached:
            return CompanyDTO(**cached)

        company = await self._repo.find_by_id(
            query.company_id, query.tenant_id
        )
        if not company:
            raise CompanyNotFoundError(query.company_id)

        dto = CompanyDTO.from_entity(company)
        await self._cache.set(cache_key, dto.model_dump(), ttl=300)
        return dto

    async def handle_search_companies(
        self, query: SearchCompaniesQuery
    ) -> PaginatedResult[CompanyDTO]:
        return await self._search.search_companies(
            tenant_id=query.tenant_id,
            text=query.text,
            filters=query.filters,
            page=query.page,
            per_page=query.per_page,
        )
```

### Complete Service Map

| Service | Responsibilities |
|---|---|
| **CompanyService** | CRUD, search, relationship graph, enrichment |
| **FinancialService** | Report CRUD, financial analysis, trend computation |
| **CourtService** | Case CRUD, case search, risk scoring |
| **ProcurementService** | Tender CRUD, bid tracking, award analysis |
| **CertificationService** | Certification CRUD, expiry monitoring |
| **SanctionService** | Sanction matching, list updates, risk alerts |
| **StatisticsService** | Metric aggregation, trend analysis |
| **SearchService** | Full-text search, faceted search, indexing |
| **AuthService** | Registration, login, token management, MFA |
| **TenantService** | Tenant CRUD, configuration, feature flags |
| **SubscriptionService** | Plan management, billing integration, limits |
| **AuditService** | Audit log recording, compliance queries |
| **SyncService** | Provider orchestration, sync scheduling, conflict resolution |
| **AnalyticsService** | Dashboard metrics, reports, trend computation |
| **NotificationService** | Email, webhooks, in-app notifications |
| **ExportService** | PDF/CSV/Excel report generation |

---

## 9. API Structure

### REST API Design

```
Base URL: https://api.credibil.md/v1

Authentication: Bearer <jwt_token>
Tenant Context: X-Tenant-ID header (or derived from JWT)
```

### Endpoints

```
# ── Auth ──────────────────────────────────────────────
POST   /auth/register              # Register new user
POST   /auth/login                 # Login → JWT pair
POST   /auth/refresh               # Refresh access token
POST   /auth/logout                # Invalidate refresh token
POST   /auth/mfa/enable            # Enable MFA
POST   /auth/mfa/verify            # Verify MFA code
POST   /auth/password/reset        # Request password reset
POST   /auth/password/confirm      # Confirm password reset

# ── Users ─────────────────────────────────────────────
GET    /users/me                   # Current user profile
PUT    /users/me                   # Update profile
GET    /users                      # List users (admin)
POST   /users                      # Invite user (admin)
GET    /users/{id}                 # Get user (admin)
PUT    /users/{id}                 # Update user (admin)
DELETE /users/{id}                 # Deactivate user (admin)

# ── Companies ─────────────────────────────────────────
GET    /companies                  # List companies (paginated, filterable)
POST   /companies                  # Create company (manual entry)
GET    /companies/{id}             # Get company detail
PUT    /companies/{id}             # Update company
DELETE /companies/{id}             # Soft-delete company
GET    /companies/{id}/relations   # Get company relationships
GET    /companies/{id}/financial   # Get financial reports
GET    /companies/{id}/court       # Get court cases
GET    /companies/{id}/tenders     # Get procurement participation
GET    /companies/{id}/certifications # Get certifications
GET    /companies/{id}/sanctions   # Get sanctions matches
GET    /companies/{id}/statistics  # Get statistics
GET    /companies/{id}/timeline    # Get combined timeline
POST   /companies/{id}/sync        # Trigger on-demand sync
GET    /companies/{id}/risk-score  # Get computed risk score

# ── Search ────────────────────────────────────────────
POST   /search                     # Full-text search (companies + related)
POST   /search/companies           # Company-specific search
POST   /search/sanctions           # Sanctions search
GET    /search/suggestions         # Autocomplete suggestions

# ── Financial Reports ─────────────────────────────────
GET    /financial/reports          # List all reports (cross-company)
GET    /financial/reports/{id}     # Get specific report
GET    /financial/compare          # Compare multiple companies

# ── Court Cases ───────────────────────────────────────
GET    /court/cases                # List all cases
GET    /court/cases/{id}           # Get case detail

# ── Tenders ───────────────────────────────────────────
GET    /tenders                    # List all tenders
GET    /tenders/{id}               # Get tender detail
GET    /tenders/active             # Active tenders

# ── Certifications ────────────────────────────────────
GET    /certifications             # List all certifications
GET    /certifications/{id}        # Get certification detail

# ── Sanctions ─────────────────────────────────────────
GET    /sanctions                  # List sanctions
GET    /sanctions/{id}             # Get sanction detail
POST   /sanctions/check            # Check entity against sanctions

# ── Analytics ─────────────────────────────────────────
GET    /analytics/dashboard        # Dashboard summary
GET    /analytics/trends           # Trend data
GET    /analytics/reports          # Available reports

# ── Subscriptions ─────────────────────────────────────
GET    /subscription               # Current subscription
POST   /subscription               # Create/update subscription
POST   /subscription/checkout      # Create Stripe checkout session
POST   /subscription/webhook       # Stripe webhook receiver

# ── Webhooks ──────────────────────────────────────────
GET    /webhooks                   # List webhook registrations
POST   /webhooks                   # Register webhook
PUT    /webhooks/{id}              # Update webhook
DELETE /webhooks/{id}              # Delete webhook

# ── Admin Endpoints ────────────────────────────────── (Separate prefix: /admin/v1)
GET    /admin/v1/tenants           # List all tenants
POST   /admin/v1/tenants           # Create tenant
PUT    /admin/v1/tenants/{id}      # Update tenant
GET    /admin/v1/tenants/{id}/usage # Tenant usage stats
GET    /admin/v1/users             # List all users
GET    /admin/v1/subscriptions     # List all subscriptions
GET    /admin/v1/sync/logs         # Sync history
POST   /admin/v1/sync/trigger      # Trigger sync for all/specific tenant
GET    /admin/v1/audit             # Audit log viewer
GET    /admin/v1/analytics         # Platform-wide analytics
GET    /admin/v1/system/health     # System health check
GET    /admin/v1/system/metrics    # System metrics
```

### API Response Envelope

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 25,
    "total": 1234,
    "has_next": true
  },
  "request_id": "01H5X...",
  "timestamp": "2026-07-13T12:00:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "COMPANY_NOT_FOUND",
    "message": "Company with ID 'xxx' not found",
    "details": {}
  },
  "request_id": "01H5X...",
  "timestamp": "2026-07-13T12:00:00Z"
}
```

---

## 10. Authentication & Authorization

### Authentication Flow

```
┌──────┐     POST /auth/login      ┌──────────┐
│Client│──────────────────────────▶│Auth API  │
│      │◀──────────────────────────│          │
│      │  { access_token,          │          │
│      │    refresh_token }        │          │
│      │                           └──────────┘
│      │
│      │  GET /companies           ┌──────────┐
│      │  Authorization: Bearer    │API Server│
│      │──────────────────────────▶│          │
│      │                           │ Validate │
│      │                           │ JWT +    │
│      │                           │ Tenant   │
│      │                           └──────────┘
└──────┘
```

### JWT Token Structure

```json
{
  "sub": "user-uuid",
  "tenant": "tenant-uuid",
  "role": "admin",
  "permissions": ["company:read", "company:write", "sync:trigger"],
  "exp": 1689000000,
  "iat": 1689000000
}
```

### Role Hierarchy

```
Owner (tenant)
  └── Admin
       └── Editor
            └── Viewer
```

### Permissions Matrix

| Permission | Owner | Admin | Editor | Viewer |
|---|---|---|---|---|
| company:read | ✅ | ✅ | ✅ | ✅ |
| company:write | ✅ | ✅ | ✅ | ❌ |
| company:delete | ✅ | ✅ | ❌ | ❌ |
| sync:trigger | ✅ | ✅ | ❌ | ❌ |
| user:manage | ✅ | ✅ | ❌ | ❌ |
| subscription:manage | ✅ | ❌ | ❌ | ❌ |
| audit:read | ✅ | ✅ | ❌ | ❌ |
| analytics:read | ✅ | ✅ | ✅ | ✅ |
| webhook:manage | ✅ | ✅ | ❌ | ❌ |

---

## 11. Multi-Tenancy

### Tenant Isolation Strategy

**Row-Level Security (RLS)** with PostgreSQL:

```sql
-- Each API request sets the tenant context:
SET app.current_tenant_id = '<tenant-uuid>';

-- RLS policies automatically filter queries:
CREATE POLICY tenant_isolation ON companies
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Tenant Middleware

```python
# Middleware extracts tenant from JWT and sets DB session variable

class TenantMiddleware:
    async def __call__(self, request, call_next):
        tenant_id = request.state.user.tenant_id  # From JWT
        async with get_session() as session:
            await session.execute(
                text("SET app.current_tenant_id = :tid"),
                {"tid": str(tenant_id)},
            )
        response = await call_next(request)
        return response
```

### Tenant Configuration

Each tenant can have custom configuration stored in `tenants.config` (JSONB):

```json
{
  "enabled_providers": ["moldova_aps", "moldova_court"],
  "sync_frequency": "daily",
  "search_languages": ["ro", "ru", "en"],
  "notification_email": true,
  "export_watermark": true,
  "custom_fields": [
    {"name": "internal_risk_rating", "type": "select", "options": ["low", "medium", "high"]}
  ]
}
```

---

## 12. Subscriptions & Billing

### Plan Tiers

| Feature | Free | Starter | Pro | Enterprise |
|---|---|---|---|---|
| Users | 1 | 5 | 25 | Unlimited |
| Companies | 10 | 100 | 1,000 | Unlimited |
| Searches/month | 50 | 1,000 | 10,000 | Unlimited |
| Sync frequency | Manual | Weekly | Daily | Hourly |
| Data providers | Basic | All | All + Priority | All + Custom |
| API access | ❌ | Read-only | Full | Full + Webhooks |
| Export | ❌ | PDF | PDF + Excel | PDF + Excel + API |
| Support | Community | Email | Priority | Dedicated |
| Audit logs | 7 days | 30 days | 1 year | Unlimited |

### Stripe Integration Flow

```
Tenant subscribes → Create Stripe customer
                  → Create Stripe subscription
                  → Webhook: subscription.updated
                  → Update tenants.plan + subscriptions table
                  → Enforce limits via middleware
```

### Limit Enforcement

```python
class SubscriptionLimits:
    async def check_search_limit(self, tenant_id: UUID) -> bool:
        tenant = await self.tenant_repo.find(tenant_id)
        usage = await self.usage_repo.get_monthly_searches(tenant_id)
        return usage < tenant.max_searches_per_month
```

---

## 13. Background Workers & Task Queue

### Celery Architecture

```
┌──────────────────────────────────────────────────────┐
│                    REDIS BROKER                       │
│                                                      │
│  Queues:                                             │
│    ├── default     (general tasks)                   │
│    ├── etl         (extract-transform-load)          │
│    ├── sync        (data synchronization)            │
│    ├── search      (search index operations)         │
│    ├── analytics   (computation-heavy tasks)         │
│    ├── notifications (email, webhooks)               │
│    └── reports     (PDF/Excel generation)            │
└──────────────┬───────────────────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼          ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│Worker 1││Worker 2││Worker 3││Worker 4││Worker 5│
│(default││ (etl)  ││ (sync) ││(search)││(notif) │
│+notif) ││        ││        ││        ││+reports│
└────────┘└────────┘└────────┘└────────┘└────────┘
```

### Task Definitions

```python
# ETL Tasks
etl.extract_company_data           # Extract from provider → raw data
etl.transform_company_data         # Raw → domain entity mapping
etl.load_company_data              # Domain entity → database
etl.extract_financial_data
etl.extract_court_data
etl.extract_tender_data
etl.extract_certification_data
etl.extract_sanction_data
etl.extract_statistics_data

# Sync Tasks
sync.sync_all_providers            # Trigger all providers for a tenant
sync.sync_provider                 # Sync specific provider
sync.sync_company                  # Sync all data for one company
sync.reconcile_data                # Detect and resolve conflicts

# Search Tasks
search.index_company               # Index single company
search.index_batch                 # Batch index companies
search.reindex_all                 # Full reindex
search.update_index                # Update changed documents

# Analytics Tasks
analytics.compute_risk_scores      # Recalculate risk scores
analytics.compute_statistics       # Aggregate statistics
analytics.generate_trends          # Trend analysis

# Notification Tasks
notifications.send_email
notifications.send_webhook
notifications.send_alert           # Sanction/expiry alerts

# Report Tasks
reports.generate_company_report    # PDF company report
reports.generate_portfolio_report  # Multi-company report
reports.export_data                # CSV/Excel export
```

### Periodic Schedule (Celery Beat)

```python
# src/credibil/workers/schedules/periodic.py

CELERY_BEAT_SCHEDULE = {
    # ── Moldova Sync ──────────────────────────────
    "sync-moldova-companies-daily": {
        "task": "sync.sync_provider",
        "schedule": crontab(hour=2, minute=0),  # 2:00 AM UTC
        "kwargs": {"country_code": "MD", "provider_type": "company"},
    },
    "sync-moldova-courts-daily": {
        "task": "sync.sync_provider",
        "schedule": crontab(hour=3, minute=0),
        "kwargs": {"country_code": "MD", "provider_type": "court"},
    },
    "sync-moldova-tenders-daily": {
        "task": "sync.sync_provider",
        "schedule": crontab(hour=4, minute=0),
        "kwargs": {"country_code": "MD", "provider_type": "procurement"},
    },
    "sync-moldova-financial-monthly": {
        "task": "sync.sync_provider",
        "schedule": crontab(hour=5, minute=0, day_of_month=1),  # 1st of month
        "kwargs": {"country_code": "MD", "provider_type": "financial"},
    },
    "sync-sanctions-weekly": {
        "task": "sync.sync_provider",
        "schedule": crontab(hour=6, minute=0, day_of_week=1),  # Monday
        "kwargs": {"country_code": "MD", "provider_type": "sanctions"},
    },

    # ── Maintenance ────────────────────────────────
    "reindex-search-daily": {
        "task": "search.reindex_all",
        "schedule": crontab(hour=1, minute=0),
    },
    "compute-risk-scores-daily": {
        "task": "analytics.compute_risk_scores",
        "schedule": crontab(hour=7, minute=0),
    },
    "compute-analytics-daily": {
        "task": "analytics.compute_statistics",
        "schedule": crontab(hour=8, minute=0),
    },
    "check-certification-expiry-weekly": {
        "task": "notifications.check_expiry",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
    },
    "create-audit-partitions-monthly": {
        "task": "maintenance.create_audit_partitions",
        "schedule": crontab(hour=0, minute=0, day_of_month=28),
    },
    "cleanup-old-sync-logs-monthly": {
        "task": "maintenance.cleanup_sync_logs",
        "schedule": crontab(hour=0, minute=0, day_of_month=1),
    },
}
```

### Worker Configuration

```python
# src/credibil/workers/config.py

from celery import Celery

app = Celery("credibil")

app.conf.update(
    broker_url="redis://redis:6379/0",
    result_backend="redis://redis:6379/1",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "etl.*": {"queue": "etl"},
        "sync.*": {"queue": "sync"},
        "search.*": {"queue": "search"},
        "analytics.*": {"queue": "analytics"},
        "notifications.*": {"queue": "notifications"},
        "reports.*": {"queue": "reports"},
    },
    task_default_queue="default",
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_soft_time_limit=300,      # 5 min soft limit
    task_time_limit=600,           # 10 min hard limit
    task_max_retries=3,
    task_default_retry_delay=60,   # 1 min between retries
)
```

---

## 14. ETL Pipeline

### Pipeline Architecture

```
┌─────────┐    ┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ EXTRACT │───▶│  VALIDATE   │───▶│TRANSFORM │───▶│  LOAD    │───▶│  INDEX   │
│         │    │             │    │          │    │          │    │          │
│ Provider│    │ Schema +    │    │ Map to   │    │ Database │    │ Search   │
│ .fetch  │    │ Business    │    │ Domain   │    │ Upsert   │    │ Index    │
│         │    │ Rules       │    │ Entities │    │          │    │          │
└─────────┘    └─────────────┘    └──────────┘    └──────────┘    └──────────┘
      │                                                        │
      └────────────────────────────────────────────────────────┘
                    Sync Log tracks: counts, errors, timing
```

### ETL Flow per Company

```
1. TRIGGER
   └── User requests sync OR scheduled beat fires
       └── Creates SyncLog record (status: running)

2. EXTRACT
   └── For each provider_type in tenant config:
       ├── CompanyProvider.fetch_by_identifier(reg_number)
       ├── CourtProvider.fetch_cases_by_company(reg_number)
       ├── FinancialProvider.fetch_reports(reg_number)
       ├── TenderProvider.fetch_tenders_by_company(reg_number)
       ├── CertificationProvider.fetch_certifications(reg_number)
       ├── SanctionProvider.fetch_sanctions_by_entity(reg_number)
       └── StatisticsProvider.fetch_statistics(reg_number)

3. VALIDATE
   └── For each raw record:
       ├── Schema validation (Pydantic)
       ├── Business rule validation
       ├── Deduplication check
       └── Conflict detection (stale data?)

4. TRANSFORM
   └── For each valid record:
       ├── Apply country-specific mapping (mappings/*.py)
       ├── Normalize field names
       ├── Resolve relationships
       ├── Compute derived fields
       └── Generate domain entities

5. LOAD
   └── For each transformed entity:
       ├── Upsert into database (INSERT ... ON CONFLICT)
       ├── Update company.last_synced_at
       ├── Update company.data_freshness_score
       └── Emit domain event (CompanyUpdated, etc.)

6. INDEX
   └── For each changed entity:
       ├── Update Meilisearch index
       └── Update cache

7. COMPLETE
   └── Update SyncLog:
       ├── status: success / failed / partial
       ├── records_fetched, records_created, records_updated
       ├── completed_at timestamp
       └── error_message if failed
```

### ETL Task Implementation

```python
# src/credibil/workers/tasks/etl/company.py

from credibil.workers.app import app
from credibil.countries.registry import CountryRegistry


@app.task(bind=True, queue="etl", max_retries=3)
def extract_company_data(self, tenant_id: str, company_id: str, country_code: str):
    """Extract company data from external provider."""
    import asyncio

    async def _extract():
        provider_class = CountryRegistry.get_provider(country_code, "company")
        if not provider_class:
            raise ValueError(f"No company provider for {country_code}")

        # Provider config loaded from tenant settings
        provider = await _build_provider(provider_class, tenant_id)
        raw_data = await provider.fetch_by_identifier(company_id)

        if raw_data:
            # Chain to transform
            transform_company_data.delay(
                tenant_id, company_id, country_code, raw_data.dict()
            )

    asyncio.run(_extract())


@app.task(bind=True, queue="etl", max_retries=3)
def transform_company_data(self, tenant_id: str, company_id: str, country_code: str, raw_data: dict):
    """Transform raw provider data to domain entities."""
    import asyncio

    async def _transform():
        mapping_module = _import_mapping(country_code, "company")
        domain_entity = mapping_module.map_to_domain(raw_data)

        # Chain to load
        load_company_data.delay(
            tenant_id, company_id, country_code, domain_entity.dict()
        )

    asyncio.run(_transform())


@app.task(bind=True, queue="etl", max_retries=3)
def load_company_data(self, tenant_id: str, company_id: str, country_code: str, entity_data: dict):
    """Load transformed data into database."""
    import asyncio

    async def _load():
        async with get_session() as session:
            repo = SQLAlchemyCompanyRepository(session)
            entity = Company(**entity_data)
            await repo.upsert(entity)
            await session.commit()

            # Trigger search indexing
            search.index_company.delay(tenant_id, company_id)

    asyncio.run(_load())
```

---

## 15. Synchronization Architecture

### Sync Modes

| Mode | Trigger | Scope | Frequency |
|---|---|---|---|
| **Full Sync** | Scheduled / Admin trigger | All companies for all tenants | Daily / Weekly |
| **Incremental** | Scheduled | Only changed records (since last sync) | Daily |
| **On-Demand** | User request | Single company, all providers | Real-time |
| **Event-Driven** | External webhook | Specific record | Real-time |

### Sync Orchestration

```
┌──────────────────────────────────────────────────────────────────┐
│                     SYNC ORCHESTRATOR                             │
│                                                                  │
│  1. Determine sync scope (full / incremental / on-demand)        │
│  2. Check provider health                                       │
│  3. For each provider_type:                                     │
│     a. Fetch data from provider                                 │
│     b. Compare with existing data (conflict resolution)          │
│     c. Apply changes (upsert)                                   │
│     d. Record sync metrics                                      │
│  4. Update search indices                                       │
│  5. Emit sync events                                            │
│  6. Update sync log                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Conflict Resolution

```python
class ConflictResolver:
    """Resolve conflicts between local and provider data."""

    def resolve(self, local: Entity, remote: Entity, strategy: str) -> Entity:
        if strategy == "provider_wins":
            return remote  # External source is authoritative
        elif strategy == "local_wins":
            return local   # User edits take priority
        elif strategy == "newest_wins":
            if remote.updated_at > local.updated_at:
                return remote
            return local
        elif strategy == "merge":
            return self._merge(local, remote)
```

### Sync Configuration per Tenant

```json
{
  "sync": {
    "enabled": true,
    "frequency": "daily",
    "providers": {
      "company": {"enabled": true, "strategy": "provider_wins"},
      "court": {"enabled": true, "strategy": "provider_wins"},
      "financial": {"enabled": true, "strategy": "merge"},
      "procurement": {"enabled": true, "strategy": "provider_wins"},
      "certification": {"enabled": true, "strategy": "provider_wins"},
      "sanctions": {"enabled": true, "strategy": "provider_wins"},
      "statistics": {"enabled": true, "strategy": "provider_wins"}
    },
    "conflict_resolution": "provider_wins",
    "retry_on_failure": true,
    "alert_on_failure": true
  }
}
```

---

## 16. Cache Layer

### Cache Strategy

```
┌──────────────────────────────────────────────────────────────┐
│                      CACHE LAYERS                            │
│                                                              │
│  L1: In-Process Cache (TTL: 60s)                            │
│    └── Hot config, feature flags                            │
│                                                              │
│  L2: Redis Cache (TTL: 5min - 1hr)                          │
│    ├── Company details          (5 min)                      │
│    ├── Search results           (2 min)                      │
│    ├── Analytics aggregates     (15 min)                     │
│    ├── User sessions            (30 min)                     │
│    └── Provider health status   (1 min)                      │
│                                                              │
│  L3: Database (source of truth)                              │
│    └── All persistent data                                    │
└──────────────────────────────────────────────────────────────┘
```

### Cache Key Schema

```
credibil:{tenant_id}:{entity}:{id}           # Company detail
credibil:{tenant_id}:search:{hash}           # Search results
credibil:{tenant_id}:analytics:{type}:{id}   # Analytics
credibil:provider:health:{country}:{type}    # Provider health
credibil:session:{token_hash}                # User session
credibil:rate_limit:{tenant_id}:{endpoint}   # Rate limiting
```

### Cache Patterns

```python
# Cache-Aside (Lazy Loading)
async def get_company(self, company_id: UUID) -> Company:
    cache_key = f"credibil:{self.tenant_id}:company:{company_id}"

    # Try cache first
    cached = await self.cache.get(cache_key)
    if cached:
        return Company(**cached)

    # Cache miss → load from DB
    company = await self.repo.find_by_id(company_id)
    if company:
        await self.cache.set(cache_key, company.model_dump(), ttl=300)

    return company


# Write-Through (Cache invalidation on write)
async def update_company(self, company: Company) -> Company:
    await self.repo.save(company)
    cache_key = f"credibil:{self.tenant_id}:company:{company.id}"
    await self.cache.delete(cache_key)
    # Also invalidate search cache
    await self.cache.delete_pattern(
        f"credibil:{self.tenant_id}:search:*"
    )
    return company


# Cache-Aside with Stampede Protection
async def get_or_fetch_company(self, company_id: UUID) -> Company:
    cache_key = f"credibil:{self.tenant_id}:company:{company_id}"

    # Try cache
    cached = await self.cache.get(cache_key)
    if cached:
        return Company(**cached)

    # Use lock to prevent stampede
    lock_key = f"lock:company:{company_id}"
    async with self.cache.lock(lock_key, timeout=5, ttl=10):
        # Double-check after acquiring lock
        cached = await self.cache.get(cache_key)
        if cached:
            return Company(**cached)

        company = await self.repo.find_by_id(company_id)
        if company:
            await self.cache.set(cache_key, company.model_dump(), ttl=300)
        return company
```

### Cache Invalidation Events

| Event | Cache Keys Invalidated |
|---|---|
| `CompanyUpdated` | `company:{id}`, `search:*` |
| `SyncCompleted` | `company:{id}`, `search:*`, `analytics:*` |
| `TenantConfigChanged` | All keys for tenant |
| `UserUpdated` | `session:{token}` |

---

## 17. Search Architecture

### Search Engine: Meilisearch

```
┌──────────────────────────────────────────────────────────────┐
│                     MEILISEARCH                               │
│                                                              │
│  Indexes:                                                    │
│  ├── companies          (primary search index)               │
│  ├── companies_v2       (reindex target, swap on completion) │
│  ├── court_cases        (court case search)                  │
│  ├── tenders            (procurement search)                 │
│  └── sanctions          (sanctions search)                   │
│                                                              │
│  Filters:                                                    │
│  ├── country_code       (string)                             │
│  ├── status             (string)                             │
│  ├── legal_form         (string)                             │
│  ├── industry_codes     (string[])                           │
│  ├── has_court_cases    (bool)                               │
│  ├── has_sanctions      (bool)                               │
│  └── last_synced_at     (datetime)                           │
│                                                              │
│  Sortable:                                                   │
│  ├── name               (string)                             │
│  ├── relevance_score    (float)                              │
│  ├── data_freshness     (float)                              │
│  └── created_at         (datetime)                           │
│                                                              │
│  Tenant isolation: filter by tenant_id in all queries       │
└──────────────────────────────────────────────────────────────┘
```

### Search Document Schema

```json
{
  "id": "company-uuid",
  "tenant_id": "tenant-uuid",
  "name": "SC Example SRL",
  "name_normalized": "sc example srl",
  "registration_number": "12345678",
  "tax_id": "MD1234567",
  "country_code": "MD",
  "legal_form": "SRL",
  "status": "active",
  "city": "Chisinau",
  "region": "Chisinau",
  "industry_codes": ["6201", "6202"],
  "employee_count_range": "50-249",
  "has_court_cases": true,
  "has_sanctions": false,
  "has_financial_reports": true,
  "court_cases_count": 3,
  "sanctions_count": 0,
  "data_freshness_score": 0.95,
  "last_synced_at": "2026-07-13T00:00:00Z",
  "created_at": "2026-01-01T00:00:00Z"
}
```

### Search Features

```
Full-Text Search
  └── "Example SRL Chisinau" → matches name, city

Faceted Search
  └── Filter by: status, legal_form, country, industry

Autocomplete
  └── Typing "exam" → ["SC Example SRL", "Example Trading SRL"]

Typo-Tolerance
  └── "Exmple" → "Example"

Multi-Language
  └── Romanian, Russian, English tokenization

Search Ranking
  └── Name match > Registration match > City match > Full-text
```

### Search Index Maintenance

```
On Company Create/Update:
  └── Async task: index_company
       ├── Transform domain entity → search document
       └── Upsert into Meilisearch

On Sync Complete:
  └── Async task: reindex_changed
       └── Batch update all changed companies

Full Reindex (nightly):
  └── Create new index (companies_v2)
       ├── Load all companies from DB
       ├── Batch upload to Meilisearch
       └── Swap indexes (atomic)
```

---

## 18. Audit Logs

### What Gets Audited

| Action | Entity | Details |
|---|---|---|
| `user.login` | User | IP, user agent |
| `user.logout` | User | |
| `company.create` | Company | Full entity |
| `company.update` | Company | Changed fields only |
| `company.delete` | Company | Soft delete |
| `company.view` | Company | Accessed fields |
| `sync.trigger` | SyncLog | Provider, scope |
| `sync.complete` | SyncLog | Records changed |
| `subscription.change` | Subscription | Plan change details |
| `tenant.config_change` | Tenant | Config diff |
| `webhook.register` | Webhook | URL, events |
| `export.generate` | Export | Type, filters |

### Audit Log Implementation

```python
# Audit logging via decorator/middleware

class AuditMiddleware:
    """Automatically log API actions."""

    async def __call__(self, request, call_next):
        response = await call_next(request)

        if self._should_audit(request, response):
            await self._log_audit(
                tenant_id=request.state.tenant_id,
                user_id=request.state.user.id,
                action=self._derive_action(request),
                resource_type=self._derive_resource(request),
                resource_id=self._extract_resource_id(request),
                changes=self._compute_changes(request, response),
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
            )

        return response
```

### Audit Log Queries

```python
# Common audit queries
class AuditQueries:
    async def get_company_history(
        self, tenant_id: UUID, company_id: UUID, limit: int = 50
    ) -> list[AuditLog]:
        """Get all audit events for a specific company."""

    async def get_user_activity(
        self, tenant_id: UUID, user_id: UUID, days: int = 30
    ) -> list[AuditLog]:
        """Get user activity in the last N days."""

    async def get_recent_changes(
        self, tenant_id: UUID, resource_type: str, limit: int = 100
    ) -> list[AuditLog]:
        """Get recent changes to a resource type."""

    async def get_compliance_report(
        self, tenant_id: UUID, start_date: date, end_date: date
    ) -> ComplianceReport:
        """Generate compliance report for date range."""
```

---

## 19. Analytics & Statistics

### Dashboard Metrics

```
┌──────────────────────────────────────────────────────┐
│                 ANALYTICS DASHBOARD                    │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │Companies │ │Court     │ │Tenders   │ │Sanctions ││
│  │Tracked   │ │Cases     │ │Monitored │ │Alerts    ││
│  │  1,234   │ │    567   │ │    890   │ │     12   ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘│
│                                                      │
│  ┌──────────────────────┐ ┌──────────────────────┐   │
│  │Risk Distribution     │ │Sync Status           │   │
│  │  Low:    60%  ██████ │ │  Fresh: 85%  ████████│   │
│  │  Medium: 30%  ███    │ │  Stale: 15%  ██      │   │
│  │  High:   10%  █      │ │  Failed: 0%           │   │
│  └──────────────────────┘ └──────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │Activity Timeline (30 days)                    │    │
│  │                                               │    │
│  │  ▁▂▃▂▅▇▆▅▇█▇█▇█▅▇█▇█▇█▇█▅                   │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

### Precomputed Analytics

```python
# Analytics stored in materialized views + Redis cache

class AnalyticsService:
    async def get_dashboard(self, tenant_id: UUID) -> DashboardDTO:
        return DashboardDTO(
            companies_count=await self._get_metric(tenant_id, "companies_count"),
            court_cases_count=await self._get_metric(tenant_id, "court_cases_count"),
            tenders_count=await self._get_metric(tenant_id, "tenders_count"),
            sanctions_count=await self._get_metric(tenant_id, "sanctions_count"),
            risk_distribution=await self._get_risk_distribution(tenant_id),
            sync_status=await self._get_sync_status(tenant_id),
            recent_activity=await self._get_recent_activity(tenant_id),
            search_trends=await self._get_search_trends(tenant_id),
        )
```

### Risk Score Computation

```python
class RiskScorer:
    """Compute company risk score based on multiple factors."""

    def compute(self, company: Company, data: dict) -> RiskScore:
        factors = {
            "court_cases": self._court_risk(data["court_cases"]),
            "sanctions": self._sanction_risk(data["sanctions"]),
            "financial_health": self._financial_risk(data["financial_reports"]),
            "certification_status": self._cert_risk(data["certifications"]),
            "data_freshness": self._freshness_risk(company),
        }
        weighted_score = sum(
            factors[k] * self.WEIGHTS[k] for k in factors
        )
        return RiskScore(
            score=weighted_score,
            level=self._score_to_level(weighted_score),
            factors=factors,
        )
```

---

## 20. Frontend Architecture

### Tech Stack

| Concern | Technology |
|---|---|
| Framework | React 18+ with TypeScript |
| Build Tool | Vite |
| State Management | Zustand (client) + React Query (server) |
| Styling | Tailwind CSS + shadcn/ui |
| Routing | React Router v6 |
| Forms | React Hook Form + Zod |
| Charts | Recharts |
| Tables | TanStack Table |
| i18n | react-i18next |

### Page Structure

```
/                           → Dashboard
/login                      → Login page
/register                   → Registration

/companies                  → Company list (searchable, filterable)
/companies/:id              → Company detail (tabs)
/companies/:id/overview     → Overview tab
/companies/:id/financial    → Financial reports tab
/companies/:id/court        → Court cases tab
/companies/:id/tenders      → Tenders tab
/companies/:id/certs        → Certifications tab
/companies/:id/sanctions    → Sanctions tab
/companies/:id/relations    → Relationship graph tab
/companies/:id/statistics   → Statistics tab
/companies/:id/timeline     → Timeline (all events)
/companies/:id/sync         → Sync status

/search                     → Advanced search page

/analytics                  → Analytics dashboard
/analytics/trends           → Trend analysis

/certifications             → Certifications overview
/sanctions                  → Sanctions overview

/settings                   → Tenant settings
/settings/profile           → User profile
/settings/team              → Team management
/settings/billing           → Subscription management
/settings/webhooks          → Webhook configuration
```

### Component Architecture

```
src/
├── components/
│   ├── ui/                     # shadcn/ui primitives
│   │   ├── button.tsx
│   │   ├── dialog.tsx
│   │   ├── table.tsx
│   │   ├── form.tsx
│   │   └── ...
│   │
│   ├── layout/
│   │   ├── AppShell.tsx        # Main layout (sidebar + content)
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── Breadcrumbs.tsx
│   │
│   ├── company/
│   │   ├── CompanyCard.tsx
│   │   ├── CompanyDetail.tsx
│   │   ├── CompanyTimeline.tsx
│   │   ├── RelationshipGraph.tsx
│   │   └── RiskBadge.tsx
│   │
│   ├── financial/
│   │   ├── FinancialTable.tsx
│   │   ├── FinancialChart.tsx
│   │   └── ComparisonView.tsx
│   │
│   ├── court/
│   │   ├── CourtCaseCard.tsx
│   │   └── CourtTimeline.tsx
│   │
│   ├── search/
│   │   ├── SearchBar.tsx
│   │   ├── SearchFilters.tsx
│   │   ├── SearchResults.tsx
│   │   └── Autocomplete.tsx
│   │
│   └── charts/
│       ├── BarChart.tsx
│       ├── LineChart.tsx
│       └── PieChart.tsx
│
├── hooks/
│   ├── useCompanies.ts         # React Query hooks
│   ├── useCompany.ts
│   ├── useSearch.ts
│   ├── useAuth.ts
│   └── ...
│
├── lib/
│   ├── api.ts                  # Axios instance + interceptors
│   ├── auth.ts                 # Token management
│   ├── utils.ts
│   └── validators.ts           # Zod schemas
```

---

## 21. Admin Panel Architecture

### Separate SPA

The admin panel is a separate React application deployed independently.

```
/admin/* routes → Admin SPA
```

### Admin Pages

```
/admin/login                       → Admin login
/admin/dashboard                   → Platform overview
/admin/tenants                     → Tenant list
/admin/tenants/:id                 → Tenant detail + config
/admin/tenants/:id/usage           → Usage metrics
/admin/users                       → All users
/admin/subscriptions               → Subscription overview
/admin/sync                        → Sync status + logs
/admin/sync/trigger                → Manual sync trigger
/admin/audit                       → Audit log viewer
/admin/analytics                   → Platform analytics
/admin/system/health               → Service health
/admin/system/config               → System configuration
```

### Admin Features

- **Tenant Management:** Create, suspend, configure tenants. View usage, limits.
- **User Management:** View all users across tenants. Deactivate, impersonate.
- **Sync Management:** Monitor sync status. Trigger manual syncs. View sync logs.
- **Audit Viewer:** Search/filter audit logs. Export compliance reports.
- **System Health:** Service status, queue depths, error rates, latency.
- **Analytics:** Platform-wide metrics, tenant growth, feature usage.

---

## 22. Deployment Architecture

### Development

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports: ["8000:8000"]
    depends_on: [db, redis, search]
    environment:
      DATABASE_URL: postgresql+asyncpg://credibil:credibil@db:5432/credibil
      REDIS_URL: redis://redis:6379/0
      MEILISEARCH_URL: http://search:7700

  db:
    image: postgres:15
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  search:
    image: getmeili/meilisearch:v1.3
    ports: ["7700:7700"]
    volumes: [msdata:/meili_data]

  worker:
    build: .
    command: celery -A credibil.workers.app worker -l info -Q default,etl,sync,search,analytics,notifications,reports
    depends_on: [db, redis]

  beat:
    build: .
    command: celery -A credibil.workers.app beat -l info
    depends_on: [redis]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]

  admin:
    build: ./admin
    ports: ["3001:3001"]

volumes:
  pgdata:
  msdata:
```

### Production

```
┌──────────────────────────────────────────────────────────────┐
│                    PRODUCTION STACK                           │
│                                                              │
│  Load Balancer (Nginx/Traefik)                               │
│    ├── api.credibil.md → API servers (2+ replicas)          │
│    ├── admin.credibil.md → Admin panel                      │
│    └── credibil.md → Frontend (CDN)                         │
│                                                              │
│  API Servers (FastAPI + Uvicorn)                             │
│    └── 2+ replicas behind load balancer                     │
│                                                              │
│  Workers (Celery)                                            │
│    ├── 2x ETL workers                                       │
│    ├── 2x Sync workers                                      │
│    ├── 1x Search worker                                     │
│    ├── 1x Notification worker                               │
│    └── 1x Report worker                                     │
│                                                              │
│  Database (PostgreSQL)                                       │
│    ├── Primary (write)                                       │
│    └── Replica (read) - optional                             │
│                                                              │
│  Cache (Redis)                                               │
│    └── Single instance with persistence                     │
│                                                              │
│  Search (Meilisearch)                                        │
│    └── Single instance                                       │
│                                                              │
│  Object Storage (S3/MinIO)                                   │
│    └── For reports, exports, documents                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 23. Observability

### Logging

```python
# Structured JSON logging
import structlog

logger = structlog.get_logger()

# Usage
logger.info(
    "company.synced",
    company_id=str(company.id),
    tenant_id=str(tenant_id),
    provider="moldova_aps",
    records_updated=5,
    duration_ms=1234,
)
```

### Metrics (Prometheus)

```
# Key metrics
credibil_api_requests_total{method, endpoint, status}
credibil_api_request_duration_seconds{method, endpoint}
credibil_sync_records_fetched_total{provider, country}
credibil_sync_records_updated_total{provider, country}
credibil_sync_duration_seconds{provider, country}
credibil_sync_errors_total{provider, country}
credibil_search_queries_total
credibil_search_duration_seconds
credibil_cache_hits_total{cache_layer}
credibil_cache_misses_total{cache_layer}
credibil_worker_tasks_total{task, status}
credibil_worker_task_duration_seconds{task}
credibil_db_query_duration_seconds{operation}
credibil_active_tenants_total
credibil_active_users_total
```

### Health Checks

```python
# GET /health
{
    "status": "healthy",
    "version": "1.0.0",
    "checks": {
        "database": {"status": "healthy", "latency_ms": 2},
        "redis": {"status": "healthy", "latency_ms": 1},
        "search": {"status": "healthy", "latency_ms": 5},
        "workers": {"status": "healthy", "active_tasks": 3}
    }
}
```

---

## 24. Security

### Security Measures

| Layer | Measure |
|---|---|
| **Transport** | TLS 1.3 everywhere |
| **Authentication** | JWT (RS256) with short-lived access tokens (15 min) + refresh tokens (7 days) |
| **Password** | bcrypt with work factor 12 |
| **MFA** | TOTP (RFC 6238) via authenticator apps |
| **Rate Limiting** | Per-tenant rate limiting (Redis-based) |
| **Input Validation** | Pydantic schemas on all endpoints |
| **SQL Injection** | SQLAlchemy parameterized queries |
| **XSS** | React auto-escaping + CSP headers |
| **CSRF** | SameSite cookies + CSRF tokens |
| **Data Encryption** | AES-256 for sensitive fields at rest |
| **API Keys** | HMAC-signed for API access |
| **Audit** | All mutations logged |
| **Secrets** | Environment variables, never in code |
| **Dependencies** | Automated vulnerability scanning |
| **RLS** | PostgreSQL row-level security for tenant isolation |

### Rate Limiting

```python
# Per-tenant, per-endpoint rate limits
RATE_LIMITS = {
    "free": {"search": "50/day", "api": "100/hour"},
    "starter": {"search": "1000/month", "api": "1000/hour"},
    "pro": {"search": "10000/month", "api": "10000/hour"},
    "enterprise": {"search": "unlimited", "api": "unlimited"},
}
```

---

## Summary: Adding a New Country

**Steps to add a new country (e.g., Romania):**

1. Create `src/credibil/countries/romania/` directory
2. Create `config.py` with Romania-specific API URLs, credentials
3. Implement 7 providers: `providers/{company,court,financial,procurement,certification,sanctions,statistics}.py`
4. Each provider implements the corresponding port from `ports/providers/`
5. Create `mappings/*.py` for data transformation
6. Create `parsers/*.py` if needed for custom data formats
7. Register providers in `romania/__init__.py` using `@provider("RO", "company")` decorator
8. Add `"RO"` to supported countries in configuration
9. Add Celery Beat schedules for Romania sync tasks

**No changes to:** core domain, services, API, frontend, database schema (new data goes into JSONB `metadata`), or any other country's code.
