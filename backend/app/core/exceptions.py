from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from backend.app.core.constants import ErrorCode

class AppException(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
        retryable: bool = False
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.retryable = retryable
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details,
                "retryable": self.retryable,
            }
        }

class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.AUTHENTICATION_FAILED,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )

class PermissionDeniedError(AppException):
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.PERMISSION_DENIED,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )

class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )

class BudgetExceededError(AppException):
    def __init__(self, message: str = "Workspace budget exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.BUDGET_EXCEEDED,
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            details=details,
        )

class ProviderError(AppException):
    def __init__(self, message: str, retryable: bool = True, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.PROVIDER_UNAVAILABLE,
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
            retryable=retryable,
        )
