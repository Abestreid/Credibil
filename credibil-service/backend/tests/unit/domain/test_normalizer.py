from __future__ import annotations

from datetime import date

from credibil.countries.moldova.normalizer import (
    normalize_caem,
    normalize_date,
    normalize_idno,
    normalize_legal_form,
    normalize_postal_code,
    normalize_status,
    parse_founders,
    raw_row_to_company,
)
from credibil.domain.company.entities import CompanyStatus, LegalForm


class TestNormalizeIdno:
    def test_valid_13_digits(self) -> None:
        assert normalize_idno("1234567890123") == "1234567890123"

    def test_strips_whitespace(self) -> None:
        assert normalize_idno(" 1234567890123 ") == "1234567890123"

    def test_truncates_long(self) -> None:
        assert normalize_idno("123456789012345") == "1234567890123"


class TestNormalizeDate:
    def test_none(self) -> None:
        assert normalize_date(None) is None

    def test_date_object(self) -> None:
        d = date(2020, 1, 15)
        assert normalize_date(d) == d

    def test_iso_string(self) -> None:
        assert normalize_date("2020-01-15") == date(2020, 1, 15)

    def test_dot_string(self) -> None:
        assert normalize_date("15.01.2020") == date(2020, 1, 15)

    def test_empty_string(self) -> None:
        assert normalize_date("") is None

    def test_none_string(self) -> None:
        assert normalize_date("None") is None


class TestNormalizeCaem:
    def test_valid_2_digit(self) -> None:
        assert normalize_caem("62") == "62"

    def test_valid_4_digit(self) -> None:
        assert normalize_caem("62.01") == "62.01"

    def test_empty(self) -> None:
        assert normalize_caem("") is None

    def test_invalid(self) -> None:
        assert normalize_caem("12345") is None


class TestNormalizePostalCode:
    def test_valid(self) -> None:
        assert normalize_postal_code("MD-2012") == "MD-2012"

    def test_invalid(self) -> None:
        assert normalize_postal_code("2012") is None


class TestNormalizeLegalForm:
    def test_srl(self) -> None:
        assert normalize_legal_form("1") == LegalForm.SRL

    def test_sa(self) -> None:
        assert normalize_legal_form("2") == LegalForm.SA

    def test_unknown(self) -> None:
        assert normalize_legal_form("99") == LegalForm.OTHER


class TestNormalizeStatus:
    def test_liquidated(self) -> None:
        assert normalize_status("1", "2023-01-01") == CompanyStatus.LIQUIDATED

    def test_active(self) -> None:
        assert normalize_status("1", None) == CompanyStatus.ACTIVE


class TestParseFounders:
    def test_empty(self) -> None:
        assert parse_founders("") == []

    def test_none_string(self) -> None:
        assert parse_founders("None") == []

    def test_with_idnp(self) -> None:
        result = parse_founders("Ion Popescu (1234567890123)")
        assert len(result) == 1
        assert result[0]["name"] == "Ion Popescu"
        assert result[0]["idnp"] == "1234567890123"

    def test_multiple(self) -> None:
        result = parse_founders("Ion Popescu (1234567890123), Maria (9876543210987)")
        assert len(result) == 2
        assert result[0]["name"] == "Ion Popescu"
        assert result[1]["name"] == "Maria"


class TestRawRowToCompany:
    def test_basic_conversion(self) -> None:
        raw = {
            "idno": "1234567890123",
            "registration_date": "2020-01-15",
            "full_name": "SRL Exemplu",
            "legal_form_code": "1",
            "address": "str. Test 1, Chișinău",
            "CUATM": "1000000",
            "directors": "Ion Director (1111111111111)",
            "founders": "Maria Founder (2222222222222)",
            "activities_licensed": "Software",
            "activities_unlicensed": "",
            "liquidation_date": None,
        }
        company = raw_row_to_company(raw)
        assert company.idno == "1234567890123"
        assert company.name_ro == "SRL Exemplu"
        assert company.legal_form == LegalForm.SRL
        assert company.status == CompanyStatus.ACTIVE
        assert company.founder_count == 1
        assert company.director_count == 1
        assert "provenance" in company.metadata
        assert "founders" in company.metadata
