from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=255)


class LoginCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str


class RefreshTokenCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    refresh_token: str


class ChangePasswordCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
