from __future__ import annotations

from typing import TYPE_CHECKING

from credibil.application.auth.dto import TokenPairDTO, UserDTO
from credibil.config import get_settings
from credibil.domain.user.entities import User, UserRole, UserStatus
from credibil.domain.user.errors import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.application.auth.commands import (
        ChangePasswordCommand,
        LoginCommand,
        RefreshTokenCommand,
        RegisterCommand,
    )
    from credibil.ports.auth.hasher import PasswordHasher
    from credibil.ports.auth.tokens import TokenService
    from credibil.ports.repositories.user import UserRepository


class AuthHandlers:
    """Application service for authentication operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._user_repo = user_repo
        self._hasher = password_hasher
        self._tokens = token_service
        self._settings = get_settings()

    async def register(self, cmd: RegisterCommand) -> UserDTO:
        existing = await self._user_repo.find_by_email(cmd.email)
        if existing:
            raise UserAlreadyExistsError(cmd.email)

        user = User(
            email=cmd.email,
            hashed_password=self._hasher.hash(cmd.password),
            full_name=cmd.full_name,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )
        saved = await self._user_repo.save(user)
        return UserDTO.model_validate(saved.__dict__)

    async def login(self, cmd: LoginCommand) -> TokenPairDTO:
        user = await self._user_repo.find_by_email(cmd.email)
        if not user:
            raise InvalidCredentialsError()

        if not self._hasher.verify(cmd.password, user.hashed_password):
            raise InvalidCredentialsError()

        if user.status != UserStatus.ACTIVE:
            raise InvalidCredentialsError()

        user.record_login()
        await self._user_repo.save(user)

        claims = {
            "role": user.role.value,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        }
        access_token = self._tokens.create_access_token(str(user.id), claims)
        refresh_token = self._tokens.create_refresh_token(str(user.id), claims)

        return TokenPairDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._settings.jwt_access_token_ttl,
        )

    async def refresh_token(self, cmd: RefreshTokenCommand) -> TokenPairDTO:
        try:
            payload = self._tokens.decode_refresh_token(cmd.refresh_token)
        except ValueError:
            raise InvalidCredentialsError() from None

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentialsError()

        from uuid import UUID

        user = await self._user_repo.find_by_id(UUID(user_id))
        if not user:
            raise UserNotFoundError(user_id)

        if user.status != UserStatus.ACTIVE:
            raise InvalidCredentialsError()

        claims = {
            "role": user.role.value,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        }
        access_token = self._tokens.create_access_token(str(user.id), claims)
        refresh_token = self._tokens.create_refresh_token(str(user.id), claims)

        return TokenPairDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._settings.jwt_access_token_ttl,
        )

    async def get_user(self, user_id: UUID) -> UserDTO:
        user = await self._user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        return UserDTO.model_validate(user.__dict__)

    async def change_password(self, cmd: ChangePasswordCommand) -> None:
        from uuid import UUID

        user = await self._user_repo.find_by_id(UUID(cmd.user_id))
        if not user:
            raise UserNotFoundError(cmd.user_id)

        if not self._hasher.verify(cmd.current_password, user.hashed_password):
            raise InvalidCredentialsError()

        user.update(hashed_password=self._hasher.hash(cmd.new_password))
        await self._user_repo.save(user)
