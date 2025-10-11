"""
QBO Authentication Service

Handles system QBO token management:
- System tokens stored in system_integration_tokens table
- Auto-refresh expired access tokens
- Manual OAuth flow when refresh token expires

Usage:
    auth_service = QBOAuthService("system", QBOEnvironment.SANDBOX)
    access_token = auth_service.get_valid_access_token()  # Auto-refreshes if needed
    auth_service.initiate_system_oauth_flow()  # One-time setup
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
import logging
import secrets
import os
from enum import Enum
import time
import json

from infra.config.exceptions import IntegrationError
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
            
            auth_url = self._generate_real_auth_url(state)
            
            return {
                "auth_url": auth_url,
                "state": state,
                "business_id": self.business_id,
                "environment": self.environment.value
            }
            
        except IntegrationError as e:
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
        except IntegrationError as e:
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
            
        except IntegrationError as e:
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
        except IntegrationError as e:
            self.logger.error(f"Failed to exchange real QBO tokens: {e}")
            raise IntegrationError("Failed to exchange QBO tokens", {"error": str(e)})
    
    def get_valid_access_token(self) -> Optional[str]:
        """
        Get valid access token for QBO API calls.
        
        Returns:
            Valid access token or None if not available
        """
        try:
            # Load tokens from database (system tokens)
            tokens = self._load_system_tokens()
            if not tokens:
                self.logger.warning("No system tokens found in database")
                return None
            
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')
            access_expires_at = tokens.get('access_expires_at')
            refresh_expires_at = tokens.get('refresh_expires_at')
            
            if not access_token:
                self.logger.warning("No access token found")
                return None
            
            # Check if access token is expired (with 5 minute buffer)
            now = datetime.now(timezone.utc)
            if access_expires_at:
                if isinstance(access_expires_at, str):
                    access_expires_at = datetime.fromisoformat(access_expires_at)
                if access_expires_at.tzinfo is None:
                    access_expires_at = access_expires_at.replace(tzinfo=timezone.utc)
                
                if now >= access_expires_at - timedelta(minutes=5):
                    self.logger.info("Access token expired, attempting refresh")
                    self.logger.info("Refresh token available for refresh")
                    if refresh_token and refresh_expires_at:
                        # Check if refresh token is still valid
                        if isinstance(refresh_expires_at, str):
                            refresh_expires_at = datetime.fromisoformat(refresh_expires_at)
                        if refresh_expires_at.tzinfo is None:
                            refresh_expires_at = refresh_expires_at.replace(tzinfo=timezone.utc)
                        
                        if now < refresh_expires_at:
                            new_tokens = self._refresh_tokens(refresh_token)
                            if new_tokens:
                                self.logger.info("Got new tokens from refresh")
                                self._save_system_tokens(new_tokens)
                                return new_tokens.get('access_token')
                        else:
                            self.logger.error("Refresh token expired - manual OAuth flow required")
                            self._prompt_manual_refresh()
                            return None
                    else:
                        self.logger.warning("No refresh token available")
            return access_token
            
        except Exception as e:
            self.logger.error(f"Failed to get valid access token: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if business has valid QBO connection."""
        try:
            # Check if we have a valid access token
            access_token = self.get_valid_access_token()
            return access_token is not None
            
        except Exception as e:
            self.logger.error(f"Failed to check connection status: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect QBO integration."""
        try:
            # Load existing data
            data = {}
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'r') as f:
                    data = json.load(f)
            
            # Remove tokens for this business
            if self.business_id in data:
                del data[self.business_id]
                
                # Save back to file
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.logger.info(f"Disconnected QBO for business {self.business_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect QBO: {e}")
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status with troubleshooting info."""
        try:
            connected = self.is_connected()
            tokens = self._load_system_tokens()
            
            status = QBOIntegrationStatuses.CONNECTED if connected else QBOIntegrationStatuses.DISCONNECTED
            
            result = {
                "connected": connected,
                "status": status,
                "platform": "qbo",
                "business_id": self.business_id,
                "environment": self.environment.value
            }
            
            if tokens:
                result.update({
                    "access_expires_at": tokens.get('access_expires_at'),
                    "refresh_expires_at": tokens.get('refresh_expires_at'),
                    "external_id": tokens.get('external_id')
                })
            
            # Add troubleshooting info
            if not connected:
                result["troubleshooting"] = self._get_troubleshooting_info()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get connection status: {e}")
            return {
                "connected": False,
                "status": QBOIntegrationStatuses.ERROR,
                "platform": "qbo",
                "business_id": self.business_id,
                "error": str(e),
                "troubleshooting": self._get_troubleshooting_info()
            }
    
    def _get_troubleshooting_info(self) -> Dict[str, str]:
        """Get troubleshooting information for connection issues."""
        return {
            "no_tokens": "Run: poetry run python -c \"from mvp.infra.rails.qbo.auth import QBOAuthService, QBOEnvironment; QBOAuthService('system', QBOEnvironment.SANDBOX).initiate_system_oauth_flow()\"",
            "expired_tokens": "Run the same command above to refresh tokens",
            "api_errors": "Check QBO sandbox credentials in .env file",
            "database_errors": "Check _clean/rowcol.db exists and is accessible"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check with actionable recommendations."""
        try:
            # Check if we have tokens
            tokens = self._load_system_tokens()
            if not tokens:
                return {
                    "status": "no_tokens",
                    "message": "No QBO tokens found in database",
                    "action": "Run OAuth flow to get initial tokens",
                    "command": "poetry run python -c \"from mvp.infra.rails.qbo.auth import QBOAuthService, QBOEnvironment; QBOAuthService('system', QBOEnvironment.SANDBOX).initiate_system_oauth_flow()\""
                }
            
            # Check token expiration
            now = datetime.now(timezone.utc)
            access_expires = tokens.get('access_expires_at')
            refresh_expires = tokens.get('refresh_expires_at')
            
            if access_expires:
                if isinstance(access_expires, str):
                    access_expires = datetime.fromisoformat(access_expires)
                if access_expires.tzinfo is None:
                    access_expires = access_expires.replace(tzinfo=timezone.utc)
                
                if now >= access_expires:
                    return {
                        "status": "access_expired",
                        "message": "Access token expired - will auto-refresh",
                        "action": "System will attempt auto-refresh",
                        "command": "Check logs for refresh status"
                    }
            
            if refresh_expires:
                if isinstance(refresh_expires, str):
                    refresh_expires = datetime.fromisoformat(refresh_expires)
                if refresh_expires.tzinfo is None:
                    refresh_expires = refresh_expires.replace(tzinfo=timezone.utc)
                
                if now >= refresh_expires:
                    return {
                        "status": "refresh_expired",
                        "message": "Refresh token expired - manual OAuth required",
                        "action": "Run OAuth flow to get new tokens",
                        "command": "poetry run python -c \"from mvp.infra.rails.qbo.auth import QBOAuthService, QBOEnvironment; QBOAuthService('system', QBOEnvironment.SANDBOX).initiate_system_oauth_flow()\""
                    }
            
            # Test API connectivity
            try:
                from .client import QBORawClient
                client = QBORawClient("system", tokens.get('external_id', ''))
                response = client.get("companyinfo/1")
                return {
                    "status": "healthy",
                    "message": "QBO connection working properly",
                    "action": "No action needed",
                    "company_name": response.get('QueryResponse', {}).get('CompanyInfo', [{}])[0].get('CompanyName', 'Unknown')
                }
            except Exception as e:
                return {
                    "status": "api_error",
                    "message": f"QBO API call failed: {e}",
                    "action": "Check QBO credentials and network connectivity",
                    "command": "Verify QBO sandbox credentials in .env file"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {e}",
                "action": "Check system configuration",
                "command": "Check database connectivity and configuration"
            }
    
    def _load_system_tokens(self) -> Optional[Dict[str, Any]]:
        """Load system tokens from database."""
        try:
            from sqlalchemy import create_engine, text
            
            # Use the clean root database
            database_url = 'sqlite:///../../_clean/rowcol.db'  # Use the clean root database
            engine = create_engine(database_url)
            
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT access_token, refresh_token, access_expires_at, refresh_expires_at, external_id
                    FROM system_integration_tokens 
                    WHERE rail = 'qbo' 
                    AND environment = 'sandbox'
                    AND status = 'active'
                    ORDER BY updated_at DESC
                    LIMIT 1
                """)).fetchone()
                
                if result:
                    return {
                        'access_token': result[0],
                        'refresh_token': result[1],
                        'access_expires_at': result[2],
                        'refresh_expires_at': result[3],
                        'external_id': result[4]
                    }
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to load system tokens: {e}")
            return None

    def _load_tokens(self) -> Optional[Dict[str, Any]]:
        """Load tokens from storage file (legacy method)."""
        try:
            if not os.path.exists(TOKEN_FILE):
                return None
            
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
                return data.get(self.business_id)
                
        except Exception as e:
            self.logger.error(f"Failed to load tokens: {e}")
            return None
    
    def _save_system_tokens(self, tokens: Dict[str, Any]) -> bool:
        """Save system tokens to database."""
        try:
            from sqlalchemy import create_engine, text
            
            self.logger.info("Saving refreshed tokens to database")
            
            # Use the clean root database
            database_url = 'sqlite:///../../_clean/rowcol.db'  # Use the clean root database
            engine = create_engine(database_url)
            
            with engine.connect() as conn:
                # Check if record exists
                existing = conn.execute(text("""
                    SELECT id FROM system_integration_tokens 
                    WHERE rail = 'qbo' AND environment = 'sandbox'
                """)).fetchone()
                
                if existing:
                    # Update existing system tokens
                    conn.execute(text("""
                        UPDATE system_integration_tokens 
                        SET access_token = :access_token,
                            refresh_token = :refresh_token,
                            access_expires_at = :access_expires_at,
                            refresh_expires_at = :refresh_expires_at,
                            status = 'active',
                            updated_at = :updated_at
                        WHERE rail = 'qbo' 
                        AND environment = 'sandbox'
                    """), {
                        'access_token': tokens.get('access_token'),
                        'refresh_token': tokens.get('refresh_token'),
                        'access_expires_at': tokens.get('access_expires_at'),
                        'refresh_expires_at': tokens.get('refresh_expires_at'),
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    })
                else:
                    # Insert new system tokens
                    conn.execute(text("""
                        INSERT INTO system_integration_tokens 
                        (rail, environment, external_id, access_token, refresh_token, 
                         access_expires_at, refresh_expires_at, status, created_at, updated_at)
                        VALUES ('qbo', 'sandbox', :external_id, :access_token, :refresh_token,
                                :access_expires_at, :refresh_expires_at, 'active', :created_at, :updated_at)
                    """), {
                        'external_id': tokens.get('external_id', 'system'),
                        'access_token': tokens.get('access_token'),
                        'refresh_token': tokens.get('refresh_token'),
                        'access_expires_at': tokens.get('access_expires_at'),
                        'refresh_expires_at': tokens.get('refresh_expires_at'),
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    })
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save system tokens: {e}")
            return False

    def _save_tokens(self, tokens: Dict[str, Any]) -> bool:
        """Save tokens to storage file (legacy method)."""
        try:
            # Load existing data
            data = {}
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'r') as f:
                    data = json.load(f)
            
            # Update with new tokens
            data[self.business_id] = tokens
            
            # Save back to file
            with open(TOKEN_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save tokens: {e}")
            return False
    
    def _refresh_tokens(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token."""
        try:
            import requests
            
            # QBO token refresh endpoint
            token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
            
            # Prepare refresh request
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            # Basic auth with client credentials
            auth = (qbo_config.client_id, qbo_config.client_secret)
            
            # Make refresh request
            response = requests.post(
                token_url,
                data=data,
                auth=auth,
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.logger.info("Token refresh successful - tokens obtained")
                
                # Calculate expiration times based on QBO docs
                now = datetime.utcnow()
                access_expires_at = now + timedelta(seconds=token_data.get('expires_in', 3600))
                refresh_expires_at = now + timedelta(seconds=token_data.get('x_refresh_token_expires_in', 8726400))
                
                return {
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token'),
                    'access_expires_at': access_expires_at.isoformat(),
                    'refresh_expires_at': refresh_expires_at.isoformat(),
                    'business_id': self.business_id,
                    'refreshed_at': now.isoformat()
                }
            else:
                self.logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to refresh tokens: {e}")
            return None

    def _prompt_manual_refresh(self):
        """Prompt user to manually refresh system tokens."""
        print("\n" + "="*60)
        print("🚨 QBO REFRESH TOKEN EXPIRED - MANUAL OAUTH REQUIRED")
        print("="*60)
        print("Run this command to refresh system tokens:")
        print()
        print("  poetry run python -c \"from mvp.infra.rails.qbo.auth import QBOAuthService, QBOEnvironment; QBOAuthService('system', QBOEnvironment.SANDBOX).initiate_system_oauth_flow()\"")
        print()
        print("="*60 + "\n")
    
    def initiate_system_oauth_flow(self) -> bool:
        """
        Initiate OAuth flow for system token setup.
        This is a one-time setup for system QBO access.
        """
        try:
            import webbrowser
            from intuitlib.client import AuthClient
            from intuitlib.enums import Scopes
            
            print("🔗 Initiating QBO OAuth flow for system tokens...")
            
            # Create auth client
            auth_client = AuthClient(
                client_id=qbo_config.client_id,
                client_secret=qbo_config.client_secret,
                environment=qbo_config.environment,
                redirect_uri=qbo_config.redirect_uri
            )
            
            # Get authorization URL
            auth_url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
            
            print("🔗 Opening QBO authorization URL...")
            print(f"If browser doesn't open, copy this URL:\n\n{auth_url}\n")
            
            # Open browser
            try:
                webbrowser.open(auth_url)
            except:
                print("Could not open browser automatically")
            
            # Get authorization code from user
            auth_code = input("Enter the authorization code from the URL: ").strip()
            
            if not auth_code:
                print("❌ Authorization code required")
                return False
            
            # Exchange code for tokens
            print("Exchanging authorization code for tokens...")
            auth_client.get_bearer_token(auth_code)
            
            access_token = auth_client.access_token
            refresh_token = auth_client.refresh_token
            
            # Get realm_id from environment
            realm_id = os.getenv('QBO_REALM_ID')
            if not realm_id:
                print("❌ QBO_REALM_ID not found in environment")
                return False
            
            # Calculate expiration times
            now = datetime.now(timezone.utc)
            access_expires_at = now + timedelta(seconds=3600)  # 1 hour
            refresh_expires_at = now + timedelta(seconds=8726400)  # 101 days
            
            # Store tokens in database
            tokens = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'access_expires_at': access_expires_at.isoformat(),
                'refresh_expires_at': refresh_expires_at.isoformat()
            }
            
            if self._save_system_tokens(tokens):
                print("✅ System tokens stored successfully!")
                print(f"Realm ID: {realm_id}")
                print(f"Access expires: {access_expires_at}")
                print(f"Refresh expires: {refresh_expires_at}")
                return True
            else:
                print("❌ Failed to store system tokens")
                return False
                
        except Exception as e:
            print(f"❌ OAuth flow failed: {e}")
            return False
    
    def store_tokens(self, access_token: str, refresh_token: str, expires_in: int = 3600) -> bool:
        """Store tokens for this business."""
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            tokens = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': expires_at.isoformat(),
                'business_id': self.business_id,
                'stored_at': datetime.utcnow().isoformat()
            }
            
            return self._save_tokens(tokens)
            
        except Exception as e:
            self.logger.error(f"Failed to store tokens: {e}")
            return False