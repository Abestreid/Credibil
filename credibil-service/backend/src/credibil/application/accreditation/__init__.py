from uuid import UUID

from pydantic import BaseModel, ConfigDict

from credibil.domain.accreditation.entities import AccreditationCategory, AccreditationStatus


class SyncAccreditationsCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: AccreditationCategory | None = None


class GetAccreditationQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accreditation_id: UUID | None = None
    certificate_number: str | None = None


class ListAccreditationsQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: AccreditationCategory | None = None
    status: AccreditationStatus | None = None
    keyword: str | None = None
    limit: int = 100
    offset: int = 0


class GetAccreditationStatisticsQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: AccreditationCategory | None = None
