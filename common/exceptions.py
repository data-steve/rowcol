"""Custom exception classes for Oodaloo application."""

class OodalooBaseException(Exception):
    """Base exception class for all Oodaloo-specific exceptions."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class BusinessError(OodalooBaseException):
    """Raised when business logic validation fails."""
    pass

class BusinessNotFoundError(BusinessError):
    """Raised when a business cannot be found."""
    pass

class UserError(OodalooBaseException):
    """Raised when user operations fail."""
    pass

class UserNotFoundError(UserError):
    """Raised when a user cannot be found."""
    pass

class AuthenticationError(OodalooBaseException):
    """Raised when authentication fails."""
    pass

class AuthorizationError(OodalooBaseException):
    """Raised when user lacks permission for an operation."""
    pass

class IntegrationError(OodalooBaseException):
    """Raised when external integration fails."""
    pass

class QBOIntegrationError(IntegrationError):
    """Raised when QuickBooks Online integration fails."""
    pass

class EmailDeliveryError(IntegrationError):
    """Raised when email delivery fails."""
    pass

class TrayError(OodalooBaseException):
    """Raised when tray operations fail."""
    pass

class TrayItemNotFoundError(TrayError):
    """Raised when a tray item cannot be found."""
    pass

class RunwayCalculationError(BusinessError):
    """Raised when runway calculation fails."""
    pass

class OnboardingError(OodalooBaseException):
    """Raised when onboarding process fails."""
    pass

class ValidationError(OodalooBaseException):
    """Raised when data validation fails."""
    pass

class ConfigurationError(OodalooBaseException):
    """Raised when application configuration is invalid."""
    pass

class DataIngestionError(OodalooBaseException):
    """Raised when data ingestion fails."""
    pass
