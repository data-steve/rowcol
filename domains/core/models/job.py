from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class Job(Base, TimestampMixin, TenantMixin):
    __tablename__ = "jobs"
    
    job_id = Column(String(50), primary_key=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    name = Column(String(255), nullable=False)
    platform_job_id = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True)
    
    # Relationships
    firm = relationship("Firm", back_populates="jobs")
