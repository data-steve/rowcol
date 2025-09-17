from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Vendor(Base, TimestampMixin, TenantMixin):
    __tablename__ = "vendors"
    vendor_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    canonical_vendor_id = Column(Integer, ForeignKey('vendor_canonicals.id'), nullable=True)
    qbo_vendor_id = Column(String(255), nullable=True, index=True)
    w9_status = Column(String, default="pending")  # pending, received, verified
    default_gl_account = Column(String, nullable=True)  # Default GL account
    terms = Column(String, nullable=True)  # Payment terms (e.g., Net 30)
    fingerprint_hash = Column(String, nullable=True)  # For deduplication
    vendor_canonical = relationship("VendorCanonical")
    business = relationship("Business")