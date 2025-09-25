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
        "industry"
    ]
    REQUIRED_USER_FIELDS = [
        "email", 
        "full_name",
        "password_hash"
    ]

class RunwayAnalysisSettings:
    """Settings for runway replay and analysis calculations."""
    # AP (Accounts Payable) optimization factors
    AP_OPTIMIZATION_EFFICIENCY = 0.1      # 10% of overdue AP can be optimized for runway protection
    AP_CRITICAL_THRESHOLD = 0.2           # AP > 20% of cash triggers critical issue
    
    # AR (Accounts Receivable) collection factors  
    AR_COLLECTION_EFFICIENCY = 0.3        # 30% collection efficiency for overdue AR
    AR_SIGNIFICANT_THRESHOLD = 10000       # AR amounts above $10k considered significant
    
    # Runway calculation defaults
    DEFAULT_DAILY_BURN_RATE = 1000        # $1000/day fallback burn rate estimate
    RUNWAY_CRITICAL_DAYS = 30             # Runway below 30 days triggers critical alert
    
    # Default financial values for development/fallback (when QBO data unavailable)
    DEFAULT_CASH_BALANCE = 100000         # $100k default cash balance
    DEFAULT_MONTHLY_REVENUE = 25000       # $25k default monthly revenue
    DEFAULT_MONTHLY_EXPENSES = 15000      # $15k default monthly expenses
    DEFAULT_EMPLOYEE_COUNT = 5            # 5 employees default
    
    # Hygiene score impact factors
    HYGIENE_BILL_DUE_DATE_IMPACT = 0.5    # 0.5 days runway impact per bill missing due date
    HYGIENE_UNCATEGORIZED_IMPACT = 0.2    # 0.2 days runway impact per uncategorized transaction
    HYGIENE_LARGE_INVOICE_IMPACT = 1.0    # 1.0 days runway impact per large unpaid invoice
    HYGIENE_VENDOR_TERMS_IMPACT = 0.3     # 0.3 days runway impact per vendor missing payment terms
    HYGIENE_LARGE_INVOICE_THRESHOLD = 5000 # Invoices above $5k considered "large"
    
    # Hygiene scoring
    HYGIENE_MAX_ISSUES = 5                # Maximum number of issue types we check
    HYGIENE_POINTS_PER_ISSUE = 20         # Lose 20 points per issue type found
    HYGIENE_OVERDUE_INVOICE_THRESHOLD = 5 # More than 5 overdue invoices = high severity

class ProofOfValueThresholds:
    """Thresholds for test drive proof statements and marketing language."""
    SIGNIFICANT_RUNWAY_PROTECTION = 10    # 10+ days = significant protection achieved
    MANY_INSIGHTS_THRESHOLD = 5           # 5+ insights = substantial analysis value

# RunwayThresholds class moved to business_rules.py to avoid duplication

class DataQualityThresholds:
    """
    Domain-specific thresholds for different types of data quality analysis.
    
    These thresholds are based on industry standards and business impact:
    - Hygiene Score: Subjective business assessment, 80% is reasonable for "excellent"
    - Data Consistency: Critical for system integrity, requires 95% for "excellent"  
    - Data Completeness: Missing data impacts accuracy, requires 90% for "excellent"
    """
    
    # Hygiene Score thresholds (business assessment of QBO data quality)
    HYGIENE_EXCELLENT = 80                # 80+ = excellent (most issues resolved)
    HYGIENE_GOOD = 60                     # 60-79 = good (minor issues remain)  
    HYGIENE_FAIR = 40                     # 40-59 = fair (several issues)
    # Below 40 = needs_attention (significant data quality problems)
    
    # Data Consistency thresholds (referential integrity, entity matching)
    CONSISTENCY_EXCELLENT = 95            # 95+ = excellent (high data integrity)
    CONSISTENCY_GOOD = 85                 # 85-94 = good (minor inconsistencies)
    CONSISTENCY_FAIR = 70                 # 70-84 = fair (some data mismatches)
    # Below 70 = needs_attention (significant integrity issues)
    
    # Data Completeness thresholds (required fields populated)
    COMPLETENESS_EXCELLENT = 90           # 90+ = excellent (comprehensive data)
    COMPLETENESS_GOOD = 75                # 75-89 = good (most fields complete)
    COMPLETENESS_FAIR = 60                # 60-74 = fair (key fields missing)
    # Below 60 = needs_attention (insufficient data for analysis)

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
