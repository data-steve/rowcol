from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class Payment(Base, TimestampMixin, TenantMixin):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    qbo_id = Column(String, nullable=True)  # QBO payment ID
    invoice_ids = Column(JSON, nullable=True)  # References invoices
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    method = Column(String, nullable=True)  # e.g., check, ACH
    client = relationship("Client")