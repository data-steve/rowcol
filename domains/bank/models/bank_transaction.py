"""
Bank Transaction Model for Oodaloo

PURPOSE: Simple bank transaction tracking for single business owners
- Store bank feed transactions from QBO
- Basic categorization for cash flow tracking  
- Support runway calculations with actual bank data

SCOPE: Oodaloo Phase 2-3 (single business owner)
NOT: Multi-client allocation, complex rules engine (that's RowCol - see _parked/)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin
from datetime import datetime

class BankTransaction(Base, TimestampMixin):
    """
    Simple bank transaction for Oodaloo business owners.
    
    Stores bank feed data with basic categorization for cash flow tracking.
    """
    __tablename__ = "bank_transactions"

    id = Column(String(36), primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False, index=True)
    
    # QBO Integration
    qbo_transaction_id = Column(String(255), nullable=True, index=True)
    qbo_bank_account_id = Column(String(255), nullable=True)
    
    # Transaction Data
    amount_cents = Column(Integer, nullable=False)  # Store as cents for precision
    description = Column(String(500), nullable=False)
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Simple Categorization (Phase 2)
    category = Column(String(100), nullable=True)  # Office, Travel, Marketing, etc.
    notes = Column(Text, nullable=True)  # User notes
    
    # Source Tracking
    source = Column(String(50), nullable=False, default='qbo_bank_feed')  # qbo_bank_feed, manual, csv_import
    account_name = Column(String(200), nullable=True)  # Bank account name
    
    # Simple Status
    is_reviewed = Column(String(10), default='false')  # User has reviewed this transaction
    
    # Relationships
    business = relationship("Business", back_populates="bank_transactions")

    @property
    def amount_dollars(self) -> float:
        """Convert cents to dollars for display."""
        return self.amount_cents / 100.0
    
    @property
    def is_income(self) -> bool:
        """True if this is income (positive amount)."""
        return self.amount_cents > 0
    
    @property
    def is_expense(self) -> bool:
        """True if this is an expense (negative amount)."""
        return self.amount_cents < 0

# TODO: Phase 2 - Add simple categorization
# - Common expense categories (Office, Travel, Marketing, Equipment)
# - User-defined custom categories
# - Category suggestions based on description

# TODO: Phase 3 - QBO Integration  
# - Real-time bank feed imports
# - Bank account reconciliation
# - Automatic duplicate detection

# PARKED for RowCol:
# - Rules engine and automation
# - Multi-client allocation
# - Approval workflows
# - Complex GL account mapping
# - Unbundling and fee analysis
