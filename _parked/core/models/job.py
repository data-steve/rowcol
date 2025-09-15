from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Job(Base, TimestampMixin, TenantMixin):
    __tablename__ = "jobs"
    
    job_id = Column(String, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    integration_id = Column(String, ForeignKey("integrations.integration_id"), nullable=True)
    platform_job_id = Column(String, nullable=True)  # External platform job ID
    name = Column(String, nullable=False)
    status = Column(String, default="active")  # active, completed, cancelled
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    platform_metadata = Column(JSON, nullable=True)  # Platform-specific job data
    
    # Relationships
    firm = relationship("Firm")
    client = relationship("Client")
    integration = relationship("Integration", back_populates="jobs")
    transactions = relationship("Transaction", back_populates="job")

