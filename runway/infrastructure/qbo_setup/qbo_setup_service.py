"""
QBO Setup Service - Infrastructure Layer

Handles the one-time QBO connection process as infrastructure,
not as part of the user onboarding experience.

This service orchestrates QBO connection establishment using both
QBOAuthService and QBOConnectionManager for robust first-time setup.
"""
from sqlalchemy.orm import Session
from domains.integrations.qbo.auth import QBOAuthService
from domains.integrations.qbo.client import get_qbo_provider
from domains.integrations.qbo.config import qbo_config
from runway.experiences.test_drive import TestDriveService
from domains.core.models.integration import Integration
from common.exceptions import IntegrationError
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class QBOSetupService:
    """
    Service for handling QBO connection setup process.
    
    This service orchestrates the complete QBO setup flow:
    1. Initiate OAuth flow
    2. Complete OAuth flow
    3. Establish connection manager
    4. Generate test drive data
    5. Verify connection health
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def start_qbo_connection(self, business_id: str, user_id: str) -> Dict[str, Any]:
        """
        Initiate QBO OAuth flow for first-time connection.
        
        Args:
            business_id: Business identifier
            user_id: User initiating the connection
            
        Returns:
            Dict containing OAuth URL and state information
        """
        logger.info(f"Starting QBO connection setup for business {business_id}")
        
        auth_service = QBOAuthService(self.db, business_id)
        result = auth_service.initiate_oauth_flow(user_id)
        
        # Add setup context
        result["setup_type"] = "first_time"
        result["infrastructure"] = "qbo_setup"
        
        return result
    
    def complete_qbo_connection(self, state: str, code: str, realm_id: str) -> Dict[str, Any]:
        """
        Complete QBO OAuth flow and establish full connection infrastructure.
        
        This method:
        1. Completes OAuth flow via QBOAuthService
        2. Establishes QBOConnectionManager for ongoing operations
        3. Generates test drive data
        4. Verifies connection health
        
        Args:
            state: OAuth state parameter
            code: Authorization code from QBO
            realm_id: QBO realm ID
            
        Returns:
            Dict containing connection status and test drive data
        """
        logger.info(f"Completing QBO connection setup with state {state}")
        
        # Find the business_id from the state
        integration = self.db.query(Integration).filter(
            Integration.oauth_state == state
        ).first()
        
        if not integration:
            raise IntegrationError("Invalid OAuth state", {"error": "State not found"})
        
        business_id = integration.business_id
        
        # Complete OAuth flow
        auth_service = QBOAuthService(self.db, business_id)
        auth_result = auth_service.complete_oauth_flow(state, code, realm_id)
        
        if auth_result.get("status") != "connected":
            return auth_result
        
        # Establish connection manager for ongoing operations
        try:
            connection_manager = get_qbo_connection_manager(self.db, business_id)
            connection_status = connection_manager.get_connection_health()
            
            logger.info(f"QBO connection manager established for business {business_id}")
        except Exception as e:
            logger.warning(f"Failed to establish connection manager: {e}")
            connection_status = {"status": "warning", "message": "Connection manager setup failed"}
        
        # Generate test drive data after successful connection
        test_drive_data = None
        test_drive_error = None
        
        try:
            test_drive_service = TestDriveService(self.db)
            test_drive_data = test_drive_service.generate_test_drive(business_id)
            logger.info(f"Test drive data generated for business {business_id}")
        except Exception as e:
            test_drive_error = str(e)
            logger.error(f"Failed to generate test drive data: {e}")
        
        # Combine all results
        result = {
            **auth_result,
            "setup_complete": True,
            "infrastructure": "qbo_setup",
            "connection_manager_status": connection_status,
            "test_drive": test_drive_data,
            "test_drive_error": test_drive_error
        }
        
        return result
    
    def get_qbo_connection_status(self, business_id: str) -> Dict[str, Any]:
        """
        Get comprehensive QBO connection status including connection manager health.
        
        Args:
            business_id: Business identifier
            
        Returns:
            Dict containing detailed connection status
        """
        # Get basic auth status
        auth_service = QBOAuthService(self.db, business_id)
        auth_status = auth_service.get_connection_status()
        
        # Get connection manager health if connected
        connection_manager_status = None
        if auth_status.get("connected"):
            try:
                connection_manager = get_qbo_connection_manager(self.db, business_id)
                connection_manager_status = connection_manager.get_connection_health()
            except Exception as e:
                connection_manager_status = {"status": "error", "message": str(e)}
        
        return {
            **auth_status,
            "connection_manager": connection_manager_status,
            "infrastructure": "qbo_setup"
        }
    
    def disconnect_qbo(self, business_id: str) -> Dict[str, Any]:
        """
        Disconnect QBO integration and clean up connection manager.
        
        Args:
            business_id: Business identifier
            
        Returns:
            Dict containing disconnection status
        """
        logger.info(f"Disconnecting QBO for business {business_id}")
        
        # Disconnect via auth service
        auth_service = QBOAuthService(self.db, business_id)
        auth_result = auth_service.disconnect()
        
        # Clean up connection manager if it exists
        try:
            connection_manager = get_qbo_connection_manager(self.db, business_id)
            connection_manager.cleanup()
            logger.info(f"Connection manager cleaned up for business {business_id}")
        except Exception as e:
            logger.warning(f"Failed to cleanup connection manager: {e}")
        
        return {
            "status": "disconnected" if auth_result else "error",
            "message": "QBO integration disconnected successfully" if auth_result else "QBO integration not found",
            "infrastructure": "qbo_setup"
        }
    
    def verify_connection_health(self, business_id: str) -> Dict[str, Any]:
        """
        Verify QBO connection health and test API connectivity.
        
        Args:
            business_id: Business identifier
            
        Returns:
            Dict containing health verification results
        """
        try:
            connection_manager = get_qbo_connection_manager(self.db, business_id)
            health_status = connection_manager.get_connection_health()
            
            # Test API connectivity
            test_result = connection_manager.test_api_connectivity()
            
            return {
                "status": "healthy" if health_status.get("status") == "healthy" else "degraded",
                "connection_manager": health_status,
                "api_test": test_result,
                "infrastructure": "qbo_setup"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "infrastructure": "qbo_setup"
            }
