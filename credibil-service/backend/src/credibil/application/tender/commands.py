from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from uuid import UUID


class ListTendersQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    limit: int = 50
    offset: int = 0
    status: str | None = None
    buyer_idno: str | None = None


class GetTenderQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tender_id: UUID


class GetTenderByOcidQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ocid: str


class GetTendersByBuyerQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str
    limit: int = 50
    offset: int = 0


class GetTendersBySupplierQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str
    limit: int = 50
    offset: int = 0


class GetTenderAnalyticsQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str


class SyncRecentTendersCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    limit: int = 50


class SyncTendersByBuyerCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str
    limit: int = 50
