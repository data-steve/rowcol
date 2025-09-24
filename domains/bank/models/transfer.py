"""
Preamble: Defines the Transfer SQLAlchemy model for Stage 1C of the Escher project.
Supports linking bank transactions for transfer detection.
References: Stage 1C requirements, models/base.py, models/bank_transaction.py.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Transfer(Base, TimestampMixin, TenantMixin):
    __tablename__ = "transfers"
    
    transfer_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    source_transaction_id = Column(Integer, ForeignKey("bank_transactions.id"), nullable=False)
    destination_transaction_id = Column(Integer, ForeignKey("bank_transactions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String(500), nullable=True)
    
    # Relationships
    source_transaction = relationship("BankTransaction", foreign_keys=[source_transaction_id])
    destination_transaction = relationship("BankTransaction", foreign_keys=[destination_transaction_id])