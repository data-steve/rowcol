from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Suggestion(Base, TimestampMixin, TenantMixin):
    __tablename__ = "suggestions"
    suggestion_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    txn_id = Column(String, nullable=False)
    top_k = Column(JSON, nullable=False)  # [{account, class, confidence}]
    chosen_idx = Column(Integer, nullable=True)
    business = relationship("Business")