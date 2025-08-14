from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class Vendor(Base, TimestampMixin, TenantMixin):
    __tablename__ = "vendors"
    vendor_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    canonical_id = Column(Integer, ForeignKey("vendor_canonical.vendor_id"), nullable=True)
    qbo_id = Column(String, nullable=True)  # QBO vendor ID
    w9_status = Column(String, default="pending")  # pending, received, verified
    default_gl_account = Column(String, nullable=True)  # Default GL account
    terms = Column(String, nullable=True)  # Payment terms (e.g., Net 30)
    fingerprint_hash = Column(String, nullable=True)  # For deduplication
    vendor_canonical = relationship("VendorCanonical")
    client = relationship("Client")