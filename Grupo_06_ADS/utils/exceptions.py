"""
Custom exceptions for the application.
"""
from fastapi import HTTPException, status
from typing import Optional


class BaseAppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundError(BaseAppException):
    """Resource not found error."""

    def __init__(self, resource: str, detail: Optional[str] = None):
        super().__init__(
            message=f"{resource} nao encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UnauthorizedError(BaseAppException):
    """Unauthorized access error."""

    def __init__(self, message: str = "Nao autorizado", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ForbiddenError(BaseAppException):
    """Forbidden access error."""

    def __init__(self, message: str = "Acesso negado", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class BadRequestError(BaseAppException):
    """Bad request error."""

    def __init__(self, message: str = "Requisicao invalida", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class ConflictError(BaseAppException):
    """Conflict error (duplicate, etc)."""

    def __init__(self, message: str = "Conflito de dados", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class ValidationError(BaseAppException):
    """Validation error."""

    def __init__(self, message: str = "Dados invalidos", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class DatabaseError(BaseAppException):
    """Database operation error."""

    def __init__(self, message: str = "Erro no banco de dados", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class ExternalServiceError(BaseAppException):
    """External service error."""

    def __init__(self, service: str, detail: Optional[str] = None):
        super().__init__(
            message=f"Erro no servico externo: {service}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail
        )


def handle_exception(exc: Exception) -> HTTPException:
    """Convert exception to HTTPException."""
    if isinstance(exc, BaseAppException):
        return HTTPException(
            status_code=exc.status_code,
            detail={
                "error": exc.message,
                "detail": exc.detail
            }
        )
    elif isinstance(exc, HTTPException):
        return exc
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
