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

from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import logging
import webbrowser
from enum import Enum

from infra.config.exceptions import IntegrationError
from .config import qbo_config

logger = logging.getLogger(__name__)


class QBOEnvironment(Enum):
    """QBO environment types."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class QBOAuthService:
    """QBO authentication service for system tokens."""
    
    def __init__(self, business_id: str, environment: QBOEnvironment = QBOEnvironment.SANDBOX):
        self.business_id = business_id
        self.environment = environment
        self.logger = logging.getLogger(f"{__name__}.{business_id}")
    
    def get_valid_access_token(self) -> Optional[str]:
        """Get valid access token for QBO API calls. Auto-refreshes if needed."""
        try:
            tokens = self._load_system_tokens()
            if not tokens:
                self.logger.warning("No system tokens found")
                return None
            
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')
            access_expires_at = tokens.get('access_expires_at')
            refresh_expires_at = tokens.get('refresh_expires_at')
            
            if not access_token:
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
                    if refresh_token and refresh_expires_at:
                        # Check if refresh token is still valid
                        if isinstance(refresh_expires_at, str):
                            refresh_expires_at = datetime.fromisoformat(refresh_expires_at)
                        if refresh_expires_at.tzinfo is None:
                            refresh_expires_at = refresh_expires_at.replace(tzinfo=timezone.utc)
                        
                        if now < refresh_expires_at:
                            new_tokens = self._refresh_tokens(refresh_token)
                            if new_tokens:
                                self._save_system_tokens(new_tokens)
                                return new_tokens.get('access_token')
                        else:
                            self.logger.error("Refresh token expired - manual OAuth required")
                            return None
                    else:
                        self.logger.warning("No refresh token available")
            
            return access_token
            
        except Exception as e:
            self.logger.error(f"Failed to get valid access token: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if business has valid QBO connection."""
        return self.get_valid_access_token() is not None
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status."""
        try:
            connected = self.is_connected()
            tokens = self._load_system_tokens()
            
            result = {
                "connected": connected,
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
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get connection status: {e}")
            return {
                "connected": False,
                "platform": "qbo",
                "business_id": self.business_id,
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check with actionable recommendations."""
        try:
            # Check if we have tokens
            tokens = self._load_system_tokens()
            if not tokens:
                return {
                    "status": "no_tokens",
                    "message": "No QBO tokens found in database",
                    "action": "Run OAuth flow to get initial tokens"
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
                        "action": "System will attempt auto-refresh"
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
                        "action": "Run OAuth flow to get new tokens"
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
                    "company_name": response.get('CompanyInfo', {}).get('CompanyName', 'Unknown')
                }
            except Exception as e:
                return {
                    "status": "api_error",
                    "message": f"QBO API call failed: {e}",
                    "action": "Check QBO credentials and network connectivity"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {e}",
                "action": "Check system configuration"
            }
    
    def initiate_system_oauth_flow(self) -> bool:
        """Initiate OAuth flow for system token setup."""
        try:
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
            
            # Get authorization code and realm_id from user
            print("After authorizing, you'll be redirected to a URL like:")
            print("http://localhost:8001/callback?code=XXXXX&realmId=XXXXX&state=XXXXX")
            print()
            auth_code = input("Enter the authorization code from the URL: ").strip()
            realm_id = input("Enter the realmId from the URL: ").strip()
            
            if not auth_code or not realm_id:
                print("❌ Authorization code and realmId required")
                return False
            
            # Exchange code for tokens
            print("🔄 Exchanging authorization code for tokens...")
            auth_client.get_bearer_token(auth_code)
            
            access_token = auth_client.access_token
            refresh_token = auth_client.refresh_token
            
            # Calculate expiration times
            now = datetime.now(timezone.utc)
            access_expires_at = now + timedelta(seconds=3600)  # 1 hour
            refresh_expires_at = now + timedelta(seconds=8726400)  # 101 days
            
            # Store tokens in database
            tokens = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'access_expires_at': access_expires_at,
                'refresh_expires_at': refresh_expires_at,
                'external_id': realm_id
            }
            
            if self._save_system_tokens(tokens):
                print("✅ System tokens stored successfully!")
                print(f"   Realm ID: {realm_id}")
                print(f"   Access expires: {access_expires_at}")
                print(f"   Refresh expires: {refresh_expires_at}")
                return True
            else:
                print("❌ Failed to store system tokens")
                return False
                
        except Exception as e:
            print(f"❌ OAuth flow failed: {e}")
            return False
    
    def _load_system_tokens(self) -> Optional[Dict[str, Any]]:
        """Load system tokens from database."""
        try:
            from infra.db.session import SessionLocal
            from infra.db.models import SystemIntegrationToken
            
            with SessionLocal() as session:
                token = session.query(SystemIntegrationToken).filter(
                    SystemIntegrationToken.rail == 'qbo',
                    SystemIntegrationToken.environment == 'sandbox',
                    SystemIntegrationToken.status == 'active'
                ).order_by(SystemIntegrationToken.updated_at.desc()).first()
                
                if token:
                    return {
                        'access_token': token.access_token,
                        'refresh_token': token.refresh_token,
                        'access_expires_at': token.access_expires_at,
                        'refresh_expires_at': token.refresh_expires_at,
                        'external_id': token.external_id
                    }
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to load system tokens: {e}")
            return None
    
    def _save_system_tokens(self, tokens: Dict[str, Any]) -> bool:
        """Save system tokens to database."""
        try:
            from infra.db.session import SessionLocal
            from infra.db.models import SystemIntegrationToken
            
            with SessionLocal() as session:
                # Check if record exists
                existing = session.query(SystemIntegrationToken).filter(
                    SystemIntegrationToken.rail == 'qbo',
                    SystemIntegrationToken.environment == 'sandbox'
                ).first()
                
                if existing:
                    # Update existing tokens
                    existing.access_token = tokens.get('access_token')
                    existing.refresh_token = tokens.get('refresh_token')
                    existing.access_expires_at = tokens.get('access_expires_at')
                    existing.refresh_expires_at = tokens.get('refresh_expires_at')
                    existing.status = 'active'
                else:
                    # Insert new tokens
                    new_token = SystemIntegrationToken(
                        rail='qbo',
                        environment='sandbox',
                        external_id=tokens.get('external_id', 'system'),
                        access_token=tokens.get('access_token'),
                        refresh_token=tokens.get('refresh_token'),
                        access_expires_at=tokens.get('access_expires_at'),
                        refresh_expires_at=tokens.get('refresh_expires_at'),
                        status='active'
                    )
                    session.add(new_token)
                
                session.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save system tokens: {type(e).__name__}: {str(e)}")
            return False
    
    def _refresh_tokens(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token."""
        try:
            import requests
            from tenacity import (
                retry,
                stop_after_attempt,
                wait_exponential,
                retry_if_exception_type,
            )
            from requests.exceptions import Timeout, ConnectionError
            
            token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            auth = (qbo_config.client_id, qbo_config.client_secret)
            
            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                retry=retry_if_exception_type((Timeout, ConnectionError)),
            )
            def _do_refresh():
                return requests.post(
                    token_url,
                    data=data,
                    auth=auth,
                    headers={'Accept': 'application/json'},
                    timeout=(5.0, 30.0),
                )
            
            response = _do_refresh()
            
            if response.status_code == 200:
                token_data = response.json()
                self.logger.info("Token refresh successful")
                
                now = datetime.utcnow()
                access_expires_at = now + timedelta(seconds=token_data.get('expires_in', 3600))
                refresh_expires_at = now + timedelta(seconds=token_data.get('x_refresh_token_expires_in', 8726400))
                
                return {
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token'),
                    'access_expires_at': access_expires_at,
                    'refresh_expires_at': refresh_expires_at,
                    'business_id': self.business_id,
                }
            else:
                self.logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to refresh tokens: {e}")
            return None