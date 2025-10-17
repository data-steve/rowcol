"""
Raw QBO HTTP Client

Production-grade QBO client with rate limiting, retry logic, and error handling.
Extends BaseAPIClient with QBO-specific patterns.
"""

import logging
from typing import Dict
import requests

from infra.api.base_client import (
    BaseAPIClient,
    create_qbo_rate_limit_config,
    create_qbo_retry_config,
)
from infra.api.exceptions import (
    APIError,
    RateLimitError,
    AuthenticationError,
    ServerError,
)
from .config import qbo_config
from .auth import QBOAuthService

logger = logging.getLogger(__name__)


class QBORawClient(BaseAPIClient):
    """Production-grade QBO HTTP client with rate limiting and retry logic."""
    
    def __init__(self, business_id: str, realm_id: str):
        # Initialize with QBO-specific rate limiting and retry configs
        super().__init__(
            rate_limit_config=create_qbo_rate_limit_config(),
            retry_config=create_qbo_retry_config(),
        )
        
        self.business_id = business_id
        self.realm_id = realm_id
        self.base_url = f"{qbo_config.api_base_url}/{realm_id}"
        
        # Get auth service for token management
        self.auth_service = QBOAuthService(business_id) if business_id else None
        
        logger.info(f"Initialized QBORawClient for business {business_id}, realm {realm_id}")
    
    def get_base_url(self) -> str:
        """Get the base URL for QBO API."""
        return self.base_url
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for QBO API requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        # Get access token if auth service is available
        if self.auth_service:
            try:
                access_token = self.auth_service.get_valid_access_token()
                if access_token:
                    headers["Authorization"] = f"Bearer {access_token}"
                    logger.debug("Using access token for QBO API request")
                else:
                    logger.warning(f"No valid access token for business {self.business_id}")
            except Exception as e:
                logger.error(f"Failed to get access token: {e}")
        else:
            logger.warning("No auth service available - requests will fail")
        
        return headers
    
    def handle_error_response(self, response: requests.Response) -> APIError:
        """Handle QBO-specific error responses."""
        status_code = response.status_code
        
        try:
            error_data = response.json()
            fault = error_data.get("Fault", {})
            errors = fault.get("Error", [])
            error_type = fault.get("type", "Unknown")
            
            if errors:
                error_msg = errors[0].get("Message", "Unknown QBO error")
                error_detail = errors[0].get("Detail", "")
                error_code = errors[0].get("code", "")
            else:
                error_msg = f"QBO API error: {error_type}"
                error_detail = ""
                error_code = ""
            
            # Log the full error for debugging
            logger.error(
                f"QBO API error: {error_msg} (code: {error_code}, type: {error_type})"
            )
            if error_detail:
                logger.debug(f"Error detail: {error_detail}")
        
        except Exception as e:
            # If we can't parse the error, use generic message
            logger.error(f"Failed to parse QBO error response: {e}")
            error_msg = f"QBO API error: {response.text}"
            error_type = "Unknown"
        
        # Convert to appropriate error type
        if status_code == 401:
            return AuthenticationError(error_msg, status_code)
        elif status_code == 429:
            # QBO rate limit - extract retry-after header
            retry_after = int(response.headers.get("Retry-After", 60))
            return RateLimitError(error_msg, retry_after)
        elif status_code >= 500:
            return ServerError(error_msg, status_code)
        else:
            return APIError(error_msg, status_code=status_code)