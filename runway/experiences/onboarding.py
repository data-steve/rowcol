from fastapi import HTTPException
from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.user import User
from domains.core.models.integration import Integration
from domains.core.services.audit_log import AuditLogService
from domains.integrations import SmartSyncService
from runway.experiences.test_drive import TestDriveService
from db.transaction import db_transaction
from common.exceptions import (
    OnboardingError, 
    BusinessNotFoundError, 
    IntegrationError,
    ValidationError
)
from config.business_rules import OnboardingSettings, IntegrationStatuses, RunwayAnalysisSettings
from typing import Dict, Any, List
from datetime import datetime, timedelta
import secrets
import os
import logging

logger = logging.getLogger(__name__)

class OnboardingService:
    def __init__(self, db: Session):
        self.db = db
        self.environment = os.getenv("ENVIRONMENT", "development")

    def start_qbo_connection(self, business_id: str, user_id: str) -> Dict[str, Any]:
        """Delegate QBO connection setup to infrastructure service."""
        from runway.infrastructure.qbo_setup.qbo_setup_service import QBOSetupService
        
        service = QBOSetupService(self.db)
        return service.start_qbo_connection(business_id, user_id)

    async def complete_qbo_connection(self, state: str, authorization_code: str, realm_id: str) -> Dict[str, Any]:
        """Delegate QBO connection completion to infrastructure service."""
        from runway.infrastructure.qbo_setup.qbo_setup_service import QBOSetupService
        
        service = QBOSetupService(self.db)
        return await service.complete_qbo_connection(state, authorization_code, realm_id)

    # QBO connection logic moved to domains/integrations/qbo/
    # Onboarding now delegates to QBOAuthService

    async def get_onboarding_status(self, business_id: str) -> Dict[str, Any]:
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
            "initial_sync": await self._check_initial_sync_completed(business_id),
            "digest_configured": self._check_digest_configured(business_id),
            "first_tray_review": await self._check_first_tray_review(business_id)
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
            "test_drive_available": {
                "test_drive_url": f"/api/v1/test-drive/{business_id}/test-drive",
                "hygiene_score_url": f"/api/v1/test-drive/{business_id}/hygiene-score"
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

    async def qualify_onboarding(self, business_data: Dict[str, Any], user_data: Dict[str, Any]) -> Business:
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
                
                # Log onboarding start - critical business event
                from domains.core.models.audit_log import AuditAction, EntityType, AuditSource
                audit_service = AuditLogService(self.db)
                await audit_service.log_audit_event(
                    user_id=user.user_id,
                    business_id=business.business_id,
                    action=AuditAction.SIGNUP,
                    entity_type=EntityType.USER,
                    entity_id=user.user_id,
                    new_values={
                        "business_name": business.name,
                        "industry": business.industry,
                        "user_email": user.email,
                        "user_role": user.role
                    },
                    source=AuditSource.USER,
                    context_metadata={
                        "onboarding_event": "business_started",
                        "business_id": business.business_id
                    }
                )
                
                logger.info(f"Business onboarding started: {business.business_id} for user: {user.user_id}")
                return business
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Onboarding qualification failed: {str(e)}", exc_info=True)
            raise OnboardingError("Onboarding failed", {"error": str(e)})
    
    # Test drive generation delegated to TestDriveService
    # Use TestDriveService.generate_test_drive() directly when needed
    
    async def _check_initial_sync_completed(self, business_id: str) -> bool:
        """Check if initial QBO data sync has been completed."""
        try:
            from domains.integrations import SmartSyncService
            smart_sync = SmartSyncService(self.db, business_id)
            qbo_data = await smart_sync.get_qbo_data_for_digest()
            
            # Check if we have meaningful data (bills, invoices, or cash data)
            has_bills = len(qbo_data.get("bills", [])) > 0
            has_invoices = len(qbo_data.get("invoices", [])) > 0
            has_cash_data = qbo_data.get("cash_position", 0) > 0
            
            return has_bills or has_invoices or has_cash_data
        except Exception as e:
            logger.warning(f"Error checking initial sync for business {business_id}: {e}")
            return False
    
    def _check_digest_configured(self, business_id: str) -> bool:
        """Check if digest preferences have been configured."""
        try:
            # For now, assume digest is configured if business exists and QBO is connected
            # In the future, this could check for specific digest preferences
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            integration = self.db.query(Integration).filter(
                Integration.business_id == business_id,
                Integration.platform == "qbo"
            ).first()
            
            return bool(business and integration and integration.status == "connected")
        except Exception as e:
            logger.warning(f"Error checking digest configuration for business {business_id}: {e}")
            return False
    
    async def _check_first_tray_review(self, business_id: str) -> bool:
        """Check if user has reviewed tray items."""
        try:
            # For now, assume tray has been reviewed if we have QBO data
            # In the future, this could check for specific user interactions
            from domains.integrations import SmartSyncService
            smart_sync = SmartSyncService(self.db, business_id)
            qbo_data = await smart_sync.get_qbo_data_for_digest()
            
            # If we have bills or invoices, assume user has seen them in the tray
            has_bills = len(qbo_data.get("bills", [])) > 0
            has_invoices = len(qbo_data.get("invoices", [])) > 0
            
            return has_bills or has_invoices
        except Exception as e:
            logger.warning(f"Error checking tray review for business {business_id}: {e}")
            return False
