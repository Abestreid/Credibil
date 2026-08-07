from __future__ import annotations

from credibil.countries.moldova.providers.moldac_provider import (
    CATEGORY_SLUGS,
    CATEGORY_STANDARDS,
    MOLDACProvider,
    _parse_contact_info,
    _parse_date,
)
from credibil.domain.accreditation.entities import AccreditationCategory, AccreditationStatus


class TestParseDate:
    def test_valid_date(self):
        assert _parse_date("15.01.2020") is not None
        assert _parse_date("15.01.2020").day == 15
        assert _parse_date("15.01.2020").month == 1
        assert _parse_date("15.01.2020").year == 2020

    def test_empty_date(self):
        assert _parse_date("") is None
        assert _parse_date("  ") is None
        assert _parse_date(None) is None

    def test_invalid_date(self):
        assert _parse_date("not-a-date") is None

    def test_short_year(self):
        result = _parse_date("15.01.20")
        assert result is not None


class TestParseContactInfo:
    def test_full_contact(self):
        html = (
            "Adresa juridica: str. Test 1, Chisinau<br>"
            "Tel.: +37322123456<br>"
            "Fax.: +37322123457<br>"
            "e-mail: test@test.md"
        )
        result = _parse_contact_info(html)
        assert result["address"] == "Adresa juridica: str. Test 1, Chisinau"
        assert result["phone"] == "+37322123456"
        assert result["fax"] == "+37322123457"
        assert result["email"] == "test@test.md"

    def test_partial_contact(self):
        html = "str. Test 1<br>Tel.: +37322123456"
        result = _parse_contact_info(html)
        assert "Test 1" in (result["address"] or "")
        assert result["phone"] == "+37322123456"
        assert result["fax"] is None
        assert result["email"] is None


class TestCategorySlugs:
    def test_all_slugs_mapped(self):
        assert len(CATEGORY_SLUGS) == 7
        assert "laboratoare-de-incercari" in CATEGORY_SLUGS
        assert "organisme-de-inspectie" in CATEGORY_SLUGS

    def test_all_standards_mapped(self):
        assert len(CATEGORY_STANDARDS) == 7
        assert "17025" in CATEGORY_STANDARDS[AccreditationCategory.TESTING_LAB]
        assert "15189" in CATEGORY_STANDARDS[AccreditationCategory.MEDICAL_LAB]


class TestMOLDACProvider:
    def test_init(self):
        provider = MOLDACProvider(rate_limit_delay=0.0)
        assert provider.rate_limit_delay == 0.0
        assert provider.BASE_URL == "https://acreditare.md"

    def test_cell_text_none(self):
        provider = MOLDACProvider()
        assert provider._cell_text(None) == ""

    def test_parse_category_page_empty(self):
        provider = MOLDACProvider()
        result = provider._parse_category_page(
            "<html><body></body></html>", AccreditationCategory.TESTING_LAB
        )
        assert result == []

    def test_parse_div_row_missing_cols(self):
        provider = MOLDACProvider()
        from bs4 import BeautifulSoup

        html = '<div class="detail__row"><div class="detail__col">1</div></div>'
        soup = BeautifulSoup(html, "html.parser")
        row = soup.find("div")
        result = provider._parse_div_row(row, AccreditationCategory.TESTING_LAB)
        assert result is None

    def test_parse_html_table_with_data(self):
        provider = MOLDACProvider()
        from bs4 import BeautifulSoup

        html = """
        <table>
            <tr>
                <th>Nr.</th>
                <th>Name</th>
                <th>Contact</th>
                <th>Certificate</th>
                <th>Annex</th>
                <th>Status</th>
                <th>Remarks</th>
            </tr>
            <tr>
                <td>1</td>
                <td>Test Lab SRL<br>Ion Popescu</td>
                <td>str. Test 1<br>Tel.: +37322123456</td>
                <td><a href="https://example.com/cert.pdf">LI - 004</a></td>
                <td><a href="https://example.com/annex1.pdf">Anexa 1</a></td>
                <td><span><i class="status status--1"></i>Activ</span></td>
                <td></td>
            </tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        results = provider._parse_html_table(table, AccreditationCategory.TESTING_LAB)
        assert len(results) == 1
        acc = results[0]
        assert acc.organization_name == "Test Lab SRL"
        assert acc.director_name == "Ion Popescu"
        assert acc.certificate_number == "LI - 004"
        assert acc.status == AccreditationStatus.ACTIVE
        assert acc.phone == "+37322123456"
        assert acc.certificate_url == "https://example.com/cert.pdf"

    def test_parse_div_table_with_data(self):
        provider = MOLDACProvider()

        html = """
        <div class="detail__table">
            <div class="detail__row head">
                <div class="detail__col">Nr.</div>
                <div class="detail__col">Name</div>
                <div class="detail__col">Contact</div>
                <div class="detail__col">Certificate</div>
                <div class="detail__col">Annex</div>
                <div class="detail__col">Status</div>
                <div class="detail__col">Remarks</div>
            </div>
            <div class="detail__row">
                <div class="detail__col">1</div>
                <div class="detail__col">Test Lab SRL<br>Ion Popescu</div>
                <div class="detail__col">str. Test 1<br>Tel.: +37322123456</div>
                <div class="detail__col"><a href="https://example.com/cert.pdf">LI - 004</a></div>
                <div class="detail__col"><a href="https://example.com/annex1.pdf">Anexa 1</a></div>
                <div class="detail__col"><span><i class="status status--1"></i>Activ</span></div>
                <div class="detail__col"></div>
            </div>
        </div>
        """
        results = provider._parse_category_page(html, AccreditationCategory.TESTING_LAB)
        assert len(results) == 1
        acc = results[0]
        assert acc.organization_name == "Test Lab SRL"
        assert acc.certificate_number == "LI - 004"
        assert acc.status == AccreditationStatus.ACTIVE

    def test_status_parsing_withdrawn(self):
        provider = MOLDACProvider()

        html = """
        <div class="detail__table">
            <div class="detail__row head">
                <div class="detail__col">Nr.</div>
                <div class="detail__col">Name</div>
                <div class="detail__col">Contact</div>
                <div class="detail__col">Certificate</div>
                <div class="detail__col">Annex</div>
                <div class="detail__col">Status</div>
                <div class="detail__col">Remarks</div>
            </div>
            <div class="detail__row">
                <div class="detail__col">1</div>
                <div class="detail__col">Test Lab</div>
                <div class="detail__col">str. Test</div>
                <div class="detail__col"><a href="#">LI-001</a></div>
                <div class="detail__col"></div>
                <div class="detail__col"><span><i class="status status--4"></i>Retras</span></div>
                <div class="detail__col">Retras din 28.07.2025</div>
            </div>
        </div>
        """
        results = provider._parse_category_page(html, AccreditationCategory.TESTING_LAB)
        assert len(results) == 1
        assert results[0].status == AccreditationStatus.WITHDRAWN
        assert results[0].remarks == "Retras din 28.07.2025"

    def test_multiple_annexes(self):
        provider = MOLDACProvider()
        from bs4 import BeautifulSoup

        html = """
        <table>
            <tr>
                <td>1</td>
                <td>Lab</td>
                <td>Address</td>
                <td><a href="cert.pdf">LI-001</a></td>
                <td>
                    <a href="annex1.pdf">Anexa 1: Scope</a>
                    <a href="annex2.pdf">Anexa 2: Equipment</a>
                </td>
                <td>Activ</td>
                <td></td>
            </tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        results = provider._parse_html_table(table, AccreditationCategory.TESTING_LAB)
        assert len(results) == 1
        assert len(results[0].annex_urls) == 2
        assert results[0].annex_urls[0]["name"] == "Anexa 1: Scope"
        assert results[0].annex_urls[1]["name"] == "Anexa 2: Equipment"
