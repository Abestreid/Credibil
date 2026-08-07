from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id
from credibil.domain.sanctions.enums import RiskLevel, SanctionStatus, SanctionType

if TYPE_CHECKING:
    from uuid import UUID


class SanctionsEntry:
    """A single sanctions listing against a person or company."""

    def __init__(
        self,
        *,
        entry_id: UUID | None = None,
        target_name: str,
        target_idno: str | None = None,
        target_idnp: str | None = None,
        sanction_type: SanctionType,
        status: SanctionStatus = SanctionStatus.ACTIVE,
        list_name: str | None = None,
        list_url: str | None = None,
        country_code: str | None = None,
        reason: str | None = None,
        program: str | None = None,
        listed_date: date | None = None,
        last_updated: date | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = entry_id or new_id()
        self.target_name = target_name
        self.target_idno = target_idno
        self.target_idnp = target_idnp
        self.sanction_type = sanction_type
        self.status = status
        self.list_name = list_name
        self.list_url = list_url
        self.country_code = country_code
        self.reason = reason
        self.program = program
        self.listed_date = listed_date
        self.last_updated = last_updated
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        allowed = {
            "target_name",
            "sanction_type",
            "status",
            "list_name",
            "list_url",
            "country_code",
            "reason",
            "program",
            "listed_date",
            "last_updated",
            "metadata",
        }
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<SanctionsEntry name={self.target_name!r} "
            f"type={self.sanction_type.value} status={self.status.value}>"
        )


class RiskAssessment:
    """Aggregated risk assessment for a company or person."""

    def __init__(
        self,
        *,
        assessment_id: UUID | None = None,
        target_idno: str | None = None,
        target_idnp: str | None = None,
        target_name: str | None = None,
        overall_risk: RiskLevel = RiskLevel.UNKNOWN,
        sanctions_risk: RiskLevel = RiskLevel.UNKNOWN,
        litigation_risk: RiskLevel = RiskLevel.UNKNOWN,
        financial_risk: RiskLevel = RiskLevel.UNKNOWN,
        sanctions_count: int = 0,
        active_cases_count: int = 0,
        total_cases_count: int = 0,
        risk_factors: list[str] | None = None,
        assessed_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = assessment_id or new_id()
        self.target_idno = target_idno
        self.target_idnp = target_idnp
        self.target_name = target_name
        self.overall_risk = overall_risk
        self.sanctions_risk = sanctions_risk
        self.litigation_risk = litigation_risk
        self.financial_risk = financial_risk
        self.sanctions_count = sanctions_count
        self.active_cases_count = active_cases_count
        self.total_cases_count = total_cases_count
        self.risk_factors = risk_factors or []
        self.assessed_at = assessed_at or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"<RiskAssessment idno={self.target_idno!r} overall={self.overall_risk.value}>"
