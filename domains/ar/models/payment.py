"""
Payment model for AR domain.
Represents customer payments applied to invoices.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Payment(Base, TimestampMixin, TenantMixin):
    __tablename__ = "payments"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    qbo_id = Column(String, nullable=True)
    invoice_ids = Column(JSON, nullable=True)  # List of invoice IDs this payment applies to
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    method = Column(String, nullable=False)  # ACH, check, credit_card, etc.
    status = Column(String, default="pending")  # pending, applied, refunded
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    
    class Config:
        from_attributes = True
