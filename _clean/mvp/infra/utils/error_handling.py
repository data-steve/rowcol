"""
Error Handling Utilities - Centralized Error Management

Provides decorators and utilities for consistent error handling across
infrastructure services, eliminating duplicated try/except patterns.

Key Patterns:
- API call error handling
- Database operation error handling  
- External service error handling
- Retry logic with exponential backoff
"""

import logging
import functools
from typing import Callable, Any, Optional, Type, List
from enum import Enum

from infra.config.exceptions import IntegrationError, ValidationError

logger = logging.getLogger(__name__)


class ErrorContext(Enum):
    """Context for error handling."""
    API_CALL = "api_call"
    DATABASE_OPERATION = "database_operation"
    EXTERNAL_SERVICE = "external_service"
    FILE_OPERATION = "file_operation"
    NETWORK_OPERATION = "network_operation"


def handle_integration_errors(
    context: ErrorContext = ErrorContext.API_CALL,
    reraise: bool = True,
    default_return: Any = None,
    log_errors: bool = True
):
    """
    Decorator for handling integration errors consistently.
    
    Args:
        context: The type of operation being performed
        reraise: Whether to reraise the exception after logging
        default_return: Value to return if error is caught and not reraised
        log_errors: Whether to log errors
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except IntegrationError as e:
                if log_errors:
                    logger.error(f"{context.value} failed in {func.__name__}: {e}")
                if reraise:
                    raise
                return default_return
            except ValidationError as e:
                if log_errors:
                    logger.error(f"Validation error in {func.__name__}: {e}")
                if reraise:
                    raise
                return default_return
            except Exception as e:
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                if reraise:
                    raise IntegrationError(f"{context.value} failed: {str(e)}")
                return default_return
        return wrapper
    return decorator


def handle_database_errors(
    reraise: bool = True,
    default_return: Any = None,
    log_errors: bool = True
):
    """
    Decorator for handling database operation errors.
    
    Args:
        reraise: Whether to reraise the exception after logging
        default_return: Value to return if error is caught and not reraised
        log_errors: Whether to log errors
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Database operation failed in {func.__name__}: {e}")
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_on: Optional[List[Type[Exception]]] = None
):
    """
    Decorator for retrying operations with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        retry_on: List of exception types to retry on (default: all exceptions)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import random
            import time
            
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this exception
                    if retry_on and not any(isinstance(e, exc_type) for exc_type in retry_on):
                        raise
                    
                    # Don't retry on the last attempt
                    if attempt == max_attempts - 1:
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed in {func.__name__}: {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)
            
            # If we get here, all retries failed
            logger.error(f"All {max_attempts} attempts failed in {func.__name__}")
            raise last_exception
            
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    *args,
    context: ErrorContext = ErrorContext.API_CALL,
    default_return: Any = None,
    log_errors: bool = True,
    **kwargs
) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        context: Context for error logging
        default_return: Value to return if error occurs
        log_errors: Whether to log errors
        **kwargs: Keyword arguments for the function
    
    Returns:
        Function result or default_return if error occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"{context.value} failed in {func.__name__}: {e}")
        return default_return


class ErrorHandler:
    """Context manager for error handling."""
    
    def __init__(
        self,
        context: ErrorContext = ErrorContext.API_CALL,
        reraise: bool = True,
        default_return: Any = None,
        log_errors: bool = True
    ):
        self.context = context
        self.reraise = reraise
        self.default_return = default_return
        self.log_errors = log_errors
        self.error_occurred = False
        self.last_error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_occurred = True
            self.last_error = exc_val
            
            if self.log_errors:
                logger.error(f"{self.context.value} failed: {exc_val}")
            
            if not self.reraise:
                return True  # Suppress the exception
        
        return False  # Don't suppress the exception



