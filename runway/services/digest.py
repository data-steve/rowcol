from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from domains.core.models.business import Business
from domains.core.models.user import User
from domains.ap.models.bill import Bill
from domains.ar.models.invoice import Invoice
from domains.core.services.qbo_integration import QBOIntegrationService
from runway.services.email import EmailService
from common.exceptions import BusinessNotFoundError, RunwayCalculationError, EmailDeliveryError
from config.business_rules import DigestSettings, RunwayThresholds
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DigestService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()

    def calculate_runway(self, business_id: str) -> Dict[str, float]:
        """Calculate runway metrics for a business"""
        business = self.db.query(Business).filter(Business.business_id == business_id).first()
        if not business:
            raise ValueError("Business not found")
        
        qbo = QBOIntegrationService(business)
        
        # Get recent balance data
        balances = self.db.query(Balance).filter(
            Balance.business_id == business_id,
            Balance.snapshot_date >= datetime.utcnow() - timedelta(days=1)
        ).all()
        
        # Get AR and AP data from QBO
        overdue_invoices = qbo.get_invoices(self.db, aging_days=30)
        upcoming_bills = qbo.get_bills(self.db, due_days=14)
        
        # Calculate totals
        cash = sum(b.available_balance for b in balances)
        ar_total = sum(i["amount"] for i in overdue_invoices)
        ap_total = sum(b["amount"] for b in upcoming_bills)
        
        # Calculate burn rate using business rules
        burn_rate = DigestSettings.DEFAULT_BURN_RATE_MONTHLY
        runway_days = (cash + ar_total - ap_total) / (burn_rate / 30) if burn_rate else 0
        
        return {
            "runway_days": max(0, runway_days),
            "cash": cash,
            "ar_overdue": ar_total,
            "ap_due_soon": ap_total,
            "burn_rate": burn_rate,
            "net_position": cash + ar_total - ap_total
        }

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
