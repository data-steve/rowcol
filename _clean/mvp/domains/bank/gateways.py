"""
Bank (Balances) Domain Gateway for MVP

Rail-agnostic interface for account balances operations.
Products call this; it decides cache vs. remote via sync orchestrator.
"""

from typing import Protocol, List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

from infra.sync.entity_policy import FreshnessHint

class AccountBalance(BaseModel):
    """Domain model for an account balance."""
    account_id: str
    advisor_id: str
    business_id: str
    qbo_id: str
    account_name: Optional[str] = None
    available: Decimal
    current: Decimal
    account_type: Optional[str] = None  # checking, savings, etc.
    source_version: Optional[str] = None
    last_synced_at: Optional[datetime] = None

class ListBalancesQuery(BaseModel):
    """Query parameters for listing account balances."""
    advisor_id: str
    business_id: str
    account_type: Optional[str] = None  # Filter by account type
    freshness_hint: FreshnessHint = "CACHED_OK"

class BalancesGateway(Protocol):
    """
    Rail-agnostic interface for account balances operations.
    
    This protocol defines the interface that all balances implementations must follow.
    The actual implementation will use the sync orchestrator to handle caching
    and data freshness according to the Smart Sync pattern.
    """
    
    def list(self, query: ListBalancesQuery) -> List[AccountBalance]:
        """
        List account balances for an advisor and business.
        
        Args:
            query: Query parameters including advisor_id, business_id, account_type, and freshness_hint
            
        Returns:
            List of AccountBalance domain objects
        """
        ...
    
    def get_by_id(self, advisor_id: str, business_id: str, account_id: str) -> Optional[AccountBalance]:
        """
        Get a specific account balance by ID.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            account_id: Account identifier
            
        Returns:
            AccountBalance domain object or None if not found
        """
        ...
    
    def get_total_available(self, advisor_id: str, business_id: str) -> Decimal:
        """
        Get total available balance across all accounts.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            
        Returns:
            Total available balance
        """
        ...
    
    def get_total_current(self, advisor_id: str, business_id: str) -> Decimal:
        """
        Get total current balance across all accounts.
        
        Args:
            advisor_id: Advisor identifier
            business_id: Business identifier
            
        Returns:
            Total current balance
        """
        ...
