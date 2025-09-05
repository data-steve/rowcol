"""
Preamble: Defines SQLAlchemy models for PayrollBatch and PayrollRemittance for Stage 1D of the Escher project.
Supports payroll reconciliation with tenant isolation via firm_id.
References: Stage 1D requirements, models/base.py, models/firm.py, models/client.py, models/bank_transaction.py.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class PayrollBatch(Base, TimestampMixin, TenantMixin):
    __tablename__ = "payroll_batches"
    
    batch_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    total_amount = Column(Float, nullable=False)
    payroll_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")  # pending, reconciled, unmatched
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    description = Column(String(500), nullable=True)
    
    client = relationship("Client")
    remittances = relationship("PayrollRemittance", back_populates="batch")

class PayrollRemittance(Base, TimestampMixin, TenantMixin):
    __tablename__ = "payroll_remittances"
    
    remittance_id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("payroll_batches.batch_id"), nullable=False)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    amount = Column(Float, nullable=False)
    tax_agency = Column(String(100), nullable=False)  # e.g., IRS, State
    remittance_date = Column(DateTime, nullable=False)
    transaction_id = Column(Integer, ForeignKey("bank_transactions.transaction_id"), nullable=True)
    status = Column(String(50), default="pending")  # pending, reconciled, unmatched
    
    batch = relationship("PayrollBatch", back_populates="remittances")
    transaction = relationship("BankTransaction")