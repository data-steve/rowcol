from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class PolicyProfile(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'policy_profiles'
    profile_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    # rules = relationship("Rule", back_populates="policy_profile")  # Parked for Phase 0
    thresholds = Column(JSON, nullable=False)  # {posting, variance, capitalization, manual_jes, ocr_review}
    revenue_policy = Column(String, nullable=True)
    cutoff_rules = Column(JSON, nullable=True)
    tickmark_map = Column(JSON, nullable=True)
    deliverable_prefs = Column(JSON, nullable=True)
    pricing_tier = Column(String, default="basic")  # basic, pro, enterprise
    doc_volume = Column(Integer, default=0)
    
    business = relationship("Business", foreign_keys=[business_id])