"""
Infrastructure Utilities

Common utilities for validation, error handling, and enums across the MVP infrastructure.
"""

from .validation import (
    ValidationSeverity,
    ValidationResult,
    ValidationRule,
    DataValidator,
    BusinessDataValidator,
    FinancialDataValidator,
    validate_business_data,
    validate_financial_data,
    validate_user_input,
)
from .error_handling import (
    ErrorContext,
    handle_integration_errors,
    handle_database_errors,
    retry_with_backoff,
    safe_execute,
    ErrorHandler,
)
from .enums import (
    SyncStrategy,
    SyncPriority,
    BulkSyncStrategy,
    JobStatus,
    JobPriority,
)

__all__ = [
    # Validation
    "ValidationSeverity",
    "ValidationResult",
    "ValidationRule",
    "DataValidator",
    "BusinessDataValidator",
    "FinancialDataValidator",
    "validate_business_data",
    "validate_financial_data",
    "validate_user_input",
    # Error handling
    "ErrorContext",
    "handle_integration_errors",
    "handle_database_errors",
    "retry_with_backoff",
    "safe_execute",
    "ErrorHandler",
    # Enums
    "SyncStrategy",
    "SyncPriority",
    "BulkSyncStrategy",
    "JobStatus",
    "JobPriority",
]

