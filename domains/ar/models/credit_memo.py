from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class CreditMemo(Base, TimestampMixin, TenantMixin):
    __tablename__ = "credit_memos"
    memo_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    qbo_id = Column(String, nullable=True)  # QBO credit memo ID
    invoice_id = Column(Integer, ForeignKey("invoices.invoice_id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="review")  # review, applied, processed
    invoice = relationship("Invoice")
    client = relationship("Client")