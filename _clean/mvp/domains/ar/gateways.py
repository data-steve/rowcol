"""
AR (Invoices) Domain Gateway for MVP

Rail-agnostic interface for invoices operations.
Products call this; it decides cache vs. remote via sync orchestrator.
"""

from typing import Protocol, List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime

from infra.sync.entity_policy import FreshnessHint

class Invoice(BaseModel):
    """Domain model for an invoice."""
    invoice_id: str
    advisor_id: str
    business_id: str
    qbo_id: str
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    due_date: Optional[date] = None
    amount: Decimal
    status: str = "OPEN"  # OPEN, PARTIAL, PAID
    source_version: Optional[str] = None
    last_synced_at: Optional[datetime] = None

class ListInvoicesQuery(BaseModel):
    """Query parameters for listing invoices."""
    advisor_id: str
    business_id: str
    status: str = "OPEN"  # OPEN, PARTIAL, PAID, or ALL
    freshness_hint: FreshnessHint = "CACHED_OK"

class UpdateInvoiceRequest(BaseModel):
    """Request to update an invoice."""
    invoice_id: str
    advisor_id: str
    business_id: str
    updates: dict  # Field updates to apply

class InvoicesGateway(Protocol):
    """
    Rail-agnostic interface for invoices operations.
    
    This protocol defines the interface that all invoices implementations must follow.
    The actual implementation will use the sync orchestrator to handle caching
    and data freshness according to the Smart Sync pattern.
    """
    
    def list(self, query: ListInvoicesQuery) -> List[Invoice]:
        """
        List invoices for an advisor and business.
        
        Args:
            query: Query parameters including advisor_id, business_id, status, and freshness_hint
            
        Returns:
            List of Invoice domain objects
        """
        ...
    
    def list_incomplete(self, query: ListInvoicesQuery) -> List[Invoice]:
        """
        List invoices with missing data for Hygiene Tray.
        
        Only returns invoices that have data quality issues:
        - Missing customer_name
        - Missing due_date
        - Zero or negative amount
        - Missing required QBO fields
        
        Args:
            query: Query parameters including advisor_id, business_id, status, and freshness_hint
            
        Returns:
            List of Invoice domain objects with missing data
        """
        ...
    
    def list_collections_ready(self, query: ListInvoicesQuery) -> List[Invoice]:
        """
        List invoices ready for collections attention for Decision Console.
        
        Only returns invoices that are complete and need collections attention:
        - Has customer_name
        - Has due_date
        - Has positive amount
        - Status is OPEN or PARTIAL
        - All required QBO fields present
        - Overdue by specified days (default 30+ days)
        
        Args:
            query: Query parameters including advisor_id, business_id, status, and freshness_hint
            
        Returns:
            List of Invoice domain objects ready for collections attention
        """
        ...
    
    def list_by_aging_days(self, query: ListInvoicesQuery, aging_days: int = 30) -> List[Invoice]:
        """
        List invoices by aging days.
        
        Args:
            query: Query parameters including advisor_id, business_id, status, and freshness_hint
            aging_days: Number of days to look back for aging (default 30)
            
        Returns:
            List of Invoice domain objects by aging days
        """
        ...
    
    def get_by_id(self, advisor_id: str, business_id: str, invoice_id: str) -> Optional[Invoice]:
        """
        Get a specific invoice by ID.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            invoice_id: Invoice identifier
            
        Returns:
            Invoice domain object or None if not found
        """
        ...
    
    def update_invoice(self, request: UpdateInvoiceRequest) -> bool:
        """
        Update an invoice.
        
        Args:
            request: Update request with invoice details
            
        Returns:
            True if update was successful, False otherwise
        """
        ...
    
    def get_payment_history(self, invoice_id: str) -> List[dict]:
        """
        Get payment history for an invoice (AR - invoices that have received payment).
        
        Args:
            invoice_id: Invoice identifier
            
        Returns:
            List of payment history records (invoices that have received payment)
        """
        ...
