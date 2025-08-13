from sqlalchemy import Column, Integer, String, JSON,ForeignKey
from .base import Base, TimestampMixin, TenantMixin
from sqlalchemy.orm import relationship

class Correction(Base, TimestampMixin, TenantMixin):
    __tablename__ = "corrections"
    correction_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    txn_id = Column(String, nullable=False)
    raw_descriptor = Column(String, nullable=False)
    suggested = Column(JSON, nullable=True)  # {account, class, confidence}
    final = Column(JSON, nullable=False)  # {account, class, memo}
    rationale = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    scope = Column(String, default="client")  # client, global
    client = relationship("Client")
    created_by_user = relationship("User")