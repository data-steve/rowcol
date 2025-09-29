"""
Hygiene Tray Data Orchestrator

Manages data pulling for the Hygiene Tray experience, which focuses on
data quality issues that need to be fixed before bills and invoices
can be processed for decision-making.

This orchestrator follows the ADR-006 Data Orchestrator Pattern:
- Pulls bills and invoices with data quality issues
- Provides clean interface between TrayService and domain services
- Maintains ADR-001 domain separation principles
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from infra.qbo.smart_sync import SmartSyncService
import logging

logger = logging.getLogger(__name__)


class HygieneTrayDataOrchestrator:
    """
    Data orchestrator for Hygiene Tray experience.
    
    Pulls bills and invoices that have data quality issues and need
    to be cleaned up before they can be used for decision-making.
    """
    
    def __init__(self, db: Session):
        self.db = db
        # Initialize SmartSyncService for QBO data
        self.smart_sync = SmartSyncService("", "", db)
    
    async def get_tray_data(self, business_id: str) -> Dict[str, Any]:
        """
        Get all data needed for the Hygiene Tray experience.
        
        Args:
            business_id: The business to get data for
            
        Returns:
            Dictionary containing bills and invoices with data quality issues
        """
        try:
            # Initialize SmartSyncService with business_id
            smart_sync = SmartSyncService(business_id, "", self.db)
            
            # Pull bills and invoices from QBO
            bills_data = await smart_sync.get_bills()
            invoices_data = await smart_sync.get_invoices()
            company_info = await smart_sync.get_company_info()
            
            # Extract the actual data arrays
            bills = bills_data.get("bills", [])
            invoices = invoices_data.get("invoices", [])
            balances = company_info.get("balances", [])
            
            logger.info(f"Retrieved tray data for business {business_id}: "
                       f"{len(bills)} bills, {len(invoices)} invoices")
            
            return {
                "bills": bills,
                "invoices": invoices,
                "balances": balances,
                "business_id": business_id,
                "synced_at": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error getting tray data for business {business_id}: {e}")
            raise
    
    async def get_tray_items(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Get combined list of all tray items (bills + invoices) for easy processing.
        
        Args:
            business_id: The business to get items for
            
        Returns:
            Combined list of bills and invoices with data quality issues
        """
        data = await self.get_tray_data(business_id)
        
        # Combine bills and invoices into single list
        tray_items = []
        
        # Add bills with type indicator
        for bill in data["bills"]:
            bill["item_type"] = "bill"
            tray_items.append(bill)
        
        # Add invoices with type indicator
        for invoice in data["invoices"]:
            invoice["item_type"] = "invoice"
            tray_items.append(invoice)
        
        return tray_items
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
