"""
Infrastructure Configuration for MVP

This module provides configuration utilities and exception classes for the MVP.
"""

from .exceptions import (
    OodalooBaseException,
    BusinessError,
    BusinessNotFoundError,
    UserError,
    UserNotFoundError,
    AuthenticationError,
    AuthorizationError,
    IntegrationError,
    QBOIntegrationError,
    EmailDeliveryError,
    TrayError,
    TrayItemNotFoundError,
    RunwayCalculationError,
    OnboardingError,
    ValidationError,
    ConfigurationError,
    DataIngestionError,
    TenantAccessError,
    QBOSyncError,
    BusinessRuleViolationError,
)

__all__ = [
    "OodalooBaseException",
    "BusinessError",
    "BusinessNotFoundError", 
    "UserError",
    "UserNotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "IntegrationError",
    "QBOIntegrationError",
    "EmailDeliveryError",
    "TrayError",
    "TrayItemNotFoundError",
    "RunwayCalculationError",
    "OnboardingError",
    "ValidationError",
    "ConfigurationError",
    "DataIngestionError",
    "TenantAccessError",
    "QBOSyncError",
    "BusinessRuleViolationError",
]
