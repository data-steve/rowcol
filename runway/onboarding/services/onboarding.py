from fastapi import HTTPException
from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.user import User
from domains.core.models.integration import Integration
from domains.core.services.audit_log import AuditLogService
from db.transaction import db_transaction
from common.exceptions import (
    OnboardingError, 
    BusinessNotFoundError, 
    IntegrationError,
    ValidationError
)
from config.business_rules import OnboardingSettings, IntegrationStatuses
from typing import Dict, Any, List
from datetime import datetime, timedelta
import secrets
import os
import logging

logger = logging.getLogger(__name__)

class OnboardingService:
    def __init__(self, db: Session):
        self.db = db
        self.qbo_client_id = os.getenv("QBO_CLIENT_ID", "mock_client_id")
        self.qbo_redirect_uri = os.getenv("QBO_REDIRECT_URI", "http://localhost:8000/auth/qbo/callback")
        self.environment = os.getenv("ENVIRONMENT", "development")

    def start_qbo_connection(self, business_id: str, user_id: str) -> Dict[str, Any]:
        """Initiate QBO OAuth flow with mock or real authorization URL."""
        if self.environment == "development" or os.getenv("USE_MOCK_QBO", "true").lower() == "true":
            return self._mock_qbo_auth_start(business_id, user_id)
        else:
            return self._real_qbo_auth_start(business_id, user_id)

    def _mock_qbo_auth_start(self, business_id: str, user_id: str) -> Dict[str, Any]:
        """Mock QBO OAuth start for development."""
        state = secrets.token_urlsafe(32)
        
        # Store state in database for validation
        try:
            with db_transaction(self.db):
                integration = Integration(
                    business_id=business_id,
                    platform="qbo",
                    status=IntegrationStatuses.CONNECTING,
                    oauth_state=state,
                    created_by=user_id
                )
                self.db.add(integration)
        except Exception as e:
            logger.error(f"Failed to store OAuth state for business {business_id}: {e}")
            raise IntegrationError("Failed to initiate QBO connection", {"error": str(e)})
        
        mock_auth_url = f"http://localhost:8000/mock/qbo/auth?state={state}&business_id={business_id}"
        
        return {
            "auth_url": mock_auth_url,
            "state": state,
            "expires_in": 3600,
            "mock": True,
            "instructions": "This is a mock QBO connection. Click the URL to simulate OAuth flow."
        }

    def _real_qbo_auth_start(self, business_id: str, user_id: str) -> Dict[str, Any]:
        """Real QBO OAuth start for production."""
        from intuitlib.client import AuthClient
        from intuitlib.enums import Scopes
        
        state = secrets.token_urlsafe(32)
        
        # Store state in database for validation
        try:
            with db_transaction(self.db):
                integration = Integration(
                    business_id=business_id,
                    platform="qbo",
                    status=IntegrationStatuses.CONNECTING,
                    oauth_state=state,
                    created_by=user_id
                )
                self.db.add(integration)
        except Exception as e:
            logger.error(f"Failed to store OAuth state for business {business_id}: {e}")
            raise IntegrationError("Failed to initiate QBO connection", {"error": str(e)})
        
        auth_client = AuthClient(
            client_id=self.qbo_client_id,
            client_secret=os.getenv("QBO_CLIENT_SECRET"),
            redirect_uri=self.qbo_redirect_uri,
            environment="sandbox"
        )
        
        scopes = [Scopes.ACCOUNTING]
        auth_url = auth_client.get_authorization_url(scopes, state)
        
        return {
            "auth_url": auth_url,
            "state": state,
            "expires_in": 3600,
            "mock": False
        }

    def complete_qbo_connection(self, state: str, authorization_code: str, realm_id: str) -> Dict[str, Any]:
        """Complete QBO OAuth flow and store tokens."""
        # Find integration by state
        integration = self.db.query(Integration).filter(
            Integration.oauth_state == state,
            Integration.platform == "qbo",
            Integration.status == IntegrationStatuses.CONNECTING
        ).first()
        
        if not integration:
            logger.warning(f"Invalid or expired OAuth state: {state}")
            raise IntegrationError("Invalid or expired OAuth state")
        
        if self.environment == "development" or os.getenv("USE_MOCK_QBO", "true").lower() == "true":
            return self._mock_qbo_auth_complete(integration, authorization_code, realm_id)
        else:
            return self._real_qbo_auth_complete(integration, authorization_code, realm_id)

    def _mock_qbo_auth_complete(self, integration: Integration, auth_code: str, realm_id: str) -> Dict[str, Any]:
        """Mock QBO OAuth completion."""
        try:
            with db_transaction(self.db):
                # Update integration with mock tokens
                integration.status = IntegrationStatuses.CONNECTED
                integration.access_token = f"mock_access_token_{secrets.token_hex(16)}"
                integration.refresh_token = f"mock_refresh_token_{secrets.token_hex(16)}"
                integration.token_expires_at = datetime.now() + timedelta(hours=1)
                integration.realm_id = realm_id or f"mock_realm_{secrets.randint(100000, 999999)}"
                integration.connected_at = datetime.now()
                
                # Update business with QBO info
                business = self.db.query(Business).filter(
                    Business.business_id == integration.business_id
                ).first()
                if not business:
                    raise BusinessNotFoundError(f"Business {integration.business_id} not found")
                
                business.qbo_id = integration.realm_id
                business.qbo_connected = True
                
                # Log successful connection
                audit_service = AuditLogService(self.db)
                audit_service.log_event(
                    business_id=integration.business_id,
                    user_id=integration.created_by,
                    event_type="qbo_connected",
                    details={"realm_id": integration.realm_id, "mock": True}
                )
                
        except (BusinessNotFoundError, IntegrationError):
            raise
        except Exception as e:
            logger.error(f"Mock QBO auth completion failed: {e}", exc_info=True)
            raise IntegrationError("QBO connection failed", {"error": str(e)})
        
        return {
            "status": "connected",
            "realm_id": integration.realm_id,
            "business_id": integration.business_id,
            "mock": True,
            "message": "Mock QBO connection successful"
        }

    def _real_qbo_auth_complete(self, integration: Integration, auth_code: str, realm_id: str) -> Dict[str, Any]:
        """Real QBO OAuth completion."""
        from intuitlib.client import AuthClient
        
        auth_client = AuthClient(
            client_id=self.qbo_client_id,
            client_secret=os.getenv("QBO_CLIENT_SECRET"),
            redirect_uri=self.qbo_redirect_uri,
            environment="sandbox"
        )
        
        try:
            auth_client.get_bearer_token(auth_code, realm_id=realm_id)
            
            with db_transaction(self.db):
                # Update integration with real tokens
                integration.status = IntegrationStatuses.CONNECTED
                integration.access_token = auth_client.access_token
                integration.refresh_token = auth_client.refresh_token
                integration.token_expires_at = datetime.now() + timedelta(hours=1)
                integration.realm_id = realm_id
                integration.connected_at = datetime.now()
                
                # Update business with QBO info
                business = self.db.query(Business).filter(
                    Business.business_id == integration.business_id
                ).first()
                if not business:
                    raise BusinessNotFoundError(f"Business {integration.business_id} not found")
                
                business.qbo_id = realm_id
                business.qbo_connected = True
                
                # Log successful connection
                audit_service = AuditLogService(self.db)
                audit_service.log_event(
                    business_id=integration.business_id,
                    user_id=integration.created_by,
                    event_type="qbo_connected",
                    details={"realm_id": realm_id}
                )
            
            return {
                "status": "connected",
                "realm_id": realm_id,
                "business_id": integration.business_id,
                "mock": False,
                "message": "QBO connection successful"
            }
            
        except (BusinessNotFoundError, IntegrationError):
            raise
        except Exception as e:
            # Mark integration as failed
            try:
                with db_transaction(self.db):
                    integration.status = IntegrationStatuses.FAILED
                    integration.error_message = str(e)
            except Exception as db_error:
                logger.error(f"Failed to update integration status: {db_error}")
            
            logger.error(f"QBO OAuth completion failed: {str(e)}", exc_info=True)
            raise IntegrationError("QBO connection failed", {"error": str(e)})

    def get_onboarding_status(self, business_id: str) -> Dict[str, Any]:
        """Get comprehensive onboarding status for a business."""
        business = self.db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Check QBO integration status
        qbo_integration = self.db.query(Integration).filter(
            Integration.business_id == business_id,
            Integration.platform == "qbo"
        ).first()
        
        # Calculate completion percentage
        steps_completed = 0
        total_steps = 5
        
        steps = {
            "business_created": bool(business),
            "qbo_connected": bool(qbo_integration and qbo_integration.status == "connected"),
            "initial_sync": False,  # TODO: Check if initial data sync completed
            "digest_configured": False,  # TODO: Check if digest preferences set
            "first_tray_review": False  # TODO: Check if user has reviewed tray items
        }
        
        steps_completed = sum(steps.values())
        completion_percentage = (steps_completed / total_steps) * 100
        
        return {
            "business_id": business_id,
            "business_name": business.name,
            "completion_percentage": completion_percentage,
            "steps": steps,
            "qbo_integration": {
                "status": qbo_integration.status if qbo_integration else "not_started",
                "realm_id": qbo_integration.realm_id if qbo_integration else None,
                "connected_at": qbo_integration.connected_at.isoformat() if qbo_integration and qbo_integration.connected_at else None,
                "mock": self.environment == "development" or os.getenv("USE_MOCK_QBO", "true").lower() == "true"
            },
            "next_steps": self._get_next_steps(steps)
        }

    def _get_next_steps(self, steps: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Get recommended next steps based on current onboarding progress."""
        next_steps = []
        
        if not steps["qbo_connected"]:
            next_steps.append({
                "step": "connect_qbo",
                "title": "Connect QuickBooks Online",
                "description": "Link your QBO account to sync financial data",
                "priority": "high",
                "estimated_time": "2-3 minutes"
            })
        elif not steps["initial_sync"]:
            next_steps.append({
                "step": "initial_sync",
                "title": "Initial Data Sync",
                "description": "Sync your recent transactions and account balances",
                "priority": "high",
                "estimated_time": "5-10 minutes"
            })
        elif not steps["digest_configured"]:
            next_steps.append({
                "step": "configure_digest",
                "title": "Configure Weekly Digest",
                "description": "Set up your weekly runway email preferences",
                "priority": "medium",
                "estimated_time": "2-3 minutes"
            })
        elif not steps["first_tray_review"]:
            next_steps.append({
                "step": "review_tray",
                "title": "Review Prep Tray",
                "description": "Check and resolve pending financial items",
                "priority": "medium",
                "estimated_time": "5-15 minutes"
            })
        else:
            next_steps.append({
                "step": "complete",
                "title": "Onboarding Complete!",
                "description": "You're all set up and ready to manage your runway",
                "priority": "low",
                "estimated_time": "0 minutes"
            })
        
        return next_steps

    def qualify_onboarding(self, business_data: Dict[str, Any], user_data: Dict[str, Any]) -> Business:
        """Create business and initial user with enhanced validation."""
        # Enhanced business validation
        for field in OnboardingSettings.REQUIRED_BUSINESS_FIELDS:
            if field not in business_data or not business_data[field]:
                raise ValidationError(f"Missing required business field: {field}")
        
        # Enhanced user validation
        for field in OnboardingSettings.REQUIRED_USER_FIELDS:
            if field not in user_data or not user_data[field]:
                raise ValidationError(f"Missing required user field: {field}")
        
        try:
            with db_transaction(self.db):
                # Create business
                business = Business(**business_data)
                self.db.add(business)
                self.db.flush()  # Get business_id without committing
                
                # Create initial user
                user_data["business_id"] = business.business_id
                user_data["role"] = user_data.get("role", "owner")
                user = User(**user_data)
                self.db.add(user)
                self.db.flush()  # Get user_id without committing
                
                # Log onboarding start
                audit_service = AuditLogService(self.db)
                audit_service.log_event(
                    business_id=business.business_id,
                    user_id=user.user_id,
                    event_type="onboarding_started",
                    details={
                        "business_name": business.name,
                        "industry": business.industry,
                        "employee_count": business.employee_count
                    }
                )
                
                logger.info(f"Business onboarding started: {business.business_id}")
                return business
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Onboarding qualification failed: {str(e)}", exc_info=True)
            raise OnboardingError("Onboarding failed", {"error": str(e)})
