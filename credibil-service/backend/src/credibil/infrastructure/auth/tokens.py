from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from credibil.config import get_settings
from credibil.ports.auth.tokens import TokenService


class JWTTokenService(TokenService):
    """JWT token service using python-jose."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def create_access_token(
        self,
        subject: str,
        claims: dict[str, Any] | None = None,
    ) -> str:
        now = datetime.now(UTC)
        expire = now + timedelta(seconds=self._settings.jwt_access_token_ttl)
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": now,
            "type": "access",
        }
        if claims:
            payload.update(claims)
        return jwt.encode(
            payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm
        )

    def create_refresh_token(
        self,
        subject: str,
        claims: dict[str, Any] | None = None,
    ) -> str:
        now = datetime.now(UTC)
        expire = now + timedelta(seconds=self._settings.jwt_refresh_token_ttl)
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": now,
            "type": "refresh",
        }
        if claims:
            payload.update(claims)
        return jwt.encode(
            payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm]
            )
            if payload.get("type") != "access":
                raise ValueError("Invalid token type: expected access token")
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}") from e

    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm]
            )
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type: expected refresh token")
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}") from e
