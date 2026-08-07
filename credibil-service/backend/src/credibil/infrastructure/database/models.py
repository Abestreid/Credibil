# Import all model modules so they register with Base.metadata
from credibil.infrastructure.database import (
    models_accreditation,  # noqa: F401
    models_audit,  # noqa: F401
    models_company,  # noqa: F401
    models_court,  # noqa: F401
    models_enforcement,  # noqa: F401
    models_financial,  # noqa: F401
    models_monitoring,  # noqa: F401
    models_organization,  # noqa: F401
    models_relationship,  # noqa: F401
    models_sanctions,  # noqa: F401
    models_sync,  # noqa: F401
    models_tender,  # noqa: F401
    models_user,  # noqa: F401
)
from credibil.infrastructure.database.base import Base  # noqa: F401
