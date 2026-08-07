from __future__ import annotations

from fastapi import APIRouter

from credibil.api.v1.accreditations.routes import router as accreditations_router
from credibil.api.v1.analytics.routes import router as analytics_router
from credibil.api.v1.companies.routes import router as companies_router
from credibil.api.v1.court.routes import router as court_router
from credibil.api.v1.enforcement.routes import router as enforcement_router
from credibil.api.v1.export.routes import router as export_router
from credibil.api.v1.financial.routes import router as financial_router
from credibil.api.v1.relationship.routes import router as relationship_router
from credibil.api.v1.sanctions.routes import router as sanctions_router
from credibil.api.v1.search.routes import router as search_router
from credibil.api.v1.tenders.routes import router as tenders_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(companies_router)
v1_router.include_router(financial_router)
v1_router.include_router(court_router)
v1_router.include_router(enforcement_router)
v1_router.include_router(tenders_router)
v1_router.include_router(accreditations_router)
v1_router.include_router(search_router)
v1_router.include_router(analytics_router)
v1_router.include_router(relationship_router)
v1_router.include_router(sanctions_router)
v1_router.include_router(export_router)
