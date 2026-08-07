class SanctionsError(Exception):
    """Base sanctions error."""


class SanctionsNotFoundError(SanctionsError):
    """Sanctions entry not found."""


class SanctionsFetchError(SanctionsError):
    """Failed to fetch sanctions data from external source."""


class SanctionsSyncError(SanctionsError):
    """Sanctions sync failed."""
