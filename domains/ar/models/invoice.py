from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Invoice(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'invoices'
    invoice_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    qbo_invoice_id = Column(String(255), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=True)
    # job_id = Column(String, ForeignKey("jobs.job_id"), nullable=True)  # Parked for Phase 0 - no job costing
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total = Column(Float, nullable=False)
    lines = Column(JSON, nullable=True)  # Invoice line items
    status = Column(String, default="draft")  # draft, sent, paid, review
    confidence = Column(Float, default=0.0)  # OCR confidence score
    attachment_refs = Column(JSON, nullable=True)  # Document references
    customer = relationship("Customer")
    business = relationship("Business")
    
