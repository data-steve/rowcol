from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Document(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'documents'
    document_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    document_type_id = Column(Integer, ForeignKey('document_types.type_id'), nullable=False)
    file_path = Column(String(255), nullable=False)
    period = Column(String, nullable=False)  # e.g., "2025-Q1"
    type = Column(String, nullable=False)  # invoice, statement, receipt, payroll
    file_ref = Column(String, nullable=False)  # File path or URL
    hash = Column(String, nullable=False)  # File hash for deduplication
    upload_date = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # pending, processed, archived, review
    extracted_fields = Column(JSON, nullable=True)  # {vendor, amount, date, address, confidence}
    review_status = Column(String, nullable=True)
    business = relationship("Business")