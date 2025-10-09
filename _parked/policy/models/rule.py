from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Rule(Base, TimestampMixin, TenantMixin):
    __tablename__ = "rules"
    rule_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    policy_profile_id = Column(Integer, ForeignKey('policy_profiles.profile_id'), nullable=False)
    field = Column(String(255), nullable=False)
    priority = Column(Integer, nullable=False)
    match_type = Column(String, nullable=False)  # exact, regex, contains, amount, transfer
    pattern = Column(String, nullable=False)
    output = Column(JSON, nullable=False)  # {account, class, memo, confidence}
    scope = Column(String, default="global")  # global, business
    
    business = relationship("Business")