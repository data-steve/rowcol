from typing import Tuple, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class QBOAuth:
    """Centralized QBO authentication and token management.
    
    Handles OAuth flow, token storage, and automatic refresh for all QBO integrations.
    This replaces the anti-pattern of individual services managing their own tokens.
    """
    
    def __init__(self):
        self.tokens = {}  # business_id -> {"access": str, "refresh": str, "expires_at": datetime}
        self.refresh_in_progress = set()  # Track ongoing refresh operations

    def initiate_oauth(self, redirect_uri: str) -> str:
        """Initiate OAuth flow and return authorization URL."""
        return "https://mock.qbo.auth/url?state=mock_state"

    def exchange_tokens(self, code: str, business_id: int) -> Tuple[str, Optional[str]]:
        """Exchange authorization code for access and refresh tokens."""
        access = f"mock_access_{business_id}"
        refresh = f"mock_refresh_{business_id}"
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Mock 1-hour expiry
        
        self.tokens[business_id] = {
            "access": access,
            "refresh": refresh, 
            "expires_at": expires_at
        }
        logger.info(f"Tokens exchanged for business {business_id}")
        return access, refresh

    def get_valid_token(self, business_id: int) -> Optional[str]:
        """Get a valid access token, refreshing if necessary."""
        if business_id not in self.tokens:
            logger.warning(f"No tokens found for business {business_id}")
            return None
            
        token_data = self.tokens[business_id]
        
        # Check if token is still valid (with 5-minute buffer)
        if datetime.utcnow() + timedelta(minutes=5) < token_data["expires_at"]:
            return token_data["access"]
            
        # Token needs refresh
        return self._refresh_token(business_id)

    def _refresh_token(self, business_id: int) -> Optional[str]:
        """Refresh access token for a business."""
        if business_id in self.refresh_in_progress:
            logger.info(f"Token refresh already in progress for business {business_id}")
            return None
            
        try:
            self.refresh_in_progress.add(business_id)
            token_data = self.tokens[business_id]
            
            # Mock token refresh (in production, this would call QBO API)
            new_access = f"mock_access_{business_id}_{datetime.utcnow().timestamp()}"
            new_expires = datetime.utcnow() + timedelta(hours=1)
            
            # Update token data
            self.tokens[business_id].update({
                "access": new_access,
                "expires_at": new_expires
            })
            
            logger.info(f"Token refreshed successfully for business {business_id}")
            return new_access
            
        except Exception as e:
            logger.error(f"Token refresh failed for business {business_id}: {e}")
            return None
        finally:
            self.refresh_in_progress.discard(business_id)

    def revoke_tokens(self, business_id: int) -> bool:
        """Revoke tokens for a business (e.g., on disconnect)."""
        if business_id in self.tokens:
            del self.tokens[business_id]
            logger.info(f"Tokens revoked for business {business_id}")
            return True
        return False

    def is_connected(self, business_id: int) -> bool:
        """Check if business has valid QBO connection."""
        return business_id in self.tokens

# Singleton instance for centralized token management
qbo_auth = QBOAuth()
