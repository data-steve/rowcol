from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from domains.core.models.business import Business
from domains.core.models.user import User
from runway.services.0_data_orchestrators.digest_data_orchestrator import DigestDataOrchestrator, DigestConfig
from runway.services.1_calculators.runway_calculator import RunwayCalculator
from runway.services.1_calculators.insight_calculator import InsightCalculator
from common.exceptions import BusinessNotFoundError, EmailDeliveryError
from infra.config import DigestSettings, feature_gates
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DigestService:
    def __init__(self, db: Session):
        self.db = db
        # Use DigestDataOrchestrator for data management
        self.data_orchestrator = DigestDataOrchestrator(db)
        # Add insight calculator for enhanced analysis
        self.insight_calculator = InsightCalculator(db, "digest", validate_business=False)
        # self.email_service = EmailService()  # TODO: Create email service

    def calculate_runway(self, business_id: str) -> Dict[str, float]:
        """Calculate runway metrics for a business using centralized RunwayCalculator."""
        business = self.db.query(Business).filter(Business.business_id == business_id).first()
        if not business:
            raise ValueError("Business not found")
        
        # Use centralized RunwayCalculator for all runway calculations
        runway_calculator = RunwayCalculator(self.db, business_id)
        runway_data = runway_calculator.calculate_current_runway()
        
        # Return data in digest-specific format
        return {
            "runway_days": runway_data.get("current_runway_days", 0),
            "cash": runway_data.get("cash_position", 0),
            "ar_overdue": runway_data.get("ar_position", 0),
            "ap_due_soon": runway_data.get("ap_position", 0),
            "burn_rate": runway_data.get("burn_rate", {}).get("monthly_burn", 0),
            "net_position": runway_data.get("net_position", 0)
        }
    
    async def get_digest_data(self, business_id: str) -> Dict[str, Any]:
        """Get digest data using DigestDataOrchestrator with feature gating."""
        try:
            # Use weekly digest configuration
            config = DigestConfig.for_weekly()
            digest_data = await self.data_orchestrator.get_digest_data(business_id, config)
            
            # Apply feature gating to control data sources
            if feature_gates.can_use_feature("qbo_only_mode"):
                # QBO-only mode: Show only QBO data, hide multi-rail features
                digest_data = self._filter_qbo_only_data(digest_data)
            elif not feature_gates.can_use_feature("multi_rail_data_sources"):
                # Limited mode: Show available data sources only
                digest_data = self._filter_available_data_sources(digest_data)
            
            return digest_data
            
        except Exception as e:
            logger.error(f"Error getting digest data for business {business_id}: {e}")
            raise

    async def generate_and_send_digest(self, business_id: str) -> Dict[str, any]:
        """Generate digest and send email to business owner"""
        try:
            # Get business and owner
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise ValueError(f"Business {business_id} not found")
            
            owner = self.db.query(User).filter(
                User.business_id == business_id,
                User.role == "owner"
            ).first()
            
            if not owner:
                logger.warning(f"No owner found for business {business_id}")
                return {"success": False, "error": "No owner email found"}
            
            # Calculate runway metrics
            digest_data = self.calculate_runway(business_id)
            
            # Send digest email
            email_result = await self.email_service.send_digest_email(
                to_email=owner.email,
                business_name=business.name,
                digest_data=digest_data
            )
            
            if email_result.success:
                logger.info(f"Digest sent successfully to {owner.email} for business {business.name}")
                return {
                    "success": True,
                    "message_id": email_result.message_id,
                    "provider": email_result.provider,
                    "digest_data": digest_data
                }
            else:
                logger.error(f"Failed to send digest: {email_result.error}")
                return {
                    "success": False,
                    "error": email_result.error,
                    "digest_data": digest_data
                }
                
        except BusinessNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating digest for business {business_id}: {e}", exc_info=True)
            raise EmailDeliveryError("Digest generation failed", {"error": str(e)})

    async def send_digest_to_all_businesses(self) -> Dict[str, any]:
        """Send digest to all active businesses"""
        businesses = self.db.query(Business).all()
        results = []
        
        for business in businesses:
            result = await self.generate_and_send_digest(business.business_id)
            results.append({
                "business_id": business.business_id,
                "business_name": business.name,
                **result
            })
        
        successful = sum(1 for r in results if r.get("success"))
        total = len(results)
        
        logger.info(f"Digest batch complete: {successful}/{total} successful")
        
        return {
            "total_businesses": total,
            "successful_sends": successful,
            "failed_sends": total - successful,
            "results": results
        }

    def get_digest_preview(self, business_id: str) -> Dict[str, any]:
        """Get digest data without sending email (for testing/preview)"""
        try:
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise ValueError(f"Business {business_id} not found")
            
            digest_data = self.calculate_runway(business_id)
            
            return {
                "success": True,
                "business_name": business.name,
                "digest_data": digest_data,
                "html_preview": self.email_service._generate_digest_html(business.name, digest_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating digest preview: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _filter_qbo_only_data(self, digest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter digest data to show only QBO data sources."""
        filtered_data = digest_data.copy()
        
        # Remove multi-rail specific data
        if "data_sources" in filtered_data:
            filtered_data["data_sources"] = {
                "qbo": filtered_data["data_sources"].get("qbo", {}),
                "available_rails": ["qbo"]
            }
        
        # Remove Ramp-specific features
        if "reserve_management" in filtered_data:
            del filtered_data["reserve_management"]
        
        if "payment_execution" in filtered_data:
            del filtered_data["payment_execution"]
        
        # Add QBO-only mode indicator
        filtered_data["mode"] = "qbo_only"
        filtered_data["limitations"] = [
            "Payment execution requires external processing",
            "Reserve management not available",
            "Multi-rail data sources disabled"
        ]
        
        return filtered_data
    
    def _filter_available_data_sources(self, digest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter digest data based on available data sources."""
        filtered_data = digest_data.copy()
        
        # Get available data sources from feature gates
        available_sources = feature_gates.get_available_data_sources()
        
        if "data_sources" in filtered_data:
            filtered_sources = {}
            for source in available_sources:
                if source in filtered_data["data_sources"]:
                    filtered_sources[source] = filtered_data["data_sources"][source]
            filtered_data["data_sources"] = filtered_sources
            filtered_data["data_sources"]["available_rails"] = available_sources
        
        return filtered_data
