"""
Decision Console Data Orchestrator

Manages data pulling and state management for the Decision Console experience,
which provides a "single pane of glass" for making context-laden financial
decisions with prioritization.

This orchestrator follows the ADR-006 Data Orchestrator Pattern:
- Pulls bills and invoices ready for decision-making
- Manages decision queue state
- Provides clean interface between ConsoleService and domain services
- Maintains ADR-001 domain separation principles
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from domains.qbo.services.sync_service import QBOSyncService
from domains.core.models.business import Business
import logging
import json

logger = logging.getLogger(__name__)


class DecisionConsoleDataOrchestrator:
    """
    Data orchestrator for Decision Console experience.
    
    Pulls bills and invoices ready for decision-making and manages
    the decision queue state for the console experience.
    """
    
    def __init__(self, db: Session):
        self.db = db
        # Initialize SmartSyncService for QBO data
        self.smart_sync = QBOSyncService("", "", db)
    
    async def get_console_data(self, business_id: str) -> Dict[str, Any]:
        """
        Get all data needed for the Decision Console experience.
        
        Args:
            business_id: The business to get data for
            
        Returns:
            Dictionary containing bills, invoices, balances, and decision queue
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
            
            # Get current decision queue
            decision_queue = await self._get_decision_queue(business_id)
            
            logger.info(f"Retrieved console data for business {business_id}: "
                       f"{len(bills)} bills, {len(invoices)} invoices, "
                       f"{len(decision_queue)} decisions in queue")
            
            return {
                "bills": bills,
                "invoices": invoices,
                "balances": balances,
                "decision_queue": decision_queue,
                "business_id": business_id,
                "synced_at": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error getting console data for business {business_id}: {e}")
            raise
    
    async def add_decision(self, business_id: str, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a decision to the decision queue.
        
        Args:
            business_id: The business the decision is for
            decision: The decision data to store
            
        Returns:
            Updated console data with the new decision added
        """
        try:
            # Store the decision in the queue
            await self._store_decision(business_id, decision)
            
            # Return updated console data
            return await self.get_console_data(business_id)
            
        except Exception as e:
            logger.error(f"Error adding decision for business {business_id}: {e}")
            raise
    
    async def finalize_decisions(self, business_id: str) -> Dict[str, Any]:
        """
        Process all decisions in the queue and clear it.
        
        Args:
            business_id: The business to process decisions for
            
        Returns:
            Results of processing the decisions
        """
        try:
            # Get current decision queue
            decisions = await self._get_decision_queue(business_id)
            
            if not decisions:
                return {
                    "status": "success",
                    "decisions_processed": 0,
                    "message": "No decisions to process"
                }
            
            # Process each decision
            processed_count = 0
            errors = []
            
            for decision in decisions:
                try:
                    # Process the decision (e.g., send to QBO)
                    await self._process_decision(business_id, decision)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Error processing decision {decision.get('id')}: {e}")
                    errors.append({"decision_id": decision.get('id'), "error": str(e)})
            
            # Clear the decision queue
            await self._clear_decision_queue(business_id)
            
            logger.info(f"Finalized {processed_count} decisions for business {business_id}")
            
            return {
                "status": "success",
                "decisions_processed": processed_count,
                "errors": errors,
                "message": f"Processed {processed_count} decisions successfully"
            }
            
        except Exception as e:
            logger.error(f"Error finalizing decisions for business {business_id}: {e}")
            raise
    
    async def _get_decision_queue(self, business_id: str) -> List[Dict[str, Any]]:
        """Get the current decision queue for a business.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                return []
            
            # For now, store decisions in business metadata
            # In the future, this could be a separate DecisionQueue model
            if hasattr(business, 'metadata') and business.metadata:
                metadata = json.loads(business.metadata) if isinstance(business.metadata, str) else business.metadata
                return metadata.get('decision_queue', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting decision queue for business {business_id}: {e}")
            return []
    
    async def _store_decision(self, business_id: str, decision: Dict[str, Any]) -> None:
        """Store a decision in the decision queue.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise ValueError(f"Business {business_id} not found")
            
            # Get current decision queue
            current_queue = await self._get_decision_queue(business_id)
            
            # Add new decision with timestamp
            decision_with_meta = {
                **decision,
                "id": f"decision_{len(current_queue) + 1}",
                "created_at": self._get_current_timestamp(),
                "status": "pending"
            }
            
            current_queue.append(decision_with_meta)
            
            # Update business metadata
            metadata = json.loads(business.metadata) if business.metadata else {}
            metadata['decision_queue'] = current_queue
            business.metadata = json.dumps(metadata)
            
            self.db.commit()
            
            logger.info(f"Stored decision for business {business_id}")
            
        except Exception as e:
            logger.error(f"Error storing decision for business {business_id}: {e}")
            raise
    
    async def _process_decision(self, business_id: str, decision: Dict[str, Any]) -> None:
        """Process a single decision (e.g., send to QBO)."""
        # This is where we would integrate with QBO API to process the decision
        # For now, just log the decision
        logger.info(f"Processing decision {decision.get('id')} for business {business_id}: {decision}")
        
        # TODO: Implement actual QBO integration for decision processing
    
    async def _clear_decision_queue(self, business_id: str) -> None:
        """Clear the decision queue for a business.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                return
            
            # Clear decision queue from metadata
            metadata = json.loads(business.metadata) if business.metadata else {}
            metadata['decision_queue'] = []
            business.metadata = json.dumps(metadata)
            
            self.db.commit()
            
            logger.info(f"Cleared decision queue for business {business_id}")
            
        except Exception as e:
            logger.error(f"Error clearing decision queue for business {business_id}: {e}")
            raise
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
