"""Custom exceptions and FastAPI exception handlers."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class CivicLensError(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ConfigurationError(CivicLensError):
    """Raised when required configuration is missing or invalid."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class ServiceUnavailableError(CivicLensError):
    """Raised when an external service is unavailable."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class NotFoundError(CivicLensError):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(CivicLensError):
    """Raised when a resource conflict occurs."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class BadRequestError(CivicLensError):
    """Raised when the request is invalid."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


def _error_payload(
    *,
    message: str,
    status_code: int,
    details: Any | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(CivicLensError)
    async def civiclens_error_handler(_: Request, exc: CivicLensError) -> JSONResponse:
        logger.error("CivicLens error: %s", exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(message=exc.message, status_code=exc.status_code),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                message=str(exc.detail),
                status_code=exc.status_code,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_payload(
                message="Validation error",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=exc.errors(),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(
                message="Internal server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )
