from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select

from credibil.domain.user.entities import User, UserRole, UserStatus
from credibil.infrastructure.database.models_user import UserModel
from credibil.ports.repositories.user import UserRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyUserRepository(UserRepository):
    """PostgreSQL user repository via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, user: User) -> User:
        model = self._to_model(user)
        merged = await self._session.merge(model)
        await self._session.flush()
        await self._session.refresh(merged)
        return self._to_domain(merged)

    async def delete(self, user_id: UUID) -> None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_users(
        self,
        tenant_id: UUID | None = None,
        offset: int = 0,
        limit: int = 25,
    ) -> tuple[list[User], int]:
        base = select(UserModel)
        count_q = select(func.count()).select_from(UserModel)

        if tenant_id:
            base = base.where(UserModel.tenant_id == tenant_id)
            count_q = count_q.where(UserModel.tenant_id == tenant_id)

        total_result = await self._session.execute(count_q)
        total = total_result.scalar_one()

        base = base.order_by(UserModel.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(base)
        models = list(result.scalars().all())
        return [self._to_domain(m) for m in models], total

    async def count_by_email(self, email: str) -> int:
        stmt = select(func.count()).select_from(UserModel).where(UserModel.email == email.lower())
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def exists(self, user_id: UUID) -> bool:
        stmt = select(func.count()).select_from(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0

    def _to_domain(self, model: UserModel) -> User:
        return User(
            user_id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=UserRole(model.role),
            status=UserStatus(model.status),
            tenant_id=model.tenant_id,
            last_login_at=model.last_login_at,
            metadata=model.metadata_ if model.metadata_ else {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            tenant_id=user.tenant_id,
            last_login_at=user.last_login_at,
            metadata_=user.metadata,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
