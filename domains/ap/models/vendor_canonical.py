from sqlalchemy import Column, Integer, String, Float, ForeignKey   
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class VendorCanonical(Base, TimestampMixin, TenantMixin):
    __tablename__ = "vendor_canonical"
    vendor_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    raw_name = Column(String, nullable=False)
    canonical_name = Column(String, nullable=False)
    mcc = Column(String, nullable=True)  # Merchant Category Code
    naics = Column(String, nullable=True)  # NAICS code
    default_gl_account = Column(String, nullable=True)
    confidence = Column(Float, default=0.0)  # 0.0–1.0
    client = relationship("Client")