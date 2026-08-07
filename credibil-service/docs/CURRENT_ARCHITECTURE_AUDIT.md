# Credibil Codebase Architecture Audit

**Date:** 2026-07-16  
**Auditor:** Automated (opencode)  
**Scope:** Complete codebase inspection — backend, frontend, infrastructure, data pipelines

---

## 1. TECHNOLOGY STACK

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend framework | FastAPI | 0.111+ |
| Python | CPython | 3.12 (Dockerfile) / 3.11+ (pyproject.toml) |
| Frontend framework | React + TypeScript | 18.3 / 5.5 |
| Build tool | Vite | 5.4 |
| CSS | Tailwind CSS | 3.4 |
| Routing (frontend) | react-router-dom | 6.23 |
| Data fetching (frontend) | @tanstack/react-query | 5.50 |
| HTTP client (frontend) | Axios | 1.7 |
| Database | PostgreSQL | 16 (Alpine) |
| Search engine | Meilisearch | v1.12 (dev) / v1.7 (prod) |
| Cache / Broker | Redis | 7 (Alpine) |
| Task queue | Celery + Redis broker | 5.4 |
| Scheduler | Celery Beat | built into Celery |
| ORM | SQLAlchemy (async) | 2.0+ with asyncpg |
| Migrations | Alembic | 1.13+ |
| HTTP client (backend) | httpx | 0.27+ |
| Auth | python-jose (JWT) + bcrypt + passlib | — |
| Config | pydantic-settings | 2.3+ |
| Logging | structlog | 24.1+ |
| Metrics | prometheus-client | 0.21+ |
| Telemetry | OpenTelemetry (SDK + FastAPI/HTTPX/SQLAlchemy instrumentation) | 1.25+ |
| HTML parsing | BeautifulSoup4 | 4.12+ |
| Spreadsheet parsing | openpyxl | 3.1+ |
| Search SDK (backend) | meilisearch-python-sdk | 3.0+ |
| Testing | pytest + pytest-asyncio + pytest-cov | 8.2+ |
| Test fixtures | factory-boy + in-memory repos | 3.3+ |
| Linting | ruff | 0.4+ |
| Type checking | mypy (strict mode) | 1.10+ |
| Pre-commit | ruff + prettier + standard hooks | — |
| Container runtime | Docker + Docker Compose | v3.8 syntax |
| Reverse proxy (prod) | nginx | Alpine |
| CI/CD | GitHub Actions | — |
| Container registry | GHCR (ghcr.io) | — |
| Deployment target | SSH to single server | — |

---

## 2. DOCKER ARCHITECTURE

### 2.1 Development (`docker-compose.yml`)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `api` | `infrastructure/docker/Dockerfile` (base stage) | `9000:8000` | FastAPI app (single worker, `--reload`) |
| `worker` | Same Dockerfile | none exposed | Celery worker, 4 concurrent processes |
| `beat` | Same Dockerfile | none exposed | Celery Beat scheduler |
| `postgres` | `postgres:16-alpine` | `5432:5432` | Primary database |
| `redis` | `redis:7-alpine` | `6379:6379` | Celery broker + cache |
| `meilisearch` | `getmeili/meilisearch:v1.12` | `7700:7700` | Full-text search engine |

**Health checks:** postgres (`pg_isready`), redis (`redis-cli ping`), meilisearch (`curl /health`).  
**Volumes:** `postgres_data`, `redis_data`, `meilisearch_data` (persistent named volumes).  
**Dependency chain:** api/worker/beat depend on postgres+redis+meilisearch (service_healthy).  
**No nginx in dev** — API exposed directly.

### 2.2 Production (`docker-compose.prod.yml`)

7 services: api, worker, beat, postgres, redis, meilisearch, **nginx**.

| Service | Resource Limits | Network |
|---------|----------------|---------|
| nginx | 0.5 CPU, 128MB | frontend (external-facing) |
| api | 2 CPU, 1GB | frontend + backend |
| worker | 2 CPU, 1GB | backend (internal only) |
| beat | 0.5 CPU, 256MB | backend |
| postgres | 2 CPU, 2GB | backend |
| redis | 1 CPU, 512MB | backend |
| meilisearch | 1 CPU, 1GB | backend |

**Network isolation:** `backend` network is `internal: true` — no internet access. Only nginx bridges to API.  
**Hardening:** No default fallback values for secrets. API health check on `/health/ready`. Worker `--max-tasks-per-child=1000`. Redis `maxmemory 512mb allkeys-lru`.

### 2.3 Dockerfile (`infrastructure/docker/Dockerfile`)

Multi-stage, 25 lines:
- **base:** python:3.12-slim, installs uv, `pip install -e ".[dev]"` (installs dev deps even in prod!)
- **production:** Extends base, creates non-root `credibil` user, runs uvicorn with `--workers 4`

**Issues:**
- Dev dependencies (pytest, ruff, mypy) are installed in the production image.
- No `.dockerignore` found — full context sent to Docker daemon (`.venv/`, `node_modules/`, `.git/`).

### 2.4 Nginx (`infrastructure/nginx/nginx.conf`)

- TLS 1.2+ with strong ciphers, HTTP→HTTPS redirect
- Rate limit: 30 req/s per IP, burst=20 nodelay
- Security headers: X-Frame-Options DENY, HSTS 2yr, X-Content-Type-Options nosniff
- Proxies to `api:8000`, `/health` exempt from rate limiting
- **Missing:** No gzip compression, no WebSocket support, no static asset caching, server_name only `credibil.md` (not `api.credibil.md`)

---

## 3. APPLICATION ARCHITECTURE

### 3.1 Layer Map

```
backend/src/credibil/
├── main.py                    # FastAPI app factory + lifespan
├── config.py                  # Pydantic Settings (CREDIBIL_ env prefix)
│
├── core/                      # Framework-agnostic utilities
│   ├── cache.py               # Redis cache + @cached decorator
│   ├── database.py            # AsyncEngine + session factory
│   ├── exceptions.py          # AppError hierarchy + FastAPI handler
│   ├── id.py                  # ULID-based UUID generator
│   ├── metrics.py             # Prometheus counters/histograms + middleware
│   ├── pagination.py          # PageParams, PaginatedResult
│   └── telemetry.py           # OpenTelemetry setup
│
├── ports/                     # Abstract interfaces (13 repository ABCs + 4 provider ABCs)
│   ├── auth/                  # PasswordHasher, TokenService
│   ├── providers/             # BaseProvider, SearchProvider, SanctionsProvider, StorageProvider
│   └── repositories/          # company, sync_history, relationship, accreditation, tender,
│                              # financial_report, court_case, user, organization, sanctions,
│                              # audit_log, apikey, subscription
│
├── domain/                    # Entities, value objects, errors, events
│   ├── company/               # Company, CompanyStatus, LegalForm, IDNO, CAEM
│   ├── sync/                  # SyncHistory, FieldProvenance
│   ├── relationship/          # Person, CompanyRelationship
│   ├── accreditation/         # Accreditation (7 categories, 4 statuses)
│   ├── tender/                # Tender, TenderAward, TenderBid, OCDS enums
│   ├── court/                 # CourtCase, CourtHearing
│   ├── financial/             # FinancialReport
│   ├── sanctions/             # SanctionsEntry, RiskAssessment
│   ├── search/                # SearchDocument, SearchQuery, MatchType
│   ├── audit/                 # AuditLogEntry
│   ├── user/                  # User, UserRole, UserStatus
│   ├── organization/          # Organization, OrganizationPlan
│   ├── apikey/                # APIKey
│   └── subscription/          # Subscription
│
├── application/               # Handlers, commands, queries, DTOs
│   ├── company/               # CompanyHandlers (CRUD)
│   ├── search/                # SearchHandlers + SearchService (Cyrillic, IDNO detect, multi-tier matching)
│   ├── analytics/             # DashboardService + court/tender/financial/growth/margin/liquidity analytics
│   ├── accreditation/         # AccreditationHandlers
│   ├── tender/                # TenderHandlers
│   ├── financial/             # FinancialHandlers
│   ├── court/                 # CourtHandlers
│   └── auth/                  # AuthHandlers (register, login, refresh, change_password)
│
├── infrastructure/            # Concrete implementations
│   ├── database/
│   │   ├── models_*.py        # 11 SQLAlchemy model files
│   │   └── repositories/      # 12 repository implementations
│   ├── search/
│   │   ├── meilisearch.py     # MeilisearchProvider
│   │   └── mappers.py         # CompanyMapper, PersonMapper
│   ├── auth/
│   │   ├── hasher.py          # BcryptPasswordHasher
│   │   └── tokens.py          # JWTTokenService
│   ├── storage/
│   │   └── local.py           # LocalStorageProvider (disk)
│   └── cache/                 # EMPTY — no implementation
│
├── api/                       # FastAPI routes + middleware
│   ├── health.py              # /health, /health/ready, /health/live
│   ├── middleware/             # RequestID, Timing, AuditLog, RateLimit, SecurityHeaders
│   ├── auth/                  # /register, /login, /refresh, /change-password
│   ├── admin/                 # 5 admin endpoints (all stubs returning empty data)
│   └── v1/                    # All v1 sub-routers
│       ├── companies/
│       ├── search/
│       ├── accreditations/
│       ├── tenders/
│       ├── court/
│       ├── financial/
│       ├── analytics/
│       └── relationship/
│
├── countries/moldova/         # Moldova-specific data providers
│   ├── normalizer.py          # Cyrillic/diacritics normalizer
│   ├── providers/
│   │   ├── ckan_provider.py
│   │   ├── depozitar_provider.py
│   │   ├── statistica_provider.py
│   │   ├── mtender_provider.py
│   │   ├── moldac_provider.py
│   │   └── justitie_provider.py
│   └── sync/
│       ├── orchestrator.py            # CKANSyncOrchestrator
│       ├── financial_orchestrator.py  # FinancialSyncOrchestrator
│       ├── tender_orchestrator.py     # TenderSyncOrchestrator
│       ├── court_orchestrator.py      # CourtSyncOrchestrator
│       └── moldac_orchestrator.py     # MoldacSyncOrchestrator
│
└── workers/
    ├── celery_app.py          # Celery config + 5 beat schedules
    └── tasks.py               # 11 Celery tasks
```

### 3.2 Data Flow

1. **External data** → Provider (httpx/BS4) → Domain entities
2. **Sync orchestrator** → Repository (SQLAlchemy) → PostgreSQL
3. **Search indexing** → MeilisearchProvider → Meilisearch
4. **API request** → Route → Application handler → Repository/Provider → Response
5. **Frontend** → Axios → FastAPI → handler → DB/Meilisearch → JSON → React Query → UI
6. **Celery task** → creates DB session → orchestrator → provider + repo → stores data

---

## 4. DATABASE

### 4.1 Alembic Status

**CRITICAL: The `alembic/versions/` directory is EMPTY.** No migrations have ever been generated. The SQLAlchemy models define 11+ tables but there is no migration history. To use the database, you must run `alembic revision --autogenerate` first.

### 4.2 Tables (from SQLAlchemy models)

| Table | Model File | PK | Key Fields | Source |
|-------|-----------|-----|------------|--------|
| `companies` | models_company.py | UUID `id` | idno (unique), name_ro, name_ru, registration_date, status, legal_form, legal_address, caem, caem_description, metadata (JSONB) | CKAN bulk import |
| `sync_histories` | models_sync.py | UUID `id` | entity_type, source, sync_type, status, records_total/created/updated/failed, started_at, completed_at | Internal tracking |
| `persons` | models_relationship.py | UUID `id` | full_name, idnp (unique), person_type, nationality, metadata | Extracted from relationships |
| `company_relationships` | models_relationship.py | UUID `id` | person_id (FK→persons), company_idno, relationship_type, is_current, metadata | CKAN + relationship extraction |
| `accreditations` | models_accreditation.py | UUID `id` | organization_name, director_name, certificate_number (unique), category, standard, status, issue_date, expiry_date | MOLDAC scraper |
| `tenders` | models_tender.py | UUID `id` | ocid (unique), title, status, buyer_idno, value_amount, value_currency, published_date | MTender OCDS API |
| `tender_awards` | models_tender.py | UUID `id` | tender_ocid, ocds_award_id, status, supplier_idno, value_amount | MTender OCDS API |
| `tender_bids` | models_tender.py | UUID `id` | tender_ocid, ocds_bid_id, status, tenderer_idno, value_amount | MTender OCDS API |
| `financial_reports` | models_financial.py | UUID `id` | company_idno, year, revenue, expenses, profit, total_assets, total_liabilities, equity, employees_count | Depozitar/Statistica |
| `court_cases` | models_court.py | UUID `id` | case_number, court_name, case_type, status, plaintiff_name, defendant_name, judge_name | instente.justice.md scraper |
| `court_hearings` | models_court.py | UUID `id` | case_number, hearing_date, hearing_time, court_name, room, judge_name | instente.justice.md scraper |
| `users` | models_user.py | UUID `id` | email (unique), full_name, hashed_password, role, status, tenant_id | Internal auth |
| `organizations` | models_organization.py | UUID `id` | name, slug, plan, status | Internal SaaS |
| `subscriptions` | models_organization.py | UUID `id` | organization_id (FK), plan, stripe_*.json, status | Internal SaaS |
| `api_keys` | models_organization.py | UUID `id` | organization_id (FK), key_prefix, key_hash, scopes | Internal SaaS |
| `sanctions_entries` | models_sanctions.py | UUID `id` | entity_name, entity_type, sanction_type, source_country, list_name, is_active | Not implemented |
| `risk_assessments` | models_sanctions.py | UUID `id` | company_idno, risk_level, risk_score, factors (JSONB) | Not implemented |
| `audit_logs` | models_audit.py | UUID `id` | user_id, action, entity_type, entity_id, old/new values, ip_address | Middleware capture |

**Key observations:**
- Most foreign keys are NOT enforced at DB level. `company_idno` on financial_reports, tenders, court_cases are plain strings, not FK constraints.
- Only `company_relationships.person_id` → `persons.id` has an actual ForeignKey.
- `companies.idno` has a unique constraint.
- No GIN indexes or full-text search indexes exist yet (no migrations).
- Row-Level Security (RLS) is described in ARCHITECTURE.md but not implemented in any model or migration.

### 4.3 Entity Relationships

```
Company (idno) ──1:N── FinancialReport (company_idno)
Company (idno) ──1:N── CourtCase (plaintiff_idno / defendant_idno)
Company (idno) ──1:N── Tender (buyer_idno)
Company (idno) ──1:N── CompanyRelationship (company_idno) ──N:1── Person (id)
Accreditation ── standalone (organization_name matches company name loosely)
```

**Missing relationships:**
- Sanctions are not linked to companies (no data).
- Risk assessments are not generated.
- Court cases reference companies by IDNO string only (no FK).

---

## 5. DATA INGESTION ARCHITECTURE

### 5.1 CKAN Provider (`ckan_provider.py`)

| Aspect | Detail |
|--------|--------|
| **Source** | dataset.gov.md (Moldova open data portal) |
| **URL** | https://dataset.gov.md |
| **API** | CKAN REST API (`/api/3/action/package_show`) |
| **Dataset ID** | `a1f38191-f35c-4180-8d80-297851a08f60` |
| **Data format** | XLSX bulk download |
| **Integration method** | HTTP API metadata + XLSX file download |
| **Celery task** | `sync_moldova_bulk` (daily at 02:00 UTC) |
| **Orchestrator** | `CKANSyncOrchestrator` (full + incremental) |
| **DB tables** | `companies`, `company_relationships`, `persons` |
| **CAPTCHA** | None on CKAN API |
| **Auth** | None required |
| **Dedup** | By IDNO (upsert) |
| **Status** | **Implemented and verified** — provider fetches metadata, gets download URL, orchestrator handles full/incremental sync |
| **Limitation** | Bulk XLSX may be large; requires parsing with openpyxl (not visible in provider but handled in orchestrator) |

### 5.2 Depozitar Provider (`depozitar_provider.py`)

| Aspect | Detail |
|--------|--------|
| **Source** | Depozitarul Public al Situațiilor Financiare |
| **URL** | https://depozitar-cabinet.statistica.md/api/public/v1 |
| **Integration method** | Public REST API (JSON) |
| **Steps** | 1) GET `/fs/economic-agent?idno={IDNO}` → list of FS UUIDs, 2) GET `/fs/{UUID}` → full statement |
| **Celery task** | `sync_financial_report` (on-demand), `sync_financial_all_years` (on-demand) |
| **Orchestrator** | `FinancialSyncOrchestrator` |
| **DB tables** | `financial_reports` |
| **CAPTCHA** | None (public endpoints) |
| **Auth** | None required |
| **Dedup** | By company_idno + year |
| **Caching** | Permanent: already-stored reports are never re-fetched |
| **Status** | **Implemented and verified** — full parsing of P&L and balance sheet from XBRL-based groups |
| **Known issue** | Launched Feb 2024, replaces old Statistica infoRSF. May not have data for older companies. |

### 5.3 Statistica Provider (`statistica_provider.py`) — FALLBACK

| Aspect | Detail |
|--------|--------|
| **Source** | statistica.md infoRSF |
| **URL** | https://webapp.statistica.md/infoRSF/ |
| **Integration method** | HTML scraping |
| **CAPTCHA** | **YES — max 20 queries/day** |
| **Status** | **Implemented but blocked by CAPTCHA** |
| **Fallback behavior** | Used as fallback when Depozitar fails. Will fail after 20 requests/day. |
| **Limitation** | **Hard rate limit with CAPTCHA.** Code does NOT bypass CAPTCHA. Will return errors when limit hit. |

### 5.4 MTender Provider (`mtender_provider.py`)

| Aspect | Detail |
|--------|--------|
| **Source** | MTender public procurement portal |
| **URL** | https://public.mtender.gov.md |
| **Integration method** | OCDS (Open Contracting Data Standard) REST API |
| **Endpoints** | GET `/tenders` (list with cursor pagination), GET `/tenders/{ocid}` (full record) |
| **Celery task** | `sync_tenders_recent` (daily at 04:00 UTC, limit=50) |
| **Orchestrator** | `TenderSyncOrchestrator` |
| **DB tables** | `tenders`, `tender_awards`, `tender_bids` |
| **CAPTCHA** | None |
| **Auth** | None required |
| **User-Agent** | "Mozilla/5.0 (compatible; CredibilBot/1.0)" |
| **Dedup** | By OCID (upsert) |
| **Status** | **Implemented and verified** — parses compiled releases, awards, bids |
| **Limitation** | Fetches one tender at a time (N+1 calls). Only recent 50 per daily sync. No historical backfill. |

### 5.5 MOLDAC Provider (`moldac_provider.py`)

| Aspect | Detail |
|--------|--------|
| **Source** | acreditare.md (Moldova National Accreditation Center) |
| **URL** | https://acreditare.md |
| **Integration method** | HTML scraping (BeautifulSoup4) |
| **Categories** | 7: Testing Labs, Calibration Labs, Medical Labs, Product Cert Bodies, Organic Cert Bodies, Management System Cert Bodies, Inspection Bodies |
| **Celery task** | `sync_moldova_accreditations` (daily at 05:00 UTC) |
| **Orchestrator** | `MoldacSyncOrchestrator` |
| **DB tables** | `accreditations` |
| **CAPTCHA** | None on acreditare.md |
| **Rate limiting** | 1 second delay between requests (`rate_limit_delay=1.0`) |
| **Auth** | None required |
| **Dedup** | By certificate_number (unique constraint) |
| **Status** | **Implemented and verified** — parses both div-based and table-based HTML layouts |
| **Limitation** | HTML structure may change, breaking the scraper. Date parsing is fragile (extracts dates from remarks text). |

### 5.6 Instante Provider (`justitie_provider.py`)

| Aspect | Detail |
|--------|--------|
| **Source** | instente.justice.md (Moldovan court information system) |
| **URL** | https://instante.justice.md |
| **Integration method** | HTML scraping (regex-based, no BeautifulSoup) |
| **Celery tasks** | `sync_court_cases` (on-demand), `sync_court_hearings` (daily at 03:00 UTC) |
| **Orchestrator** | `CourtSyncOrchestrator` |
| **DB tables** | `court_cases`, `court_hearings` |
| **CAPTCHA** | **Not explicitly handled** — portal is a Drupal 7 site. No CAPTCHA handling code exists. If CAPTCHA appears, the scraper will fail silently. |
| **Auth** | None required |
| **User-Agent** | "Mozilla/5.0 (compatible; CredibilBot/1.0)" |
| **Courts** | 17 court slugs defined (Supreme, 3 Appeal, 13 JUDECATORIE) |
| **Status** | **Implemented but fragile** — relies entirely on regex parsing of HTML. No BeautifulSoup. |
| **Limitation** | **Very fragile HTML parsing.** Regex patterns assume specific HTML structure that may change. No CAPTCHA handling. Drupal 7 site may have rate limiting. Only searches by IDNO, no comprehensive case ingestion. |

### 5.7 Sanctions Provider

| Aspect | Detail |
|--------|--------|
| **Status** | **NOT IMPLEMENTED** |
| **Code** | `SanctionsProvider` ABC exists in `ports/providers/sanctions.py`. No concrete implementation. |
| **Models** | `SanctionsEntryModel` and `RiskAssessmentModel` exist in DB but no data flows in. |
| **API** | Dashboard references sanctions data but returns empty. |

### 5.8 Storage Provider

| Aspect | Detail |
|--------|--------|
| **Status** | **Implemented (basic)** — `LocalStorageProvider` saves files to disk |
| **Location** | `infrastructure/storage/local.py` |
| **Used by** | CKAN orchestrator to store downloaded XLSX files |

---

## 6. SEARCH ARCHITECTURE

### 6.1 Search Service (`application/search/`)

- **IDNO detection:** Regex pattern matching 8-13 digit IDNOs
- **Cyrillic transliteration:** Latin→Cyrillic mapping for Moldovan names
- **Diacritics stripping:** Romanian diacritics (ă, â, î, ș, ț) → base letters
- **Multi-tier match classification:**
  1. `EXACT_IDNO` — exact numeric IDNO match
  2. `EXACT_NAME` — exact name match (after normalization)
  3. `NORMALIZED_NAME` — normalized name match (diacritics stripped, lowercased)
  4. `PREFIX` — name starts with query
  5. `TRANSLITERATION` — transliterated match
  6. `FUZZY` — Meilisearch typo tolerance

### 6.2 Meilisearch Integration (`infrastructure/search/meilisearch.py`)

- **Index:** `companies` and `persons`
- **Searchable fields:** idno, name_ro, name_ru, legal_form, caem, caem_description, director_names, founder_names
- **Typo tolerance:** Default Meilisearch settings (built-in)
- **Ranking:** Meilisearch default (words, typo, proximity, attribute, sort)
- **Reindexing:** `search_reindex_all` Celery task (daily at 01:00 UTC) — reads from PostgreSQL, batches of 500, adds to Meilisearch

### 6.3 Search Request Lifecycle

```
Frontend search input → useCompanySearch(query)
  → GET /api/v1/search/companies?q=<query>&limit=20
  → SearchRoute → SearchHandlers.handle_search()
    → SearchService.classify_query(query) → detects IDNO vs name
    → SearchService.search(query) → MeilisearchProvider.search()
      → Meilisearch SDK → Meilisearch server
    → Returns SearchResponse with match_type per hit
  → JSON response → frontend renders HitCard with match type badges
```

### 6.4 Search Health

- `GET /api/v1/search/health` endpoint exists
- Frontend has `useSearchHealth()` hook but it is **unused**

---

## 7. FRONTEND ARCHITECTURE

### 7.1 Routes

| Route | Component | Auth | Status |
|-------|-----------|------|--------|
| `/login` | LoginPage | No | **Functional** — email/password form, JWT storage |
| `/` | Redirect → `/dashboard` | Yes | — |
| `/dashboard` | DashboardPage | Yes | **Functional** — paginated company table |
| `/search` | SearchPage | Yes | **Functional** — full-text search with match type indicators |
| `/companies/:id` | CompanyDetailPage | Yes | **Functional** — 7 parallel API calls, 489 lines |
| `/persons/:id` | PersonDetailPage | Yes | **Functional** — person + connected companies |
| `/accreditations` | AccreditationsPage | Yes | **Functional** — keyword filter, table |

### 7.2 CompanyDetailPage Sections

1. Company header (14 fields)
2. Relationships (person cards with roles)
3. Risk indicators (from dashboard API)
4. Sanctions (from dashboard API)
5. Timeline events
6. Financial summary + table (with on-demand sync trigger)
7. Court cases table
8. Public procurement table
9. Accreditations table

### 7.3 Authentication Flow

- JWT stored in `localStorage` (access + refresh tokens)
- Axios interceptor attaches `Authorization: Bearer` header
- On 401: attempts token refresh via `POST /api/v1/auth/refresh`
- On refresh failure: clears localStorage, redirects to `/login`
- **Not httpOnly cookies** — vulnerable to XSS

### 7.4 Unused Hooks (defined but never called by any page)

- `useAutocomplete` — suggests autocomplete feature was planned
- `useCourtAnalytics` — deeper court analytics
- `useTenderAnalytics` — tender analytics dashboard
- `useSearchHealth` — search health monitoring

### 7.5 UI Components

All custom, hand-rolled with Tailwind. No UI library (no shadcn, MUI, Ant Design).
- `Spinner`, `LoadingState`, `ErrorState`, `EmptyState`, `Badge`
- `formatCurrency` (MDL), `formatDate`, `statusVariant`

---

## 8. AUTHENTICATION AND SAAS

### 8.1 What Exists

| Feature | Status | Notes |
|---------|--------|-------|
| User model | ✅ Implemented | Email, password, role, status, tenant_id |
| Registration | ✅ Implemented | `POST /api/v1/auth/register` |
| Login | ✅ Implemented | `POST /api/v1/auth/login` → JWT pair |
| Token refresh | ✅ Implemented | `POST /api/v1/auth/refresh` |
| Change password | ⚠️ **BUG** | `user_id=""` hardcoded — cannot identify current user |
| JWT (access 15min + refresh 7d) | ✅ Implemented | python-jose, HS256 |
| Role hierarchy | ✅ Defined | Owner > Admin > Editor > Viewer |
| Auth dependencies | ✅ Implemented | `get_current_user`, `require_admin`, `require_analyst_or_admin` |
| Organization model | ✅ Implemented | name, slug, plan, status |
| Subscription model | ✅ Implemented | Stripe fields (price_id, subscription_id, etc.) |
| API key model | ✅ Implemented | key_prefix, key_hash, scopes |
| Admin endpoints | ⚠️ **STUBS** | 5 endpoints return `{"items": [], "total": 0}` |
| Multi-tenancy (RLS) | ❌ **NOT IMPLEMENTED** | Described in ARCHITECTURE.md but no DB policies exist |
| Subscription enforcement | ❌ **NOT IMPLEMENTED** | No quota checks, no plan limits |
| Billing/Stripe integration | ❌ **NOT IMPLEMENTED** | Model fields exist but no Stripe SDK, no webhooks |
| Rate limiting per plan | ❌ **NOT IMPLEMENTED** | Global rate limit only |
| API key auth | ❌ **NOT IMPLEMENTED** | Model exists, no middleware to check keys |

### 8.2 Verdict

**Credibil is NOT a real multi-user SaaS.** It is a technical application shell with:
- Working login/logout/registration
- Working JWT auth
- Database models for SaaS features (organizations, subscriptions, API keys)
- **No actual tenant isolation, no billing, no plan enforcement, no admin panel**

---

## 9. HOW TO RUN THE APPLICATION

### 9.1 Prerequisites

- Python 3.12
- Node.js 18+
- Docker + Docker Compose
- `uv` (Python package manager)

### 9.2 Environment Variables

Copy `.env.example` to `.env`. Required values:
```
DB_PASSWORD=credibil
REDIS_PASSWORD=credibil
MEILISEARCH_MASTER_KEY=dev-master-key
JWT_SECRET=<any string>
```

### 9.3 Docker Startup

```bash
# Start all services (dev mode — databases + search + API in Docker)
docker-compose up -d

# OR hybrid mode (databases in Docker, API + frontend native)
make dev
```

### 9.4 Database Setup

```bash
# CRITICAL: No migrations exist yet. Must generate first:
cd backend
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 9.5 Initial Data Import

```bash
# Via Celery task (or trigger via API):
celery -A credibil.workers.celery_app call credibil.workers.tasks.sync_moldova_bulk --kwargs='{"sync_type": "full"}'
```

### 9.6 Search Indexing

```bash
celery -A credibil.workers.celery_app call credibil.workers.tasks.search_reindex_all
```

### 9.7 Starting Frontend

```bash
cd frontend
npm install
npm run dev    # Starts on http://localhost:3000
```

### 9.8 Starting API (native)

```bash
cd backend
make run       # uvicorn on http://localhost:8000
```

### 9.9 Endpoints

| URL | Purpose |
|-----|---------|
| `http://localhost:3000` | Frontend (Vite dev server) |
| `http://localhost:8000` | API (uvicorn) |
| `http://localhost:8000/docs` | Swagger UI (debug mode only) |
| `http://localhost:8000/redoc` | ReDoc (debug mode only) |
| `http://localhost:8000/health` | Health check |
| `http://localhost:8000/health/ready` | Readiness check |
| `http://localhost:8000/health/live` | Liveness check |
| `http://localhost:8000/metrics` | Prometheus metrics |
| `http://localhost:7700` | Meilisearch dashboard (dev) |

### 9.10 Running Tests

```bash
cd backend
make test           # pytest tests/ -v
make test-cov       # with coverage
make lint           # ruff check + format check
make typecheck      # mypy src/
```

---

## 10. CURRENT SYSTEM STATUS

| Component | Implemented | Has Real Data | Working | Data Source | Main Limitation |
|-----------|-------------|---------------|---------|-------------|-----------------|
| Company registry | ✅ Yes | ⚠️ After sync | ✅ Yes | CKAN XLSX (dataset.gov.md) | Must run `sync_moldova_bulk` first; no migrations exist |
| Persons | ✅ Yes | ⚠️ After sync | ✅ Yes | Extracted from company relationships | No standalone person ingestion |
| Company relationships | ✅ Yes | ⚠️ After sync | ✅ Yes | Extracted from CKAN data | Depends on bulk sync |
| Financial reports | ✅ Yes | ⚠️ On-demand | ✅ Yes | Depozitar Public API | Must trigger per-company; Statistica fallback blocked by CAPTCHA |
| Statistical classifiers | ✅ Yes | ⚠️ After sync | ✅ Yes | Embedded in CKAN data | CAEM codes from company records |
| Court cases | ✅ Yes | ⚠️ On-demand | ⚠️ Fragile | instente.justice.md HTML | Regex-based HTML parsing, no CAPTCHA handling |
| Court documents | ❌ No | ❌ No | ❌ No | — | Only case metadata, no document downloads |
| MOLDAC accreditations | ✅ Yes | ⚠️ After sync | ✅ Yes | acreditare.md HTML scraping | HTML structure changes break scraper |
| MTender procurement | ✅ Yes | ⚠️ After sync | ✅ Yes | mtender.gov.md OCDS API | Only 50 recent tenders per daily sync |
| Sanctions | ⚠️ Models only | ❌ No | ❌ No | — | Provider ABC exists, no implementation |
| Risk assessment | ⚠️ Models only | ❌ No | ❌ No | — | Model exists, no generation logic |
| Search (Meilisearch) | ✅ Yes | ⚠️ After reindex | ✅ Yes | PostgreSQL → Meilisearch | Must run `search_reindex_all` after data import |
| Frontend | ✅ Yes | N/A | ✅ Yes | Backend API | All pages functional, no mock data |
| Authentication | ✅ Yes | ⚠️ Users must register | ✅ Yes | Internal | change_password has bug; JWT in localStorage (XSS risk) |
| Multi-tenancy | ⚠️ Models only | ❌ No | ❌ No | — | RLS not implemented |
| Billing/Subscriptions | ⚠️ Models only | ❌ No | ❌ No | — | No Stripe integration |
| Admin panel | ⚠️ Stubs | ❌ No | ❌ No | — | 5 endpoints return empty arrays |
| Background sync | ✅ Yes | ✅ Scheduled | ✅ Yes | Celery Beat | 5 daily jobs configured |
| Audit logging | ✅ Middleware | ✅ Captures | ✅ Yes | Middleware | No UI to view logs |
| Metrics | ✅ Yes | ✅ /metrics | ✅ Yes | Prometheus | No dashboard (Grafana) |
| OpenTelemetry | ⚠️ Optional | ❌ No | ⚠️ If configured | OTel collector | Depends on external collector |
| Database migrations | ❌ **EMPTY** | ❌ No | ❌ **BLOCKED** | — | **No migration files exist** |
| Docker deployment | ✅ Yes | N/A | ✅ Yes | Docker Compose | Dev + prod configs present |
| CI/CD | ✅ Yes | N/A | ✅ Yes | GitHub Actions | No frontend CI |
| Backup/Restore | ✅ Scripts | N/A | ✅ Yes | pg_dump + optional S3 | No encryption, no automated scheduling |

---

## EXECUTIVE SUMMARY

Credibil is a **well-architected but early-stage** Moldovan business intelligence platform. The codebase demonstrates strong engineering practices: hexagonal architecture, clean separation of concerns, comprehensive type annotations, and a thoughtful data ingestion pipeline design.

**The core problem:** Despite having 155+ Python files, 6 external data provider integrations, and a complete frontend, **the database has no migrations** (`alembic/versions/` is empty). This means **nothing can run against a real database without first generating and applying migrations.** This is the single biggest blocker.

**Working end-to-end:** Once migrations are generated, the following flow works: CKAN bulk sync → PostgreSQL → Meilisearch reindex → Frontend search/detail views. Financial data, tenders, accreditations, and court cases all have working ingestion pipelines triggered on-demand or via daily Celery Beat schedules.

**Not working:** Sanctions (no provider), risk assessment (no logic), multi-tenancy (no RLS), billing (no Stripe), admin panel (stubs), court document downloads (not implemented). The Statistica fallback for financial data is blocked by CAPTCHA (max 20 queries/day). The court case scraper is fragile (regex-based HTML parsing). The `change_password` endpoint has a bug. JWT is stored in localStorage (XSS vulnerable). Dev dependencies are installed in the production Docker image.

---

## 10 MOST IMPORTANT ARCHITECTURAL PROBLEMS

1. **No database migrations** — `alembic/versions/` is empty. The entire application is blocked from running against PostgreSQL without first generating and applying migrations.

2. **Dev dependencies in production image** — Dockerfile installs `pip install -e ".[dev]"` in the base stage, which the production stage inherits. Test/lint tools are in the production image.

3. **No foreign key constraints** — Most cross-table references (`company_idno`, `buyer_idno`, `plaintiff_idno`) are plain strings with no FK enforcement. Data integrity depends entirely on application logic.

4. **JWT stored in localStorage** — Not httpOnly cookies. Vulnerable to XSS attacks. Every frontend JS file can read the token.

5. **Fragile HTML scraping** — Court case provider uses regex to parse Drupal 7 HTML. No BeautifulSoup. Will break on any site redesign. No CAPTCHA handling.

6. **Statistica CAPTCHA blocks fallback** — The financial data fallback provider hits a CAPTCHA wall (max 20 queries/day). Code silently fails when limit is reached.

7. **No `.dockerignore`** — Docker builds send the full repo context including `.venv/`, `node_modules/`, `.git/` to the Docker daemon. Slow builds, large context.

8. **Meilisearch version mismatch** — Dev uses v1.12, production uses v1.7. Behavioral differences between versions may cause search inconsistencies.

9. **Change password bug** — `ChangePasswordCommand` in `api/auth/routes.py:82` is created with `user_id=""` (empty string), making the endpoint non-functional.

10. **No nginx gzip, no WebSocket, wrong server_name** — Production nginx lacks compression, WebSocket support, and only handles `credibil.md` instead of `api.credibil.md`.

---

## 10 MOST IMPORTANT MISSING OR INCOMPLETE FEATURES

1. **Database migrations** — Zero migration files. Tables are defined in models but cannot be created.

2. **Sanctions data ingestion** — Provider ABC exists, models exist, dashboard references sanctions — but no provider implementation exists.

3. **Multi-tenancy / Row-Level Security** — ARCHITECTURE.md describes comprehensive RLS, but no policies exist in any migration or model.

4. **Billing / Stripe integration** — Subscription model has Stripe fields but no SDK, no webhooks, no payment flow.

5. **Admin panel** — 5 endpoints exist but all return `{"items": [], "total": 0}`. No admin UI.

6. **Court document downloads** — Only case metadata is scraped. No PDF/document fetching.

7. **Frontend autocomplete** — Hook `useAutocomplete` is defined but unused. No autocomplete UI.

8. **Frontend CI pipeline** — `.github/workflows/ci.yml` only handles Python. No frontend linting, testing, or type checking in CI.

9. **Risk assessment engine** — `RiskAssessment` model exists but no scoring logic, no factor computation.

10. **API key authentication** — `APIKey` model exists but no middleware to validate API keys on requests.

---

## FILE PATH

```
docs/CURRENT_ARCHITECTURE_AUDIT.md
```
