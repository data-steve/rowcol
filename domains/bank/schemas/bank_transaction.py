"""
Bank Transaction Schemas for Oodaloo

PURPOSE: Simple bank transaction schemas for single business owners
- Basic transaction data for QBO imports
- Simple categorization for cash flow tracking
- Cash flow summaries for runway calculations

SCOPE: Oodaloo Phase 2-3 (single business owner)
NOT: Multi-client fields, complex rules (that's RowCol - see _parked/)
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BankTransactionBase(BaseModel):
    """Base bank transaction data."""
    description: str = Field(..., description="Transaction description")
    amount_cents: int = Field(..., description="Amount in cents for precision")
    transaction_date: datetime = Field(..., description="When the transaction occurred")
    account_name: Optional[str] = Field(None, description="Bank account name")
    category: Optional[str] = Field(None, description="Expense category (Office, Travel, etc.)")
    notes: Optional[str] = Field(None, description="User notes")

class BankTransactionCreate(BankTransactionBase):
    """Schema for creating bank transactions."""
    qbo_transaction_id: Optional[str] = Field(None, description="QBO transaction ID")
    qbo_bank_account_id: Optional[str] = Field(None, description="QBO bank account ID")
    source: str = Field(default="qbo_bank_feed", description="Source of transaction data")

class BankTransactionResponse(BankTransactionBase):
    """Schema for bank transaction API responses."""
    id: str = Field(..., description="Transaction ID")
    business_id: str = Field(..., description="Business ID")
    qbo_transaction_id: Optional[str] = None
    source: str = Field(..., description="Source of transaction data")
    is_reviewed: str = Field(..., description="Has user reviewed this transaction")
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    amount_dollars: float = Field(..., description="Amount in dollars")
    is_income: bool = Field(..., description="True if income (positive)")
    is_expense: bool = Field(..., description="True if expense (negative)")

    class Config:
        from_attributes = True

class BankTransactionCategorize(BaseModel):
    """Schema for categorizing transactions."""
    category: str = Field(..., description="Category name (Office, Travel, Marketing, etc.)")
    notes: Optional[str] = Field(None, description="Optional categorization notes")

class CashFlowSummary(BaseModel):
    """Schema for cash flow summary data."""
    period_days: int = Field(..., description="Number of days in summary period")
    total_in_cents: int = Field(..., description="Total income in cents")
    total_out_cents: int = Field(..., description="Total expenses in cents")
    net_flow_cents: int = Field(..., description="Net cash flow in cents")
    transaction_count: int = Field(..., description="Number of transactions")
    
    @property
    def total_in_dollars(self) -> float:
        """Total income in dollars."""
        return self.total_in_cents / 100.0
    
    @property
    def total_out_dollars(self) -> float:
        """Total expenses in dollars."""
        return self.total_out_cents / 100.0
    
    @property
    def net_flow_dollars(self) -> float:
        """Net cash flow in dollars."""
        return self.net_flow_cents / 100.0

# TODO: Phase 3 - QBO Import Schemas
# class QBOBankFeedImport(BaseModel):
#     """Schema for importing QBO bank feed data."""
#     account_id: str
#     transactions: List[dict]

# PARKED for RowCol:
# - Multi-client transaction allocation
# - Rules and automation schemas
# - Complex approval workflows
# - Transfer detection schemas
