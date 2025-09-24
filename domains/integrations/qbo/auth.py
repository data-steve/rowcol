"""
QBO Authentication Service - Centralized QBO OAuth Management

This service centralizes all QBO authentication logic, replacing the scattered
auth code in onboarding and other services.

Key Responsibilities:
- OAuth flow initiation and completion
- Token storage and management
- Automatic token refresh
- Connection status tracking
- Mock vs real environment handling
"""

from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import secrets
import os
from enum import Enum
import time
import json

from domains.core.services.base_service import TenantAwareService
from domains.core.models.integration import Integration, IntegrationStatuses
from common.exceptions import IntegrationError
from .config import qbo_config

logger = logging.getLogger(__name__)

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'dev_tokens.json')


class QBOEnvironment(Enum):
    """QBO environment types."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"
    MOCK = "mock"

class QBOAuthService(TenantAwareService):
    """
    Centralized QBO authentication service.
    
    This service handles all QBO OAuth flows, token management, and connection
    status tracking. It replaces the scattered auth logic in onboarding.
    """
    
    def __init__(self, db: Session, business_id: str, override_environment: QBOEnvironment = None):
        super().__init__(db, business_id)
        self.logger = logging.getLogger(__name__)
        
        # QBO configuration from centralized config
        self.client_id = qbo_config.client_id
        self.client_secret = qbo_config.client_secret
        self.redirect_uri = qbo_config.redirect_uri
        self.environment = override_environment or self._determine_environment()
        
        self.logger.info(f"Initialized QBOAuthService for business {business_id} in {self.environment.value} mode")
    
    def _determine_environment(self) -> QBOEnvironment:
        """Determine QBO environment based on configuration."""
        if qbo_config.is_mock_mode:
            return QBOEnvironment.MOCK
        elif qbo_config.is_production:
            return QBOEnvironment.PRODUCTION
        else:
            return QBOEnvironment.SANDBOX
    
    def initiate_oauth_flow(self, user_id: str) -> Dict[str, Any]:
        """
        Initiate QBO OAuth flow.
        
        Args:
            user_id: ID of the user initiating the connection
            
        Returns:
            Dict containing auth URL and state information
        """
        try:
            state = secrets.token_urlsafe(32)
            
            # Store OAuth state in database
            with self.db.begin():
                integration = Integration(
                    business_id=self.business_id,
                    platform="qbo",
                    status=IntegrationStatuses.CONNECTING,
                    oauth_state=state,
                    created_by=user_id
                )
                self.db.add(integration)
            
            # Generate appropriate auth URL based on environment
            if self.environment == QBOEnvironment.MOCK:
                auth_url = self._generate_mock_auth_url(state)
            else:
                auth_url = self._generate_real_auth_url(state)
            
            self.logger.info(f"Initiated QBO OAuth flow for business {self.business_id}")
            
            return {
                "auth_url": auth_url,
                "state": state,
                "expires_in": 3600,
                "environment": self.environment.value,
                "mock": self.environment == QBOEnvironment.MOCK
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initiate QBO OAuth flow: {e}", exc_info=True)
            raise IntegrationError("Failed to initiate QBO connection", {"error": str(e)})
    
    def _generate_mock_auth_url(self, state: str) -> str:
        """Generate mock auth URL for development/testing."""
        return qbo_config.get_auth_url(state, self.business_id)
    
    def _generate_real_auth_url(self, state: str) -> str:
        """Generate real QBO auth URL."""
        try:
            from intuitlib.client import AuthClient
            from intuitlib.enums import Scopes
            
            auth_client = AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                environment=self.environment.value
            )
            
            scopes = [Scopes.ACCOUNTING]
            return auth_client.get_authorization_url(scopes, state)
            
        except ImportError:
            self.logger.error("Intuit SDK not available for real QBO auth")
            raise IntegrationError("QBO SDK not available", {"error": "Intuit SDK not installed"})
        except Exception as e:
            self.logger.error(f"Failed to generate real QBO auth URL: {e}")
            raise IntegrationError("Failed to generate QBO auth URL", {"error": str(e)})
    
    def complete_oauth_flow(self, state: str, authorization_code: str, realm_id: str) -> Dict[str, Any]:
        """
        Complete QBO OAuth flow and store tokens.
        
        Args:
            state: OAuth state parameter
            authorization_code: Authorization code from QBO
            realm_id: QBO realm ID
            
        Returns:
            Dict containing connection status and business info
        """
        try:
            # Validate state parameter
            integration = self.db.query(Integration).filter(
                Integration.business_id == self.business_id,
                Integration.platform == "qbo",
                Integration.oauth_state == state
            ).first()
            
            if not integration:
                raise IntegrationError("Invalid OAuth state", {"error": "State mismatch"})
            
            # Exchange code for tokens
            if self.environment == QBOEnvironment.MOCK:
                access_token, refresh_token = self._exchange_mock_tokens(authorization_code)
            else:
                access_token, refresh_token = self._exchange_real_tokens(authorization_code)
            
            # Store tokens and update integration status
            with self.db.begin():
                integration.access_token = access_token
                integration.refresh_token = refresh_token
                integration.realm_id = realm_id
                integration.status = IntegrationStatuses.CONNECTED.value
                integration.connected_at = datetime.utcnow()
                integration.oauth_state = None  # Clear state after successful connection
            
            self.logger.info(f"Successfully completed QBO OAuth flow for business {self.business_id}")
            
            return {
                "status": "connected",
                "business_id": self.business_id,
                "realm_id": realm_id,
                "environment": self.environment.value,
                "connected_at": integration.connected_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to complete QBO OAuth flow: {e}", exc_info=True)
            raise IntegrationError("Failed to complete QBO connection", {"error": str(e)})
    
    def _exchange_mock_tokens(self, authorization_code: str) -> Tuple[str, str]:
        """Exchange authorization code for mock tokens."""
        access_token = f"mock_access_{self.business_id}_{datetime.utcnow().timestamp()}"
        refresh_token = f"mock_refresh_{self.business_id}_{datetime.utcnow().timestamp()}"
        
        self.logger.info(f"Generated mock tokens for business {self.business_id}")
        return access_token, refresh_token
    
    def _exchange_real_tokens(self, authorization_code: str) -> Tuple[str, str]:
        """Exchange authorization code for real QBO tokens."""
        try:
            from intuitlib.client import AuthClient
            
            auth_client = AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                environment=self.environment.value
            )
            
            # Exchange code for tokens
            auth_client.get_bearer_token(authorization_code, realm_id=None)
            
            return auth_client.access_token, auth_client.refresh_token
            
        except ImportError:
            self.logger.error("Intuit SDK not available for real QBO token exchange")
            raise IntegrationError("QBO SDK not available", {"error": "Intuit SDK not installed"})
        except Exception as e:
            self.logger.error(f"Failed to exchange real QBO tokens: {e}")
            raise IntegrationError("Failed to exchange QBO tokens", {"error": str(e)})
    
    def get_valid_access_token(self) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token or None if not available
        """
        try:
            integration = self.db.query(Integration).filter(
                Integration.business_id == self.business_id,
                Integration.platform == "qbo",
                Integration.status == IntegrationStatuses.CONNECTED.value
            ).first()
            
            if not integration or not integration.access_token:
                # Self-heal from dev token file
                if self._load_tokens_from_dev_file():
                    integration = self.db.query(Integration).filter(
                        Integration.business_id == self.business_id,
                        Integration.platform == "qbo",
                        Integration.status == IntegrationStatuses.CONNECTED.value
                    ).first()
                    if not integration or not integration.access_token:
                        self.logger.warning(f"No QBO integration found for business {self.business_id}")
                        return None
                else:
                    self.logger.warning(f"No QBO integration found for business {self.business_id}")
                    return None
            
            # Check if token needs refresh
            if self._token_needs_refresh(integration):
                return self._refresh_access_token(integration)
            
            return integration.access_token
            
        except Exception as e:
            self.logger.error(f"Failed to get valid access token: {e}", exc_info=True)
            return None
    
    def _load_tokens_from_dev_file(self) -> bool:
        """
        If dev_tokens.json exists, load it into the database.
        This makes the system self-healing after a database reset in local dev.
        """
        if not os.path.exists(TOKEN_FILE):
            return False

        try:
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)

            # Check if tokens are expired
            refresh_expires = datetime.fromisoformat(tokens['refresh_token_expires_at'])
            if datetime.utcnow() >= refresh_expires:
                self.logger.warning(f"Dev tokens in {TOKEN_FILE} have expired. Please run get_qbo_tokens.py.")
                os.remove(TOKEN_FILE)  # Remove expired file
                return False
            
            # Check if an integration record already exists
            integration = self.db.query(Integration).filter(
                Integration.business_id == self.business_id,
                Integration.platform == "qbo"
            ).first()

            if integration:
                # Update existing record
                integration.access_token = tokens['access_token']
                integration.refresh_token = tokens['refresh_token']
                integration.realm_id = tokens['realm_id']
                integration.token_expires_at = datetime.fromisoformat(tokens['token_expires_at'])
                integration.expires_at = refresh_expires
                integration.status = IntegrationStatuses.CONNECTED.value
                self.logger.info(f"Refreshed DB tokens from {TOKEN_FILE} for business {self.business_id}")
            else:
                # Create new integration record from the token file
                from domains.core.models.business import Business
                business = self.db.query(Business).filter(Business.business_id == self.business_id).first()
                if not business:
                    business = Business(business_id=self.business_id, name="QBO Dev Business (from token file)")
                    self.db.add(business)

                integration = Integration(
                    business_id=self.business_id,
                    platform="qbo",
                    status=IntegrationStatuses.CONNECTED.value,
                    access_token=tokens['access_token'],
                    refresh_token=tokens['refresh_token'],
                    realm_id=tokens['realm_id'],
                    token_expires_at=datetime.fromisoformat(tokens['token_expires_at']),
                    expires_at=refresh_expires
                )
                self.db.add(integration)
                self.logger.info(f"Loaded tokens from {TOKEN_FILE} into new DB record for business {self.business_id}")

            self.db.commit()
            return True

        except Exception as e:
            self.logger.error(f"Failed to load tokens from dev file '{TOKEN_FILE}': {e}", exc_info=True)
            return False
    
    def force_refresh_and_get_new_token(self) -> Optional[str]:
        """
        Forcibly refreshes the access token, even if it hasn't expired,
        and returns the new one.
        """
        try:
            integration = self.db.query(Integration).filter(
                Integration.business_id == self.business_id,
                Integration.platform == "qbo"
            ).first()

            if not integration:
                self.logger.warning(f"Cannot force refresh: No QBO integration found for business {self.business_id}")
                return None

            return self._refresh_access_token(integration)
        except Exception as e:
            self.logger.error(f"Failed to force refresh token: {e}", exc_info=True)
            return None
    
    def _token_needs_refresh(self, integration: Integration) -> bool:
        """Check if access token needs refresh."""
        if not integration.token_expires_at:
            return False
        
        # Refresh if token expires within 5 minutes
        return datetime.utcnow() + timedelta(minutes=5) >= integration.token_expires_at
    
    def _refresh_access_token(self, integration: Integration) -> Optional[str]:
        """Refresh access token."""
        try:
            if self.environment == QBOEnvironment.MOCK:
                return self._refresh_mock_token(integration)
            else:
                return self._refresh_real_token(integration)
                
        except Exception as e:
            self.logger.error(f"Failed to refresh access token: {e}", exc_info=True)
            return None
    
    def _refresh_mock_token(self, integration: Integration) -> str:
        """Refresh a mock token for testing."""
        self.logger.info("Refreshing mock QBO token")
        new_access_token = f"mock_access_token_{int(time.time())}"
        new_refresh_token = f"mock_refresh_token_{int(time.time())}"
        
        integration.access_token = new_access_token
        integration.refresh_token = new_refresh_token
        integration.expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Commit changes directly as the session is already in a transaction
        # from the test fixture. Using 'begin()' would create a nested
        # transaction that causes errors with SQLite in tests.
        self.db.add(integration)
        self.db.commit()
        
        return new_access_token
    
    def _refresh_real_token(self, integration: Integration) -> str:
        """Refresh real QBO access token."""
        try:
            from intuitlib.client import AuthClient
            
            auth_client = AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                environment=self.environment.value
            )
            
            # Refresh token
            auth_client.refresh(refresh_token=integration.refresh_token)
            
            # Update stored tokens in database
            integration.access_token = auth_client.access_token
            integration.refresh_token = auth_client.refresh_token
            # QBO access tokens expire in 1 hour (3600 seconds)
            # QBO refresh tokens expire in 101 days (8726400 seconds)
            integration.token_expires_at = datetime.utcnow() + timedelta(seconds=auth_client.expires_in)
            # Store when refresh token expires (101 days from now)
            integration.expires_at = datetime.utcnow() + timedelta(seconds=8726400)
            
            # Commit changes - let the existing transaction handle this
            self.db.add(integration)
            self.db.commit()
            
            self.logger.info(f"Refreshed real token for business {self.business_id}")
            return auth_client.access_token
            
        except ImportError:
            self.logger.error("Intuit SDK not available for real QBO token refresh")
            return None
        except Exception as e:
            self.logger.error(f"Failed to refresh real QBO token: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if business has valid QBO connection."""
        try:
            integration = self.db.query(Integration).filter(
                Integration.business_id == self.business_id,
                Integration.platform == "qbo",
                Integration.status == IntegrationStatuses.CONNECTED.value
            ).first()
            
            return integration is not None and integration.access_token is not None
            
        except Exception as e:
            self.logger.error(f"Failed to check QBO connection status: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect QBO integration."""
        try:
            integration = self.db.query(Integration).filter(
                Integration.business_id == self.business_id,
                Integration.platform == "qbo"
            ).first()
            
            if integration:
                with self.db.begin():
                    integration.status = IntegrationStatuses.DISCONNECTED
                    integration.disconnected_at = datetime.utcnow()
                    # Clear sensitive data
                    integration.access_token = None
                    integration.refresh_token = None
                    integration.oauth_state = None
                
                self.logger.info(f"Disconnected QBO integration for business {self.business_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect QBO integration: {e}", exc_info=True)
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status."""
        try:
            integration = self.db.query(Integration).filter(
                Integration.business_id == self.business_id,
                Integration.platform == "qbo"
            ).first()
            
            if not integration:
                return {
                    "connected": False,
                    "status": "not_connected",
                    "environment": self.environment.value
                }
            
            return {
                "connected": integration.status == IntegrationStatuses.CONNECTED.value,
                "status": integration.status.value,
                "environment": self.environment.value,
                "realm_id": integration.realm_id,
                "connected_at": integration.connected_at.isoformat() if integration.connected_at else None,
                "disconnected_at": integration.disconnected_at.isoformat() if integration.disconnected_at else None,
                "has_access_token": integration.access_token is not None,
                "has_refresh_token": integration.refresh_token is not None,
                "token_expires_at": integration.token_expires_at.isoformat() if integration.token_expires_at else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get connection status: {e}", exc_info=True)
            return {
                "connected": False,
                "status": "error",
                "error": str(e),
                "environment": self.environment.value
            }
 