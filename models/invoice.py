from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class Invoice(Base, TimestampMixin, TenantMixin):
    __tablename__ = "invoices"
    invoice_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    qbo_id = Column(String, nullable=True)  # QBO invoice ID
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total = Column(Float, nullable=False)
    lines = Column(JSON, nullable=True)  # Invoice line items
    status = Column(String, default="draft")  # draft, sent, paid, review
    confidence = Column(Float, default=0.0)  # OCR confidence score
    attachment_refs = Column(JSON, nullable=True)  # Document references
    customer = relationship("Customer")
    client = relationship("Client")
    
