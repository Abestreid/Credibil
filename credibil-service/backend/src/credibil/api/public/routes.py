from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from credibil.api.public.schemas import (
    CompaniesListResponse,
    CompanyPublic,
    CompanyResponse,
    CourtCasePublic,
    CourtListResponse,
    EnforcementListResponse,
    EnforcementPublic,
    KeyInfo,
    RelationshipPersonPublic,
    RelationshipsResponse,
)
from credibil.api.public.security import (
    APIKeyContext,
    get_db_session,
    require_api_key,
    require_scope,
)
from credibil.infrastructure.database.repositories.company import SQLAlchemyCompanyRepository
from credibil.infrastructure.database.repositories.court_case import (
    SQLAlchemyCourtCaseRepository,
)
from credibil.infrastructure.database.repositories.enforcement import (
    SQLAlchemyEnforcementRepository,
)
from credibil.infrastructure.database.repositories.relationship import (
    SQLAlchemyPersonRepository,
    SQLAlchemyRelationshipRepository,
)

router = APIRouter(prefix="/v1")

_IDNO_PATH = Path(..., min_length=13, max_length=13, pattern=r"^\d{13}$", description="Company fiscal code")


def _enum(value: object) -> object:
    return value.value if hasattr(value, "value") else value


@router.get("/me", response_model=KeyInfo, tags=["Account"], summary="Current API key info")
async def me(ctx: APIKeyContext = Depends(require_api_key)) -> KeyInfo:
    return KeyInfo(name=ctx.name, scopes=ctx.scopes, rate_limit=ctx.rate_limit)


@router.get(
    "/companies",
    response_model=CompaniesListResponse,
    tags=["Companies"],
    summary="List companies",
)
async def list_companies(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: APIKeyContext = Depends(require_scope("companies")),
    session: AsyncSession = Depends(get_db_session),
) -> CompaniesListResponse:
    repo = SQLAlchemyCompanyRepository(session)
    companies = await repo.list_companies(limit=limit, offset=offset)
    return CompaniesListResponse(
        total=len(companies),
        limit=limit,
        offset=offset,
        data=[_company_public(c) for c in companies],
    )


@router.get(
    "/companies/{idno}",
    response_model=CompanyResponse,
    tags=["Companies"],
    summary="Get a company by IDNO",
    responses={404: {"description": "Company not found"}},
)
async def get_company(
    idno: str = _IDNO_PATH,
    ctx: APIKeyContext = Depends(require_scope("companies")),
    session: AsyncSession = Depends(get_db_session),
) -> CompanyResponse:
    repo = SQLAlchemyCompanyRepository(session)
    company = await repo.find_by_idno(idno)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return CompanyResponse(data=_company_public(company))


@router.get(
    "/companies/{idno}/enforcement",
    response_model=EnforcementListResponse,
    tags=["Enforcement"],
    summary="Enforcement proceedings for a company",
)
async def company_enforcement(
    idno: str = _IDNO_PATH,
    state: str | None = Query(default=None, pattern=r"^(active|archived)$"),
    role: str | None = Query(default=None, pattern=r"^(debtor|creditor)$"),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ctx: APIKeyContext = Depends(require_scope("enforcement")),
    session: AsyncSession = Depends(get_db_session),
) -> EnforcementListResponse:
    repo = SQLAlchemyEnforcementRepository(session)
    items = await repo.find_by_idno(idno, role=role, state=state, limit=limit, offset=offset)
    return EnforcementListResponse(
        idno=idno,
        total=await repo.count_by_idno(idno),
        active=await repo.count_by_idno(idno, state="active"),
        archived=await repo.count_by_idno(idno, state="archived"),
        data=[_enforcement_public(p, idno) for p in items],
    )


@router.get(
    "/companies/{idno}/court",
    response_model=CourtListResponse,
    tags=["Court"],
    summary="Court cases for a company",
)
async def company_court(
    idno: str = _IDNO_PATH,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ctx: APIKeyContext = Depends(require_scope("court")),
    session: AsyncSession = Depends(get_db_session),
) -> CourtListResponse:
    repo = SQLAlchemyCourtCaseRepository(session)
    cases = await repo.find_by_idno(idno, limit=limit, offset=offset)
    return CourtListResponse(
        idno=idno,
        total=await repo.count_by_idno(idno),
        data=[
            CourtCasePublic(
                case_number=c.case_number,
                case_type=str(_enum(c.case_type)),
                court_name=c.court_name,
                status=str(_enum(c.status)),
                plaintiff_name=c.plaintiff_name,
                defendant_name=c.defendant_name,
                registration_date=c.registration_date,
            )
            for c in cases
        ],
    )


@router.get(
    "/companies/{idno}/relationships",
    response_model=RelationshipsResponse,
    tags=["Relationships"],
    summary="Founders, directors and other related persons",
)
async def company_relationships(
    idno: str = _IDNO_PATH,
    ctx: APIKeyContext = Depends(require_scope("relationships")),
    session: AsyncSession = Depends(get_db_session),
) -> RelationshipsResponse:
    rel_repo = SQLAlchemyRelationshipRepository(session)
    person_repo = SQLAlchemyPersonRepository(session)
    relationships = await rel_repo.find_by_company_idno(idno)

    persons: list[RelationshipPersonPublic] = []
    for rel in relationships:
        person = await person_repo.find_by_id(rel.person_id)
        persons.append(
            RelationshipPersonPublic(
                person_id=str(rel.person_id),
                full_name=person.full_name if person else None,
                idnp=person.idnp if person else None,
                role=str(_enum(rel.relationship_type)),
                is_active=bool(getattr(rel, "is_active", True)),
            )
        )
    return RelationshipsResponse(idno=idno, data=persons)


def _company_public(c) -> CompanyPublic:
    return CompanyPublic(
        idno=c.idno,
        name_ro=c.name_ro,
        name_ru=c.name_ru,
        status=str(_enum(c.status)) if c.status else None,
        legal_form=str(_enum(c.legal_form)) if c.legal_form else None,
        legal_address=c.legal_address,
        registration_date=c.registration_date,
        caem=c.caem,
        caem_description=c.caem_description,
        founder_count=c.founder_count,
        director_count=c.director_count,
        tax_debt=c.tax_debt,
    )


def _enforcement_public(p, idno: str) -> EnforcementPublic:
    role = p.role_for_idno(idno)
    return EnforcementPublic(
        somation_id=p.somation_id,
        role=role.value if role else None,
        debtor_name=p.debtor_name,
        creditor_name=p.creditor_name,
        executory_doc_number=p.executory_doc_number,
        court_name=p.court_name,
        case_number=p.case_number,
        amount=p.amount,
        currency=p.currency,
        publication_date=p.publication_date,
        state=str(_enum(p.state)),
        source_url=p.source_url,
    )
