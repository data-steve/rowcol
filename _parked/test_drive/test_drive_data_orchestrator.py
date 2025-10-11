"""
Test Drive Data Orchestrator

Manages data pulling and state management for the Test Drive PLG experience,
which provides a "try before you buy" experience using real historical data
or sandbox demo data.

This orchestrator follows the ADR-006 Data Orchestrator Pattern:
- Pulls 4 weeks of historical data for real business analysis
- Provides sandbox demo data for prospects without real data
- Manages test drive state (progress, insights, recommendations)
- Provides clean interface between TestDriveService and domain services
- Maintains ADR-001 domain separation principles
- Ensures multi-tenant safety with business_id scoping
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from domains.qbo.services.sync_service import QBOSyncService
from domains.core.models.business import Business
import logging
import json

logger = logging.getLogger(__name__)


class TestDriveDataOrchestrator:
    """
    Data orchestrator for Test Drive PLG experience.
    
    Handles both real historical data analysis and sandbox demo data
    for prospects who don't have their own business data yet.
    Manages test drive state (progress, insights, recommendations) with
    proper multi-tenant isolation.
    """
    
    def __init__(self, db: Session):
        self.db = db  # No instance state - stateless service
        # Initialize SmartSyncService for QBO data
        self.smart_sync = QBOSyncService("", "", db)
    
    async def get_test_drive_data(self, business_id: str = None, use_sandbox: bool = False) -> Dict[str, Any]:
        """
        Get test drive data - real historical data or sandbox demo data.
        
        Args:
            business_id: The business to get data for (None for sandbox)
            use_sandbox: Whether to use sandbox data instead of real data
            
        Returns:
            Dictionary containing test drive data and state
        """
        try:
            if use_sandbox or business_id is None:
                return await self._get_sandbox_data()
            else:
                return await self._get_historical_data(business_id)
                
        except Exception as e:
            logger.error(f"Error getting test drive data: {e}")
            raise
    
    async def _get_historical_data(self, business_id: str) -> Dict[str, Any]:
        """
        Pull 4 weeks of historical data for real business analysis.
        
        Args:
            business_id: The business to get historical data for
            
        Returns:
            Dictionary containing historical data and test drive state
        """
        try:
            # Initialize SmartSyncService with business_id
            smart_sync = QBOSyncService(business_id, "", self.db)
            
            # Pull 4 weeks of historical data from QBO
            bills_data = await smart_sync.get_bills()
            invoices_data = await smart_sync.get_invoices()
            company_info = await smart_sync.get_company_info()
            
            # Extract the actual data arrays
            bills = bills_data.get("bills", [])
            invoices = invoices_data.get("invoices", [])
            balances = company_info.get("balances", [])
            
            # Get current test drive state
            test_drive_state = await self._get_test_drive_state(business_id)
            
            logger.info(f"Retrieved historical test drive data for business {business_id}: "
                       f"{len(bills)} bills, {len(invoices)} invoices")
            
            return {
                "bills": bills,
                "invoices": invoices,
                "balances": balances,
                "test_drive_state": test_drive_state,
                "business_id": business_id,
                "data_type": "historical",
                "synced_at": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error getting historical data for business {business_id}: {e}")
            raise
    
    async def _get_sandbox_data(self) -> Dict[str, Any]:
        """
        Use existing sandbox data generation for demos.
        
        Returns:
            Dictionary containing sandbox demo data and test drive state
        """
        try:
            # TODO: Integrate with existing sandbox data generation
            # For now, return mock data structure
            sandbox_data = {
                "bills": [
                    {
                        "id": "sandbox_bill_1",
                        "vendor": "Office Supplies Inc",
                        "amount": 150.00,
                        "due_date": "2024-02-15",
                        "status": "pending"
                    },
                    {
                        "id": "sandbox_bill_2", 
                        "vendor": "Internet Provider",
                        "amount": 89.99,
                        "due_date": "2024-02-20",
                        "status": "pending"
                    }
                ],
                "invoices": [
                    {
                        "id": "sandbox_invoice_1",
                        "customer": "ABC Corp",
                        "amount": 2500.00,
                        "due_date": "2024-02-25",
                        "status": "sent"
                    }
                ],
                "balances": [
                    {
                        "account": "Checking",
                        "balance": 15420.50
                    }
                ]
            }
            
            # Get sandbox test drive state
            test_drive_state = await self._get_sandbox_test_drive_state()
            
            logger.info("Retrieved sandbox test drive data")
            
            return {
                **sandbox_data,
                "test_drive_state": test_drive_state,
                "business_id": "sandbox",
                "data_type": "sandbox",
                "synced_at": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error getting sandbox data: {e}")
            raise
    
    async def update_test_drive_progress(self, business_id: str, progress: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update test drive progress and insights.
        
        Args:
            business_id: The business the progress is for
            progress: Progress data (current_step, insights, recommendations)
            
        Returns:
            Updated test drive data with progress updated
        """
        try:
            # Update the progress in test drive state
            await self._update_test_drive_progress(business_id, progress)
            
            # Return updated test drive data
            return await self.get_test_drive_data(business_id)
            
        except Exception as e:
            logger.error(f"Error updating test drive progress for business {business_id}: {e}")
            raise
    
    async def _get_test_drive_state(self, business_id: str) -> Dict[str, Any]:
        """Get the current test drive state for a business.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                return {
                    "current_step": "start",
                    "progress_percentage": 0,
                    "insights": [],
                    "recommendations": [],
                    "completed_at": None
                }
            
            # For now, store test drive state in business metadata
            # In the future, this could be a separate TestDriveState model
            if hasattr(business, 'metadata') and business.metadata:
                metadata = json.loads(business.metadata) if isinstance(business.metadata, str) else business.metadata
                return metadata.get('test_drive_state', {
                    "current_step": "start",
                    "progress_percentage": 0,
                    "insights": [],
                    "recommendations": [],
                    "completed_at": None
                })
            
            return {
                "current_step": "start",
                "progress_percentage": 0,
                "insights": [],
                "recommendations": [],
                "completed_at": None
            }
            
        except Exception as e:
            logger.error(f"Error getting test drive state for business {business_id}: {e}")
            return {
                "current_step": "start",
                "progress_percentage": 0,
                "insights": [],
                "recommendations": [],
                "completed_at": None
            }
    
    async def _get_sandbox_test_drive_state(self) -> Dict[str, Any]:
        """Get sandbox test drive state (not scoped to business_id)."""
        return {
            "current_step": "demo",
            "progress_percentage": 0,
            "insights": [],
            "recommendations": [],
            "completed_at": None,
            "is_sandbox": True
        }
    
    async def _update_test_drive_progress(self, business_id: str, progress: Dict[str, Any]) -> None:
        """Update test drive progress and insights.
        
        SECURITY: All state operations are scoped by business_id to ensure
        complete isolation between businesses in multi-tenant environment.
        """
        try:
            # CRITICAL: Always filter by business_id for multi-tenant safety
            business = self.db.query(Business).filter(Business.business_id == business_id).first()
            if not business:
                raise ValueError(f"Business {business_id} not found")
            
            # Get current test drive state
            current_state = await self._get_test_drive_state(business_id)
            
            # Update progress
            current_state.update({
                **progress,
                "updated_at": self._get_current_timestamp()
            })
            
            # Update business metadata
            metadata = json.loads(business.metadata) if business.metadata else {}
            metadata['test_drive_state'] = current_state
            business.metadata = json.dumps(metadata)
            
            self.db.commit()
            
            logger.info(f"Updated test drive progress for business {business_id}")
            
        except Exception as e:
            logger.error(f"Error updating test drive progress for business {business_id}: {e}")
            raise
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
