from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Bill(Base, TimestampMixin, TenantMixin):
    __tablename__ = "bills"
    bill_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    vendor_id = Column(Integer, ForeignKey('vendors.vendor_id'), nullable=True)
    qbo_bill_id = Column(String(255), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # pending, review, approved, paid
    extracted_fields = Column(JSON, nullable=True)  # JSON for OCR data
    gl_account = Column(String, nullable=True)  # Suggested GL account
    confidence = Column(Float, default=0.0)  # Categorization confidence
    
    vendor = relationship("Vendor")
    business = relationship("Business")