from __future__ import annotations

from enum import StrEnum


class SanctionType(StrEnum):
    INTERNATIONAL = "international"
    NATIONAL = "national"
    EU = "eu"
    US_OFAC = "us_ofac"
    UN = "un"


class SanctionStatus(StrEnum):
    ACTIVE = "active"
    LIFTED = "lifted"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
