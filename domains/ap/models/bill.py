"""
Bill model for AP bill tracking and QBO integration.

Stores bill records with approval status, payment scheduling, and QBO sync fields.
Business logic handled by BillService.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from domains.core.models.base import Base, TimestampMixin, TenantMixin
from decimal import Decimal

class BillStatus:
    """Bill status constants for approval workflow."""
    PENDING = "pending"           # Initial state - needs review
    REVIEW = "review"            # Under review by user
    APPROVED = "approved"        # Approved for payment
    SCHEDULED = "scheduled"      # Payment scheduled
    PAID = "paid"               # Payment completed
    REJECTED = "rejected"       # Rejected - will not pay
    ON_HOLD = "on_hold"         # Temporarily on hold

class BillPriority:
    """Bill priority levels for tray categorization."""
    URGENT = "urgent"           # Must pay immediately (overdue, critical vendor)
    HIGH = "high"              # Should pay soon (due within week)
    MEDIUM = "medium"          # Can pay normally (due within 30 days)
    LOW = "low"                # Can delay (not due yet)

class Bill(Base, TimestampMixin, TenantMixin):
    __tablename__ = "bills"
    bill_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.vendor_id'), nullable=True)
    
    # QBO Integration Fields
    qbo_bill_id = Column(String(255), nullable=True, index=True)
    qbo_sync_token = Column(String(50), nullable=True)  # QBO sync token for updates
    qbo_last_sync = Column(DateTime, nullable=True)     # Last QBO sync timestamp
    qbo_version = Column(String(20), nullable=True)     # QBO entity version
    
    # Core Bill Information
    bill_number = Column(String(100), nullable=True)    # Vendor's bill number
    amount_cents = Column(Integer, nullable=False)      # Amount in cents for precision
    due_date = Column(DateTime, nullable=True)
    issue_date = Column(DateTime, nullable=True)        # Bill issue date
    
    # Approval Workflow Fields
    status = Column(String(50), default=BillStatus.PENDING)
    priority = Column(String(20), nullable=True)        # BillPriority enum
    approval_status = Column(String(50), nullable=True) # Separate approval tracking
    approved_by = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Payment Scheduling Fields
    scheduled_payment_date = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)  # 'ach', 'check', 'card', 'wire'
    payment_account = Column(String(100), nullable=True) # Bank account for payment
    payment_reference = Column(String(255), nullable=True) # Payment reference number
    
    # Runway Reserve Integration
    reserve_allocation_id = Column(String(36), nullable=True) # Link to runway reserve
    is_reserved = Column(Boolean, default=False)        # Whether funds are reserved
    reserve_amount_cents = Column(Integer, default=0)   # Amount reserved for this bill
    
    # Categorization and Processing
    extracted_fields = Column(JSON, nullable=True)      # OCR/document extraction data
    gl_account = Column(String(100), nullable=True)     # Suggested GL account
    expense_category = Column(String(100), nullable=True) # Expense category
    confidence = Column(Float, default=0.0)             # Categorization confidence
    
    # Workflow Tracking
    requires_approval = Column(Boolean, default=True)   # Whether bill needs approval
    approval_threshold_cents = Column(Integer, nullable=True) # Auto-approval threshold
    is_recurring = Column(Boolean, default=False)       # Recurring bill flag
    recurring_pattern = Column(String(50), nullable=True) # 'monthly', 'quarterly', etc.
    
    # Additional Metadata
    description = Column(Text, nullable=True)           # Bill description/memo
    tags = Column(JSON, nullable=True)                  # User-defined tags
    attachments = Column(JSON, nullable=True)           # File attachments metadata
    
    # Relationships
    vendor = relationship("Vendor", back_populates="bills")
    business = relationship("Business")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    payments = relationship("Payment", back_populates="bill")
    transaction_logs = relationship("BillTransactionLog", back_populates="bill")
    
    # Hybrid properties for decimal conversion
    @hybrid_property
    def amount(self) -> Decimal:
        """Bill amount in dollars."""
        return Decimal(self.amount_cents) / 100
    
    @amount.setter
    def amount(self, value: Decimal):
        """Set amount from decimal dollars."""
        self.amount_cents = int(value * 100)
    
    @hybrid_property
    def reserve_amount(self) -> Decimal:
        """Reserved amount in dollars."""
        return Decimal(self.reserve_amount_cents) / 100
    
    @reserve_amount.setter
    def reserve_amount(self, value: Decimal):
        """Set reserved amount from decimal dollars."""
        self.reserve_amount_cents = int(value * 100)
    