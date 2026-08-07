from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class IDNO:
    """Moldovan company registration number (IDNO - 13 digits)."""

    value: str

    def __post_init__(self) -> None:
        cleaned = re.sub(r"\s+", "", self.value)
        if not re.match(r"^\d{13}$", cleaned):
            raise ValueError(f"Invalid IDNO: {self.value!r}. Must be 13 digits.")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PostalCode:
    """Moldovan postal code (MD-XXXX where X is a digit)."""

    value: str

    def __post_init__(self) -> None:
        cleaned = re.sub(r"\s+", "", self.value)
        if not re.match(r"^(MD-)?\d{4}$", cleaned, re.IGNORECASE):
            raise ValueError(f"Invalid postal code: {self.value!r}")
        if cleaned.upper().startswith("MD-"):
            cleaned = cleaned[3:]
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CAEM:
    """CAEM code (Classification of Economic Activities — NACE equivalent)."""

    value: str

    def __post_init__(self) -> None:
        cleaned = re.sub(r"\s+", "", self.value)
        if not re.match(r"^\d{2}(\.?\d{2})?$", cleaned):
            raise ValueError(f"Invalid CAEM code: {self.value!r}")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value
