from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from .base import Base, TimestampMixin, TenantMixin
from sqlalchemy.orm import relationship

class PaymentIntent(Base, TimestampMixin, TenantMixin):
    __tablename__ = "payment_intents"
    intent_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    bill_ids = Column(JSON, nullable=True)  # JSON array for bill IDs
    provider = Column(String, default="qbo")  # QBO for now
    total_amount = Column(Float, nullable=False)
    funding_account = Column(String, nullable=True)  # QBO account
    status = Column(String, default="pending")  # pending, issued, cleared
    issued_at = Column(DateTime, nullable=True)
    cleared_at = Column(DateTime, nullable=True)
    fees = Column(Float, default=0.0)
    
    client = relationship("Client")