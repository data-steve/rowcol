from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Transaction(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    qbo_transaction_id = Column(String(255), nullable=True, index=True)
    date = Column(DateTime, nullable=False)
    integration_id = Column(String(36), ForeignKey("integrations.integration_id"), nullable=True)
    platform_txn_id = Column(String, nullable=True)  # External platform transaction ID
    type = Column(String, nullable=False)  # deposit, expense, reimbursement, payroll
    amount = Column(Float, nullable=False)
    vendor_id = Column(String(36), ForeignKey("vendors.vendor_id"), nullable=True)
    # job_id = Column(String, ForeignKey("jobs.job_id"), nullable=True)  # Parked for Phase 0 - no job costing
    confidence = Column(Float, default=0.0)  # 0.0 to 1.0 confidence score
    status = Column(String, default="unmatched")  # matched, unmatched, flagged
    platform_metadata = Column(JSON, nullable=True)  # Platform-specific metadata
    
    # Relationships
    business = relationship("Business", back_populates="transactions")
    integration = relationship("Integration", back_populates="transactions")
    # job = relationship("Job", back_populates="transactions")  # Parked for Phase 0
    # vendor relationship will be added when we have vendor model in core or reference AP vendor

