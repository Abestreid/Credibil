from __future__ import annotations

from datetime import date

import pytest

from credibil.domain.relationship.entities import (
    CompanyRelationship,
    Person,
    PersonType,
    RelationshipType,
)


class TestPersonEntity:
    def test_create_natural_person(self) -> None:
        person = Person(
            idnp="1234567890123",
            full_name="Ion Popescu",
            person_type=PersonType.NATURAL,
            date_of_birth=date(1985, 3, 15),
            nationality="MD",
        )
        assert person.idnp == "1234567890123"
        assert person.full_name == "Ion Popescu"
        assert person.person_type == PersonType.NATURAL
        assert person.nationality == "MD"
        assert person.id is not None

    def test_create_legal_person(self) -> None:
        person = Person(
            full_name="SRL Exemplu",
            person_type=PersonType.LEGAL,
        )
        assert person.person_type == PersonType.LEGAL
        assert person.idnp is None

    def test_update_person(self) -> None:
        person = Person(
            idnp="1234567890123",
            full_name="Ion Popescu",
        )
        person.update(full_name="Ion Popescu-Marin", nationality="RO")
        assert person.full_name == "Ion Popescu-Marin"
        assert person.nationality == "RO"
        assert person.updated_at >= person.created_at

    def test_repr(self) -> None:
        person = Person(full_name="Test Person")
        assert "Test Person" in repr(person)


class TestCompanyRelationshipEntity:
    def test_create_founder_relationship(self) -> None:
        rel = CompanyRelationship(
            person_id=Person(full_name="A").id,
            company_idno="1234567890123",
            relationship_type=RelationshipType.FOUNDER,
            start_date=date(2020, 1, 1),
            ownership_percentage=50.0,
        )
        assert rel.relationship_type == RelationshipType.FOUNDER
        assert rel.company_idno == "1234567890123"
        assert rel.is_active is True
        assert rel.ownership_percentage == 50.0
        assert rel.id is not None

    def test_create_director_relationship(self) -> None:
        rel = CompanyRelationship(
            person_id=Person(full_name="B").id,
            company_idno="9876543210987",
            relationship_type=RelationshipType.DIRECTOR,
        )
        assert rel.relationship_type == RelationshipType.DIRECTOR
        assert rel.start_date is None

    def test_deactivate(self) -> None:
        rel = CompanyRelationship(
            person_id=Person(full_name="C").id,
            company_idno="1234567890123",
            relationship_type=RelationshipType.FOUNDER,
        )
        assert rel.is_active is True
        rel.deactivate()
        assert rel.is_active is False
        assert rel.end_date is not None

    def test_repr(self) -> None:
        person_id = Person(full_name="X").id
        rel = CompanyRelationship(
            person_id=person_id,
            company_idno="1234567890123",
            relationship_type=RelationshipType.DIRECTOR,
        )
        r = repr(rel)
        assert "1234567890123" in r
        assert "director" in r


class TestPersonRepository:
    @pytest.mark.asyncio
    async def test_save_and_find(self, person_repo: "InMemoryPersonRepository") -> None:
        person = Person(
            idnp="1234567890123",
            full_name="Ion Popescu",
        )
        await person_repo.save(person)
        found = await person_repo.find_by_id(person.id)
        assert found is not None
        assert found.full_name == "Ion Popescu"

    @pytest.mark.asyncio
    async def test_find_by_idnp(self, person_repo: "InMemoryPersonRepository") -> None:
        person = Person(
            idnp="1234567890123",
            full_name="Ion Popescu",
        )
        await person_repo.save(person)
        found = await person_repo.find_by_idnp("1234567890123")
        assert found is not None
        assert found.id == person.id

    @pytest.mark.asyncio
    async def test_count(self, person_repo: "InMemoryPersonRepository") -> None:
        await person_repo.save(Person(full_name="A"))
        await person_repo.save(Person(full_name="B"))
        assert await person_repo.count_all() == 2

    @pytest.mark.asyncio
    async def test_delete(self, person_repo: "InMemoryPersonRepository") -> None:
        person = Person(full_name="To Delete")
        await person_repo.save(person)
        await person_repo.delete(person.id)
        assert await person_repo.find_by_id(person.id) is None


class TestRelationshipRepository:
    @pytest.mark.asyncio
    async def test_save_and_find_by_company(
        self, relationship_repo: "InMemoryRelationshipRepository"
    ) -> None:
        p = Person(full_name="Founder 1")
        rel = CompanyRelationship(
            person_id=p.id,
            company_idno="1234567890123",
            relationship_type=RelationshipType.FOUNDER,
        )
        await relationship_repo.save(rel)
        results = await relationship_repo.find_by_company_idno("1234567890123")
        assert len(results) == 1
        assert results[0].id == rel.id

    @pytest.mark.asyncio
    async def test_find_by_person(
        self, relationship_repo: "InMemoryRelationshipRepository"
    ) -> None:
        p = Person(full_name="Director 1")
        rel = CompanyRelationship(
            person_id=p.id,
            company_idno="1234567890123",
            relationship_type=RelationshipType.DIRECTOR,
        )
        await relationship_repo.save(rel)
        results = await relationship_repo.find_by_person_id(p.id)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_find_shared_founders(
        self, relationship_repo: "InMemoryRelationshipRepository"
    ) -> None:
        p1 = Person(full_name="Shared Founder")
        rel_a = CompanyRelationship(
            person_id=p1.id,
            company_idno="1111111111111",
            relationship_type=RelationshipType.FOUNDER,
        )
        rel_b = CompanyRelationship(
            person_id=p1.id,
            company_idno="2222222222222",
            relationship_type=RelationshipType.FOUNDER,
        )
        await relationship_repo.save(rel_a)
        await relationship_repo.save(rel_b)

        shared = await relationship_repo.find_shared_founders("1111111111111", "2222222222222")
        assert len(shared) == 1
        assert shared[0].person_id == p1.id

    @pytest.mark.asyncio
    async def test_count_by_company(
        self, relationship_repo: "InMemoryRelationshipRepository"
    ) -> None:
        p = Person(full_name="P")
        for _ in range(3):
            rel = CompanyRelationship(
                person_id=p.id,
                company_idno="1234567890123",
                relationship_type=RelationshipType.FOUNDER,
            )
            await relationship_repo.save(rel)
        count = await relationship_repo.count_by_company("1234567890123")
        assert count == 3

    @pytest.mark.asyncio
    async def test_deactivated_not_shown_by_default(
        self, relationship_repo: "InMemoryRelationshipRepository"
    ) -> None:
        p = Person(full_name="Inactive")
        rel = CompanyRelationship(
            person_id=p.id,
            company_idno="1234567890123",
            relationship_type=RelationshipType.FOUNDER,
        )
        await relationship_repo.save(rel)
        rel.deactivate()
        await relationship_repo.save(rel)

        active = await relationship_repo.find_by_company_idno("1234567890123", active_only=True)
        assert len(active) == 0

        all_rels = await relationship_repo.find_by_company_idno("1234567890123", active_only=False)
        assert len(all_rels) == 1
