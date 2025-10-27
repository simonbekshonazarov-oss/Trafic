"""
Custom exceptions for Traffic Share platform
"""

from fastapi import HTTPException, status


class TrafficShareException(Exception):
    """Base exception for Traffic Share platform"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(TrafficShareException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(TrafficShareException):
    """Authorization related errors"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class ResourceNotFoundError(TrafficShareException):
    """Resource not found errors"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(TrafficShareException):
    """Validation related errors"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class RateLimitError(TrafficShareException):
    """Rate limit exceeded errors"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class RegionNotAllowedError(TrafficShareException):
    """Region not allowed errors"""
    def __init__(self, message: str = "Your region is not allowed"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class VPNDetectedError(TrafficShareException):
    """VPN/Proxy detected errors"""
    def __init__(self, message: str = "VPN or proxy detected"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class InsufficientBalanceError(TrafficShareException):
    """Insufficient balance errors"""
    def __init__(self, message: str = "Insufficient balance"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class PaymentError(TrafficShareException):
    """Payment processing errors"""
    def __init__(self, message: str = "Payment failed"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class PackageAllocationError(TrafficShareException):
    """Package allocation errors"""
    def __init__(self, message: str = "Package allocation failed"):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class SessionError(TrafficShareException):
    """Session related errors"""
    def __init__(self, message: str = "Session error"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class DatabaseError(TrafficShareException):
    """Database operation errors"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExternalAPIError(TrafficShareException):
    """External API call errors"""
    def __init__(self, message: str = "External API call failed"):
        super().__init__(message, status_code=status.HTTP_502_BAD_GATEWAY)


def create_http_exception(exc: TrafficShareException) -> HTTPException:
    """Convert TrafficShareException to FastAPI HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )
