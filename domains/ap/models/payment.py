"""
Payment model for AP payment tracking and QBO integration.

Stores payment records with execution status, reconciliation data, and QBO sync fields.
Business logic handled by PaymentService.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from domains.core.models.base import Base, TimestampMixin, TenantMixin
from decimal import Decimal

class PaymentStatus:
    """Payment status constants."""
    PENDING = "pending"
    SCHEDULED = "scheduled" 
    PROCESSING = "processing"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RECONCILED = "reconciled"

class PaymentType:
    """Payment type constants."""
    BILL_PAYMENT = "bill_payment"
    ADVANCE_PAYMENT = "advance_payment"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"

class Payment(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'ap_payments'
    
    payment_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=False)
    bill_id = Column(Integer, ForeignKey('bills.bill_id'), nullable=True)
    
    # QBO Integration
    qbo_payment_id = Column(String(255), nullable=True, index=True)
    qbo_sync_token = Column(String(50), nullable=True)
    qbo_last_sync = Column(DateTime, nullable=True)
    
    # Payment Core Fields
    payment_type = Column(String(50), default=PaymentType.BILL_PAYMENT)
    amount_cents = Column(Integer, nullable=False)  # Precise financial storage
    payment_date = Column(DateTime, nullable=False)
    execution_date = Column(DateTime, nullable=True)
    
    # Payment Method
    payment_method = Column(String(50), nullable=False)  # 'ach', 'check', 'card'
    payment_account = Column(String(100), nullable=True)
    check_number = Column(String(50), nullable=True)
    confirmation_number = Column(String(255), nullable=True)
    
    # Status Tracking
    status = Column(String(50), default=PaymentStatus.PENDING)
    failure_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciled_date = Column(DateTime, nullable=True)
    reconciled_by = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    bank_transaction_id = Column(String(255), nullable=True)
    
    # Processing
    processing_fee_cents = Column(Integer, default=0)
    batch_id = Column(String(36), nullable=True)
    
    # Approval (for RowCol CAS firm workflows)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_by = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="payments")
    bill = relationship("Bill", back_populates="payments")
    business = relationship("Business", back_populates="ap_payments")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    reconciled_by_user = relationship("User", foreign_keys=[reconciled_by])
    created_by_user = relationship("User", foreign_keys=[created_by])
    transaction_logs = relationship("PaymentTransactionLog", back_populates="payment")
    
    # Hybrid properties for decimal conversion (essential for financial precision)
    @hybrid_property
    def amount(self) -> Decimal:
        """Payment amount in dollars."""
        return Decimal(self.amount_cents) / 100
    
    @amount.setter
    def amount(self, value: Decimal):
        """Set amount from decimal dollars."""
        self.amount_cents = int(value * 100)
    
    @hybrid_property
    def processing_fee(self) -> Decimal:
        """Processing fee in dollars."""
        return Decimal(self.processing_fee_cents) / 100
    
    @processing_fee.setter
    def processing_fee(self, value: Decimal):
        """Set processing fee from decimal dollars."""
        self.processing_fee_cents = int(value * 100)
