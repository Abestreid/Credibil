from pydantic import BaseModel, ConfigDict


class GetUserQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str


class ListUsersQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tenant_id: str | None = None
    page: int = 1
    per_page: int = 25
