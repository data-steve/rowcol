from sqlalchemy import Column, Integer, String, ForeignKey  
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Client(Base, TimestampMixin, TenantMixin):
    __tablename__ = "clients"
    client_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    name = Column(String, nullable=False)
    qbo_id = Column(String, nullable=True)
    industry = Column(String, nullable=True)  # retail, pro_services, nonprofit
    policy_profile_id = Column(Integer, ForeignKey("policy_profiles.profile_id"), nullable=True)
    firm = relationship("Firm", back_populates="clients")
    engagements = relationship("Engagement", back_populates="client")
    policy_profile = relationship("PolicyProfile", foreign_keys=[policy_profile_id])
    preclose_checks = relationship("PreCloseCheck", back_populates="client")
    exceptions = relationship("Exception", back_populates="client")
    pbc_requests = relationship("PBCRequest", back_populates="client")
    close_checklists = relationship("CloseChecklist", back_populates="client")