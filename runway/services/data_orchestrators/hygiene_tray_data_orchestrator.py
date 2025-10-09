"""
Hygiene Tray Data Orchestrator

Manages data pulling and state management for the Hygiene Tray experience,
which focuses on data quality issues that need to be fixed before bills and
invoices can be processed for decision-making.

This orchestrator follows the ADR-006 Data Orchestrator Pattern:
- Pulls bills and invoices with data quality issues
- Manages tray item state (processing status, priorities)
- Provides clean interface between TrayService and domain services
- Maintains ADR-001 domain separation principles
- Ensures multi-tenant safety with business_id scoping
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from domains.qbo.services.sync_service import QBOSyncService
from domains.core.models.business import Business
import logging
import json

logger = logging.getLogger(__name__)


class HygieneTrayDataOrchestrator:
    """
    Data orchestrator for Hygiene Tray experience.
    
    Pulls bills and invoices that have data quality issues and need
    to be cleaned up before they can be used for decision-making.
    Manages tray item state (processing status, priorities) with
    proper multi-tenant isolation.
    """
    
    def __init__(self, db: Session):
        self.db = db  # No instance state - stateless service
        # Initialize SmartSyncService for QBO data
        self.smart_sync = QBOSyncService("", "", db)
    
    async def get_tray_data(self, business_id: str) -> Dict[str, Any]:
        """
        Get all data needed for the Hygiene Tray experience.
        
        Args:
            business_id: The business to get data for
            
        Returns:
            Dictionary containing bills, invoices, and tray state
        """
        try:
            # Initialize SmartSyncService with business_id
            smart_sync = QBOSyncService(business_id, "", self.db)
            
            # Pull bills and invoices from QBO
            bills_data = await smart_sync.get_bills()
            invoices_data = await smart_sync.get_invoices()
            company_info = await smart_sync.get_company_info()
            
            # Extract the actual data arrays
            bills = bills_data.get("bills", [])
            invoices = invoices_data.get("invoices", [])
            balances = company_info.get("balances", [])
            
            # Get current tray state
            tray_state = await self._get_tray_state(business_id)
            
            logger.info(f"Retrieved tray data for business {business_id}: "
                       f"{len(bills)} bills, {len(invoices)} invoices")
            
            return {
                "bills": bills,
                "invoices": invoices,
                "balances": balances,
                "tray_state": tray_state,
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
    
    async def update_tray_item_status(self, business_id: str, item_id: str, status: str) -> Dict[str, Any]:
        """
        Update the processing status of a tray item.
        
        Args:
            business_id: The business the item belongs to
            item_id: The ID of the item to update
            status: New status (e.g., 'processing', 'completed', 'error')
            
        Returns:
            Updated tray data with the item status updated
        """
        try:
            # Update the item status in tray state
            await self._update_item_status(business_id, item_id, status)
            
            # Return updated tray data
            return await self.get_tray_data(business_id)
            
        except Exception as e:
            logger.error(f"Error updating tray item status for business {business_id}: {e}")
            raise
    
    async def set_tray_priorities(self, business_id: str, priorities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Set priority order for tray items.
        
        Args:
            business_id: The business the priorities are for
            priorities: List of items with their priority order
            
        Returns:
            Updated tray data with priorities set
        """
        try:
            # Store priorities in tray state
            await self._store_tray_priorities(business_id, priorities)
            
            # Return updated tray data
            return await self.get_tray_data(business_id)
            
        except Exception as e:
            logger.error(f"Error setting tray priorities for business {business_id}: {e}")
            raise
    
    async def _get_tray_state(self, business_id: str) -> Dict[str, Any]:
        """Get the current tray state for a business.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                return {"item_statuses": {}, "priorities": [], "processing_queue": []}
            
            # For now, store tray state in business metadata
            # In the future, this could be a separate TrayState model
            if hasattr(business, 'metadata') and business.metadata:
                metadata = json.loads(business.metadata) if isinstance(business.metadata, str) else business.metadata
                return metadata.get('tray_state', {
                    "item_statuses": {},
                    "priorities": [],
                    "processing_queue": []
                })
            
            return {"item_statuses": {}, "priorities": [], "processing_queue": []}
            
        except Exception as e:
            logger.error(f"Error getting tray state for business {business_id}: {e}")
            return {"item_statuses": {}, "priorities": [], "processing_queue": []}
    
    async def _update_item_status(self, business_id: str, item_id: str, status: str) -> None:
        """Update the status of a specific tray item.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise ValueError(f"Business {business_id} not found")
            
            # Get current tray state
            current_state = await self._get_tray_state(business_id)
            
            # Update item status
            current_state["item_statuses"][item_id] = {
                "status": status,
                "updated_at": self._get_current_timestamp()
            }
            
            # Update business metadata
            metadata = json.loads(business.metadata) if business.metadata else {}
            metadata['tray_state'] = current_state
            business.metadata = json.dumps(metadata)
            
            self.db.commit()
            
            logger.info(f"Updated tray item {item_id} status to {status} for business {business_id}")
            
        except Exception as e:
            logger.error(f"Error updating item status for business {business_id}: {e}")
            raise
    
    async def _store_tray_priorities(self, business_id: str, priorities: List[Dict[str, Any]]) -> None:
        """Store priority order for tray items.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise ValueError(f"Business {business_id} not found")
            
            # Get current tray state
            current_state = await self._get_tray_state(business_id)
            
            # Update priorities
            current_state["priorities"] = priorities
            
            # Update business metadata
            metadata = json.loads(business.metadata) if business.metadata else {}
            metadata['tray_state'] = current_state
            business.metadata = json.dumps(metadata)
            
            self.db.commit()
            
            logger.info(f"Updated tray priorities for business {business_id}")
            
        except Exception as e:
            logger.error(f"Error storing tray priorities for business {business_id}: {e}")
            raise
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
