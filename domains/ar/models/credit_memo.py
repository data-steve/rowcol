from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class CreditMemo(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'credit_memos'
    credit_memo_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    qbo_credit_memo_id = Column(String(255), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.invoice_id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="review")  # review, applied, processed
    invoice = relationship("Invoice")
    business = relationship("Business")