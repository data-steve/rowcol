from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Customer(Base, TimestampMixin, TenantMixin):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    qbo_id = Column(String, nullable=True)  # QBO customer ID
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    terms = Column(String, nullable=True)  # e.g., Net 30
    fingerprint_hash = Column(String, nullable=True)  # For deduplication
    client = relationship("Client")