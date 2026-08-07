from pydantic import BaseModel


class AdminApiResponse(BaseModel):
    success: bool = True
    data: dict | list | None = None
    error: dict | None = None
    request_id: str | None = None
