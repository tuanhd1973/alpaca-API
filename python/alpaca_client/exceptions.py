"""
Alpaca API Custom Exceptions
"""
from typing import Optional, Dict, Any


class AlpacaError(Exception):
    """Base exception for Alpaca API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(AlpacaError):
    """Invalid API credentials (401)."""
    pass


class ForbiddenError(AlpacaError):
    """Access denied (403)."""
    pass


class NotFoundError(AlpacaError):
    """Resource not found (404)."""
    pass


class RateLimitError(AlpacaError):
    """Rate limit exceeded (429)."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ValidationError(AlpacaError):
    """Invalid request parameters (422)."""
    pass


class InsufficientFundsError(AlpacaError):
    """Insufficient buying power."""
    pass


class MarketClosedError(AlpacaError):
    """Market is closed."""
    pass


class OrderError(AlpacaError):
    """Order-related error."""
    pass


class PositionError(AlpacaError):
    """Position-related error."""
    pass


class APIError(AlpacaError):
    """Generic API error (5xx)."""
    pass
