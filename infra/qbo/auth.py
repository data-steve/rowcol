"""
QBO Authentication Service - Simplified Version

This service provides QBO authentication functionality without database dependencies
to avoid circular imports.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import secrets
import os
from enum import Enum
import time
import json

from common.exceptions import IntegrationError
from .config import qbo_config
from .dtos import QBOIntegrationDTO, QBOIntegrationStatuses

logger = logging.getLogger(__name__)

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'dev_tokens.json')


class QBOEnvironment(Enum):
    """QBO environment types."""
    MOCK = "mock"
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class QBOAuthService:
    """
    QBO authentication service that doesn't depend on domain models.
    
    This service provides QBO OAuth functionality without database dependencies
    to avoid circular imports.
    """
    
    def __init__(self, business_id: str, environment: QBOEnvironment = QBOEnvironment.MOCK):
        self.business_id = business_id
        self.environment = environment
        self.logger = logging.getLogger(f"{__name__}.{business_id}")
        
        logger.info(f"Initialized QBOAuthService for business {business_id}, environment {environment.value}")
    
    def initiate_oauth_flow(self, user_id: str) -> Dict[str, Any]:
        """
        Initiate QBO OAuth flow and return authorization URL.
        
        Args:
            user_id: ID of the user initiating the flow
            
        Returns:
            Dict containing authorization URL and state
        """
        try:
            # Generate OAuth state for security
            state = secrets.token_urlsafe(32)
            
            if self.environment == QBOEnvironment.MOCK:
                auth_url = self._generate_mock_auth_url(state)
            else:
                auth_url = self._generate_real_auth_url(state)
            
            return {
                "auth_url": auth_url,
                "state": state,
                "business_id": self.business_id,
                "environment": self.environment.value
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initiate QBO OAuth flow: {e}", exc_info=True)
            raise IntegrationError("Failed to initiate QBO connection", {"error": str(e)})
    
    def _generate_mock_auth_url(self, state: str) -> str:
        """Generate mock auth URL for development/testing."""
        base_url = qbo_config.api_base_url.replace('/v3/company', '')
        return f"{base_url}/oauth2/v1/authorize?client_id={qbo_config.client_id}&scope=com.intuit.quickbooks.accounting&redirect_uri={qbo_config.redirect_uri}&response_type=code&state={state}"
    
    def _generate_real_auth_url(self, state: str) -> str:
        """Generate real QBO auth URL using Intuit SDK."""
        try:
            from intuitlib.client import AuthClient
            from intuitlib.enums import Scopes
            
            auth_client = AuthClient(
                client_id=qbo_config.client_id,
                client_secret=qbo_config.client_secret,
                environment=qbo_config.environment,
                redirect_uri=qbo_config.redirect_uri
            )
            
            return auth_client.get_authorization_url([Scopes.ACCOUNTING], state)
            
        except ImportError:
            self.logger.error("Intuit SDK not available for real QBO auth")
            raise IntegrationError("QBO SDK not available", {"error": "Intuit SDK not installed"})
        except Exception as e:
            self.logger.error(f"Failed to generate real QBO auth URL: {e}")
            raise IntegrationError("Failed to generate QBO auth URL", {"error": str(e)})
    
    def complete_oauth_flow(self, state: str, authorization_code: str, realm_id: str) -> Dict[str, Any]:
        """
        Complete OAuth flow by exchanging authorization code for access token.
        
        Args:
            state: OAuth state parameter
            authorization_code: Authorization code from QBO
            realm_id: QBO company ID
            
        Returns:
            Dict containing access token and connection details
        """
        try:
            # Exchange code for tokens
            if self.environment == QBOEnvironment.MOCK:
                access_token, refresh_token = self._exchange_mock_tokens(authorization_code)
            else:
                access_token, refresh_token = self._exchange_real_tokens(authorization_code)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "realm_id": realm_id,
                "business_id": self.business_id,
                "status": QBOIntegrationStatuses.CONNECTED,
                "connected_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to complete QBO OAuth flow: {e}", exc_info=True)
            raise IntegrationError("Failed to complete QBO connection", {"error": str(e)})
    
    def _exchange_mock_tokens(self, authorization_code: str) -> Tuple[str, str]:
        """Exchange authorization code for mock tokens."""
        self.logger.info("Exchanging mock QBO tokens")
        
        # Generate mock tokens
        access_token = f"mock_access_token_{int(time.time())}"
        refresh_token = f"mock_refresh_token_{int(time.time())}"
        
        return access_token, refresh_token
    
    def _exchange_real_tokens(self, authorization_code: str) -> Tuple[str, str]:
        """Exchange authorization code for real QBO tokens."""
        try:
            from intuitlib.client import AuthClient
            
            auth_client = AuthClient(
                client_id=qbo_config.client_id,
                client_secret=qbo_config.client_secret,
                environment=qbo_config.environment,
                redirect_uri=qbo_config.redirect_uri
            )
            
            auth_client.get_bearer_token(authorization_code)
            
            return auth_client.access_token, auth_client.refresh_token
            
        except ImportError:
            self.logger.error("Intuit SDK not available for real QBO token exchange")
            raise IntegrationError("QBO SDK not available", {"error": "Intuit SDK not installed"})
        except Exception as e:
            self.logger.error(f"Failed to exchange real QBO tokens: {e}")
            raise IntegrationError("Failed to exchange QBO tokens", {"error": str(e)})
    
    def get_valid_access_token(self) -> Optional[str]:
        """
        Get valid access token for QBO API calls.
        
        Returns:
            Valid access token or None if not available
        """
        try:
            # For now, return None - this would need to be implemented
            # with proper token storage and refresh logic
            self.logger.warning("get_valid_access_token not fully implemented in simplified version")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get valid access token: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if business has valid QBO connection."""
        try:
            # For now, return False - this would need to be implemented
            # with proper connection status checking
            self.logger.warning("is_connected not fully implemented in simplified version")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check connection status: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect QBO integration."""
        try:
            # For now, return True - this would need to be implemented
            # with proper disconnection logic
            self.logger.warning("disconnect not fully implemented in simplified version")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect QBO: {e}")
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status."""
        try:
            return {
                "connected": self.is_connected(),
                "status": QBOIntegrationStatuses.DISCONNECTED,
                "platform": "qbo",
                "business_id": self.business_id,
                "environment": self.environment.value,
                "message": "Simplified auth service - full implementation needed"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get connection status: {e}")
            return {
                "connected": False,
                "status": QBOIntegrationStatuses.ERROR,
                "platform": "qbo",
                "business_id": self.business_id,
                "error": str(e)
            }