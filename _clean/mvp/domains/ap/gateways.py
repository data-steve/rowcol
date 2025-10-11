"""
AP (Bills) Domain Gateway for MVP

Rail-agnostic interface for bills operations.
Products call this; it decides cache vs. remote via sync orchestrator.
"""

from typing import Protocol, List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime

from infra.sync.entity_policy import FreshnessHint

class Bill(BaseModel):
    """Domain model for a bill."""
    bill_id: str
    advisor_id: str
    business_id: str
    qbo_id: str
    vendor_id: Optional[str] = None
    vendor_name: Optional[str] = None
    due_date: Optional[date] = None
    amount: Decimal
    status: str = "OPEN"  # OPEN, SCHEDULED, PAID
    source_version: Optional[str] = None
    last_synced_at: Optional[datetime] = None

class ListBillsQuery(BaseModel):
    """Query parameters for listing bills."""
    advisor_id: str
    business_id: str
    status: str = "OPEN"  # OPEN, SCHEDULED, PAID, or ALL
    freshness_hint: FreshnessHint = "CACHED_OK"

class UpdateBillRequest(BaseModel):
    """Request to update a bill."""
    bill_id: str
    advisor_id: str
    business_id: str
    updates: dict  # Field updates to apply

class BillsGateway(Protocol):
    """
    Rail-agnostic interface for bills operations.
    
    This protocol defines the interface that all bills implementations must follow.
    The actual implementation will use the sync orchestrator to handle caching
    and data freshness according to the Smart Sync pattern.
    """
    
    def list(self, query: ListBillsQuery) -> List[Bill]:
        """
        List bills for an advisor and business.
        
        Args:
            query: Query parameters including advisor_id, business_id, status, and freshness_hint
            
        Returns:
            List of Bill domain objects
        """
        ...
    
    def list_incomplete(self, query: ListBillsQuery) -> List[Bill]:
        """
        List bills with missing data for Hygiene Tray.
        
        Only returns bills that have data quality issues:
        - Missing vendor_name
        - Missing due_date
        - Zero or negative amount
        - Missing required QBO fields
        
        Args:
            query: Query parameters including advisor_id, business_id, status, and freshness_hint
            
        Returns:
            List of Bill domain objects with missing data
        """
        ...
    
    def list_payment_ready(self, query: ListBillsQuery) -> List[Bill]:
        """
        List bills ready for payment scheduling for Decision Console.
        
        Only returns bills that are complete and ready for payment scheduling:
        - Has vendor_name
        - Has due_date
        - Has positive amount
        - Status is OPEN or SCHEDULED
        - All required QBO fields present
        
        Args:
            query: Query parameters including advisor_id, business_id, status, and freshness_hint
            
        Returns:
            List of Bill domain objects ready for payment scheduling
        """
        ...
    
    def list_by_due_days(self, query: ListBillsQuery, due_days: int = 30) -> List[Bill]:
        """
        List bills due within specified days.
        
        Args:
            query: Query parameters including advisor_id, business_id, status, and freshness_hint
            due_days: Number of days to look ahead (default 30)
            
        Returns:
            List of Bill domain objects due within specified days
        """
        ...
    
    def get_by_id(self, advisor_id: str, business_id: str, bill_id: str) -> Optional[Bill]:
        """
        Get a specific bill by ID.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            bill_id: Bill identifier
            
        Returns:
            Bill domain object or None if not found
        """
        ...
    
    def update_bill(self, request: UpdateBillRequest) -> bool:
        """
        Update a bill.
        
        Args:
            request: Update request with bill details
            
        Returns:
            True if update was successful, False otherwise
        """
        ...
    
    def get_payment_history(self, bill_id: str) -> List[dict]:
        """
        Get payment history for a bill (AP - bills that have been sent for payment).
        
        Args:
            bill_id: Bill identifier
            
        Returns:
            List of payment history records (bills that have been paid)
        """
        ...
    
