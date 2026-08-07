from __future__ import annotations

from datetime import date

from credibil.countries.moldova.providers.unej_provider import UnejProvider
from credibil.domain.enforcement.entities import (
    EnforcementProceeding,
    EnforcementRole,
    EnforcementState,
)

SAMPLE_LIST_HTML = """
<html><body>
<div class="somation-card">
  <a href="/somations/1399">Somație debitor SRL "TRANS CARGO LOGISTIC"</a>
  <div class="addr">Mun. Chișinău, str. Ismail 84</div>
  <span>IDNO *******31705</span>
  <div>Creditor: BC "MAIB" S.A.</div>
  <span>Publicată: 09-12-2025</span>
</div>
<div class="somation-card">
  <a href="/somations/1398">Somație debitor Ceragem Individual</a>
  <span>IDNP *******44556</span>
  <span>Publicată: 05.12.2025</span>
</div>
<a href="/somations/1399">duplicate link should be ignored</a>
</body></html>
"""

SAMPLE_DETAIL_HTML = """
<html><body><article>
Somație debitor SRL "TRANS CARGO LOGISTIC", IDNO *******31705, cu domiciliul Chișinău.
Creditor MOLDASIG S.A., IDNO 1002600053315, email office@moldasig.md.
În baza documentului executoriu nr. 2-11109/25 din 09.12.2025 emis de
Judecătoria Chișinău, sediul Centru, dosarul nr. 2-1393/2025, suma de 4.460,50 lei.
Termen de plată voluntară 15 zile. Publicată: 09.12.2025.
</article></body></html>
"""


def _provider() -> UnejProvider:
    # Bypass __init__ so no httpx client / network is created for pure parsing.
    return UnejProvider.__new__(UnejProvider)


def test_parse_list_extracts_rows_and_dedupes() -> None:
    rows = _provider()._parse_list(SAMPLE_LIST_HTML)
    by_id = {r.somation_id: r for r in rows}

    assert set(by_id) == {1399, 1398}  # duplicate /somations/1399 collapsed

    first = by_id[1399]
    assert first.debtor_name == 'SRL "TRANS CARGO LOGISTIC"'
    assert first.debtor_idno_masked == "*******31705"
    assert first.publication_date == date(2025, 12, 9)
    assert first.source_url.endswith("/somations/1399")


def test_parse_detail_extracts_structured_fields() -> None:
    data = _provider()._parse_detail(SAMPLE_DETAIL_HTML, 1399)

    assert data["debtor_name"] == 'SRL "TRANS CARGO LOGISTIC"'
    assert data["debtor_idno_masked"] == "*******31705"
    assert data["creditor_idno"] == "1002600053315"  # creditor IDNO is unmasked
    assert data["executory_doc_number"] == "2-11109/25"
    assert data["case_number"] == "2-1393/2025"  # anchored to "dosarul nr."
    assert data["court_name"].startswith("Judecătoria Chișinău")
    assert data["amount"] == 4460.5
    assert data["currency"] == "MDL"


def test_role_derivation_and_masked_match() -> None:
    proceeding = EnforcementProceeding(
        somation_id=1,
        debtor_idno_masked="*******31705",
        creditor_idno="1002600053315",
        state=EnforcementState.ACTIVE,
    )

    assert proceeding.role_for_idno("1002600053315") is EnforcementRole.CREDITOR
    assert proceeding.role_for_idno("9999999999999") is None
    assert proceeding.matches_masked_idno("1013600031705") is True
    assert proceeding.matches_masked_idno("1013600099999") is False

    proceeding.debtor_idno = "1013600031705"
    assert proceeding.role_for_idno("1013600031705") is EnforcementRole.DEBTOR


def test_amount_parses_moldovan_formatting() -> None:
    from credibil.countries.moldova.providers.unej_provider import _parse_amount

    assert _parse_amount("4.460,50") == 4460.5
    assert _parse_amount("1 200") == 1200.0
    assert _parse_amount("nonsense") is None
