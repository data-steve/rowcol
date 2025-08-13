from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class PolicyProfile(Base, TimestampMixin, TenantMixin):
    __tablename__ = "policy_profiles"
    profile_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    thresholds = Column(JSON, nullable=False)  # {posting, variance, capitalization, manual_jes, ocr_review}
    revenue_policy = Column(String, nullable=True)
    cutoff_rules = Column(JSON, nullable=True)
    tickmark_map = Column(JSON, nullable=True)
    deliverable_prefs = Column(JSON, nullable=True)
    pricing_tier = Column(String, default="basic")  # basic, pro, enterprise
    doc_volume = Column(Integer, default=0)
    
    client = relationship("Client", foreign_keys=[client_id])