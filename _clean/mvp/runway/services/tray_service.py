"""
Tray Service - Hygiene and Data Quality Management

This service provides hygiene tray functionality for advisors to manage
data quality issues and sync problems. It uses domain gateways directly
with filtering methods for incomplete records.
"""

from typing import Dict, Any, List, Optional, Protocol
import logging

logger = logging.getLogger(__name__)

class TrayService:
    """Service for hygiene tray functionality."""
    
    def __init__(self, advisor_id: str, business_id: str, realm_id: str, 
                 bills_gateway, invoices_gateway):
        self.advisor_id = advisor_id
        self.business_id = business_id
        self.realm_id = realm_id
        self.bills_gateway = bills_gateway
        self.invoices_gateway = invoices_gateway
        
        logger.info(f"Initialized TrayService for advisor {advisor_id}, business {business_id}")
    
    async def get_bill_tray(self) -> Dict[str, Any]:
        """Get bills with hygiene issues for advisor review."""
        from mvp.domains.ap.models import ListBillsQuery
        
        # Get incomplete bills using domain gateway filtering
        query = ListBillsQuery(
            advisor_id=self.advisor_id,
            business_id=self.business_id,
            realm_id=self.realm_id
        )
        
        incomplete_bills = await self.bills_gateway.list_incomplete(query)
        
        # Organize by urgency (simplified for now)
        urgent_bills = [bill for bill in incomplete_bills if self._is_urgent(bill)]
        upcoming_bills = [bill for bill in incomplete_bills if not self._is_urgent(bill)]
        
        return {
            "advisor_id": self.advisor_id,
            "business_id": self.business_id,
            "urgent_bills": urgent_bills,
            "upcoming_bills": upcoming_bills,
            "urgent_count": len(urgent_bills),
            "upcoming_count": len(upcoming_bills),
            "total_count": len(incomplete_bills),
            "total_amount": sum(bill.amount for bill in incomplete_bills),
            "last_updated": "2024-01-01T00:00:00Z"  # TODO: Get from sync orchestrator
        }
    
    async def fix_bill_hygiene(self, bill_id: str, fixes: Dict[str, Any]) -> bool:
        """Fix hygiene issues in bill data."""
        try:
            # TODO: Implement bill update through domain gateway
            logger.info(f"Fixing hygiene issues for bill {bill_id}: {fixes}")
            return True
        except Exception as e:
            logger.error(f"Failed to fix hygiene issues for bill {bill_id}: {e}")
            return False
    
    async def get_hygiene_summary(self) -> Dict[str, Any]:
        """Get summary of hygiene issues and data quality."""
        bill_tray = await self.get_bill_tray()
        
        return {
            "advisor_id": self.advisor_id,
            "business_id": self.business_id,
            "total_bills": bill_tray["total_count"],
            "urgent_issues": bill_tray["urgent_count"],
            "upcoming_issues": bill_tray["upcoming_count"],
            "total_amount": bill_tray["total_amount"],
            "runway_impact": self._calculate_runway_impact(bill_tray["total_amount"]),
            "last_updated": bill_tray["last_updated"]
        }
    
    def _is_urgent(self, bill) -> bool:
        """Check if bill has urgent hygiene issues."""
        # Simplified urgency logic - bills missing critical data are urgent
        return (
            not bill.vendor_name or
            not bill.due_date or
            bill.amount <= 0
        )
    
    def _calculate_runway_impact(self, total_amount: float) -> int:
        """Calculate runway impact in days (simplified)."""
        # TODO: Implement proper runway calculation
        return int(total_amount / 1000)  # Simplified: $1000 per day
