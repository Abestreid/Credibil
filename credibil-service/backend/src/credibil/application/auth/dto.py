from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: str
    status: str
    tenant_id: UUID | None = None
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TokenPairDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
