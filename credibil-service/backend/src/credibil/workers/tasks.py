from __future__ import annotations

import logging

from credibil.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _reset_db_engine() -> None:
    """Reset the global async engine so the asyncpg pool binds to the current event loop.

    Celery's ForkPoolWorker forks child processes, inheriting the parent's event loop.
    When asyncio.run() creates a new loop, asyncpg connections from the old loop fail.
    """
    import asyncio

    import credibil.core.database as _db_mod

    # Dispose old engine to release its connection pool
    if _db_mod._engine is not None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(_db_mod._engine.dispose())
            else:
                loop.run_until_complete(_db_mod._engine.dispose())
        except Exception:
            pass
    _db_mod._engine = None
    _db_mod._session_factory = None


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def sync_company_data(self, company_id: str) -> dict:
    """Sync company data from external providers."""
    logger.info("Syncing company data for %s", company_id)
    try:
        return {"status": "success", "company_id": company_id}
    except Exception as exc:
        logger.error("Failed to sync company %s: %s", company_id, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def sync_all_companies(self) -> dict:
    """Sync all companies from external providers."""
    logger.info("Starting full company sync")
    try:
        return {"status": "success", "synced": 0}
    except Exception as exc:
        logger.error("Full sync failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2)
def generate_report(self, company_id: str, report_type: str) -> dict:
    """Generate a due diligence report for a company."""
    logger.info("Generating %s report for company %s", report_type, company_id)
    try:
        return {"status": "success", "company_id": company_id, "report_type": report_type}
    except Exception as exc:
        logger.error("Report generation failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def sync_moldova_bulk(self, sync_type: str = "incremental") -> dict:
    """Trigger CKAN bulk sync for Moldova company data.

    Args:
        sync_type: 'full' or 'incremental'. Incremental runs daily.
    """
    import asyncio

    from credibil.countries.moldova.sync.orchestrator import CKANSyncOrchestrator

    logger.info("Starting Moldova CKAN bulk sync (type=%s)", sync_type)

    async def _run() -> dict:
        from credibil.core.database import get_session
        from credibil.infrastructure.database.repositories.company import (
            SQLAlchemyCompanyRepository,
        )
        from credibil.infrastructure.database.repositories.sync_history import (
            SQLAlchemySyncHistoryRepository,
        )
        from credibil.infrastructure.storage.local import LocalStorageProvider

        _reset_db_engine()

        async with get_session() as session:
            company_repo = SQLAlchemyCompanyRepository(session)
            sync_repo = SQLAlchemySyncHistoryRepository(session)
            storage = LocalStorageProvider()

            orchestrator = CKANSyncOrchestrator(
                company_repo=company_repo,
                sync_repo=sync_repo,
                storage=storage,
                session=session,
            )

            if sync_type == "full":
                result = await orchestrator.sync_full()
            else:
                result = await orchestrator.sync_incremental()

            return {
                "status": "success",
                "sync_id": str(result.id),
                "records_total": result.records_total,
                "records_created": result.records_created,
                "records_updated": result.records_updated,
                "records_failed": result.records_failed,
            }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Moldova bulk sync failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def sync_financial_report(self, company_idno: str, year: int) -> dict:
    """Fetch and store financial report for one company+year from Depozitar (primary) or Statistica (fallback)."""
    import asyncio

    logger.info("Syncing financial report for %s/%d", company_idno, year)

    async def _run() -> dict:
        from credibil.core.database import get_session
        from credibil.countries.moldova.providers.depozitar_provider import DepozitarProvider
        from credibil.countries.moldova.providers.statistica_provider import StatisticaProvider
        from credibil.countries.moldova.sync.financial_orchestrator import FinancialSyncOrchestrator
        from credibil.infrastructure.database.repositories.financial_report import (
            SQLAlchemyFinancialReportRepository,
        )
        from credibil.infrastructure.database.repositories.sync_history import (
            SQLAlchemySyncHistoryRepository,
        )

        _reset_db_engine()

        async with get_session() as session:
            financial_repo = SQLAlchemyFinancialReportRepository(session)
            sync_repo = SQLAlchemySyncHistoryRepository(session)

            async with DepozitarProvider() as depozitar, StatisticaProvider() as statistica:
                orchestrator = FinancialSyncOrchestrator(
                    financial_repo=financial_repo,
                    sync_repo=sync_repo,
                    provider=depozitar,
                    fallback_provider=statistica,
                )

                report = await orchestrator.fetch_and_store(company_idno, year)

                return {
                    "status": "success",
                    "report_id": str(report.id),
                    "company_idno": company_idno,
                    "year": year,
                    "revenue": report.revenue,
                    "profit": report.profit,
                }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Financial sync failed for %s/%d: %s", company_idno, year, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def sync_financial_all_years(self, company_idno: str) -> dict:
    """Fetch all available financial statements for a company from the Depozitar.

    Uses the Depozitar's listing endpoint to discover all years, then fetches each.
    Permanent caching ensures already-stored reports are never re-fetched.
    """
    import asyncio

    logger.info("Syncing all financial years for %s", company_idno)

    async def _run() -> dict:
        from credibil.core.database import get_session
        from credibil.countries.moldova.providers.depozitar_provider import DepozitarProvider
        from credibil.countries.moldova.providers.statistica_provider import StatisticaProvider
        from credibil.countries.moldova.sync.financial_orchestrator import FinancialSyncOrchestrator
        from credibil.infrastructure.database.repositories.financial_report import (
            SQLAlchemyFinancialReportRepository,
        )
        from credibil.infrastructure.database.repositories.sync_history import (
            SQLAlchemySyncHistoryRepository,
        )

        _reset_db_engine()

        async with get_session() as session:
            financial_repo = SQLAlchemyFinancialReportRepository(session)
            sync_repo = SQLAlchemySyncHistoryRepository(session)

            async with DepozitarProvider() as depozitar, StatisticaProvider() as statistica:
                orchestrator = FinancialSyncOrchestrator(
                    financial_repo=financial_repo,
                    sync_repo=sync_repo,
                    provider=depozitar,
                    fallback_provider=statistica,
                )

                reports = await orchestrator.fetch_all_available(company_idno)

                return {
                    "status": "success",
                    "company_idno": company_idno,
                    "reports_fetched": len(reports),
                    "years": [r.year for r in reports],
                }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Financial all-years sync failed for %s: %s", company_idno, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=300)
def sync_financial_scan(self) -> dict:
    """Phase 1: Scan all companies via Depozitar listing endpoint.

    The listing endpoint (/fs/economic-agent?idno=X) is NOT rate-limited,
    so we can scan all 283K companies quickly. Results are stored in the
    financial_manifest table for Phase 2 to fetch.
    """
    import asyncio

    CONCURRENCY = 50

    logger.info("Starting financial manifest scan (concurrency=%d)", CONCURRENCY)

    async def _run() -> dict:
        from sqlalchemy import text

        from credibil.core.database import get_session_factory
        from credibil.countries.moldova.providers.depozitar_provider import DepozitarProvider

        _reset_db_engine()
        factory = get_session_factory()
        sem = asyncio.Semaphore(CONCURRENCY)

        # Create manifest table if not exists
        async with factory() as session:
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS financial_manifest (
                    id SERIAL PRIMARY KEY,
                    company_idno VARCHAR(13) NOT NULL,
                    year INTEGER NOT NULL,
                    fs_uuid VARCHAR(36) NOT NULL,
                    source VARCHAR(10),
                    fetched BOOLEAN DEFAULT FALSE,
                    scanned_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(company_idno, year)
                )
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_manifest_unfetched
                ON financial_manifest(company_idno)
                WHERE NOT fetched
            """))
            await session.commit()

        # Get all IDNOs
        async with factory() as session:
            result = await session.execute(
                text("SELECT idno FROM companies WHERE idno IS NOT NULL ORDER BY idno")
            )
            all_idnos = [row[0] for row in result.fetchall()]

        # Get already-scanned IDNOs
        async with factory() as session:
            result = await session.execute(
                text("SELECT DISTINCT company_idno FROM financial_manifest")
            )
            already_scanned = {row[0] for row in result.fetchall()}

        to_scan = [idno for idno in all_idnos if idno not in already_scanned]

        logger.info(
            "Manifest scan: %d total, %d already scanned, %d to scan",
            len(all_idnos),
            len(already_scanned),
            len(to_scan),
        )

        if not to_scan:
            return {"status": "success", "total": len(all_idnos), "scanned": 0, "has_data": 0, "no_data": 0}

        has_data = 0
        no_data = 0
        scanned = 0

        async def _scan_one(idno: str) -> list[dict]:
            """Scan one company's listing. Returns list of year/uuid entries."""
            async with sem:
                async with DepozitarProvider() as depozitar:
                    try:
                        entries = await depozitar.fetch_available_years(idno)
                        return entries if entries else []
                    except Exception as e:
                        logger.warning("Scan failed for %s: %s", idno, e)
                        return []

        # Process in batches
        for batch_start in range(0, len(to_scan), 1000):
            batch = to_scan[batch_start: batch_start + 1000]
            tasks = [_scan_one(idno) for idno in batch]
            results = await asyncio.gather(*tasks)

            # Insert results into manifest
            async with factory() as session:
                for idno, entries in zip(batch, results):
                    scanned += 1
                    if entries:
                        has_data += 1
                        for entry in entries:
                            year = entry.get("year")
                            fs_id = entry.get("id")
                            source = entry.get("source")
                            if year and fs_id:
                                await session.execute(
                                    text("""
                                        INSERT INTO financial_manifest (company_idno, year, fs_uuid, source)
                                        VALUES (:idno, :year, :uuid, :source)
                                        ON CONFLICT (company_idno, year) DO NOTHING
                                    """),
                                    {"idno": idno, "year": year, "uuid": fs_id, "source": source},
                                )
                    else:
                        no_data += 1

                await session.commit()

            logger.info(
                "Manifest scan: %d/%d done (%.1f%%), has_data=%d no_data=%d",
                scanned,
                len(to_scan),
                scanned / len(to_scan) * 100,
                has_data,
                no_data,
            )

        return {
            "status": "success",
            "total": len(all_idnos),
            "already_scanned": len(already_scanned),
            "scanned": scanned,
            "has_data": has_data,
            "no_data": no_data,
        }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Manifest scan failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=600, time_limit=None, soft_time_limit=None)
def sync_financial_fetch(self) -> dict:
    """Fetch financial details from manifest via X-Forwarded-For rotation.

    Each request gets a random XFF header, so the server sees a different IP per request.
    No proxies needed - the server trusts XFF headers.
    """
    import asyncio

    CONCURRENCY = 30

    logger.info("Starting financial detail fetch (XFF mode, concurrency=%d)", CONCURRENCY)

    async def _run() -> dict:
        import json

        from sqlalchemy import text

        from credibil.core.database import get_session_factory
        from credibil.countries.moldova.providers.depozitar_provider import DepozitarProvider

        _reset_db_engine()
        factory = get_session_factory()
        sem = asyncio.Semaphore(CONCURRENCY)

        async with factory() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM financial_manifest WHERE NOT fetched")
            )
            unfetched = result.scalar()

        logger.info("Financial fetch: %d entries to fetch", unfetched)

        if not unfetched:
            return {"status": "success", "fetched": 0, "failed": 0}

        fetched = 0
        failed = 0
        done = 0

        async def _fetch_one(entry: dict, provider: DepozitarProvider) -> tuple[str, bool]:
            async with sem:
                try:
                    raw = await provider.fetch_financial_statement(entry["uuid"])
                    if raw is None:
                        return ("error", False)
                    parsed = provider._parse_statement(raw, entry["idno"], entry["year"])
                    if parsed:
                        # Calculate business category based on employees and revenue
                        from credibil.countries.moldova.normalizer import classify_business_category
                        category = classify_business_category(
                            employees_count=parsed.get("employees_count"),
                            revenue=parsed.get("revenue"),
                            total_assets=parsed.get("total_assets"),
                        )
                        parsed["business_category"] = category

                        async with factory() as session:
                            await session.execute(
                                text("""
                                    INSERT INTO financial_reports (
                                        id, company_idno, year, period, company_name, caem_code,
                                        caem_description, business_category,
                                        revenue, expenses, profit, total_assets, total_liabilities, equity,
                                        cost_of_goods_sold, distribution_expenses, admin_expenses,
                                        other_operating_expenses, financial_income, financial_expenses, income_tax,
                                        current_assets, fixed_assets, inventories, trade_receivables,
                                        cash_and_banks, short_term_debt, long_term_debt, share_capital,
                                        operating_cash_flow, investing_cash_flow, financing_cash_flow,
                                        employees_count, source_url, raw_data, metadata, fetched_at
                                    ) VALUES (
                                        gen_random_uuid(), :company_idno, :year, 'annual', :company_name, :caem_code,
                                        :caem_description, :business_category,
                                        :revenue, :expenses, :profit, :total_assets, :total_liabilities, :equity,
                                        :cost_of_goods_sold, :distribution_expenses, :admin_expenses,
                                        :other_operating_expenses, :financial_income, :financial_expenses, :income_tax,
                                        :current_assets, :fixed_assets, :inventories, :trade_receivables,
                                        :cash_and_banks, :short_term_debt, :long_term_debt, :share_capital,
                                        :operating_cash_flow, :investing_cash_flow, :financing_cash_flow,
                                        :employees_count, :source_url, CAST(:raw_data AS jsonb), CAST(:metadata AS jsonb), NOW()
                                    )
                                    ON CONFLICT (company_idno, year) DO UPDATE SET
                                        company_name = EXCLUDED.company_name,
                                        caem_code = EXCLUDED.caem_code,
                                        caem_description = EXCLUDED.caem_description,
                                        business_category = EXCLUDED.business_category,
                                        revenue = EXCLUDED.revenue,
                                        expenses = EXCLUDED.expenses,
                                        profit = EXCLUDED.profit,
                                        total_assets = EXCLUDED.total_assets,
                                        total_liabilities = EXCLUDED.total_liabilities,
                                        equity = EXCLUDED.equity,
                                        cost_of_goods_sold = EXCLUDED.cost_of_goods_sold,
                                        distribution_expenses = EXCLUDED.distribution_expenses,
                                        admin_expenses = EXCLUDED.admin_expenses,
                                        other_operating_expenses = EXCLUDED.other_operating_expenses,
                                        financial_income = EXCLUDED.financial_income,
                                        financial_expenses = EXCLUDED.financial_expenses,
                                        income_tax = EXCLUDED.income_tax,
                                        current_assets = EXCLUDED.current_assets,
                                        fixed_assets = EXCLUDED.fixed_assets,
                                        inventories = EXCLUDED.inventories,
                                        trade_receivables = EXCLUDED.trade_receivables,
                                        cash_and_banks = EXCLUDED.cash_and_banks,
                                        short_term_debt = EXCLUDED.short_term_debt,
                                        long_term_debt = EXCLUDED.long_term_debt,
                                        share_capital = EXCLUDED.share_capital,
                                        operating_cash_flow = EXCLUDED.operating_cash_flow,
                                        investing_cash_flow = EXCLUDED.investing_cash_flow,
                                        financing_cash_flow = EXCLUDED.financing_cash_flow,
                                        employees_count = EXCLUDED.employees_count,
                                        source_url = EXCLUDED.source_url,
                                        raw_data = EXCLUDED.raw_data,
                                        metadata = EXCLUDED.metadata,
                                        fetched_at = NOW(),
                                        updated_at = NOW()
                                """),
                                {
                                    "company_idno": entry["idno"],
                                    "year": entry["year"],
                                    "company_name": parsed.get("company_name"),
                                    "caem_code": parsed.get("caem_code"),
                                    "caem_description": parsed.get("caem_description"),
                                    "business_category": parsed.get("business_category"),
                                    "revenue": parsed.get("revenue"),
                                    "expenses": parsed.get("expenses"),
                                    "profit": parsed.get("profit"),
                                    "total_assets": parsed.get("total_assets"),
                                    "total_liabilities": parsed.get("total_liabilities"),
                                    "equity": parsed.get("equity"),
                                    "cost_of_goods_sold": parsed.get("cost_of_goods_sold"),
                                    "distribution_expenses": parsed.get("distribution_expenses"),
                                    "admin_expenses": parsed.get("admin_expenses"),
                                    "other_operating_expenses": parsed.get("other_operating_expenses"),
                                    "financial_income": parsed.get("financial_income"),
                                    "financial_expenses": parsed.get("financial_expenses"),
                                    "income_tax": parsed.get("income_tax"),
                                    "current_assets": parsed.get("current_assets"),
                                    "fixed_assets": parsed.get("fixed_assets"),
                                    "inventories": parsed.get("inventories"),
                                    "trade_receivables": parsed.get("trade_receivables"),
                                    "cash_and_banks": parsed.get("cash_and_banks"),
                                    "short_term_debt": parsed.get("short_term_debt"),
                                    "long_term_debt": parsed.get("long_term_debt"),
                                    "share_capital": parsed.get("share_capital"),
                                    "operating_cash_flow": parsed.get("operating_cash_flow"),
                                    "investing_cash_flow": parsed.get("investing_cash_flow"),
                                    "financing_cash_flow": parsed.get("financing_cash_flow"),
                                    "employees_count": parsed.get("employees_count"),
                                    "source_url": parsed.get("source_url"),
                                    "raw_data": json.dumps(parsed.get("raw_data", {}), default=str),
                                    "metadata": json.dumps(parsed.get("metadata", {}), default=str),
                                },
                            )
                            await session.execute(
                                text("UPDATE financial_manifest SET fetched = TRUE WHERE id = :id"),
                                {"id": entry["id"]},
                            )
                            # Update company's business_category (use latest year's data)
                            if category:
                                await session.execute(
                                    text("""
                                        UPDATE companies 
                                        SET business_category = :category, updated_at = NOW()
                                        WHERE idno = :idno 
                                        AND (business_category IS NULL OR business_category = '' OR updated_at < NOW() - INTERVAL '1 day')
                                    """),
                                    {"idno": entry["idno"], "category": category},
                                )
                            await session.commit()
                        return ("stored", True)
                    else:
                        async with factory() as session:
                            await session.execute(
                                text("UPDATE financial_manifest SET fetched = TRUE WHERE id = :id"),
                                {"id": entry["id"]},
                            )
                            await session.commit()
                        return ("empty", True)
                except Exception as e:
                    logger.warning("Fetch failed for %s/%d: %s", entry["idno"], entry["year"], e)
                    return ("error", False)

        async with DepozitarProvider() as depozitar:
            while True:
                async with factory() as session:
                    result = await session.execute(
                        text("""
                            SELECT id, company_idno, year, fs_uuid
                            FROM financial_manifest
                            WHERE NOT fetched
                            ORDER BY RANDOM()
                            LIMIT :limit
                        """),
                        {"limit": CONCURRENCY * 3},
                    )
                    batch = [
                        {"id": row[0], "idno": row[1], "year": row[2], "uuid": row[3]}
                        for row in result.fetchall()
                    ]

                if not batch:
                    break

                tasks = [_fetch_one(entry, depozitar) for entry in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for r in results:
                    done += 1
                    if isinstance(r, Exception):
                        failed += 1
                    elif r[0] == "stored":
                        fetched += 1
                    elif r[0] == "error":
                        failed += 1

                if done % 100 == 0:
                    logger.info(
                        "Financial fetch: %d done, stored=%d failed=%d",
                        done, fetched, failed,
                    )

        return {
            "status": "success",
            "total_manifest": unfetched,
            "fetched": fetched,
            "failed": failed,
        }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Financial fetch failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def sync_court_cases(self, idno: str) -> dict:
    """Search and store court cases for a company IDNO from instente.justice.md."""
    import asyncio

    logger.info("Syncing court cases for IDNO %s", idno)

    async def _run() -> dict:
        from credibil.core.database import get_session
        from credibil.countries.moldova.providers.justitie_provider import InstanteProvider
        from credibil.countries.moldova.sync.court_orchestrator import CourtSyncOrchestrator
        from credibil.infrastructure.database.repositories.court_case import (
            SQLAlchemyCourtCaseRepository,
            SQLAlchemyCourtHearingRepository,
        )
        from credibil.infrastructure.database.repositories.sync_history import (
            SQLAlchemySyncHistoryRepository,
        )

        _reset_db_engine()

        async with get_session() as session:
            case_repo = SQLAlchemyCourtCaseRepository(session)
            hearing_repo = SQLAlchemyCourtHearingRepository(session)
            sync_repo = SQLAlchemySyncHistoryRepository(session)
            provider = InstanteProvider()

            orchestrator = CourtSyncOrchestrator(
                case_repo=case_repo,
                hearing_repo=hearing_repo,
                sync_repo=sync_repo,
                provider=provider,
            )

            cases = await orchestrator.search_by_idno(idno)

            return {
                "status": "success",
                "idno": idno,
                "cases_found": len(cases),
            }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Court case sync failed for %s: %s", idno, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def sync_court_hearings(self, court_slug: str | None = None) -> dict:
    """Sync hearing agenda entries from instente.justice.md."""
    import asyncio

    logger.info("Syncing court hearings (court=%s)", court_slug or "all")

    async def _run() -> dict:
        from credibil.core.database import get_session
        from credibil.countries.moldova.providers.justitie_provider import InstanteProvider
        from credibil.countries.moldova.sync.court_orchestrator import CourtSyncOrchestrator
        from credibil.infrastructure.database.repositories.court_case import (
            SQLAlchemyCourtCaseRepository,
            SQLAlchemyCourtHearingRepository,
        )
        from credibil.infrastructure.database.repositories.sync_history import (
            SQLAlchemySyncHistoryRepository,
        )

        _reset_db_engine()

        async with get_session() as session:
            case_repo = SQLAlchemyCourtCaseRepository(session)
            hearing_repo = SQLAlchemyCourtHearingRepository(session)
            sync_repo = SQLAlchemySyncHistoryRepository(session)
            provider = InstanteProvider()

            orchestrator = CourtSyncOrchestrator(
                case_repo=case_repo,
                hearing_repo=hearing_repo,
                sync_repo=sync_repo,
                provider=provider,
            )

            hearings = await orchestrator.sync_hearings(court_slug=court_slug)

            return {
                "status": "success",
                "court_slug": court_slug,
                "hearings_synced": len(hearings),
            }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Court hearings sync failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def sync_enforcement_by_idno(self, idno: str) -> dict:
    """Resolve enforcement proceedings for a company IDNO from unej.md."""
    import asyncio

    logger.info("Syncing enforcement proceedings for IDNO %s", idno)

    async def _run() -> dict:
        from credibil.core.database import get_session
        from credibil.countries.moldova.providers.unej_provider import UnejProvider
        from credibil.countries.moldova.sync.enforcement_orchestrator import (
            EnforcementSyncOrchestrator,
        )
        from credibil.infrastructure.database.repositories.enforcement import (
            SQLAlchemyEnforcementRepository,
        )
        from credibil.infrastructure.database.repositories.sync_history import (
            SQLAlchemySyncHistoryRepository,
        )

        _reset_db_engine()

        async with get_session() as session:
            provider = UnejProvider()
            try:
                orchestrator = EnforcementSyncOrchestrator(
                    enforcement_repo=SQLAlchemyEnforcementRepository(session),
                    sync_repo=SQLAlchemySyncHistoryRepository(session),
                    provider=provider,
                )
                proceedings = await orchestrator.search_by_idno(idno)
                return {
                    "status": "success",
                    "idno": idno,
                    "proceedings_found": len(proceedings),
                }
            finally:
                await provider.close()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Enforcement sync failed for %s: %s", idno, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=600)
def sync_enforcement_full(self, max_pages: int = 60) -> dict:
    """Daily full crawl of the unej.md Somații board.

    Upserts every entry and archives ones that have disappeared from the source.
    """
    import asyncio

    logger.info("Starting full enforcement crawl (max_pages=%d)", max_pages)

    async def _run() -> dict:
        from credibil.core.database import get_session
        from credibil.countries.moldova.providers.unej_provider import UnejProvider
        from credibil.countries.moldova.sync.enforcement_orchestrator import (
            EnforcementSyncOrchestrator,
        )
        from credibil.infrastructure.database.repositories.enforcement import (
            SQLAlchemyEnforcementRepository,
        )
        from credibil.infrastructure.database.repositories.sync_history import (
            SQLAlchemySyncHistoryRepository,
        )

        _reset_db_engine()

        async with get_session() as session:
            provider = UnejProvider()
            try:
                orchestrator = EnforcementSyncOrchestrator(
                    enforcement_repo=SQLAlchemyEnforcementRepository(session),
                    sync_repo=SQLAlchemySyncHistoryRepository(session),
                    provider=provider,
                )
                result = await orchestrator.full_sync(max_pages=max_pages)
                return {"status": "success", **result}
            finally:
                await provider.close()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Full enforcement crawl failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=300)
def run_monitoring_checks(self) -> dict:
    """Daily sweep: snapshot every monitored company, diff, and notify on change."""
    import asyncio
    from datetime import datetime

    async def _run() -> dict:
        from credibil.api.monitoring.dependencies import build_engine
        from credibil.core.database import get_session

        _reset_db_engine()

        batch_id = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        async with get_session() as session:
            engine = build_engine(session)
            result = await engine.run_checks(batch_id)
            return {"status": "success", "batch_id": batch_id, **result}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Monitoring checks failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def sync_tenders_recent(self, limit: int = 50) -> dict:
    """Sync recent tenders from mtender.gov.md OCDS API."""
    import asyncio

    logger.info("Syncing recent tenders (limit=%d)", limit)

    async def _run() -> dict:
        from credibil.core.database import get_session
        from credibil.countries.moldova.providers.mtender_provider import MTenderProvider
        from credibil.countries.moldova.sync.tender_orchestrator import TenderSyncOrchestrator
        from credibil.infrastructure.database.repositories.sync_history import (
            SQLAlchemySyncHistoryRepository,
        )
        from credibil.infrastructure.database.repositories.tender import (
            SQLAlchemyTenderAwardRepository,
            SQLAlchemyTenderBidRepository,
            SQLAlchemyTenderRepository,
        )

        _reset_db_engine()

        async with get_session() as session:
            tender_repo = SQLAlchemyTenderRepository(session)
            award_repo = SQLAlchemyTenderAwardRepository(session)
            bid_repo = SQLAlchemyTenderBidRepository(session)
            sync_repo = SQLAlchemySyncHistoryRepository(session)
            provider = MTenderProvider()

            orchestrator = TenderSyncOrchestrator(
                tender_repo=tender_repo,
                award_repo=award_repo,
                bid_repo=bid_repo,
                sync_repo=sync_repo,
                provider=provider,
            )

            result = await orchestrator.sync_recent(limit=limit)

            return {"status": "success", **result}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Tender sync failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def search_reindex_all(self) -> dict:
    """Reindex all search indexes from PostgreSQL.

    Uses the public SearchProvider.index_documents() API.
    Includes relationship data (directors, founders) for companies
    and connected company data for persons.
    """
    import asyncio

    logger.info("Starting full search reindex")

    async def _run() -> dict:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        from credibil.config import get_settings
        from credibil.domain.search.entities import SearchDocument, SearchIndex
        from credibil.infrastructure.search.meilisearch import MeilisearchProvider

        settings = get_settings()
        search_provider = MeilisearchProvider(
            url=settings.meilisearch_url,
            api_key=settings.meilisearch_api_key,
        )
        await search_provider._ensure_indexes()

        engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        session_factory = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

        async with session_factory() as session:
            # Reindex companies with relationship data
            result = await session.execute(text("SELECT COUNT(*) FROM companies"))
            total_companies = result.scalar()
            logger.info("search.reindex.companies total=%d", total_companies)

            offset = 0
            batch_size = 500
            companies_indexed = 0

            while offset < total_companies:
                rows = (
                    await session.execute(
                        text(
                            "SELECT c.idno, c.name_ro, c.name_ru, c.registration_date, "
                            "c.status, c.legal_form, c.legal_address, c.caem, c.caem_description, "
                            "COALESCE(d.directors, ARRAY[]::text[]) as directors, "
                            "COALESCE(f.founders, ARRAY[]::text[]) as founders "
                            "FROM companies c "
                            "LEFT JOIN LATERAL ("
                            "  SELECT array_agg(p.full_name) as directors "
                            "  FROM company_relationships cr "
                            "  JOIN persons p ON cr.person_id = p.id "
                            "  WHERE cr.company_idno = c.idno AND cr.relationship_type = 'director'"
                            ") d ON true "
                            "LEFT JOIN LATERAL ("
                            "  SELECT array_agg(p.full_name) as founders "
                            "  FROM company_relationships cr "
                            "  JOIN persons p ON cr.person_id = p.id "
                            "  WHERE cr.company_idno = c.idno AND cr.relationship_type = 'founder'"
                            ") f ON true "
                            "ORDER BY c.idno LIMIT :limit OFFSET :offset"
                        ),
                        {"limit": batch_size, "offset": offset},
                    )
                ).fetchall()

                if not rows:
                    break

                docs = [
                    SearchDocument(
                        id=row[0] or "",
                        index=SearchIndex.COMPANIES,
                        data={
                            "entity_type": "company",
                            "idno": row[0] or "",
                            "name_ro": row[1] or "",
                            "name_ru": row[2] or "",
                            "registration_date": str(row[3]) if row[3] else None,
                            "status": row[4] or "",
                            "legal_form": row[5] or "",
                            "legal_address": row[6] or "",
                            "caem": row[7] or "",
                            "caem_description": row[8] or "",
                            "director_names": row[9] or [],
                            "founder_names": row[10] or [],
                        },
                    )
                    for row in rows
                ]

                await search_provider.index_documents(SearchIndex.COMPANIES, docs)
                companies_indexed += len(docs)
                offset += batch_size

                if companies_indexed % 5000 == 0:
                    logger.info("search.reindex.companies.progress %d/%d", companies_indexed, total_companies)

            logger.info("search.reindex.companies.complete total=%d", companies_indexed)

            # Reindex persons with relationship data
            result = await session.execute(text("SELECT COUNT(*) FROM persons"))
            total_persons = result.scalar()
            logger.info("search.reindex.persons total=%d", total_persons)

            offset = 0
            persons_indexed = 0

            while offset < total_persons:
                rows = (
                    await session.execute(
                        text(
                            "SELECT p.id, p.full_name, p.idnp, p.person_type, p.nationality, "
                            "COALESCE(cn.company_names, ARRAY[]::text[]) as company_names, "
                            "COALESCE(ci.company_idnos, ARRAY[]::text[]) as company_idnos, "
                            "COALESCE(rt.relationship_types, ARRAY[]::text[]) as relationship_types "
                            "FROM persons p "
                            "LEFT JOIN LATERAL ("
                            "  SELECT array_agg(DISTINCT c.name_ro) as company_names "
                            "  FROM company_relationships cr "
                            "  JOIN companies c ON cr.company_idno = c.idno "
                            "  WHERE cr.person_id = p.id"
                            ") cn ON true "
                            "LEFT JOIN LATERAL ("
                            "  SELECT array_agg(DISTINCT cr.company_idno) as company_idnos "
                            "  FROM company_relationships cr "
                            "  WHERE cr.person_id = p.id"
                            ") ci ON true "
                            "LEFT JOIN LATERAL ("
                            "  SELECT array_agg(DISTINCT cr.relationship_type) as relationship_types "
                            "  FROM company_relationships cr "
                            "  WHERE cr.person_id = p.id"
                            ") rt ON true "
                            "ORDER BY p.id LIMIT :limit OFFSET :offset"
                        ),
                        {"limit": batch_size, "offset": offset},
                    )
                ).fetchall()

                if not rows:
                    break

                docs = [
                    SearchDocument(
                        id=str(row[0]),
                        index=SearchIndex.PERSONS,
                        data={
                            "entity_type": "person",
                            "full_name": row[1] or "",
                            "idnp": row[2] or "",
                            "person_type": row[3] or "",
                            "nationality": row[4] or "",
                            "company_names": row[5] or [],
                            "company_idnos": row[6] or [],
                            "relationship_types": row[7] or [],
                            "connected_companies_count": len(row[6] or []),
                        },
                    )
                    for row in rows
                ]

                await search_provider.index_documents(SearchIndex.PERSONS, docs)
                persons_indexed += len(docs)
                offset += batch_size

                if persons_indexed % 5000 == 0:
                    logger.info("search.reindex.persons.progress %d/%d", persons_indexed, total_persons)

            logger.info("search.reindex.persons.complete total=%d", persons_indexed)

        await engine.dispose()
        return {
            "status": "success",
            "companies_indexed": companies_indexed,
            "persons_indexed": persons_indexed,
            "total_indexed": companies_indexed + persons_indexed,
        }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Search reindex failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def sync_sanctions_all_companies(self) -> dict:
    """Check all companies against SDN sanctions lists.

    Uses batch search for efficiency. Stores results in the
    sanctions_entries table for fast lookups.
    Runs weekly (Sunday 07:00 UTC) to keep sanctions data fresh.
    """
    import asyncio

    logger.info("Starting sanctions check sweep for all companies")

    async def _run() -> dict:
        from sqlalchemy import text

        from credibil.config import get_settings
        from credibil.core.database import get_session
        from credibil.infrastructure.sanctions.sdn_provider import SDNProvider

        settings = get_settings()
        if not settings.sdn_api_key:
            logger.warning("SDN API key not configured, skipping sanctions sweep")
            return {"status": "skipped", "reason": "no_api_key"}

        _reset_db_engine()

        async with get_session() as session:
            result = await session.execute(
                text(
                    "SELECT idno, name_ro FROM companies WHERE name_ro IS NOT NULL AND name_ro != '' ORDER BY idno"
                )
            )
            companies = [(row[0], row[1]) for row in result.fetchall()]

            logger.info("Sanctions sweep: checking %d companies", len(companies))

            async with SDNProvider(
                api_key=settings.sdn_api_key, base_url=settings.sdn_api_url
            ) as sdn:
                sanctioned = 0
                checked = 0
                errors = 0

                # Process in batches of 50
                batch_size = 50
                for i in range(0, len(companies), batch_size):
                    batch = companies[i : i + batch_size]
                    names = [name for _, name in batch]

                    try:
                        entries = await sdn.batch_search(names, only_sanctioned=False)
                        sanctioned += len([e for e in entries if e.status.value == "active"])
                        checked += len(batch)
                    except Exception as e:
                        errors += len(batch)
                        logger.warning("Batch %d failed: %s", i // batch_size, e)

            return {
                "status": "success",
                "total": len(companies),
                "checked": checked,
                "sanctioned": sanctioned,
                "errors": errors,
            }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Sanctions sweep failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def sync_moldova_accreditations(self, category: str | None = None) -> dict:
    """Sync accreditation data from acreditare.md (MOLDAC)."""
    import asyncio

    logger.info("Syncing MOLDAC accreditations (category=%s)", category or "all")

    async def _run() -> dict:
        from credibil.core.database import get_session
        from credibil.countries.moldova.providers.moldac_provider import MOLDACProvider
        from credibil.countries.moldova.sync.moldac_orchestrator import MoldacSyncOrchestrator
        from credibil.infrastructure.database.repositories.accreditation import (
            SQLAlchemyAccreditationRepository,
        )
        from credibil.infrastructure.database.repositories.sync_history import (
            SQLAlchemySyncHistoryRepository,
        )

        _reset_db_engine()

        async with get_session() as session:
            accreditation_repo = SQLAlchemyAccreditationRepository(session)
            sync_repo = SQLAlchemySyncHistoryRepository(session)
            provider = MOLDACProvider()

            orchestrator = MoldacSyncOrchestrator(
                provider=provider,
                accreditation_repo=accreditation_repo,
                sync_repo=sync_repo,
            )

            if category:
                from credibil.domain.accreditation.entities import AccreditationCategory

                result = await orchestrator.sync_category(AccreditationCategory(category))
            else:
                result = await orchestrator.sync_all_categories()

            return {
                "status": "success",
                "sync_id": str(result.id),
                "records_created": result.records_created,
                "records_updated": result.records_updated,
                "records_unchanged": result.records_unchanged,
                "errors": result.errors,
            }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("MOLDAC sync failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def sync_tax_debt(self, company_idno: str) -> dict:
    """Fetch tax debt for a single company from SFS via FlareSolverr.

    This is an on-demand task triggered when a user clicks "Refresh" on a company page.
    Each request takes ~10-60s (FlareSolverr launches Selenium browser, bypasses Cloudflare,
    submits the tax debt form, and parses the response).
    Results are cached in the companies table with a fetched_at timestamp.
    """
    import asyncio

    async def _run() -> dict:
        _reset_db_engine()
        from sqlalchemy import text

        from credibil.core.database import get_session_factory
        from credibil.countries.moldova.providers.sfs_provider import SFSProvider

        provider = SFSProvider()

        logger.info("Fetching tax debt for IDNO %s", company_idno)
        result = await provider.fetch_tax_debt(company_idno)
        await provider.close()

        if result.error:
            logger.warning("SFS error for %s: %s", company_idno, result.error)
            return {"status": "error", "error": result.error, "idno": company_idno}

        # Update the company record with tax debt and fetched_at timestamp
        session_factory = get_session_factory()
        async with session_factory() as session:
            await session.execute(
                text(
                    "UPDATE companies "
                    "SET tax_debt = :amount, tax_debt_fetched_at = NOW(), updated_at = NOW() "
                    "WHERE idno = :idno"
                ),
                {"amount": result.total_amount, "idno": company_idno},
            )
            await session.commit()

        logger.info(
            "Tax debt for %s: has_debt=%s, amount=%s",
            company_idno,
            result.has_debt,
            result.total_amount,
        )
        return {
            "status": "success",
            "idno": company_idno,
            "has_debt": result.has_debt,
            "total_amount": result.total_amount,
        }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Tax debt fetch failed for %s: %s", company_idno, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, soft_time_limit=86400, time_limit=86400)
def sync_tax_debt_all(self) -> dict:
    """Bulk fetch tax debt from SFS reusing a single FlareSolverr session.

    Reuses one browser session across all requests to save the overhead of
    launching Chrome + solving Cloudflare for each IDNO individually.
    On failure a new session is created and the request is retried once.
    """
    import asyncio

    async def _run() -> dict:
        _reset_db_engine()
        from sqlalchemy import text

        from credibil.core.database import get_session_factory
        from credibil.countries.moldova.providers.sfs_provider import SFSProvider

        session_factory = get_session_factory()
        provider = SFSProvider()

        # Fetch IDs (only those never fetched)
        async with session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT idno FROM companies "
                    "WHERE tax_debt_fetched_at IS NULL "
                    "AND idno ~ '^\\d{13}$' "
                    "ORDER BY idno"
                )
            )
            idnos = [row[0] for row in result.fetchall()]

        if not idnos:
            logger.info("No companies left to fetch")
            return {"status": "success", "total": 0, "fetched": 0, "errors": 0}

        logger.info("Starting bulk tax debt fetch for %d companies", len(idnos))

        # Create a reusable FlareSolverr session
        session_id = await provider._create_session()
        logger.debug("Created shared FlareSolverr session %s", session_id)

        fetched = 0
        errors = 0
        i = 0

        try:
            while i < len(idnos):
                idno = idnos[i]

                try:
                    debt_result = await provider._fetch_one(idno, session_id)

                    if debt_result.error:
                        # Session might have expired — create a new one and retry
                        logger.warning(
                            "FlareSolverr error for %s (%s), creating new session",
                            idno, debt_result.error,
                        )
                        try:
                            await provider._destroy_session(session_id)
                        except Exception:
                            pass
                        session_id = await provider._create_session()
                        continue  # retry same IDNO with fresh session

                    # Success — write to DB
                    async with session_factory() as session:
                        await session.execute(
                            text(
                                "UPDATE companies "
                                "SET tax_debt = :amount, tax_debt_fetched_at = NOW(), "
                                "updated_at = NOW() "
                                "WHERE idno = :idno"
                            ),
                            {"amount": debt_result.total_amount, "idno": idno},
                        )
                        await session.commit()

                    fetched += 1
                    i += 1

                    if fetched % 10 == 0:
                        elapsed = (fetched / (max(1, (i - fetched + errors))))
                        logger.info(
                            "Tax debt progress: %d/%d fetched, %d errors "
                            "(~%d req/hr)",
                            fetched, len(idnos), errors,
                            int(3600 / (elapsed if elapsed else 10)),
                        )

                except Exception as e:
                    logger.error("Failed to fetch tax debt for %s: %s", idno, e)
                    errors += 1
                    i += 1
                    continue

        finally:
            try:
                await provider._destroy_session(session_id)
            except Exception:
                pass
            await provider.close()

        logger.info("Bulk tax debt fetch complete: %d fetched, %d errors", fetched, errors)
        return {
            "status": "success",
            "total": len(idnos),
            "fetched": fetched,
            "errors": errors,
        }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Bulk tax debt fetch failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def sync_tax_debt_from_date_gov(self, company_idno: str) -> dict:
    """Fetch tax debt for a single company from date.gov.md via FlareSolverr.

    This is an alternative to the SFS provider that uses date.gov.md
    which provides "Restanțe față de bugetul de stat" data.
    """
    import asyncio

    async def _run() -> dict:
        _reset_db_engine()
        from sqlalchemy import text

        from credibil.core.database import get_session_factory
        from credibil.countries.moldova.providers.date_gov_provider import DateGovProvider

        provider = DateGovProvider()

        logger.info("Fetching tax debt from date.gov.md for IDNO %s", company_idno)
        result = await provider.fetch_company_debt(company_idno)
        await provider.close()

        if result.error:
            logger.warning("date.gov.md error for %s: %s", company_idno, result.error)
            return {"status": "error", "error": result.error, "idno": company_idno}

        # Update the company record with tax debt and fetched_at timestamp
        session_factory = get_session_factory()
        async with session_factory() as session:
            await session.execute(
                text(
                    "UPDATE companies "
                    "SET tax_debt = :amount, tax_debt_fetched_at = NOW(), updated_at = NOW() "
                    "WHERE idno = :idno"
                ),
                {"amount": result.total_amount, "idno": company_idno},
            )
            await session.commit()

        logger.info(
            "Tax debt from date.gov.md for %s: has_debt=%s, amount=%s",
            company_idno,
            result.has_debt,
            result.total_amount,
        )
        return {
            "status": "success",
            "idno": company_idno,
            "has_debt": result.has_debt,
            "total_amount": result.total_amount,
        }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("Tax debt fetch from date.gov.md failed for %s: %s", company_idno, exc)
        raise self.retry(exc=exc)
