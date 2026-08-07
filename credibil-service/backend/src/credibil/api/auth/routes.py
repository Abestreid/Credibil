from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from credibil.api.auth.schemas import (
    AuthApiResponse,
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from credibil.application.auth.commands import (
    ChangePasswordCommand,
    LoginCommand,
    RefreshTokenCommand,
    RegisterCommand,
)
from credibil.application.auth.handlers import AuthHandlers
from credibil.core.database import get_session_dependency
from credibil.infrastructure.auth.hasher import BcryptPasswordHasher
from credibil.infrastructure.auth.tokens import JWTTokenService
from credibil.infrastructure.database.repositories.user import SQLAlchemyUserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_handlers(session: AsyncSession) -> AuthHandlers:
    return AuthHandlers(
        user_repo=SQLAlchemyUserRepository(session),
        password_hasher=BcryptPasswordHasher(),
        token_service=JWTTokenService(),
    )


@router.post("/register", response_model=AuthApiResponse, status_code=201)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session_dependency),
) -> AuthApiResponse:
    handlers = _get_handlers(session)
    cmd = RegisterCommand(**body.model_dump())
    result = await handlers.register(cmd)
    return AuthApiResponse(data=UserResponse(**result.model_dump()).model_dump())


@router.post("/login", response_model=AuthApiResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session_dependency),
) -> AuthApiResponse:
    handlers = _get_handlers(session)
    cmd = LoginCommand(**body.model_dump())
    result = await handlers.login(cmd)
    return AuthApiResponse(data=TokenResponse(**result.model_dump()).model_dump())


@router.post("/refresh", response_model=AuthApiResponse)
async def refresh_token(
    body: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session_dependency),
) -> AuthApiResponse:
    handlers = _get_handlers(session)
    cmd = RefreshTokenCommand(**body.model_dump())
    result = await handlers.refresh_token(cmd)
    return AuthApiResponse(data=TokenResponse(**result.model_dump()).model_dump())


@router.post("/change-password", response_model=AuthApiResponse)
async def change_password(
    body: ChangePasswordRequest,
    session: AsyncSession = Depends(get_session_dependency),
) -> AuthApiResponse:
    handlers = _get_handlers(session)
    cmd = ChangePasswordCommand(
        user_id="",
        current_password=body.current_password,
        new_password=body.new_password,
    )
    await handlers.change_password(cmd)
    return AuthApiResponse(data={"message": "Password changed successfully"})
