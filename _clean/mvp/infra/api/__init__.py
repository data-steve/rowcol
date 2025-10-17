"""
API Infrastructure

Production-grade API client patterns including rate limiting, retry logic,
circuit breaker, and error handling.
"""

from .base_client import (
    BaseAPIClient,
    RateLimitConfig,
    RetryConfig,
)
from .exceptions import (
    APIError,
    APIErrorType,
    RateLimitError,
    AuthenticationError,
    NetworkError,
)

__all__ = [
    "BaseAPIClient",
    "RateLimitConfig",
    "RetryConfig",
    "APIError",
    "APIErrorType",
    "RateLimitError",
    "AuthenticationError",
    "NetworkError",
]

