from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Payment(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'ap_payments'
    payment_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False, index=True)
    qbo_id = Column(String(50), nullable=True, index=True)
    vendor_id = Column(String(50), ForeignKey("vendors.vendor_id"), nullable=False)
    bill_id = Column(Integer, ForeignKey('bills.bill_id'), nullable=True)
    qbo_payment_id = Column(String(255), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")
    # business = relationship("Business", back_populates="ap_payments")  # Parked for Phase 0
    vendor = relationship("Vendor")
    bill = relationship("Bill")
