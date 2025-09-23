from fastapi import HTTPException
from sqlalchemy.orm import Session
from domains.core.models.business import Business
from domains.core.models.user import User
from domains.core.models.integration import Integration
from domains.core.services.audit_log import AuditLogService
from domains.integrations.smart_sync import SmartSyncService
from runway.core.services.data_quality_analyzer import DataQualityAnalyzer
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
                
                # Generate Runway Replay - retroactive digest showing what we would have recommended
                runway_replay = self.generate_runway_replay(integration.business_id)
                
                # Generate Initial Hygiene Score - surface data quality issues
                hygiene_score = self.generate_initial_hygiene_score(integration.business_id)
                
                # Store both runway replay and hygiene score in integration details
                integration.runway_replay_data = runway_replay
                integration.runway_replay_data["hygiene_score"] = hygiene_score
                
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
                
                # Generate Runway Replay - retroactive digest showing what we would have recommended
                runway_replay = self.generate_runway_replay(integration.business_id)
                
                # Generate Initial Hygiene Score - surface data quality issues
                hygiene_score = self.generate_initial_hygiene_score(integration.business_id)
                
                # Store both runway replay and hygiene score in integration details
                integration.runway_replay_data = runway_replay
                integration.runway_replay_data["hygiene_score"] = hygiene_score
            
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
    
    async def generate_runway_replay(self, business_id: str) -> Dict[str, Any]:
        """
        Generate a retroactive 4-week runway digest showing what Oodaloo would have recommended.
        
        MVP Implementation: Uses historical QBO data to simulate past runway decisions.
        Shows proof of value by demonstrating insights we would have provided.
        
        Args:
            business_id: Business identifier
            
        Returns:
            Dict containing runway replay data with weekly breakdowns and recommendations
        """
        try:
            logger.info(f"Generating runway replay for business {business_id}")
            
            # Get business info
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise BusinessNotFoundError(f"Business {business_id} not found")
            
            # Use SmartSyncService to get historical QBO data
            smart_sync = SmartSyncService(self.db, business_id)
            qbo_data = await smart_sync.get_qbo_data_for_digest()
            
            # Generate 4 weeks of historical analysis
            weeks_data = []
            current_date = datetime.now()
            
            for week_offset in range(4, 0, -1):  # 4 weeks ago to 1 week ago
                week_start = current_date - timedelta(weeks=week_offset)
                week_end = week_start + timedelta(days=6)
                
                # MVP: Simulate historical data based on current QBO state
                # In production, this would use actual historical data
                week_analysis = self._generate_weekly_analysis(
                    business_id, week_start, week_end, qbo_data, week_offset
                )
                weeks_data.append(week_analysis)
            
            # Calculate overall impact metrics
            total_runway_protected = sum(week["runway_protected_days"] for week in weeks_data)
            total_recommendations = sum(len(week["recommendations"]) for week in weeks_data)
            critical_catches = sum(1 for week in weeks_data if week["critical_issues"] > 0)
            
            replay_summary = {
                "business_name": business.name,
                "replay_period": "Past 4 weeks",
                "generated_at": current_date.isoformat(),
                "total_runway_protected_days": total_runway_protected,
                "total_recommendations": total_recommendations,
                "critical_catches": critical_catches,
                "weeks": weeks_data,
                "proof_statement": self._generate_proof_statement(
                    total_runway_protected, total_recommendations, critical_catches
                )
            }
            
            logger.info(f"Runway replay generated: {total_runway_protected} days protected, {total_recommendations} recommendations")
            return replay_summary
            
        except BusinessNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate runway replay for {business_id}: {e}", exc_info=True)
            # Return minimal replay data on error
            return {
                "business_name": business.name if 'business' in locals() else "Unknown",
                "error": "Could not generate full replay",
                "message": "We're still setting up your historical analysis. Your weekly digest will start next week!",
                "generated_at": datetime.now().isoformat()
            }
    
    def _generate_weekly_analysis(self, business_id: str, week_start: datetime, 
                                 week_end: datetime, qbo_data: Dict[str, Any], 
                                 week_offset: int) -> Dict[str, Any]:
        """
        Generate analysis for a specific week using current QBO data as baseline.
        
        MVP Approach: Simulate realistic scenarios based on current business state.
        """
        # Extract actual QBO data
        invoices = qbo_data.get("invoices", [])
        bills = qbo_data.get("bills", [])
        balances = qbo_data.get("balances", [])
        
        # Calculate actual financial position from QBO data
        total_cash = sum(balance.get("current_balance", 0) for balance in balances)
        ar_amount = sum(inv.get("amount", 0) for inv in invoices if inv.get("status") != "paid")
        ap_amount = sum(bill.get("amount", 0) for bill in bills if bill.get("status") != "paid")
        
        # Calculate runway based on actual data
        monthly_expenses = sum(bill.get("amount", 0) for bill in bills) if bills else 0
        daily_burn = monthly_expenses / 30 if monthly_expenses > 0 else RunwayAnalysisSettings.DEFAULT_DAILY_BURN_RATE
        runway_days = (total_cash + ar_amount - ap_amount) / daily_burn if daily_burn > 0 else 0
        
        # Generate recommendations based on actual data patterns
        recommendations = []
        runway_protected = 0
        critical_issues = 0
        
        # Analyze overdue bills for AP optimization using core analyzer
        data_quality_analyzer = DataQualityAnalyzer(self.db, business_id)
        overdue_bills = [bill for bill in bills if data_quality_analyzer.is_bill_overdue_by_date(bill, week_end)]
        if overdue_bills:
            overdue_amount = sum(bill.get("amount", 0) for bill in overdue_bills)
            if overdue_amount > 0:
                protected_days = (overdue_amount * RunwayAnalysisSettings.AP_OPTIMIZATION_EFFICIENCY) / daily_burn
                recommendations.append({
                    "type": "ap_timing",
                    "action": f"Address ${overdue_amount:,.0f} in overdue bills",
                    "runway_impact": f"+{protected_days:.1f} days",
                    "reasoning": "Resolve overdue payments to avoid late fees"
                })
                runway_protected += protected_days
                if overdue_amount > total_cash * RunwayAnalysisSettings.AP_CRITICAL_THRESHOLD:
                    critical_issues += 1
        
        # Analyze overdue invoices for AR collection using core analyzer
        overdue_invoices = [inv for inv in invoices if data_quality_analyzer.is_invoice_overdue_by_date(inv, week_end)]
        if overdue_invoices:
            overdue_ar = sum(inv.get("amount", 0) for inv in overdue_invoices)
            if overdue_ar > 0:
                protected_days = (overdue_ar * RunwayAnalysisSettings.AR_COLLECTION_EFFICIENCY) / daily_burn
                recommendations.append({
                    "type": "ar_collections",
                    "action": f"Follow up on ${overdue_ar:,.0f} in overdue invoices",
                    "runway_impact": f"+{protected_days:.1f} days",
                    "reasoning": "Accelerate collections on aging receivables"
                })
                runway_protected += protected_days
        
        # Critical runway assessment
        if runway_days < RunwayAnalysisSettings.RUNWAY_CRITICAL_DAYS:
            critical_issues += 1
            recommendations.append({
                "type": "critical_alert",
                "action": "Immediate cash flow review needed",
                "runway_impact": "Prevents shortfall",
                "reasoning": "Runway below 2-week safety threshold"
            })
        
        return {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "week_label": f"{week_offset} week{'s' if week_offset > 1 else ''} ago",
            "runway_days": round(runway_days, 1),
            "cash_position": total_cash,
            "ar_outstanding": round(ar_amount),
            "ap_upcoming": round(ap_amount),
            "recommendations": recommendations,
            "runway_protected_days": round(runway_protected, 1),
            "critical_issues": critical_issues
        }
    
    def _generate_proof_statement(self, total_protected: float, total_recs: int, 
                                 critical_catches: int) -> str:
        """Generate a compelling proof statement for the runway replay."""
        if total_protected > 10:
            return f"In just 4 weeks, Oodaloo would have protected {total_protected:.0f} days of runway with {total_recs} smart recommendations!"
        elif critical_catches > 0:
            return f"Oodaloo caught {critical_catches} critical cash flow issue{'s' if critical_catches > 1 else ''} that could have caused problems."
        elif total_recs > 0:
            return f"Oodaloo identified {total_recs} optimization opportunities to improve your cash flow management."
        else:
            return "Your cash flow looks healthy! Oodaloo will help you maintain this strong position."
    
    def generate_initial_hygiene_score(self, business_id: str) -> Dict[str, Any]:
        """
        Generate an initial hygiene score by analyzing QBO data quality issues.
        
        MVP Implementation: Identifies common data quality issues that affect runway accuracy.
        Translates hygiene fixes into runway impact to motivate immediate action.
        
        Args:
            business_id: Business identifier
            
        Returns:
            Dict containing hygiene score, issues found, and runway impact of fixes
        """
        try:
            logger.info(f"Generating hygiene score for business {business_id}")
            
            # Get business info
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise BusinessNotFoundError(f"Business {business_id} not found")
            
            # Use SmartSyncService to get current QBO data
            smart_sync = SmartSyncService(self.db, business_id)
            qbo_data = smart_sync.get_qbo_data_for_digest()
            
            # Use core DataQualityAnalyzer for comprehensive hygiene analysis
            data_quality_analyzer = DataQualityAnalyzer(self.db, business_id)
            hygiene_analysis = data_quality_analyzer.calculate_hygiene_score(qbo_data)
            
            # Extract results from core analyzer
            hygiene_score = hygiene_analysis["hygiene_score"]
            issues = hygiene_analysis["issues"]
            total_runway_impact_days = hygiene_analysis["total_runway_impact_days"]
            
            # Determine overall health level based on score
            if hygiene_score >= 90:
                health_level = "excellent"
                health_message = "Your QBO data is in excellent shape for accurate runway tracking!"
            elif hygiene_score >= 75:
                health_level = "good"
                health_message = "Your QBO data is mostly clean with room for improvement."
            elif hygiene_score >= 60:
                health_level = "fair"
                health_message = "Some data quality issues are affecting your runway accuracy."
            elif hygiene_score >= 40:
                health_level = "needs_attention"
                health_message = "Several data quality issues need attention for accurate runway tracking."
            else:
                health_level = "critical"
                health_message = "Your data quality needs immediate attention for reliable runway analysis."
            
            # Generate priority recommendations
            priority_fixes = sorted(issues, key=lambda x: x["runway_impact_days"], reverse=True)[:3]
            
            hygiene_result = {
                "business_name": business.name,
                "hygiene_score": hygiene_score,
                "health_level": health_level,
                "health_message": health_message,
                "total_issues_found": len(issues),
                "total_runway_impact_days": round(total_runway_impact_days, 1),
                "issues": issues,
                "priority_fixes": priority_fixes,
                "summary_statement": self._generate_hygiene_summary(
                    hygiene_score, len(issues), total_runway_impact_days
                ),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Hygiene score generated: {hygiene_score}/100, {len(issues)} issues, +{total_runway_impact_days:.1f} days potential")
            return hygiene_result
            
        except BusinessNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate hygiene score for {business_id}: {e}", exc_info=True)
            # Return minimal hygiene data on error
            return {
                "business_name": business.name if 'business' in locals() else "Unknown",
                "hygiene_score": 50,  # Neutral score
                "health_level": "unknown",
                "health_message": "We're still analyzing your QBO data quality.",
                "error": "Could not complete full analysis",
                "generated_at": datetime.now().isoformat()
            }
    
    
    
    
    def _generate_hygiene_summary(self, score: int, issue_count: int, 
                                 runway_impact: float) -> str:
        """Generate a compelling summary statement for the hygiene score."""
        if runway_impact > 5:
            return f"Fix these {issue_count} data quality issues to protect **+{runway_impact:.0f} days** of runway!"
        elif issue_count > 0:
            return f"Clean up {issue_count} data quality issue{'s' if issue_count > 1 else ''} to improve runway accuracy."
        else:
            return "Excellent! Your QBO data is clean and ready for accurate runway tracking."
