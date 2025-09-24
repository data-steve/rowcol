"""
ARPayment Model - AR Payment Data Structure

This model defines the data structure for AR payments:
- Payment receipt and recording fields
- Invoice matching and allocation data
- Deposit reconciliation data fields
- QBO payment synchronization identifiers

Business logic handled by PaymentMatchingService.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from domains.core.models.base import Base, TimestampMixin, TenantMixin
from datetime import datetime
from typing import Optional

class ARPayment(Base, TimestampMixin, TenantMixin):
    """
    AR Payment Model for Data Storage
    
    Data structure for AR payments. Business logic handled by PaymentMatchingService.
    """
    __tablename__ = 'ar_payments'
    
    # Core Identity
    payment_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False, index=True)
    qbo_payment_id = Column(String(255), nullable=True, index=True)
    
    # Payment Information
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    received_date = Column(DateTime, nullable=True)  # When payment was actually received
    
    # Payment Method and Details
    payment_method = Column(String(50), nullable=True)  # check, ach, credit_card, cash, wire
    reference_number = Column(String(100), nullable=True)  # Check number, transaction ID, etc.
    payment_account = Column(String(100), nullable=True)  # Bank account where received
    
    # Matching and Allocation
    primary_invoice_id = Column(Integer, ForeignKey('invoices.invoice_id'), nullable=True)
    allocation_details = Column(JSON, nullable=True)  # How payment is allocated across invoices
    matching_confidence = Column(Float, default=0.0)  # Confidence in automatic matching (0-1)
    matching_method = Column(String(50), nullable=True)  # auto, manual, fuzzy, exact
    
    # Status and Processing
    status = Column(String(50), default="pending")  # pending, matched, reconciled, disputed, reversed
    processing_status = Column(String(50), default="unprocessed")  # unprocessed, processing, processed, failed
    is_reconciled = Column(Boolean, default=False)  # Reconciled with bank deposit
    is_fully_allocated = Column(Boolean, default=False)  # Fully allocated to invoices
    
    # Reconciliation Information
    bank_transaction_id = Column(String(255), nullable=True)  # Link to bank transaction
    deposit_date = Column(DateTime, nullable=True)  # When deposited in bank
    reconciliation_date = Column(DateTime, nullable=True)  # When reconciled
    reconciliation_notes = Column(Text, nullable=True)
    
    # Dispute and Adjustment Handling
    is_disputed = Column(Boolean, default=False)
    dispute_reason = Column(Text, nullable=True)
    dispute_date = Column(DateTime, nullable=True)
    adjustment_amount = Column(Float, default=0.0)  # Write-offs, discounts, etc.
    
    # Metadata and Notes
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)  # Additional custom fields (renamed from metadata to avoid SQLAlchemy conflict)
    
    # Relationships
    business = relationship("Business", back_populates="ar_payments")
    customer = relationship("Customer")
    primary_invoice = relationship("Invoice", foreign_keys=[primary_invoice_id])
    
    @hybrid_property
    def net_amount(self) -> float:
        """Calculate net payment amount after adjustments."""
        return self.amount + self.adjustment_amount
    
    @hybrid_property
    def unallocated_amount(self) -> float:
        """Calculate amount not yet allocated to invoices."""
        if not self.allocation_details:
            return self.net_amount
        
        allocated = sum(
            allocation.get("amount", 0) 
            for allocation in self.allocation_details.get("allocations", [])
        )
        
        return self.net_amount - allocated
    
    @hybrid_property
    def days_since_received(self) -> Optional[int]:
        """Calculate days since payment was received."""
        if self.received_date:
            return (datetime.utcnow() - self.received_date).days
        return None
    
    @hybrid_property
    def is_overpayment(self) -> bool:
        """Check if this is an overpayment (more than invoice total)."""
        if self.primary_invoice and self.primary_invoice.total:
            return self.net_amount > self.primary_invoice.total
        return False
    

# For backward compatibility, keep Payment as alias
Payment = ARPayment
