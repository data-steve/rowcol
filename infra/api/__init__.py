"""
API Client Infrastructure

This package contains all API client implementations and base classes for
external service integrations.

Components:
- base_client: Base classes and utilities for API clients
- qbo_client: QuickBooks Online API client
- plaid_client: Plaid API client (future)
- stripe_client: Stripe API client (future)
"""

from .base_client import (
    BaseAPIClient,
    BatchAPIClient,
    APIPlatform,
    APIErrorType,
    APIError,
    RateLimitError,
    AuthenticationError,
    RateLimitConfig,
    RetryConfig,
    CacheConfig,
    create_rate_limit_config,
    create_retry_config
)

__all__ = [
    "BaseAPIClient",
    "BatchAPIClient", 
    "APIPlatform",
    "APIErrorType",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "RateLimitConfig",
    "RetryConfig",
    "CacheConfig",
    "create_rate_limit_config",
    "create_retry_config"
]
