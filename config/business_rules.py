"""Business rules and constants for Oodaloo application."""

class RunwayThresholds:
    """Runway calculation thresholds in days."""
    CRITICAL_DAYS = 7      # Less than 1 week = critical alert
    WARNING_DAYS = 30      # Less than 1 month = warning alert  
    HEALTHY_DAYS = 90      # More than 3 months = healthy status
    
class TrayPriorities:
    """Tray item priority scoring thresholds."""
    URGENT_SCORE = 80      # Requires immediate attention (same day)
    MEDIUM_SCORE = 60      # Should be handled today
    LOW_SCORE = 40         # Can wait until tomorrow
    
    # Priority weights for different tray item types
    TYPE_WEIGHTS = {
        "overdue_bill": 35,
        "upcoming_payroll": 40,
        "overdue_invoice": 30,
        "bank_reconciliation": 25,
        "vendor_duplicate": 15,
        "missing_receipt": 10
    }

class DigestSettings:
    """Settings for weekly digest generation."""
    DEFAULT_BURN_RATE_MONTHLY = 10000.0  # Default monthly burn rate in dollars
    LOOKBACK_DAYS = 90                    # Days to look back for historical data
    FORECAST_DAYS = 30                    # Days to forecast ahead
    
class EmailSettings:
    """Email delivery settings."""
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 5
    TIMEOUT_SECONDS = 30
    
class QBOSettings:
    """QuickBooks Online integration settings."""
    TOKEN_REFRESH_BUFFER_MINUTES = 5     # Refresh token 5 minutes before expiry
    MAX_API_RETRIES = 3
    API_TIMEOUT_SECONDS = 30
    RATE_LIMIT_DELAY_SECONDS = 1
    
class OnboardingSettings:
    """Onboarding process settings."""
    OAUTH_STATE_EXPIRY_HOURS = 1         # OAuth state expires after 1 hour
    REQUIRED_BUSINESS_FIELDS = [
        "name", 
        "industry", 
        "employee_count"
    ]
    REQUIRED_USER_FIELDS = [
        "email", 
        "password_hash", 
        "full_name"
    ]

class TrayItemTypes:
    """Standard tray item types."""
    OVERDUE_BILL = "overdue_bill"
    UPCOMING_PAYROLL = "upcoming_payroll"
    OVERDUE_INVOICE = "overdue_invoice"
    BANK_RECONCILIATION = "bank_reconciliation"
    VENDOR_DUPLICATE = "vendor_duplicate"
    MISSING_RECEIPT = "missing_receipt"
    
class TrayItemStatuses:
    """Standard tray item statuses."""
    PENDING = "pending"
    RESOLVED = "resolved"
    SCHEDULED = "scheduled"
    REQUIRES_ATTENTION = "requires_attention"

class BusinessStatuses:
    """Business account statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ONBOARDING = "onboarding"

class IntegrationStatuses:
    """Integration connection statuses."""
    NOT_STARTED = "not_started"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"
    EXPIRED = "expired"

class DocumentSettings:
    """Settings for document processing."""
    DEFAULT_DOCUMENT_TYPE = "invoice"
    DEFAULT_DOCUMENT_STATUS = "pending"
    DEFAULT_REVIEW_STATUS = "pending"
    SUPPORTED_CSV_ENCODINGS = ["utf-8", "latin-1", "cp1252"]
    
    @staticmethod
    def get_current_period() -> str:
        """Get current period in YYYY-MM format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m")

class AdjustmentSettings:
    """Settings for credit memos and adjustments."""
    REVIEW_THRESHOLD_AMOUNT = 1000.0  # Credit memos above this amount require manual review
