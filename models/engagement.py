from sqlalchemy import Column, Integer, JSON, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, TenantMixin

class Engagement(Base, TimestampMixin, TenantMixin):
    __tablename__ = "engagements"
    engagement_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    service_type = Column(String, default="bookkeeping")  # bookkeeping, close, pbc_collection
    status = Column(String, default="pending")
    due_date = Column(DateTime, nullable=False)
    task_ids = Column(JSON, nullable=True, default=[])  # List of task_ids
    user_input = Column(JSON, nullable=True)  # e.g., {"qbo_account": "12345"}
    allowance_overage = Column(Float, default=0.0)
    agreed_at = Column(DateTime, nullable=True)
    health_status = Column(String, default="healthy")  # healthy, warning, critical
    compliance_status = Column(String, default="pending")  # pending, pass, fail
    e_signature = Column(JSON, nullable=True)  # {signer_id, timestamp, signature_data}
    qbo_sync_status = Column(String, default="not_started")  # not_started, syncing, success, failed
    
    client = relationship("Client", back_populates="engagements")
    firm = relationship("Firm", back_populates="engagements")
    engagement_entities = relationship("EngagementEntities", back_populates="engagement")