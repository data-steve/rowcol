"""
QBO Connection Manager - Core Infrastructure

This is mission-critical infrastructure that ensures reliable QBO connectivity
for all clients. Handles token management, health monitoring, and resilience.

Architecture Principles:
1. Zero-downtime token refresh
2. Circuit breaker pattern for API failures  
3. Comprehensive logging and monitoring
4. Graceful degradation when QBO is unavailable
5. Client-specific connection health tracking
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

from sqlalchemy.orm import Session
from domains.core.models.integration import Integration
from domains.core.models.business import Business
from common.exceptions import IntegrationError
from db.transaction import db_transaction

logger = logging.getLogger(__name__)


class QBOConnectionStatus(Enum):
    """QBO connection health states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"  
    FAILING = "failing"
    DISCONNECTED = "disconnected"
    MAINTENANCE = "maintenance"


class QBOAPIEndpoint(Enum):
    """Critical QBO API endpoints we depend on."""
    COMPANY_INFO = "companyinfo"
    BILLS = "bill"
    INVOICES = "invoice"
    ACCOUNTS = "account"
    VENDORS = "vendor"
    CUSTOMERS = "customer"
    PAYMENTS = "payment"


@dataclass
class QBOConnectionHealth:
    """QBO connection health metrics."""
    business_id: str
    status: QBOConnectionStatus
    last_successful_call: Optional[datetime]
    last_token_refresh: Optional[datetime]
    token_expires_at: Optional[datetime]
    consecutive_failures: int
    api_response_time_ms: Optional[float]
    failing_endpoints: List[str]
    error_message: Optional[str]
    updated_at: datetime


@dataclass
class QBOTokens:
    """QBO OAuth tokens with metadata."""
    access_token: str
    refresh_token: str
    expires_at: datetime
    realm_id: str
    business_id: str


class QBOConnectionManager:
    """
    Production-grade QBO connection management.
    
    Responsibilities:
    - Automatic token refresh before expiration
    - Circuit breaker pattern for API failures
    - Health monitoring and alerting
    - Graceful degradation strategies
    - Per-client connection tracking
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.connection_health: Dict[str, QBOConnectionHealth] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Configure resilient HTTP session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        # QBO API configuration
        self.qbo_base_url = "https://sandbox-quickbooks.api.intuit.com/v3/company"
        self.qbo_token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        
        # Token refresh thresholds
        self.token_refresh_threshold = timedelta(minutes=15)  # Refresh 15 min before expiry
        self.health_check_interval = timedelta(minutes=5)
        
        logger.info("QBOConnectionManager initialized")
    
    async def ensure_healthy_connection(self, business_id: str) -> bool:
        """
        Ensure QBO connection is healthy for a business.
        
        Returns True if connection is ready for use, False if degraded/failing.
        This is the main method other services should call.
        """
        try:
            # Get or initialize connection health
            if business_id not in self.connection_health:
                await self._initialize_connection_health(business_id)
            
            health = self.connection_health[business_id]
            
            # Check circuit breaker
            if self._is_circuit_open(business_id):
                logger.warning(f"Circuit breaker open for business {business_id}")
                return False
            
            # Refresh token if needed
            if await self._needs_token_refresh(business_id):
                success = await self._refresh_token(business_id)
                if not success:
                    self._record_failure(business_id, "Token refresh failed")
                    return False
            
            # Perform health check
            is_healthy = await self._perform_health_check(business_id)
            
            if is_healthy:
                self._record_success(business_id)
                return True
            else:
                self._record_failure(business_id, "Health check failed")
                return False
                
        except Exception as e:
            logger.error(f"Connection health check failed for business {business_id}: {e}")
            self._record_failure(business_id, str(e))
            return False
    
    async def get_valid_token(self, business_id: str) -> Optional[str]:
        """Get a valid access token for QBO API calls."""
        if await self.ensure_healthy_connection(business_id):
            integration = self._get_qbo_integration(business_id)
            return integration.access_token if integration else None
        return None
    
    async def make_qbo_request(self, business_id: str, endpoint: str, method: str = "GET", 
                              data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a resilient QBO API request with automatic retry and circuit breaking.
        
        This is the preferred way to make QBO API calls throughout the application.
        """
        if not await self.ensure_healthy_connection(business_id):
            logger.warning(f"QBO connection unhealthy for business {business_id}, request blocked")
            return None
        
        integration = self._get_qbo_integration(business_id)
        if not integration:
            return None
        
        url = f"{self.qbo_base_url}/{integration.realm_id}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {integration.access_token}",
            "Accept": "application/json"
        }
        
        try:
            start_time = datetime.now()
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=30)
            else:
                headers["Content-Type"] = "application/json"
                response = self.session.post(url, headers=headers, json=data, timeout=30)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                self._update_response_time(business_id, response_time)
                self._record_success(business_id)
                return response.json()
            elif response.status_code == 401:
                # Token expired, try refresh once
                logger.info(f"Token expired for business {business_id}, attempting refresh")
                if await self._refresh_token(business_id):
                    # Retry request with new token
                    integration = self._get_qbo_integration(business_id)
                    headers["Authorization"] = f"Bearer {integration.access_token}"
                    
                    if method.upper() == "GET":
                        response = self.session.get(url, headers=headers, timeout=30)
                    else:
                        response = self.session.post(url, headers=headers, json=data, timeout=30)
                    
                    if response.status_code == 200:
                        self._record_success(business_id)
                        return response.json()
                
                self._record_failure(business_id, "Authentication failed")
                return None
            else:
                self._record_failure(business_id, f"HTTP {response.status_code}: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            self._record_failure(business_id, "Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            self._record_failure(business_id, "Connection error")
            return None
        except Exception as e:
            self._record_failure(business_id, str(e))
            return None
    
    def get_connection_health(self, business_id: str) -> Optional[QBOConnectionHealth]:
        """Get current connection health for a business."""
        return self.connection_health.get(business_id)
    
    def get_all_connection_health(self) -> Dict[str, QBOConnectionHealth]:
        """Get connection health for all businesses."""
        return self.connection_health.copy()
    
    async def _initialize_connection_health(self, business_id: str):
        """Initialize connection health tracking for a business."""
        integration = self._get_qbo_integration(business_id)
        
        if integration:
            status = QBOConnectionStatus.HEALTHY
            token_expires_at = integration.token_expires_at
        else:
            status = QBOConnectionStatus.DISCONNECTED
            token_expires_at = None
        
        self.connection_health[business_id] = QBOConnectionHealth(
            business_id=business_id,
            status=status,
            last_successful_call=None,
            last_token_refresh=None,
            token_expires_at=token_expires_at,
            consecutive_failures=0,
            api_response_time_ms=None,
            failing_endpoints=[],
            error_message=None,
            updated_at=datetime.now()
        )
        
        # Initialize circuit breaker
        self.circuit_breakers[business_id] = {
            "state": "closed",  # closed, open, half-open
            "failure_count": 0,
            "last_failure_time": None,
            "next_attempt_time": None
        }
    
    async def _needs_token_refresh(self, business_id: str) -> bool:
        """Check if token needs refresh."""
        integration = self._get_qbo_integration(business_id)
        if not integration or not integration.token_expires_at:
            return True
        
        # Refresh if token expires within threshold
        return integration.token_expires_at <= datetime.now() + self.token_refresh_threshold
    
    async def _refresh_token(self, business_id: str) -> bool:
        """Refresh QBO access token."""
        try:
            integration = self._get_qbo_integration(business_id)
            if not integration or not integration.refresh_token:
                logger.error(f"No refresh token available for business {business_id}")
                return False
            
            # Get client credentials from environment
            client_id = os.getenv("QBO_CLIENT_ID")
            client_secret = os.getenv("QBO_CLIENT_SECRET")
            
            if not client_id or not client_secret:
                logger.error("QBO client credentials not configured")
                return False
            
            # Make token refresh request
            data = {
                "grant_type": "refresh_token",
                "refresh_token": integration.refresh_token
            }
            
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(client_id, client_secret)
            
            response = self.session.post(
                self.qbo_token_url,
                data=data,
                auth=auth,
                headers={"Accept": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                tokens = response.json()
                new_access_token = tokens.get("access_token")
                new_refresh_token = tokens.get("refresh_token")
                expires_in = tokens.get("expires_in", 3600)
                
                if new_access_token:
                    # Update integration with new tokens
                    with db_transaction(self.db):
                        integration.access_token = new_access_token
                        integration.refresh_token = new_refresh_token or integration.refresh_token
                        integration.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                        self.db.commit()
                    
                    # Update health tracking
                    if business_id in self.connection_health:
                        self.connection_health[business_id].last_token_refresh = datetime.now()
                        self.connection_health[business_id].token_expires_at = integration.token_expires_at
                    
                    logger.info(f"Token refreshed successfully for business {business_id}")
                    return True
            
            logger.error(f"Token refresh failed for business {business_id}: {response.status_code} {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Token refresh error for business {business_id}: {e}")
            return False
    
    async def _perform_health_check(self, business_id: str) -> bool:
        """Perform comprehensive health check."""
        try:
            # Test company info endpoint (lightweight)
            integration = self._get_qbo_integration(business_id)
            if not integration:
                return False
            
            response = await self.make_qbo_request(
                business_id, 
                f"companyinfo/{integration.realm_id}"
            )
            
            return response is not None
            
        except Exception as e:
            logger.error(f"Health check failed for business {business_id}: {e}")
            return False
    
    def _get_qbo_integration(self, business_id: str) -> Optional[Integration]:
        """Get QBO integration for a business."""
        return self.db.query(Integration).filter(
            Integration.business_id == business_id,
            Integration.platform == "qbo",
            Integration.status == "connected"
        ).first()
    
    def _record_success(self, business_id: str):
        """Record successful API call."""
        if business_id in self.connection_health:
            health = self.connection_health[business_id]
            health.status = QBOConnectionStatus.HEALTHY
            health.last_successful_call = datetime.now()
            health.consecutive_failures = 0
            health.error_message = None
            health.updated_at = datetime.now()
        
        # Reset circuit breaker
        if business_id in self.circuit_breakers:
            self.circuit_breakers[business_id]["state"] = "closed"
            self.circuit_breakers[business_id]["failure_count"] = 0
    
    def _record_failure(self, business_id: str, error_message: str):
        """Record API call failure."""
        if business_id in self.connection_health:
            health = self.connection_health[business_id]
            health.consecutive_failures += 1
            health.error_message = error_message
            health.updated_at = datetime.now()
            
            # Update status based on failure count
            if health.consecutive_failures >= 5:
                health.status = QBOConnectionStatus.FAILING
            elif health.consecutive_failures >= 2:
                health.status = QBOConnectionStatus.DEGRADED
        
        # Update circuit breaker
        self._update_circuit_breaker(business_id)
    
    def _update_response_time(self, business_id: str, response_time_ms: float):
        """Update API response time metrics."""
        if business_id in self.connection_health:
            self.connection_health[business_id].api_response_time_ms = response_time_ms
    
    def _is_circuit_open(self, business_id: str) -> bool:
        """Check if circuit breaker is open."""
        if business_id not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[business_id]
        
        if breaker["state"] == "open":
            # Check if we should try half-open
            if breaker["next_attempt_time"] and datetime.now() >= breaker["next_attempt_time"]:
                breaker["state"] = "half-open"
                return False
            return True
        
        return False
    
    def _update_circuit_breaker(self, business_id: str):
        """Update circuit breaker state after failure."""
        if business_id not in self.circuit_breakers:
            return
        
        breaker = self.circuit_breakers[business_id]
        breaker["failure_count"] += 1
        breaker["last_failure_time"] = datetime.now()
        
        # Open circuit after 5 consecutive failures
        if breaker["failure_count"] >= 5:
            breaker["state"] = "open"
            breaker["next_attempt_time"] = datetime.now() + timedelta(minutes=5)
            logger.warning(f"Circuit breaker opened for business {business_id}")


# Global connection manager instance
_connection_manager: Optional[QBOConnectionManager] = None


def get_qbo_connection_manager(db: Session) -> QBOConnectionManager:
    """Get or create the global QBO connection manager."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = QBOConnectionManager(db)
    return _connection_manager


async def ensure_qbo_health_for_all_businesses(db: Session):
    """Background task to ensure QBO health for all connected businesses."""
    manager = get_qbo_connection_manager(db)
    
    # Get all businesses with QBO integrations
    businesses = db.query(Business).join(Integration).filter(
        Integration.platform == "qbo",
        Integration.status == "connected"
    ).all()
    
    for business in businesses:
        try:
            await manager.ensure_healthy_connection(business.business_id)
        except Exception as e:
            logger.error(f"Health check failed for business {business.business_id}: {e}")


if __name__ == "__main__":
    # Test the connection manager
    from db.session import SessionLocal
    
    async def test_connection_manager():
        db = SessionLocal()
        manager = QBOConnectionManager(db)
        
        # Test with a known business ID
        business_id = "test-business-123"
        is_healthy = await manager.ensure_healthy_connection(business_id)
        
        print(f"Connection healthy: {is_healthy}")
        
        health = manager.get_connection_health(business_id)
        if health:
            print(f"Health status: {health.status}")
            print(f"Consecutive failures: {health.consecutive_failures}")
    
    asyncio.run(test_connection_manager())
