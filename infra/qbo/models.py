"""
QBO Infrastructure Models - Data Transfer Objects

These are lightweight data structures used by QBO infrastructure services.
They avoid circular dependencies by not importing domain models directly.

Key Principle: Infrastructure should not depend on domain models.
Instead, use DTOs and let domain services handle the mapping.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class QBOEnvironment(Enum):
    """QBO environment types."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class QBOConnectionStatus(Enum):
    """QBO connection status types."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    NOT_CONNECTED = "not_connected"


@dataclass
class QBOIntegrationDTO:
    """Data Transfer Object for QBO integration data."""
    business_id: str
    status: str
    platform: str = "qbo"
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    realm_id: Optional[str] = None
    environment: str = "sandbox"
    connected_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None
    oauth_state: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "business_id": self.business_id,
            "platform": self.platform,
            "status": self.status,
            "environment": self.environment,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "disconnected_at": self.disconnected_at.isoformat() if self.disconnected_at else None,
            "has_access_token": bool(self.access_token),
            "has_refresh_token": bool(self.refresh_token),
            "has_realm_id": bool(self.realm_id),
        }


@dataclass
class QBOConnectionResult:
    """Result of QBO connection operations."""
    success: bool
    status: QBOConnectionStatus
    message: str
    integration: Optional[QBOIntegrationDTO] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = {
            "success": self.success,
            "status": self.status.value,
            "message": self.message,
        }
        
        if self.integration:
            result["integration"] = self.integration.to_dict()
        
        if self.error:
            result["error"] = self.error
            
        return result
