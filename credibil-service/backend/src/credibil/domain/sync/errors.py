from __future__ import annotations

from credibil.core.exceptions import AppError


class SyncError(AppError):
    code = "SYNC_ERROR"
    message = "Sync operation failed"
    status_code = 500


class SyncAlreadyRunningError(AppError):
    code = "SYNC_ALREADY_RUNNING"
    message = "A sync operation is already in progress"
    status_code = 409

    def __init__(self, provider_id: str) -> None:
        super().__init__(details={"provider_id": provider_id})


class ProviderUnhealthyError(AppError):
    code = "PROVIDER_UNHEALTHY"
    message = "Data provider is not healthy"
    status_code = 503

    def __init__(self, provider_id: str) -> None:
        super().__init__(details={"provider_id": provider_id})


class FileStorageError(AppError):
    code = "FILE_STORAGE_ERROR"
    message = "File storage operation failed"
    status_code = 500


class DownloadError(AppError):
    code = "DOWNLOAD_ERROR"
    message = "Failed to download data file"
    status_code = 502

    def __init__(self, url: str, reason: str | None = None) -> None:
        details: dict[str, str | None] = {"url": url}
        if reason:
            details["reason"] = reason
        super().__init__(details=details)


class ParseError(AppError):
    code = "PARSE_ERROR"
    message = "Failed to parse data file"
    status_code = 422

    def __init__(self, filename: str, reason: str | None = None) -> None:
        details: dict[str, str | None] = {"filename": filename}
        if reason:
            details["reason"] = reason
        super().__init__(details=details)
