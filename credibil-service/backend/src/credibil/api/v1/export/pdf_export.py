"""PDF export generators for company and person entities.

Produces professional due-diligence-style PDF reports with:
- Multi-script Unicode support via bundled NotoSans TTF fonts
- All table cells use Paragraph objects for word-wrap
- Page decorations: header bar, footer with timestamp, watermark
- Locale-aware section headers (RO/RU)
"""

from __future__ import annotations

import io
import os
from datetime import date as _date
from datetime import datetime
from typing import Any

_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")

_FONT_DEFS: list[tuple[str, str, str]] = [
    ("CREDFont", "NotoSans-Regular.ttf", "NotoSans-Bold.ttf"),
]

_fonts_registered = False


def _init_fonts() -> bool:
    """Register bundled NotoSans fonts. Returns True if primary loaded."""
    global _fonts_registered  # noqa: PLW0603
    if _fonts_registered:
        return True
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    primary_ok = False
    for name, reg_file, bold_file in _FONT_DEFS:
        reg_path = os.path.join(_FONT_DIR, reg_file)
        bold_path = os.path.join(_FONT_DIR, bold_file)
        try:
            if os.path.exists(reg_path):
                pdfmetrics.registerFont(TTFont(name, reg_path))
                if name == "CREDFont":
                    primary_ok = True
            if os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont(name + "-Bold", bold_path))
        except Exception:
            continue
    _fonts_registered = True
    return primary_ok


def _safe(v: Any) -> str:
    return str(v) if v else ""


def _fmt_date(v: Any) -> str:
    if not v:
        return "—"
    if isinstance(v, (datetime, _date)):
        return v.isoformat()[:10]
    return str(v)[:10]


def _fmt_datetime(v: Any) -> str:
    if not v:
        return "—"
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M")
    if isinstance(v, _date):
        return v.isoformat()
    return str(v)[:16]


def _fmt_money(v: Any) -> str:
    if v is None:
        return "—"
    try:
        return f"{float(v):,.2f} MDL"
    except (ValueError, TypeError):
        return str(v)


def _section_header(title: str, styles: Any, font_reg: str, font_bold: str) -> list:
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import HRFlowable, Paragraph

    st_h2 = ParagraphStyle(
        "h2", parent=styles["Normal"],
        fontName=font_bold, fontSize=9,
        textColor=colors.HexColor("#1a56db"),
        spaceBefore=10, spaceAfter=4, leading=13,
    )
    border_color = colors.HexColor("#e2e8f0")
    return [
        Paragraph(title.upper(), st_h2),
        HRFlowable(width="100%", thickness=0.6, color=border_color, spaceAfter=4),
    ]


def _make_table(rows: list[list], col_widths: list[float], styles: Any,
                font_reg: str, font_bold: str, colors_mod: Any) -> Any:
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Table, TableStyle

    C_ACCENT = colors_mod.HexColor("#1a56db")
    C_BORDER = colors_mod.HexColor("#e2e8f0")
    C_LIGHT = colors_mod.HexColor("#f8fafc")

    st_cell = ParagraphStyle("cell", parent=styles["Normal"], fontName=font_reg, fontSize=8, leading=12)
    st_cell_hdr = ParagraphStyle("cell_h", parent=styles["Normal"], fontName=font_bold, fontSize=8,
                                 textColor=colors_mod.white, leading=12)

    wrapped = []
    for ri, row in enumerate(rows):
        new_row = []
        for cell in row:
            if isinstance(cell, Paragraph):
                new_row.append(cell)
            else:
                style = st_cell_hdr if ri == 0 else st_cell
                new_row.append(Paragraph(_safe(cell), style))
        wrapped.append(new_row)

    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), C_ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors_mod.white, C_LIGHT]),
    ]))
    return t


# ── Label translations ─────────────────────────────────────────────────────

_LABELS: dict[str, dict[str, str]] = {
    "ro": {
        "report_title": "RAPORT DE DUE DILIGENCE",
        "company_report": "RAPORT COMpanie",
        "person_report": "RAPORT PERSOANA",
        "generated_at": "Generat la",
        "section_overview": "Informații generale",
        "section_persons": "Persoane conectate",
        "section_risk": "Indicatori de risc",
        "section_court": "Cazuri judiciare",
        "section_tenders": "Licitații",
        "section_financial": "Rezumat financiar",
        "section_sanctions": "Sancțiuni",
        "section_companies": "Companii conectate",
        "label_name": "Denumire",
        "label_idno": "IDNO",
        "label_status": "Statut",
        "label_legal_form": "Formă juridică",
        "label_caem": "CAEM",
        "label_registration": "Data înregistrării",
        "label_address": "Adresa",
        "label_postal_code": "Cod poștal",
        "label_category": "Categorie",
        "label_tax_debt": "Datorie fiscală",
        "label_founders": "Fondatori",
        "label_directors": "Directori",
        "label_idnp": "IDNP",
        "label_type": "Tip",
        "label_nationality": "Naționalitate",
        "label_roles": "Roluri",
        "label_total_companies": "Total companii",
        "label_active": "Active",
        "label_liquidated": "Lichidate",
        "label_person_name": "Nume",
        "label_company_name": "Denumire companie",
        "label_company_status": "Statut companie",
        "label_relationship": "Relație",
        "label_financials": "Rezumat financiar",
        "label_revenue": "Venit",
        "label_profit": "Profit",
        "label_assets": "Active",
        "label_employees": "Angajați",
        "label_court_cases": "Cazuri",
        "label_case_number": "Număr dosar",
        "label_court_name": "Instanță",
        "label_case_type": "Tip caz",
        "label_tender_title": "Titlu licitație",
        "label_tender_value": "Valoare",
        "label_tender_status": "Statut",
        "label_win_rate": "Rata de câștig",
        "label_risk_category": "Categorie risc",
        "label_risk_level": "Nivel risc",
        "label_not_available": "Nu sunt date disponibile",
        "footer_report": "Raport generat de platforma Credibil",
        "footer_page": "Pagina",
    },
    "ru": {
        "report_title": "ОТЧЁТ О ДЬЮ-ДИЛИДЖЕНС",
        "company_report": "ОТЧЁТ ПО КОМПАНИИ",
        "person_report": "ОТЧЁТ ПО ЛИЦУ",
        "generated_at": "Дата формирования",
        "section_overview": "Общая информация",
        "section_persons": "Связанные лица",
        "section_risk": "Показатели риска",
        "section_court": "Судебные дела",
        "section_tenders": "Тендеры",
        "section_financial": "Финансовая сводка",
        "section_sanctions": "Санкции",
        "section_companies": "Связанные компании",
        "label_name": "Наименование",
        "label_idno": "ИДНО",
        "label_status": "Статус",
        "label_legal_form": "Юридическая форма",
        "label_caem": "КЭАМ",
        "label_registration": "Дата регистрации",
        "label_address": "Адрес",
        "label_postal_code": "Почтовый индекс",
        "label_category": "Категория",
        "label_tax_debt": "Налоговая задолженность",
        "label_founders": "Учредители",
        "label_directors": "Директора",
        "label_idnp": "ИНПН",
        "label_type": "Тип",
        "label_nationality": "Гражданство",
        "label_roles": "Роли",
        "label_total_companies": "Всего компаний",
        "label_active": "Активные",
        "label_liquidated": "Ликвидированные",
        "label_person_name": "ФИО",
        "label_company_name": "Название компании",
        "label_company_status": "Статус компании",
        "label_relationship": "Связь",
        "label_financials": "Финансовая сводка",
        "label_revenue": "Выручка",
        "label_profit": "Прибыль",
        "label_assets": "Активы",
        "label_employees": "Сотрудники",
        "label_court_cases": "Дела",
        "label_case_number": "Номер дела",
        "label_court_name": "Суд",
        "label_case_type": "Тип дела",
        "label_tender_title": "Название тендера",
        "label_tender_value": "Сумма",
        "label_tender_status": "Статус",
        "label_win_rate": "Процент побед",
        "label_risk_category": "Категория риска",
        "label_risk_level": "Уровень риска",
        "label_not_available": "Нет данных",
        "footer_report": "Отчёт сформирован платформой Credibil",
        "footer_page": "Страница",
    },
}


def _l(lang: str, key: str) -> str:
    """Get translated label."""
    labels = _LABELS.get(lang, _LABELS["ro"])
    return labels.get(key, key)


# ── Company PDF ─────────────────────────────────────────────────────────────

def build_company_pdf(company: dict, persons: list[dict], dashboard: dict | None,
                      lang: str = "ro") -> bytes:
    """Return a company due-diligence PDF report as raw bytes."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    _unicode = _init_fonts()
    F_REG = "CREDFont" if _unicode else "Helvetica"
    F_BOLD = "CREDFont-Bold" if _unicode else "Helvetica-Bold"

    buf = io.BytesIO()
    PAGE_W, PAGE_H = A4
    MARGIN = 18 * mm
    usable_w = PAGE_W - 2 * MARGIN

    C_DARK = colors.HexColor("#1e293b")
    C_MUTED = colors.HexColor("#64748b")
    C_BORDER = colors.HexColor("#e2e8f0")
    C_BANNER = colors.HexColor("#0f172a")
    C_OK = colors.HexColor("#16a34a")
    C_DANGER = colors.HexColor("#dc2626")

    styles = getSampleStyleSheet()

    def _ps(name, **kw):
        kw.setdefault("fontName", F_REG)
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    st_title = _ps("ttl", fontSize=18, textColor=colors.white, fontName=F_BOLD, leading=24)
    st_subtitle = _ps("sub", fontSize=9, textColor=colors.HexColor("#94a3b8"), leading=13)
    st_cell = _ps("cell", fontSize=8, textColor=C_DARK, leading=12)
    st_cell_hdr = _ps("cell_h", fontSize=8, textColor=colors.white, fontName=F_BOLD, leading=12)
    st_cell_lbl = _ps("cell_l", fontSize=8, textColor=C_MUTED, fontName=F_BOLD, leading=12)

    def _p(txt, style=None):
        return Paragraph(_safe(txt), style or st_cell)

    def _cell(txt, style=None):
        return Paragraph(_safe(txt), style or st_cell)

    def _lbl(txt):
        return _cell(txt, st_cell_lbl)

    def _section(title):
        return _section_header(title, styles, F_REG, F_BOLD)

    # ── Page decorations ────────────────────────────────────────────────
    def _on_page(canvas, doc):
        canvas.saveState()
        # Header bar
        canvas.setFillColor(C_BANNER)
        canvas.rect(0, PAGE_H - 14 * mm, PAGE_W, 14 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(F_BOLD, 8)
        canvas.drawString(MARGIN, PAGE_H - 10 * mm, "CREDIBIL — DUE DILIGENCE")
        # Watermark
        canvas.setFillColor(colors.HexColor("#e8edf5"))
        canvas.setFont(F_BOLD, 48)
        canvas.saveState()
        canvas.translate(PAGE_W / 2, PAGE_H / 2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "CREDIBIL")
        canvas.restoreState()
        # Footer
        canvas.setFillColor(C_MUTED)
        canvas.setFont(F_REG, 7)
        canvas.drawString(MARGIN, 10 * mm, _l(lang, "footer_report"))
        canvas.drawRightString(PAGE_W - MARGIN, 10 * mm,
                               f"{_l(lang, 'footer_page')} {canvas.getPageNumber()}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=22 * mm, bottomMargin=18 * mm,
    )

    story: list = []

    # ── Title banner ────────────────────────────────────────────────────
    company_name = company.get("name_ro") or company.get("name_ru") or "—"
    status_label = (company.get("status") or "—").upper()

    banner_data = [[
        Paragraph(company_name, st_title),
    ], [
        Paragraph(f"IDNO: {company.get('idno', '—')}  |  {status_label}", st_subtitle),
    ]]
    banner = Table(banner_data, colWidths=[usable_w])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_BANNER),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (-1, -1), (-1, -1), 10),
    ]))
    story.append(banner)
    story.append(Spacer(1, 8 * mm))

    # ── Overview ────────────────────────────────────────────────────────
    story.extend(_section(_l(lang, "section_overview")))

    kv_rows = [
        [_lbl(_l(lang, "label_name")), _cell(company.get("name_ro", "—"))],
        [_lbl(_l(lang, "label_idno")), _cell(company.get("idno", "—"))],
        [_lbl(_l(lang, "label_status")), _cell(status_label)],
        [_lbl(_l(lang, "label_legal_form")), _cell(company.get("legal_form", "—"))],
        [_lbl(_l(lang, "label_caem")), _cell(company.get("caem_description") or company.get("caem") or "—")],
        [_lbl(_l(lang, "label_registration")), _cell(_fmt_date(company.get("registration_date")))],
        [_lbl(_l(lang, "label_address")), _cell(company.get("legal_address") or "—")],
        [_lbl(_l(lang, "label_postal_code")), _cell(company.get("postal_code") or "—")],
        [_lbl(_l(lang, "label_category")), _cell(company.get("business_category") or "—")],
        [_lbl(_l(lang, "label_tax_debt")), _cell(_fmt_money(company.get("tax_debt")))],
    ]
    kv_table = Table(kv_rows, colWidths=[45 * mm, usable_w - 45 * mm])
    kv_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(kv_table)
    story.append(Spacer(1, 6 * mm))

    # ── Persons ─────────────────────────────────────────────────────────
    story.extend(_section(_l(lang, "section_persons")))
    if persons:
        p_rows = [[
            _cell(_l(lang, "label_person_name"), st_cell_hdr),
            _cell(_l(lang, "label_idnp"), st_cell_hdr),
            _cell(_l(lang, "label_roles"), st_cell_hdr),
        ]]
        for p in persons:
            p_rows.append([
                _cell(p.get("person_name", "—")),
                _cell(p.get("person_idnp") or "—"),
                _cell(", ".join(p.get("roles_in_current", [])) or "—"),
            ])
        story.append(_make_table(p_rows, [usable_w * 0.35, usable_w * 0.25, usable_w * 0.40],
                                 styles, F_REG, F_BOLD, colors))
    else:
        story.append(_p(_l(lang, "label_not_available")))
    story.append(Spacer(1, 6 * mm))

    # ── Dashboard sections (if available) ───────────────────────────────
    if dashboard:
        # Risk indicators
        risk_indicators = dashboard.get("risk_indicators") or []
        if risk_indicators:
            story.extend(_section(_l(lang, "section_risk")))
            r_rows = [[
                _cell(_l(lang, "label_risk_category"), st_cell_hdr),
                _cell(_l(lang, "label_risk_level"), st_cell_hdr),
            ]]
            for r in risk_indicators:
                r_rows.append([
                    _cell(r.get("category", "—")),
                    _cell((r.get("level") or "—").upper()),
                ])
            story.append(_make_table(r_rows, [usable_w * 0.5, usable_w * 0.5],
                                     styles, F_REG, F_BOLD, colors))
            story.append(Spacer(1, 6 * mm))

        # Court cases summary
        court_stats = dashboard.get("court_statistics") or {}
        if court_stats:
            story.extend(_section(_l(lang, "section_court")))
            kv = []
            total_cases = court_stats.get("total_cases")
            if total_cases is not None:
                kv.append([_lbl(_l(lang, "label_court_cases")), _cell(str(total_cases))])
            pending = court_stats.get("pending_cases")
            if pending is not None:
                kv.append([_lbl("Pending"), _cell(str(pending))])
            if kv:
                t = Table(kv, colWidths=[45 * mm, usable_w - 45 * mm])
                t.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(t)
            story.append(Spacer(1, 6 * mm))

        # Tender summary
        tender_stats = dashboard.get("tender_statistics") or {}
        if tender_stats:
            story.extend(_section(_l(lang, "section_tenders")))
            kv = []
            total_tenders = tender_stats.get("total_tenders")
            if total_tenders is not None:
                kv.append([_lbl("Total"), _cell(str(total_tenders))])
            total_value = tender_stats.get("total_value")
            if total_value is not None:
                kv.append([_lbl(_l(lang, "label_tender_value")), _cell(_fmt_money(total_value))])
            if kv:
                t = Table(kv, colWidths=[45 * mm, usable_w - 45 * mm])
                t.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(t)
            story.append(Spacer(1, 6 * mm))

        # Sanctions
        sanctions = dashboard.get("sanctions") or {}
        if sanctions:
            story.extend(_section(_l(lang, "section_sanctions")))
            is_sanctioned = sanctions.get("is_sanctioned", False)
            sanctions_count = sanctions.get("sanctions_count", 0)
            active = sanctions.get("active_sanctions", 0)
            kv = [
                [_lbl(_l(lang, "label_status")),
                 _cell("DA" if is_sanctioned else "NU",
                       ParagraphStyle("sc", parent=styles["Normal"],
                                      fontName=F_BOLD, textColor=C_DANGER if is_sanctioned else C_OK, fontSize=8))],
                [_lbl("Total"), _cell(str(sanctions_count))],
                [_lbl("Active"), _cell(str(active))],
            ]
            t = Table(kv, colWidths=[45 * mm, usable_w - 45 * mm])
            t.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t)

    # ── Build PDF ───────────────────────────────────────────────────────
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return buf.getvalue()


# ── Person PDF ──────────────────────────────────────────────────────────────

def build_person_pdf(person: dict, companies: list[dict], lang: str = "ro") -> bytes:
    """Return a person due-diligence PDF report as raw bytes."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    _unicode = _init_fonts()
    F_REG = "CREDFont" if _unicode else "Helvetica"
    F_BOLD = "CREDFont-Bold" if _unicode else "Helvetica-Bold"

    buf = io.BytesIO()
    PAGE_W, PAGE_H = A4
    MARGIN = 18 * mm
    usable_w = PAGE_W - 2 * MARGIN

    C_DARK = colors.HexColor("#1e293b")
    C_MUTED = colors.HexColor("#64748b")
    C_BORDER = colors.HexColor("#e2e8f0")
    C_BANNER = colors.HexColor("#0f172a")

    styles = getSampleStyleSheet()

    def _ps(name, **kw):
        kw.setdefault("fontName", F_REG)
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    st_title = _ps("ttl", fontSize=18, textColor=colors.white, fontName=F_BOLD, leading=24)
    st_subtitle = _ps("sub", fontSize=9, textColor=colors.HexColor("#94a3b8"), leading=13)
    st_cell = _ps("cell", fontSize=8, textColor=C_DARK, leading=12)
    st_cell_hdr = _ps("cell_h", fontSize=8, textColor=colors.white, fontName=F_BOLD, leading=12)
    st_cell_lbl = _ps("cell_l", fontSize=8, textColor=C_MUTED, fontName=F_BOLD, leading=12)

    def _p(txt, style=None):
        return Paragraph(_safe(txt), style or st_cell)

    def _cell(txt, style=None):
        return Paragraph(_safe(txt), style or st_cell)

    def _lbl(txt):
        return _cell(txt, st_cell_lbl)

    def _section(title):
        return _section_header(title, styles, F_REG, F_BOLD)

    def _on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_BANNER)
        canvas.rect(0, PAGE_H - 14 * mm, PAGE_W, 14 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(F_BOLD, 8)
        canvas.drawString(MARGIN, PAGE_H - 10 * mm, "CREDIBIL — DUE DILIGENCE")
        canvas.setFillColor(colors.HexColor("#e8edf5"))
        canvas.setFont(F_BOLD, 48)
        canvas.saveState()
        canvas.translate(PAGE_W / 2, PAGE_H / 2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "CREDIBIL")
        canvas.restoreState()
        canvas.setFillColor(C_MUTED)
        canvas.setFont(F_REG, 7)
        canvas.drawString(MARGIN, 10 * mm, _l(lang, "footer_report"))
        canvas.drawRightString(PAGE_W - MARGIN, 10 * mm,
                               f"{_l(lang, 'footer_page')} {canvas.getPageNumber()}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=22 * mm, bottomMargin=18 * mm,
    )

    story: list = []

    # ── Title banner ────────────────────────────────────────────────────
    full_name = person.get("full_name") or "—"
    idnp = person.get("idnp") or ""

    banner_data = [[
        Paragraph(full_name, st_title),
    ], [
        Paragraph(f"IDNP: {idnp}  |  {(person.get('person_type') or '—').upper()}", st_subtitle),
    ]]
    banner = Table(banner_data, colWidths=[usable_w])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_BANNER),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (-1, -1), (-1, -1), 10),
    ]))
    story.append(banner)
    story.append(Spacer(1, 8 * mm))

    # ── Overview ────────────────────────────────────────────────────────
    story.extend(_section(_l(lang, "section_overview")))

    kv_rows = [
        [_lbl(_l(lang, "label_name")), _cell(full_name)],
        [_lbl(_l(lang, "label_idnp")), _cell(idnp or "—")],
        [_lbl(_l(lang, "label_type")), _cell(person.get("person_type") or "—")],
        [_lbl(_l(lang, "label_nationality")), _cell(person.get("nationality") or "—")],
    ]
    kv_table = Table(kv_rows, colWidths=[45 * mm, usable_w - 45 * mm])
    kv_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(kv_table)
    story.append(Spacer(1, 6 * mm))

    # ── Connected companies ─────────────────────────────────────────────
    story.extend(_section(_l(lang, "section_companies")))
    if companies:
        c_rows = [[
            _cell(_l(lang, "label_company_name"), st_cell_hdr),
            _cell(_l(lang, "label_idno"), st_cell_hdr),
            _cell(_l(lang, "label_company_status"), st_cell_hdr),
            _cell(_l(lang, "label_roles"), st_cell_hdr),
        ]]
        for c in companies:
            c_rows.append([
                _cell(c.get("company_name") or "—"),
                _cell(c.get("company_idno") or "—"),
                _cell(c.get("company_status") or "—"),
                _cell(", ".join(c.get("roles", [])) or "—"),
            ])
        cw = [usable_w * 0.30, usable_w * 0.20, usable_w * 0.20, usable_w * 0.30]
        story.append(_make_table(c_rows, cw, styles, F_REG, F_BOLD, colors))
    else:
        story.append(_p(_l(lang, "label_not_available")))

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return buf.getvalue()
