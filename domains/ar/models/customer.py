from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Customer(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    qbo_customer_id = Column(String(255), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String, nullable=True)
    terms = Column(String, nullable=True)  # e.g., Net 30
    fingerprint_hash = Column(String, nullable=True)  # For deduplication
    business = relationship("Business")