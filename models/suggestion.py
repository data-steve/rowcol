from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class Suggestion(Base, TimestampMixin, TenantMixin):
    __tablename__ = "suggestions"
    suggestion_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    txn_id = Column(String, nullable=False)
    top_k = Column(JSON, nullable=False)  # [{account, class, confidence}]
    chosen_idx = Column(Integer, nullable=True)
    client = relationship("Client")