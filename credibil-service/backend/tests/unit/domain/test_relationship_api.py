"""Tests for the relationship API endpoints and extraction script."""
from __future__ import annotations

import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scripts.extract_persons import (
    _clean_name,
    _is_person_name,
    _normalize_name,
)


class TestCleanName:
    def test_strips_ownership_percentage(self) -> None:
        assert _clean_name("BRÎNZIUC ALEXANDRU (100") == "BRÎNZIUC ALEXANDRU"

    def test_strips_role_suffix(self) -> None:
        assert _clean_name("BRÎNZIUC ALEXANDRU [Administrator]") == "BRÎNZIUC ALEXANDRU"

    def test_strips_role_suffix_with_percentage(self) -> None:
        assert _clean_name("ION POPESCU (50 [Administrator]") == "ION POPESCU"

    def test_rejects_percentage_fragment(self) -> None:
        assert _clean_name("00%)") is None
        assert _clean_name("100%)") is None
        assert _clean_name("50%)") is None

    def test_rejects_empty_or_short(self) -> None:
        assert _clean_name("") is None
        assert _clean_name("AB") is None

    def test_collapses_whitespace(self) -> None:
        assert _clean_name("  ION   POPESCU  ") == "ION POPESCU"

    def test_preserves_valid_name(self) -> None:
        assert _clean_name("Brînziuc Alexandru") == "Brînziuc Alexandru"


class TestIsPersonName:
    def test_valid_two_word_name(self) -> None:
        assert _is_person_name("ION POPESCU") is True

    def test_valid_three_word_name(self) -> None:
        assert _is_person_name("ION POPESCU MARIN") is True

    def test_rejects_single_word(self) -> None:
        assert _is_person_name("ION") is False

    def test_rejects_company_srl(self) -> None:
        assert _is_person_name("S.R.L. EXEMPLU") is False

    def test_rejects_company_sa(self) -> None:
        assert _is_person_name("S.A. EXEMPLU") is False

    def test_rejects_societatea(self) -> None:
        assert _is_person_name("Societatea Comercială X") is False

    def test_rejects_empty(self) -> None:
        assert _is_person_name("") is False

    def test_rejects_numbers(self) -> None:
        assert _is_person_name("123 456") is False


class TestNormalizeName:
    def test_lowercase(self) -> None:
        assert _normalize_name("ION POPESCU") == "ion popescu"

    def test_strips_diacritics(self) -> None:
        result = _normalize_name("Brînziuc Alexandru")
        assert "î" not in result
        assert "brinziuc" in result

    def test_collapses_whitespace(self) -> None:
        assert _normalize_name("  ION   POPESCU  ") == "ion popescu"

    def test_same_name_normalizes_same(self) -> None:
        n1 = _normalize_name("BRÎNZIUC ALEXANDRU")
        n2 = _normalize_name("Brînziuc Alexandru")
        assert n1 == n2


class TestRelationshipDataModel:
    """Tests that the relationship data model correctly represents Person -> Role -> Company."""

    def test_person_with_multiple_companies(self) -> None:
        from credibil.domain.relationship.entities import CompanyRelationship, Person, RelationshipType

        person = Person(full_name="Test Person")
        rel1 = CompanyRelationship(
            person_id=person.id,
            company_idno="1111111111111",
            relationship_type=RelationshipType.FOUNDER,
        )
        rel2 = CompanyRelationship(
            person_id=person.id,
            company_idno="2222222222222",
            relationship_type=RelationshipType.DIRECTOR,
        )

        assert rel1.person_id == rel2.person_id
        assert rel1.company_idno != rel2.company_idno
        assert rel1.relationship_type != rel2.relationship_type

    def test_person_with_multiple_roles_in_same_company(self) -> None:
        from credibil.domain.relationship.entities import CompanyRelationship, Person, RelationshipType

        person = Person(full_name="Test Person")
        rel1 = CompanyRelationship(
            person_id=person.id,
            company_idno="1111111111111",
            relationship_type=RelationshipType.FOUNDER,
        )
        rel2 = CompanyRelationship(
            person_id=person.id,
            company_idno="1111111111111",
            relationship_type=RelationshipType.DIRECTOR,
        )

        assert rel1.person_id == rel2.person_id
        assert rel1.company_idno == rel2.company_idno
        assert rel1.relationship_type != rel2.relationship_type

    def test_different_persons_not_merged(self) -> None:
        from credibil.domain.relationship.entities import Person

        p1 = Person(full_name="Ion Popescu")
        p2 = Person(full_name="Ion Popescu")
        assert p1.id != p2.id

    def test_same_normalized_name_different_persons(self) -> None:
        from credibil.domain.relationship.entities import Person

        p1 = Person(full_name="BRÎNZIUC ALEXANDRU")
        p2 = Person(full_name="Brînziuc Alexandru")
        assert _normalize_name(p1.full_name) == _normalize_name(p2.full_name)
        assert p1.id != p2.id
