"""Export endpoints for company and person entities.

Returns PDF and XLSX due-diligence reports as downloadable files.
"""

from __future__ import annotations

import re
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/export", tags=["export"])


def _sanitize_filename(name: str) -> str:
    """Remove characters unsafe for filenames across OS."""
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", name)
    name = re.sub(r"_+", "_", name).strip("_. ")
    return name[:80] or "report"


def _content_disposition(filename: str, media_type: str) -> str:
    """RFC 5987 Content-Disposition header for Unicode-safe filenames."""
    safe = _sanitize_filename(filename)
    ascii_name = safe.encode("ascii", "replace").decode("ascii")
    encoded = quote(safe, safe="")
    return f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{encoded}'


async def _get_company_export_data(company_id: str) -> tuple[dict, list[dict], dict | None]:
    """Fetch aggregated company data for export."""
    from uuid import UUID

    from sqlalchemy import text

    from credibil.core.database import get_session_dependency

    async for session in get_session_dependency():
        # Resolve company (UUID or IDNO)
        if len(company_id) == 13 and company_id.isdigit():
            result = await session.execute(
                text("SELECT id, idno FROM companies WHERE idno = :idno"),
                {"idno": company_id},
            )
        else:
            try:
                uid = UUID(company_id)
            except ValueError as err:
                raise HTTPException(status_code=400, detail="Invalid company ID") from err
            result = await session.execute(
                text("SELECT id, idno FROM companies WHERE id = :id"),
                {"id": uid},
            )

        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")

        company_uuid, idno = row

        # Full company record
        result = await session.execute(
            text("SELECT * FROM companies WHERE idno = :idno"),
            {"idno": idno},
        )
        comp_row = result.mappings().fetchone()
        company = dict(comp_row) if comp_row else {}

        # Persons connected to this company
        result = await session.execute(
            text("""
                SELECT
                    p.full_name as person_name,
                    p.idnp as person_idnp,
                    array_agg(DISTINCT cr.relationship_type) as roles_in_current
                FROM company_relationships cr
                JOIN persons p ON cr.person_id = p.id
                WHERE cr.company_idno = :idno
                GROUP BY p.full_name, p.idnp
                ORDER BY p.full_name
            """),
            {"idno": idno},
        )
        persons = [dict(r) for r in result.mappings().fetchall()]

        # Dashboard data (best-effort, non-fatal if missing)
        dashboard = None
        try:
            from credibil.application.analytics.dashboard import DashboardService
            from credibil.infrastructure.database.repositories.company import (
                SQLAlchemyCompanyRepository,
            )
            from credibil.infrastructure.database.repositories.court_case import (
                SQLAlchemyCourtCaseRepository,
                SQLAlchemyCourtHearingRepository,
            )
            from credibil.infrastructure.database.repositories.financial_report import (
                SQLAlchemyFinancialReportRepository,
            )
            from credibil.infrastructure.database.repositories.relationship import (
                SQLAlchemyPersonRepository,
                SQLAlchemyRelationshipRepository,
            )
            from credibil.infrastructure.database.repositories.tender import (
                SQLAlchemyTenderAwardRepository,
                SQLAlchemyTenderBidRepository,
                SQLAlchemyTenderRepository,
            )

            svc = DashboardService(
                company_repo=SQLAlchemyCompanyRepository(session),
                financial_repo=SQLAlchemyFinancialReportRepository(session),
                court_case_repo=SQLAlchemyCourtCaseRepository(session),
                court_hearing_repo=SQLAlchemyCourtHearingRepository(session),
                tender_repo=SQLAlchemyTenderRepository(session),
                tender_award_repo=SQLAlchemyTenderAwardRepository(session),
                tender_bid_repo=SQLAlchemyTenderBidRepository(session),
                relationship_repo=SQLAlchemyRelationshipRepository(session),
                person_repo=SQLAlchemyPersonRepository(session),
                sanctions_repo=None,
            )
            dash = await svc.get_company_dashboard(idno)
            # Convert dataclass to dict for JSON-serialisable export
            dashboard = _dashboard_to_dict(dash)
        except Exception:
            pass  # Dashboard data is optional for export

        return company, persons, dashboard


def _dashboard_to_dict(dash) -> dict:
    """Best-effort conversion of CompanyDashboard dataclass to plain dict."""
    result = {}
    try:
        if dash.summary:
            s = dash.summary
            result["summary"] = {
                "idno": s.idno, "name_ro": s.name_ro, "name_ru": s.name_ru,
                "status": s.status, "legal_form": s.legal_form,
            }
    except Exception:
        pass

    try:
        if dash.risk_indicators:
            result["risk_indicators"] = [
                {"category": r.category, "level": r.level.value if hasattr(r.level, 'value') else str(r.level),
                 "score": r.score, "factors": r.factors}
                for r in dash.risk_indicators
            ]
    except Exception:
        pass

    try:
        if dash.court_statistics:
            result["court_statistics"] = dash.court_statistics
    except Exception:
        pass

    try:
        if dash.tender_statistics:
            result["tender_statistics"] = dash.tender_statistics
    except Exception:
        pass

    try:
        if dash.sanctions:
            san = dash.sanctions
            result["sanctions"] = {
                "is_sanctioned": san.is_sanctioned,
                "sanctions_count": san.sanctions_count,
                "active_sanctions": san.active_sanctions,
            }
    except Exception:
        pass

    try:
        if dash.financial:
            f = dash.financial
            result["financial"] = {
                "company_idno": f.company_idno,
                "years_analyzed": f.years_analyzed,
            }
    except Exception:
        pass

    return result


async def _get_person_export_data(person_id: str) -> tuple[dict, list[dict]]:
    """Fetch aggregated person data for export."""
    from uuid import UUID

    from sqlalchemy import text

    from credibil.core.database import get_session_dependency

    try:
        pid = UUID(person_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="Invalid person ID") from err

    async for session in get_session_dependency():
        result = await session.execute(
            text("SELECT * FROM persons WHERE id = :id"),
            {"id": pid},
        )
        person_row = result.mappings().fetchone()
        if not person_row:
            raise HTTPException(status_code=404, detail="Person not found")

        person = dict(person_row)

        result = await session.execute(
            text("""
                SELECT
                    cr.company_idno,
                    cr.relationship_type,
                    c.name_ro as company_name,
                    c.status as company_status
                FROM company_relationships cr
                LEFT JOIN companies c ON c.idno = cr.company_idno
                WHERE cr.person_id = :person_id
                ORDER BY c.name_ro, cr.relationship_type
            """),
            {"person_id": pid},
        )
        rel_rows = result.fetchall()

        # Group by company
        companies_map: dict[str, dict] = {}
        for cidno, rel_type, cname, cstatus in rel_rows:
            if cidno not in companies_map:
                companies_map[cidno] = {
                    "company_idno": cidno,
                    "company_name": cname,
                    "company_status": cstatus,
                    "roles": [],
                }
            companies_map[cidno]["roles"].append(rel_type)

        companies = sorted(companies_map.values(), key=lambda c: c.get("company_name") or "")
        return person, companies


# ── Company export endpoints ────────────────────────────────────────────────

@router.get("/company/{company_id}/pdf")
async def export_company_pdf(
    company_id: str,
    lang: str = Query(default="ro", pattern=r"^(ro|ru)$"),
) -> StreamingResponse:
    """Download a company due-diligence PDF report."""
    from credibil.api.v1.export.pdf_export import build_company_pdf

    company, persons, dashboard = await _get_company_export_data(company_id)
    pdf_bytes = build_company_pdf(company, persons, dashboard, lang=lang)

    company_name = company.get("name_ro") or company.get("name_ru") or company_id
    filename = f"credibil_{_sanitize_filename(company_name)}.pdf"

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": _content_disposition(filename, "application/pdf"),
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.get("/company/{company_id}/xlsx")
async def export_company_xlsx(
    company_id: str,
    lang: str = Query(default="ro", pattern=r"^(ro|ru)$"),
) -> StreamingResponse:
    """Download a company due-diligence XLSX workbook."""
    from credibil.api.v1.export.xlsx_export import build_company_xlsx

    company, persons, dashboard = await _get_company_export_data(company_id)
    xlsx_bytes = build_company_xlsx(company, persons, dashboard, lang=lang)

    company_name = company.get("name_ro") or company.get("name_ru") or company_id
    filename = f"credibil_{_sanitize_filename(company_name)}.xlsx"

    return StreamingResponse(
        iter([xlsx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": _content_disposition(
                filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            "Content-Length": str(len(xlsx_bytes)),
        },
    )


# ── Person export endpoints ─────────────────────────────────────────────────

@router.get("/person/{person_id}/pdf")
async def export_person_pdf(
    person_id: str,
    lang: str = Query(default="ro", pattern=r"^(ro|ru)$"),
) -> StreamingResponse:
    """Download a person due-diligence PDF report."""
    from credibil.api.v1.export.pdf_export import build_person_pdf

    person, companies = await _get_person_export_data(person_id)
    pdf_bytes = build_person_pdf(person, companies, lang=lang)

    full_name = person.get("full_name") or person_id
    filename = f"credibil_{_sanitize_filename(full_name)}.pdf"

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": _content_disposition(filename, "application/pdf"),
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.get("/person/{person_id}/xlsx")
async def export_person_xlsx(
    person_id: str,
    lang: str = Query(default="ro", pattern=r"^(ro|ru)$"),
) -> StreamingResponse:
    """Download a person due-diligence XLSX workbook."""
    from credibil.api.v1.export.xlsx_export import build_person_xlsx

    person, companies = await _get_person_export_data(person_id)
    xlsx_bytes = build_person_xlsx(person, companies, lang=lang)

    full_name = person.get("full_name") or person_id
    filename = f"credibil_{_sanitize_filename(full_name)}.xlsx"

    return StreamingResponse(
        iter([xlsx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": _content_disposition(
                filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            "Content-Length": str(len(xlsx_bytes)),
        },
    )
