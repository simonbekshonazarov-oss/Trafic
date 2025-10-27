"""Custom exceptions for the Traffic Share application."""

class TrafficShareException(Exception):
    """Base exception for Traffic Share application."""
    pass

class AuthenticationError(TrafficShareException):
    """Authentication related errors."""
    pass

class AuthorizationError(TrafficShareException):
    """Authorization related errors."""
    pass

class ValidationError(TrafficShareException):
    """Data validation errors."""
    pass

class NotFoundError(TrafficShareException):
    """Resource not found errors."""
    pass

class RateLimitError(TrafficShareException):
    """Rate limiting errors."""
    pass

class RegionNotAllowedError(TrafficShareException):
    """Region not allowed errors."""
    pass

class InsufficientBalanceError(TrafficShareException):
    """Insufficient balance errors."""
    pass

class PaymentError(TrafficShareException):
    """Payment processing errors."""
    pass

class DatabaseError(TrafficShareException):
    """Database related errors."""
    pass

class ExternalServiceError(TrafficShareException):
    """External service errors (Telegram, Cryptomus, etc.)."""
    pass
