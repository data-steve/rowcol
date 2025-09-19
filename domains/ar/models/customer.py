"""
Customer Model - AR Customer Data Structure

This model defines the data structure for AR customers:
- Customer demographics and contact information
- Payment history tracking fields
- Collection preferences storage
- Risk assessment data fields
- QBO integration identifiers

Business logic handled by CustomerService.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from domains.core.models.base import Base, TimestampMixin, TenantMixin
from datetime import datetime
from typing import Optional

class Customer(Base, TimestampMixin, TenantMixin):
    """
    Customer Model for AR Data Storage
    
    Data structure for customer information. Business logic handled by CustomerService.
    """
    __tablename__ = 'customers'
    
    # Core Identity
    customer_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    qbo_customer_id = Column(String(255), nullable=True, index=True)
    
    # Customer Information
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    contact_name = Column(String(255), nullable=True)
    
    # Address Information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True, default="US")
    
    # Payment Terms and Preferences
    terms = Column(String(50), nullable=True)  # e.g., Net 30, Net 15
    credit_limit = Column(Float, nullable=True)
    preferred_payment_method = Column(String(50), nullable=True)  # check, ach, credit_card
    
    # Payment History and Scoring
    payment_reliability_score = Column(Float, default=50.0)  # 0-100 scale
    average_payment_days = Column(Float, nullable=True)  # Average days to pay
    total_invoiced_ytd = Column(Float, default=0.0)
    total_paid_ytd = Column(Float, default=0.0)
    last_payment_date = Column(DateTime, nullable=True)
    
    # Risk Assessment
    risk_score = Column(Float, default=50.0)  # 0-100 scale (higher = riskier)
    risk_category = Column(String(20), default="medium")  # low, medium, high
    credit_status = Column(String(20), default="good")  # excellent, good, fair, poor
    
    # Collection Preferences
    collection_preferences = Column(JSON, nullable=True)  # Email frequency, phone preferences, etc.
    communication_log = Column(JSON, nullable=True)  # Track collection contacts
    last_collection_contact = Column(DateTime, nullable=True)
    collection_notes = Column(Text, nullable=True)
    
    # Status and Flags
    is_active = Column(Boolean, default=True)
    is_priority_customer = Column(Boolean, default=False)
    do_not_contact = Column(Boolean, default=False)
    
    # Metadata
    fingerprint_hash = Column(String(255), nullable=True)  # For deduplication
    tags = Column(JSON, nullable=True)  # Custom tags for categorization
    custom_fields = Column(JSON, nullable=True)  # Additional custom fields (renamed from metadata to avoid SQLAlchemy conflict)
    
    # Relationships
    business = relationship("Business")
    invoices = relationship("Invoice", back_populates="customer")
    
    @hybrid_property
    def payment_rate_percentage(self) -> float:
        """Calculate payment rate as percentage of invoiced amount."""
        if self.total_invoiced_ytd and self.total_invoiced_ytd > 0:
            return (self.total_paid_ytd / self.total_invoiced_ytd) * 100
        return 0.0
    
    @hybrid_property
    def outstanding_balance(self) -> float:
        """Calculate outstanding balance (invoiced - paid)."""
        return self.total_invoiced_ytd - self.total_paid_ytd
    
    @hybrid_property
    def days_since_last_payment(self) -> Optional[int]:
        """Calculate days since last payment."""
        if self.last_payment_date:
            return (datetime.utcnow() - self.last_payment_date).days
        return None
    