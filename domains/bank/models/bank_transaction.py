"""
Preamble: Defines the BankTransaction SQLAlchemy model for Stage 1C of the Escher project.
This model supports bank transaction creation and listing, with tenant isolation via firm_id.
References: Stage 1C requirements, models/base.py, models/firm.py, models/client.py.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin
import enum

class ProcessorType(enum.Enum):
    JOBBER_PAY = "JOBBER_PAY"
    STRIPE = "STRIPE"
    ACH = "ACH"
    CHECK = "CHECK"

class BankTransaction(Base, TimestampMixin, TenantMixin):
    __tablename__ = "bank_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    external_id = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String(500), nullable=False)
    account_id = Column(String(50), nullable=True)
    source = Column(String(50), nullable=False)  # e.g., 'qbo_feed', 'csv', 'manual', 'plaid'
    processor = Column(Enum(ProcessorType), nullable=True)
    unbundle_meta = Column(JSON, nullable=True)  # {fee, candidates, confidence}
    invoice_ids = Column(JSON, nullable=True)  # List of linked invoice IDs
    status = Column(String(50), default="pending")
    rule_id = Column(Integer, ForeignKey("rules.rule_id"), nullable=True)
    confidence = Column(Float, default=0.0)
    suggestion_id = Column(Integer, ForeignKey("suggestions.suggestion_id"), nullable=True)

    # Relationships
    client = relationship("Client")
    rule = relationship("Rule")
    suggestion = relationship("Suggestion")