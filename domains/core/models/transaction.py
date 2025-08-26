from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Transaction(Base, TimestampMixin, TenantMixin):
    __tablename__ = "transactions"
    
    txn_id = Column(String, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    integration_id = Column(String, ForeignKey("integrations.integration_id"), nullable=True)
    platform_txn_id = Column(String, nullable=True)  # External platform transaction ID
    type = Column(String, nullable=False)  # deposit, expense, reimbursement, payroll
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=True)
    job_id = Column(String, ForeignKey("jobs.job_id"), nullable=True)
    confidence = Column(Float, default=0.0)  # 0.0 to 1.0 confidence score
    status = Column(String, default="unmatched")  # matched, unmatched, flagged
    platform_metadata = Column(JSON, nullable=True)  # Platform-specific metadata
    
    # Relationships
    firm = relationship("Firm")
    client = relationship("Client")
    integration = relationship("Integration", back_populates="transactions")
    job = relationship("Job", back_populates="transactions")
    # vendor relationship will be added when we have vendor model in core or reference AP vendor

