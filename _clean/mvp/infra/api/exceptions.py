"""
API Error Hierarchy

Typed exceptions for different API error scenarios.
"""

from enum import Enum
from typing import Optional


class APIErrorType(Enum):
    """Types of API errors for handling."""
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    VALIDATION = "validation"
    SERVER_ERROR = "server_error"
    UNKNOWN = "unknown"


class APIError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(
        self, 
        message: str, 
        error_type: APIErrorType = APIErrorType.UNKNOWN, 
        status_code: Optional[int] = None, 
        retry_after: Optional[int] = None
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(message)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int):
        super().__init__(message, APIErrorType.RATE_LIMIT, retry_after=retry_after)


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, APIErrorType.AUTHENTICATION, status_code)


class NetworkError(APIError):
    """Raised when network-level errors occur."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, APIErrorType.NETWORK, status_code)


class ValidationError(APIError):
    """Raised when API request validation fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, APIErrorType.VALIDATION, status_code)


class ServerError(APIError):
    """Raised when server returns 5xx errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, APIErrorType.SERVER_ERROR, status_code)

