from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin

class ComplianceRequirement(Base, TimestampMixin):
    __tablename__ = "compliance_requirements"
    
    requirement_id = Column(Integer, primary_key=True, index=True)
    requirement_name = Column(String(255), nullable=False)
    regulatory_source = Column(String(100), nullable=False)
    frequency = Column(String(50), nullable=False)
    deadline = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

class ServiceComplianceMapping(Base, TimestampMixin):
    __tablename__ = "service_compliance_mappings"
    
    mapping_id = Column(Integer, primary_key=True, index=True)
    service_type = Column(String(100), nullable=False)
    requirement_id = Column(Integer, ForeignKey("compliance_requirements.requirement_id"), nullable=False)
    is_required = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    
    # Relationship
    requirement = relationship("ComplianceRequirement", backref="service_mappings")
