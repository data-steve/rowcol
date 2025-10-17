"""
QBO Integration Configuration

Centralized configuration for QBO URLs and settings.
"""
import os


class QBOConfig:
    """QBO configuration."""
    
    def __init__(self):
        self.environment = os.getenv("QBO_ENVIRONMENT", "sandbox")
        
        # Client credentials
        self.client_id = os.getenv("QBO_CLIENT_ID")
        self.client_secret = os.getenv("QBO_CLIENT_SECRET")
        
        # Base URLs
        self.base_url = os.getenv("BASE_URL", "http://localhost:8001")
        
        # QBO API URLs
        self.production_api_url = "https://quickbooks.api.intuit.com/v3/company"
        self.sandbox_api_url = "https://sandbox-quickbooks.api.intuit.com/v3/company"
        
        # OAuth URLs
        self.oauth_base_url = "https://oauth.platform.intuit.com/oauth2/v1"
        self.token_url = f"{self.oauth_base_url}/tokens/bearer"
        
        # Redirect URI
        self.redirect_uri = os.getenv("QBO_REDIRECT_URI", f"{self.base_url}/callback")
    
    @property
    def api_base_url(self) -> str:
        """Get the appropriate QBO API base URL based on environment."""
        if self.environment == "production":
            return self.production_api_url
        else:
            return self.sandbox_api_url
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def is_sandbox(self) -> bool:
        """Check if running in sandbox mode."""
        return self.environment == "sandbox"


# Global configuration instance
qbo_config = QBOConfig()