from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, func, or_, select

from credibil.domain.relationship.entities import (
    CompanyRelationship,
    Person,
    PersonType,
    RelationshipType,
)
from credibil.infrastructure.database.models_relationship import (
    CompanyRelationshipModel,
    PersonModel,
)
from credibil.ports.repositories.relationship import PersonRepository, RelationshipRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


# ── Person mapping ──────────────────────────────────────────────────────────


def _person_to_entity(model: PersonModel) -> Person:
    return Person(
        person_id=model.id,
        idnp=model.idnp,
        full_name=model.full_name,
        person_type=PersonType(model.person_type),
        date_of_birth=model.date_of_birth,
        nationality=model.nationality,
        metadata=model.metadata_,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _person_to_model(entity: Person) -> PersonModel:
    return PersonModel(
        id=entity.id,
        idnp=entity.idnp,
        full_name=entity.full_name,
        person_type=entity.person_type,
        date_of_birth=entity.date_of_birth,
        nationality=entity.nationality,
        metadata_=entity.metadata,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


# ── Relationship mapping ────────────────────────────────────────────────────


def _rel_to_entity(model: CompanyRelationshipModel) -> CompanyRelationship:
    return CompanyRelationship(
        relationship_id=model.id,
        person_id=model.person_id,
        company_idno=model.company_idno,
        relationship_type=RelationshipType(model.relationship_type),
        start_date=model.start_date,
        end_date=model.end_date,
        ownership_percentage=model.ownership_percentage,
        is_active=model.is_active,
        metadata=model.metadata_,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _rel_to_model(entity: CompanyRelationship) -> CompanyRelationshipModel:
    return CompanyRelationshipModel(
        id=entity.id,
        person_id=entity.person_id,
        company_idno=entity.company_idno,
        relationship_type=entity.relationship_type,
        start_date=entity.start_date,
        end_date=entity.end_date,
        ownership_percentage=entity.ownership_percentage,
        is_active=entity.is_active,
        metadata_=entity.metadata,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


# ── Person Repository ───────────────────────────────────────────────────────


class SQLAlchemyPersonRepository(PersonRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, person_id: UUID) -> Person | None:
        result = await self._session.execute(select(PersonModel).where(PersonModel.id == person_id))
        model = result.scalar_one_or_none()
        return _person_to_entity(model) if model else None

    async def find_by_idnp(self, idnp: str) -> Person | None:
        result = await self._session.execute(select(PersonModel).where(PersonModel.idnp == idnp))
        model = result.scalar_one_or_none()
        return _person_to_entity(model) if model else None

    async def save(self, person: Person) -> Person:
        existing = await self._session.get(PersonModel, person.id)
        if existing:
            existing.idnp = person.idnp
            existing.full_name = person.full_name
            existing.person_type = person.person_type
            existing.date_of_birth = person.date_of_birth
            existing.nationality = person.nationality
            existing.metadata_ = person.metadata
            existing.updated_at = person.updated_at
            await self._session.flush()
            return _person_to_entity(existing)

        model = _person_to_model(person)
        self._session.add(model)
        await self._session.flush()
        return _person_to_entity(model)

    async def delete(self, person_id: UUID) -> None:
        model = await self._session.get(PersonModel, person_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_persons(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
    ) -> list[Person]:
        stmt = select(PersonModel)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    PersonModel.full_name.ilike(pattern),
                    PersonModel.idnp.ilike(pattern),
                )
            )
        stmt = stmt.order_by(PersonModel.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [_person_to_entity(m) for m in result.scalars().all()]

    async def count_all(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(PersonModel))
        return result.scalar_one()

    async def exists(self, person_id: UUID) -> bool:
        result = await self._session.execute(
            select(func.count()).select_from(PersonModel).where(PersonModel.id == person_id)
        )
        return result.scalar_one() > 0


# ── Relationship Repository ─────────────────────────────────────────────────


class SQLAlchemyRelationshipRepository(RelationshipRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, relationship_id: UUID) -> CompanyRelationship | None:
        result = await self._session.execute(
            select(CompanyRelationshipModel).where(CompanyRelationshipModel.id == relationship_id)
        )
        model = result.scalar_one_or_none()
        return _rel_to_entity(model) if model else None

    async def save(self, relationship: CompanyRelationship) -> CompanyRelationship:
        existing = await self._session.get(CompanyRelationshipModel, relationship.id)
        if existing:
            existing.person_id = relationship.person_id
            existing.company_idno = relationship.company_idno
            existing.relationship_type = relationship.relationship_type
            existing.start_date = relationship.start_date
            existing.end_date = relationship.end_date
            existing.ownership_percentage = relationship.ownership_percentage
            existing.is_active = relationship.is_active
            existing.metadata_ = relationship.metadata
            existing.updated_at = relationship.updated_at
            await self._session.flush()
            return _rel_to_entity(existing)

        model = _rel_to_model(relationship)
        self._session.add(model)
        await self._session.flush()
        return _rel_to_entity(model)

    async def delete(self, relationship_id: UUID) -> None:
        model = await self._session.get(CompanyRelationshipModel, relationship_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def find_by_company_idno(
        self,
        idno: str,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[CompanyRelationship]:
        stmt = select(CompanyRelationshipModel).where(CompanyRelationshipModel.company_idno == idno)
        if relationship_type:
            stmt = stmt.where(CompanyRelationshipModel.relationship_type == relationship_type)
        if active_only:
            stmt = stmt.where(CompanyRelationshipModel.is_active.is_(True))
        result = await self._session.execute(stmt)
        return [_rel_to_entity(m) for m in result.scalars().all()]

    async def find_by_person_id(
        self,
        person_id: UUID,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[CompanyRelationship]:
        stmt = select(CompanyRelationshipModel).where(
            CompanyRelationshipModel.person_id == person_id
        )
        if relationship_type:
            stmt = stmt.where(CompanyRelationshipModel.relationship_type == relationship_type)
        if active_only:
            stmt = stmt.where(CompanyRelationshipModel.is_active.is_(True))
        result = await self._session.execute(stmt)
        return [_rel_to_entity(m) for m in result.scalars().all()]

    async def find_by_person_idnp(
        self,
        idnp: str,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[CompanyRelationship]:
        person = await self._find_person_by_idnp(idnp)
        if not person:
            return []
        return await self.find_by_person_id(person.id, relationship_type, active_only)

    async def find_related_companies(
        self,
        idno: str,
        active_only: bool = True,
    ) -> list[CompanyRelationship]:
        """Find all relationships where a company shares a person with another company."""
        # Get all person_ids linked to this company
        stmt_company = select(CompanyRelationshipModel.person_id).where(
            CompanyRelationshipModel.company_idno == idno
        )
        if active_only:
            stmt_company = stmt_company.where(CompanyRelationshipModel.is_active.is_(True))

        result = await self._session.execute(stmt_company)
        person_ids = [row[0] for row in result.all()]

        if not person_ids:
            return []

        # Find all other companies linked to same persons
        stmt_related = select(CompanyRelationshipModel).where(
            and_(
                CompanyRelationshipModel.person_id.in_(person_ids),
                CompanyRelationshipModel.company_idno != idno,
            )
        )
        if active_only:
            stmt_related = stmt_related.where(CompanyRelationshipModel.is_active.is_(True))

        result = await self._session.execute(stmt_related)
        return [_rel_to_entity(m) for m in result.scalars().all()]

    async def find_shared_directors(self, idno_a: str, idno_b: str) -> list[CompanyRelationship]:
        return await self._find_shared_by_type(idno_a, idno_b, RelationshipType.DIRECTOR)

    async def find_shared_founders(self, idno_a: str, idno_b: str) -> list[CompanyRelationship]:
        return await self._find_shared_by_type(idno_a, idno_b, RelationshipType.FOUNDER)

    async def count_by_company(self, idno: str) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(CompanyRelationshipModel)
            .where(
                and_(
                    CompanyRelationshipModel.company_idno == idno,
                    CompanyRelationshipModel.is_active.is_(True),
                )
            )
        )
        return result.scalar_one()

    async def count_by_person(self, person_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(CompanyRelationshipModel)
            .where(
                and_(
                    CompanyRelationshipModel.person_id == person_id,
                    CompanyRelationshipModel.is_active.is_(True),
                )
            )
        )
        return result.scalar_one()

    async def find_existing(
        self,
        person_id: UUID,
        company_idno: str,
        relationship_type: RelationshipType,
    ) -> CompanyRelationship | None:
        result = await self._session.execute(
            select(CompanyRelationshipModel).where(
                and_(
                    CompanyRelationshipModel.person_id == person_id,
                    CompanyRelationshipModel.company_idno == company_idno,
                    CompanyRelationshipModel.relationship_type == relationship_type,
                    CompanyRelationshipModel.is_active.is_(True),
                )
            )
        )
        model = result.scalar_one_or_none()
        return _rel_to_entity(model) if model else None

    async def _find_person_by_idnp(self, idnp: str) -> Person | None:
        result = await self._session.execute(select(PersonModel).where(PersonModel.idnp == idnp))
        model = result.scalar_one_or_none()
        return _person_to_entity(model) if model else None

    async def _find_shared_by_type(
        self,
        idno_a: str,
        idno_b: str,
        rel_type: RelationshipType,
    ) -> list[CompanyRelationship]:
        """Find persons that are in both company A and B with a given relationship type."""
        stmt_a = select(CompanyRelationshipModel.person_id).where(
            and_(
                CompanyRelationshipModel.company_idno == idno_a,
                CompanyRelationshipModel.relationship_type == rel_type,
                CompanyRelationshipModel.is_active.is_(True),
            )
        )
        result_a = await self._session.execute(stmt_a)
        person_ids_a = {row[0] for row in result_a.all()}

        if not person_ids_a:
            return []

        stmt_b = select(CompanyRelationshipModel).where(
            and_(
                CompanyRelationshipModel.person_id.in_(person_ids_a),
                CompanyRelationshipModel.company_idno == idno_b,
                CompanyRelationshipModel.relationship_type == rel_type,
                CompanyRelationshipModel.is_active.is_(True),
            )
        )
        result_b = await self._session.execute(stmt_b)
        return [_rel_to_entity(m) for m in result_b.scalars().all()]
