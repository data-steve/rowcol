from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Payment(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'ar_payments'
    payment_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False, index=True)
    qbo_payment_id = Column(String(255), nullable=True, index=True)
    invoice_id = Column(Integer, ForeignKey('invoices.invoice_id'), nullable=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")
    # business = relationship("Business", back_populates="ar_payments")  # Parked for Phase 0
    # customer = relationship("Customer")  # Parked for Phase 0 - missing customer_id FK
    # invoice = relationship("Invoice")    # Parked for Phase 0
