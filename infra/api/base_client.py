"""
Base API Client Infrastructure

This module provides common patterns and utilities for all API clients in the system.
It includes rate limiting, retry logic, error handling, and authentication patterns
that can be shared across QBO, Plaid, and other API integrations.

Key Features:
- Rate limiting with configurable limits per platform
- Exponential backoff retry logic
- Centralized error handling and logging
- Authentication token management
- Request/response caching
- Circuit breaker pattern for reliability
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from common.exceptions import IntegrationError

logger = logging.getLogger(__name__)


class APIPlatform(Enum):
    """Supported API platforms."""
    QBO = "qbo"
    PLAID = "plaid"
    STRIPE = "stripe"
    ZAPIER = "zapier"


class APIErrorType(Enum):
    """Types of API errors for handling."""
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    VALIDATION = "validation"
    SERVER_ERROR = "server_error"
    UNKNOWN = "unknown"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting - must be set per platform."""
    min_interval_seconds: float = 0.0  # No minimum by default
    max_calls_per_hour: int = 1000  # Generous default
    backoff_multiplier: float = 1.5
    max_retries: int = 3
    burst_limit: int = 100  # Generous default


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_multiplier: float = 2.0
    jitter: bool = True


@dataclass
class CacheConfig:
    """Configuration for response caching."""
    enabled: bool = True
    default_ttl_seconds: int = 300  # 5 minutes
    max_cache_size: int = 1000


class APIError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, error_type: APIErrorType = APIErrorType.UNKNOWN, 
                 status_code: Optional[int] = None, retry_after: Optional[int] = None):
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


class BaseAPIClient(ABC):
    """
    Base class for all API clients.
    
    Provides common functionality like rate limiting, retry logic, error handling,
    and caching that can be shared across different API integrations.
    """
    
    def __init__(self, platform: APIPlatform, business_id: str, 
                 rate_limit_config: Optional[RateLimitConfig] = None,
                 retry_config: Optional[RetryConfig] = None,
                 cache_config: Optional[CacheConfig] = None):
        self.platform = platform
        self.business_id = business_id
        
        # Configuration
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.retry_config = retry_config or RetryConfig()
        self.cache_config = cache_config or CacheConfig()
        
        # State tracking
        self.rate_limits = {
            "last_call": None,
            "hourly_calls": [],
            "burst_calls": [],
            "circuit_breaker_open": False,
            "circuit_breaker_until": None
        }
        
        # Response cache
        self.response_cache = {} if self.cache_config.enabled else None
        
        # HTTP client configuration
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        
    @abstractmethod
    def get_base_url(self) -> str:
        """Get the base URL for the API."""
        pass
    
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        pass
    
    @abstractmethod
    def handle_error_response(self, response: httpx.Response) -> APIError:
        """Handle error responses and convert to appropriate APIError."""
        pass
    
    def _should_allow_call(self) -> bool:
        """Check if API call should be allowed based on rate limiting."""
        now = datetime.now()
        
        # Check circuit breaker
        if self.rate_limits["circuit_breaker_open"]:
            if self.rate_limits["circuit_breaker_until"] and now < self.rate_limits["circuit_breaker_until"]:
                return False
            else:
                # Reset circuit breaker
                self.rate_limits["circuit_breaker_open"] = False
                self.rate_limits["circuit_breaker_until"] = None
        
        # Check minimum interval
        last_call = self.rate_limits["last_call"]
        if last_call:
            min_interval = self.rate_limit_config.min_interval_seconds
            time_since_last = (now - last_call).total_seconds()
            if time_since_last < min_interval:
                return False
        
        # Check hourly rate limit
        hourly_calls = self.rate_limits["hourly_calls"]
        hourly_calls = [call_time for call_time in hourly_calls 
                       if (now - call_time).total_seconds() < 3600]
        
        if len(hourly_calls) >= self.rate_limit_config.max_calls_per_hour:
            return False
        
        # Check burst limit (last 60 seconds)
        burst_calls = self.rate_limits["burst_calls"]
        burst_calls = [call_time for call_time in burst_calls 
                      if (now - call_time).total_seconds() < 60]
        
        if len(burst_calls) >= self.rate_limit_config.burst_limit:
            return False
        
        # Update rate limiting tracking
        self.rate_limits["last_call"] = now
        self.rate_limits["hourly_calls"] = hourly_calls + [now]
        self.rate_limits["burst_calls"] = burst_calls + [now]
        
        return True
    
    def _get_retry_after(self) -> int:
        """Get seconds to wait before retrying."""
        last_call = self.rate_limits["last_call"]
        if not last_call:
            return 0
        
        min_interval = self.rate_limit_config.min_interval_seconds
        time_since_last = (datetime.now() - last_call).total_seconds()
        if time_since_last < min_interval:
            return int(min_interval - time_since_last)
        
        return 0
    
    def _generate_cache_key(self, endpoint: str, method: str, params: Dict[str, Any]) -> str:
        """Generate a cache key for the request."""
        import hashlib
        key_data = f"{self.platform.value}:{method}:{endpoint}:{str(sorted(params.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        if not self.response_cache:
            return None
        
        cached = self.response_cache.get(cache_key)
        if not cached:
            return None
        
        # Check if cache entry is expired
        if datetime.now() - cached["timestamp"] > timedelta(seconds=self.cache_config.default_ttl_seconds):
            del self.response_cache[cache_key]
            return None
        
        return cached["data"]
    
    def _cache_response(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Cache the response data."""
        if not self.response_cache:
            return
        
        # Clean up old cache entries if we're at the limit
        if len(self.response_cache) >= self.cache_config.max_cache_size:
            # Remove oldest entries
            sorted_items = sorted(self.response_cache.items(), key=lambda x: x[1]["timestamp"])
            for key, _ in sorted_items[:len(self.response_cache) // 2]:
                del self.response_cache[key]
        
        self.response_cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    def _open_circuit_breaker(self, duration_seconds: int = 300) -> None:
        """Open the circuit breaker for the specified duration."""
        self.rate_limits["circuit_breaker_open"] = True
        self.rate_limits["circuit_breaker_until"] = datetime.now() + timedelta(seconds=duration_seconds)
        logger.warning(f"Circuit breaker opened for {self.platform.value} API for {duration_seconds} seconds")
    
    async def _make_request(self, endpoint: str, method: str = "GET", 
                          params: Optional[Dict[str, Any]] = None,
                          json_data: Optional[Dict[str, Any]] = None,
                          use_cache: bool = True) -> Dict[str, Any]:
        """
        Make an HTTP request with rate limiting, retry logic, and caching.
        
        Args:
            endpoint: API endpoint (relative to base URL)
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            json_data: JSON body for POST/PUT requests
            use_cache: Whether to use response caching
            
        Returns:
            Parsed JSON response data
            
        Raises:
            APIError: For various API-related errors
            RateLimitError: When rate limit is exceeded
            AuthenticationError: When authentication fails
        """
        # Check rate limiting
        if not self._should_allow_call():
            retry_after = self._get_retry_after()
            raise RateLimitError(f"Rate limit exceeded for {self.platform.value} API", retry_after)
        
        # Check cache first
        cache_key = None
        if use_cache and self.response_cache:
            cache_key = self._generate_cache_key(endpoint, method, params or {})
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.debug(f"Returning cached response for {endpoint}")
                return cached_response
        
        # Prepare request
        url = f"{self.get_base_url()}/{endpoint.lstrip('/')}"
        headers = self.get_auth_headers()
        headers.update({
            "Accept": "application/json",
            "User-Agent": f"Oodaloo-API-Client/1.0 ({self.platform.value})"
        })
        
        # Make the request with retry logic
        try:
            response = await self._make_request_with_retry(
                url, method, headers, params, json_data
            )
            
            # Cache successful responses
            if cache_key and self.response_cache:
                self._cache_response(cache_key, response)
            
            return response
            
        except APIError as e:
            # Handle specific error types
            if e.error_type == APIErrorType.RATE_LIMIT:
                self._open_circuit_breaker(60)  # 1 minute circuit breaker
            elif e.error_type == APIErrorType.AUTHENTICATION:
                self._open_circuit_breaker(300)  # 5 minute circuit breaker
            raise
    
    async def _make_request_with_retry(self, url: str, method: str, headers: Dict[str, str],
                                     params: Optional[Dict[str, Any]] = None,
                                     json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        
        @retry(
            stop=stop_after_attempt(self.retry_config.max_attempts),
            wait=wait_exponential(
                multiplier=self.retry_config.exponential_multiplier,
                min=self.retry_config.base_delay,
                max=self.retry_config.max_delay
            ),
            retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError))
        )
        async def _do_request():
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, params=params, json=json_data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=headers, params=params, json=json_data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check for errors
                if response.status_code >= 400:
                    error = self.handle_error_response(response)
                    raise error
                
                return response.json()
        
        return await _do_request()
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                 use_cache: bool = True) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._make_request(endpoint, "GET", params=params, use_cache=use_cache)
    
    async def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None,
                  params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._make_request(endpoint, "POST", params=params, json_data=json_data, use_cache=False)
    
    async def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None,
                 params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._make_request(endpoint, "PUT", params=params, json_data=json_data, use_cache=False)
    
    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._make_request(endpoint, "DELETE", params=params, use_cache=False)
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        if self.response_cache:
            self.response_cache.clear()
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limiting status."""
        now = datetime.now()
        hourly_calls = len([call for call in self.rate_limits["hourly_calls"] 
                           if (now - call).total_seconds() < 3600])
        burst_calls = len([call for call in self.rate_limits["burst_calls"] 
                          if (now - call).total_seconds() < 60])
        
        return {
            "platform": self.platform.value,
            "business_id": self.business_id,
            "hourly_calls": hourly_calls,
            "max_hourly_calls": self.rate_limit_config.max_calls_per_hour,
            "burst_calls": burst_calls,
            "max_burst_calls": self.rate_limit_config.burst_limit,
            "circuit_breaker_open": self.rate_limits["circuit_breaker_open"],
            "cache_size": len(self.response_cache) if self.response_cache else 0
        }


class BatchAPIClient(BaseAPIClient):
    """
    Base class for API clients that support batch operations.
    
    Extends BaseAPIClient with batch request capabilities for APIs that support
    multiple operations in a single request (like QBO's batch endpoint).
    """
    
    @abstractmethod
    async def make_batch_request(self, batch_operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make a batch API request."""
        pass
    
    def _validate_batch_operations(self, batch_operations: List[Dict[str, Any]]) -> None:
        """Validate batch operations before sending."""
        if not batch_operations:
            raise ValueError("Batch operations cannot be empty")
        
        if len(batch_operations) > 30:  # Reasonable batch size limit
            raise ValueError(f"Too many batch operations: {len(batch_operations)} (max 30)")
        
        for i, operation in enumerate(batch_operations):
            if not isinstance(operation, dict):
                raise ValueError(f"Batch operation {i} must be a dictionary")
            
            if "id" not in operation:
                raise ValueError(f"Batch operation {i} must have an 'id' field")
    
    async def _execute_batch_operations(self, batch_operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute batch operations with proper error handling."""
        self._validate_batch_operations(batch_operations)
        
        try:
            return await self.make_batch_request(batch_operations)
        except APIError as e:
            logger.error(f"Batch request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in batch request: {e}")
            raise APIError(f"Batch request failed: {str(e)}")


def create_rate_limit_config(platform: APIPlatform) -> RateLimitConfig:
    """Create platform-specific rate limit configuration.
    
    WARNING: Each platform has very different rate limits!
    - QBO: 100 calls/hour, 6 seconds between calls (very strict)
    - Plaid: 500+ calls/hour, 0.5 seconds between calls (lenient)
    - Stripe: 100+ requests/second (very lenient)
    - Generic APIs: Varies widely
    """
    configs = {
        APIPlatform.QBO: RateLimitConfig(
            min_interval_seconds=6.0,  # QBO requires 6 seconds between calls
            max_calls_per_hour=100,    # QBO's strict hourly limit
            backoff_multiplier=2.0,
            max_retries=2,
            burst_limit=5
        ),
        APIPlatform.PLAID: RateLimitConfig(
            min_interval_seconds=0.5,  # Plaid allows faster calls
            max_calls_per_hour=500,    # Plaid allows 5x more calls than QBO
            backoff_multiplier=1.5,
            max_retries=3,
            burst_limit=20
        ),
        APIPlatform.STRIPE: RateLimitConfig(
            min_interval_seconds=0.01, # Stripe allows very fast calls
            max_calls_per_hour=10000,  # Stripe allows 100x more calls than QBO
            backoff_multiplier=1.5,
            max_retries=3,
            burst_limit=100
        )
    }
    
    # Default to generous settings for unknown platforms
    # This prevents accidentally applying QBO's strict limits to other APIs
    return configs.get(platform, RateLimitConfig(
        min_interval_seconds=0.0,  # No minimum interval
        max_calls_per_hour=1000,   # Generous hourly limit
        backoff_multiplier=1.5,
        max_retries=3,
        burst_limit=50
    ))


def create_retry_config(platform: APIPlatform) -> RetryConfig:
    """Create platform-specific retry configuration."""
    configs = {
        APIPlatform.QBO: RetryConfig(
            max_attempts=2,
            base_delay=1.0,
            max_delay=30.0,
            exponential_multiplier=1.5
        ),
        APIPlatform.PLAID: RetryConfig(
            max_attempts=3,
            base_delay=0.5,
            max_delay=60.0,
            exponential_multiplier=2.0
        ),
        APIPlatform.STRIPE: RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=60.0,
            exponential_multiplier=2.0
        )
    }
    
    return configs.get(platform, RetryConfig())
