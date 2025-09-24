from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class VendorStatement(Base, TimestampMixin, TenantMixin):
    __tablename__ = "vendor_statements"
    statement_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=False)
    statement_date = Column(DateTime, nullable=False)
    file_ref = Column(String, nullable=True)  # Path to statement file
    parsed_invoices = Column(JSON, nullable=True)  # JSON of invoice data
    mismatches = Column(JSON, nullable=True)  # JSON of reconciliation mismatches
    vendor = relationship("Vendor")
    business = relationship("Business")