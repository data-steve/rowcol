from sqlalchemy import Column, Integer, String, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class VendorStatement(Base, TimestampMixin, TenantMixin):
    __tablename__ = "vendor_statements"
    statement_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=False)
    period = Column(Date, nullable=False)
    file_ref = Column(String, nullable=True)  # Path to statement file
    parsed_invoices = Column(JSON, nullable=True)  # JSON of invoice data
    mismatches = Column(JSON, nullable=True)  # JSON of reconciliation mismatches
    vendor = relationship("Vendor")
    client = relationship("Client")