from __future__ import annotations

import bcrypt

from credibil.ports.auth.hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    """BCrypt password hasher."""

    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
