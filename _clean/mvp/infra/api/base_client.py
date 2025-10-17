"""
Base API Client Infrastructure

Production-grade patterns for API clients including rate limiting, retry logic,
circuit breaker, and error handling. Adapted from legacy infrastructure for MVP.

Key Features:
- Rate limiting with configurable limits
- Exponential backoff retry logic
- Circuit breaker pattern for reliability
- Typed error hierarchy
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .exceptions import (
    APIError,
    NetworkError,
)

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    min_interval_seconds: float = 0.5  # Minimum time between calls
    max_calls_per_minute: int = 30     # Maximum calls per minute
    burst_limit: int = 10              # Short burst allowance
    backoff_multiplier: float = 2.0    # Backoff multiplier on rate limit
    max_retries: int = 3               # Maximum retry attempts


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_multiplier: float = 2.0


class BaseAPIClient(ABC):
    """
    Base class for API clients with production-grade patterns.
    
    Provides:
    - Rate limiting with configurable limits
    - Exponential backoff retry logic
    - Circuit breaker pattern
    - Proper error handling
    """
    
    def __init__(
        self,
        rate_limit_config: Optional[RateLimitConfig] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.retry_config = retry_config or RetryConfig()
        
        # Rate limiting state
        self.rate_limits = {
            "last_call": None,
            "minute_calls": [],
            "circuit_breaker_open": False,
            "circuit_breaker_until": None,
        }
        
        # Request timeout configuration
        self.timeout = (5.0, 30.0)  # (connect timeout, read timeout)
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Get the base URL for the API."""
        pass
    
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        pass
    
    @abstractmethod
    def handle_error_response(self, response: requests.Response) -> APIError:
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
        
        # Check per-minute rate limit
        minute_calls = self.rate_limits["minute_calls"]
        minute_calls = [
            call_time for call_time in minute_calls
            if (now - call_time).total_seconds() < 60
        ]
        
        if len(minute_calls) >= self.rate_limit_config.max_calls_per_minute:
            return False
        
        # Update rate limiting tracking
        self.rate_limits["last_call"] = now
        self.rate_limits["minute_calls"] = minute_calls + [now]
        
        return True
    
    def _wait_for_rate_limit(self) -> None:
        """Wait until rate limit allows next call."""
        max_wait_attempts = 10  # Prevent infinite loops
        wait_attempts = 0
        
        while not self._should_allow_call() and wait_attempts < max_wait_attempts:
            wait_attempts += 1
            
            # Calculate wait time
            last_call = self.rate_limits["last_call"]
            if last_call:
                min_interval = self.rate_limit_config.min_interval_seconds
                time_since_last = (datetime.now() - last_call).total_seconds()
                wait_time = max(0, min_interval - time_since_last)
                if wait_time > 0:
                    logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                    time.sleep(wait_time)
            else:
                # If minute limit reached, wait a bit
                time.sleep(1.0)
        
        if wait_attempts >= max_wait_attempts:
            logger.warning("Rate limit wait exceeded maximum attempts, proceeding anyway")
    
    def _open_circuit_breaker(self, duration_seconds: int = 300) -> None:
        """Open the circuit breaker for the specified duration."""
        self.rate_limits["circuit_breaker_open"] = True
        self.rate_limits["circuit_breaker_until"] = datetime.now() + timedelta(seconds=duration_seconds)
        logger.warning(f"Circuit breaker opened for {duration_seconds} seconds")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with rate limiting and retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            json_data: JSON body for POST/PUT requests
            
        Returns:
            Parsed JSON response data
            
        Raises:
            APIError: For various API-related errors
            RateLimitError: When rate limit is exceeded
            AuthenticationError: When authentication fails
        """
        # Wait for rate limit if needed
        self._wait_for_rate_limit()
        
        # Prepare request
        url = f"{self.get_base_url()}/{endpoint.lstrip('/')}"
        headers = self.get_auth_headers()
        
        # Make the request with retry logic
        try:
            response = self._make_request_with_retry(
                method, url, headers, params, json_data
            )
            return response
            
        except APIError as e:
            # Handle specific error types
            if e.error_type.value == "rate_limit":
                self._open_circuit_breaker(60)  # 1 minute circuit breaker
            elif e.error_type.value == "authentication":
                self._open_circuit_breaker(300)  # 5 minute circuit breaker
            raise
    
    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        
        @retry(
            stop=stop_after_attempt(self.retry_config.max_attempts),
            wait=wait_exponential(
                multiplier=self.retry_config.exponential_multiplier,
                min=self.retry_config.base_delay,
                max=self.retry_config.max_delay,
            ),
            retry=retry_if_exception_type((Timeout, ConnectionError)),
        )
        def _do_request():
            try:
                if method.upper() == "GET":
                    response = requests.get(
                        url, headers=headers, params=params, timeout=self.timeout
                    )
                elif method.upper() == "POST":
                    response = requests.post(
                        url, headers=headers, params=params, json=json_data, timeout=self.timeout
                    )
                elif method.upper() == "PUT":
                    response = requests.put(
                        url, headers=headers, params=params, json=json_data, timeout=self.timeout
                    )
                elif method.upper() == "DELETE":
                    response = requests.delete(
                        url, headers=headers, params=params, timeout=self.timeout
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check for errors
                if response.status_code >= 400:
                    error = self.handle_error_response(response)
                    raise error
                
                return response.json()
                
            except RequestException as e:
                # Convert requests exceptions to our API errors
                logger.error(f"Request failed: {e}")
                raise NetworkError(f"Network error: {str(e)}")
        
        return _do_request()
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params)
    
    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, params=params, json_data=json_data)
    
    def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, params=params, json_data=json_data)
    
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, params=params)
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limiting status."""
        now = datetime.now()
        minute_calls = len([
            call for call in self.rate_limits["minute_calls"]
            if (now - call).total_seconds() < 60
        ])
        
        return {
            "minute_calls": minute_calls,
            "max_calls_per_minute": self.rate_limit_config.max_calls_per_minute,
            "circuit_breaker_open": self.rate_limits["circuit_breaker_open"],
            "circuit_breaker_until": self.rate_limits["circuit_breaker_until"],
        }


def create_qbo_rate_limit_config() -> RateLimitConfig:
    """
    Create QBO-specific rate limit configuration.
    
    QBO Rate Limits:
    - Sandbox: 30 requests per minute per realm
    - Production: 500 requests per minute per realm
    - Burst: Short bursts allowed but triggers throttling
    - 429 Response: Includes Retry-After header
    """
    return RateLimitConfig(
        min_interval_seconds=0.5,  # 2 calls per second max
        max_calls_per_minute=30,   # QBO sandbox limit
        burst_limit=10,            # Allow short bursts
        backoff_multiplier=2.0,
        max_retries=3,
    )


def create_qbo_retry_config() -> RetryConfig:
    """Create QBO-specific retry configuration."""
    return RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=30.0,
        exponential_multiplier=2.0,
    )

