from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class Document(Base, TimestampMixin, TenantMixin):
    __tablename__ = "documents"
    doc_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    period = Column(String, nullable=False)  # e.g., "2025-Q1"
    type = Column(String, nullable=False)  # invoice, statement, receipt, payroll
    file_ref = Column(String, nullable=False)  # File path or URL
    hash = Column(String, nullable=False)  # File hash for deduplication
    upload_date = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # pending, processed, archived, review
    extracted_fields = Column(JSON, nullable=True)  # {vendor, amount, date, address, confidence}
    review_status = Column(String, nullable=True)
    client = relationship("Client")