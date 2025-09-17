from sqlalchemy import Column, Integer, String, JSON,ForeignKey
from domains.core.models.base import Base, TimestampMixin, TenantMixin
from sqlalchemy.orm import relationship

class Correction(Base, TimestampMixin, TenantMixin):
    __tablename__ = 'corrections'
    correction_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=True)
    suggestion_id = Column(Integer, ForeignKey('suggestions.suggestion_id'), nullable=False)
    corrected_by_user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    txn_id = Column(String, nullable=False)
    raw_descriptor = Column(String, nullable=False)
    suggested = Column(JSON, nullable=True)  # {account, class, confidence}
    final = Column(JSON, nullable=False)  # {account, class, memo}
    rationale = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    scope = Column(String, default="business")  # business, global
    business = relationship("Business") 
    # created_by_user = relationship("User")  # Parked for Phase 0 - ambiguous FK