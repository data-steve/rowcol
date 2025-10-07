"""
Rail-Specific Configuration Settings

This module contains configuration settings specific to different integration rails
(QBO, Ramp, Plaid, Stripe). Separated from core_thresholds.py to maintain clear
separation between product thresholds and integration-specific settings.

Architecture follows ADR-005: Rail-specific settings belong in dedicated config classes,
not mixed with product thresholds.
"""

import os
from typing import Dict, Any, Optional
from enum import Enum

class QBOEnvironment(Enum):
    """QBO API environments."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"

class QBOSettings:
    """QuickBooks Online integration settings."""
    
    def __init__(self):
        # Environment configuration
        self.environment = os.getenv("QBO_ENVIRONMENT", "sandbox")
        self.base_url = self._get_base_url()
        
        # API configuration
        self.token_refresh_buffer_minutes = int(os.getenv("QBO_TOKEN_REFRESH_BUFFER_MINUTES", "5"))
        self.max_api_retries = int(os.getenv("QBO_MAX_API_RETRIES", "3"))
        self.api_timeout_seconds = int(os.getenv("QBO_API_TIMEOUT_SECONDS", "30"))
        self.rate_limit_delay_seconds = int(os.getenv("QBO_RATE_LIMIT_DELAY_SECONDS", "1"))
        
        # OAuth configuration
        self.client_id = os.getenv("QBO_CLIENT_ID")
        self.client_secret = os.getenv("QBO_CLIENT_SECRET")
        self.redirect_uri = os.getenv("QBO_REDIRECT_URI")
        self.scope = os.getenv("QBO_SCOPE", "com.intuit.quickbooks.accounting")
        
        # Sync configuration
        self.sync_batch_size = int(os.getenv("QBO_SYNC_BATCH_SIZE", "100"))
        self.sync_retry_attempts = int(os.getenv("QBO_SYNC_RETRY_ATTEMPTS", "3"))
        self.sync_retry_delay_seconds = int(os.getenv("QBO_SYNC_RETRY_DELAY_SECONDS", "5"))
        
        # Feature flags
        self.enable_payment_sync = os.getenv("QBO_ENABLE_PAYMENT_SYNC", "true").lower() == "true"
        self.enable_bill_sync = os.getenv("QBO_ENABLE_BILL_SYNC", "true").lower() == "true"
        self.enable_invoice_sync = os.getenv("QBO_ENABLE_INVOICE_SYNC", "true").lower() == "true"
        self.enable_customer_sync = os.getenv("QBO_ENABLE_CUSTOMER_SYNC", "true").lower() == "true"
        self.enable_vendor_sync = os.getenv("QBO_ENABLE_VENDOR_SYNC", "true").lower() == "true"
    
    def _get_base_url(self) -> str:
        """Get QBO API base URL based on environment."""
        if self.environment == "production":
            return "https://quickbooks.intuit.com"
        else:
            return "https://sandbox-quickbooks.intuit.com"
    
    def get_auth_url(self, state: str) -> str:
        """Generate OAuth authorization URL."""
        return (
            f"{self.base_url}/oauth2/v1/authorize"
            f"?client_id={self.client_id}"
            f"&scope={self.scope}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&state={state}"
        )
    
    def get_token_url(self) -> str:
        """Get OAuth token URL."""
        return f"{self.base_url}/oauth2/v1/tokens"
    
    def get_api_url(self, company_id: str) -> str:
        """Get API base URL for specific company."""
        return f"{self.base_url}/v3/company/{company_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for debugging/logging."""
        return {
            "environment": self.environment,
            "base_url": self.base_url,
            "token_refresh_buffer_minutes": self.token_refresh_buffer_minutes,
            "max_api_retries": self.max_api_retries,
            "api_timeout_seconds": self.api_timeout_seconds,
            "rate_limit_delay_seconds": self.rate_limit_delay_seconds,
            "sync_batch_size": self.sync_batch_size,
            "sync_retry_attempts": self.sync_retry_attempts,
            "sync_retry_delay_seconds": self.sync_retry_delay_seconds,
            "enable_payment_sync": self.enable_payment_sync,
            "enable_bill_sync": self.enable_bill_sync,
            "enable_invoice_sync": self.enable_invoice_sync,
            "enable_customer_sync": self.enable_customer_sync,
            "enable_vendor_sync": self.enable_vendor_sync
        }

class RampSettings:
    """Ramp integration settings."""
    
    def __init__(self):
        # API configuration
        self.api_key = os.getenv("RAMP_API_KEY")
        self.base_url = os.getenv("RAMP_BASE_URL", "https://api.ramp.com/v1")
        self.webhook_secret = os.getenv("RAMP_WEBHOOK_SECRET")
        
        # API limits
        self.max_api_retries = int(os.getenv("RAMP_MAX_API_RETRIES", "3"))
        self.api_timeout_seconds = int(os.getenv("RAMP_API_TIMEOUT_SECONDS", "30"))
        self.rate_limit_delay_seconds = int(os.getenv("RAMP_RATE_LIMIT_DELAY_SECONDS", "1"))
        
        # Payment configuration
        self.default_payment_method = os.getenv("RAMP_DEFAULT_PAYMENT_METHOD", "ach")
        self.payment_approval_required = os.getenv("RAMP_PAYMENT_APPROVAL_REQUIRED", "true").lower() == "true"
        self.max_payment_amount = float(os.getenv("RAMP_MAX_PAYMENT_AMOUNT", "10000.00"))
        
        # Sync configuration
        self.sync_batch_size = int(os.getenv("RAMP_SYNC_BATCH_SIZE", "50"))
        self.sync_retry_attempts = int(os.getenv("RAMP_SYNC_RETRY_ATTEMPTS", "3"))
        self.sync_retry_delay_seconds = int(os.getenv("RAMP_SYNC_RETRY_DELAY_SECONDS", "5"))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for debugging/logging."""
        return {
            "base_url": self.base_url,
            "max_api_retries": self.max_api_retries,
            "api_timeout_seconds": self.api_timeout_seconds,
            "rate_limit_delay_seconds": self.rate_limit_delay_seconds,
            "default_payment_method": self.default_payment_method,
            "payment_approval_required": self.payment_approval_required,
            "max_payment_amount": self.max_payment_amount,
            "sync_batch_size": self.sync_batch_size,
            "sync_retry_attempts": self.sync_retry_attempts,
            "sync_retry_delay_seconds": self.sync_retry_delay_seconds
        }

class PlaidSettings:
    """Plaid integration settings."""
    
    def __init__(self):
        # API configuration
        self.client_id = os.getenv("PLAID_CLIENT_ID")
        self.secret = os.getenv("PLAID_SECRET")
        self.environment = os.getenv("PLAID_ENVIRONMENT", "sandbox")
        self.base_url = self._get_base_url()
        
        # API limits
        self.max_api_retries = int(os.getenv("PLAID_MAX_API_RETRIES", "3"))
        self.api_timeout_seconds = int(os.getenv("PLAID_API_TIMEOUT_SECONDS", "30"))
        self.rate_limit_delay_seconds = int(os.getenv("PLAID_RATE_LIMIT_DELAY_SECONDS", "1"))
        
        # Sync configuration
        self.sync_batch_size = int(os.getenv("PLAID_SYNC_BATCH_SIZE", "100"))
        self.sync_retry_attempts = int(os.getenv("PLAID_SYNC_RETRY_ATTEMPTS", "3"))
        self.sync_retry_delay_seconds = int(os.getenv("PLAID_SYNC_RETRY_DELAY_SECONDS", "5"))
    
    def _get_base_url(self) -> str:
        """Get Plaid API base URL based on environment."""
        if self.environment == "production":
            return "https://production.plaid.com"
        elif self.environment == "development":
            return "https://development.plaid.com"
        else:
            return "https://sandbox.plaid.com"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for debugging/logging."""
        return {
            "environment": self.environment,
            "base_url": self.base_url,
            "max_api_retries": self.max_api_retries,
            "api_timeout_seconds": self.api_timeout_seconds,
            "rate_limit_delay_seconds": self.rate_limit_delay_seconds,
            "sync_batch_size": self.sync_batch_size,
            "sync_retry_attempts": self.sync_retry_attempts,
            "sync_retry_delay_seconds": self.sync_retry_delay_seconds
        }

class StripeSettings:
    """Stripe integration settings."""
    
    def __init__(self):
        # API configuration
        self.secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.base_url = "https://api.stripe.com/v1"
        
        # API limits
        self.max_api_retries = int(os.getenv("STRIPE_MAX_API_RETRIES", "3"))
        self.api_timeout_seconds = int(os.getenv("STRIPE_API_TIMEOUT_SECONDS", "30"))
        self.rate_limit_delay_seconds = int(os.getenv("STRIPE_RATE_LIMIT_DELAY_SECONDS", "1"))
        
        # Payment configuration
        self.default_currency = os.getenv("STRIPE_DEFAULT_CURRENCY", "usd")
        self.payment_method_types = os.getenv("STRIPE_PAYMENT_METHOD_TYPES", "card,ach").split(",")
        self.max_payment_amount = float(os.getenv("STRIPE_MAX_PAYMENT_AMOUNT", "10000.00"))
        
        # Sync configuration
        self.sync_batch_size = int(os.getenv("STRIPE_SYNC_BATCH_SIZE", "100"))
        self.sync_retry_attempts = int(os.getenv("STRIPE_SYNC_RETRY_ATTEMPTS", "3"))
        self.sync_retry_delay_seconds = int(os.getenv("STRIPE_SYNC_RETRY_DELAY_SECONDS", "5"))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for debugging/logging."""
        return {
            "base_url": self.base_url,
            "max_api_retries": self.max_api_retries,
            "api_timeout_seconds": self.api_timeout_seconds,
            "rate_limit_delay_seconds": self.rate_limit_delay_seconds,
            "default_currency": self.default_currency,
            "payment_method_types": self.payment_method_types,
            "max_payment_amount": self.max_payment_amount,
            "sync_batch_size": self.sync_batch_size,
            "sync_retry_attempts": self.sync_retry_attempts,
            "sync_retry_delay_seconds": self.sync_retry_delay_seconds
        }

# Global rail configuration instances
qbo_settings = QBOSettings()
ramp_settings = RampSettings()
plaid_settings = PlaidSettings()
stripe_settings = StripeSettings()
