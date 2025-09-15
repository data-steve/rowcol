from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Business(Base, TimestampMixin, TenantMixin):
    __tablename__ = "clients"
    client_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), nullable=True)  # Nullable for single-business MVP
    name = Column(String(255), nullable=False, index=True)
    qbo_id = Column(String(50), nullable=True, index=True)
    industry = Column(String(50), nullable=True)  # agency, consulting, retail
    policy_profile_id = Column(Integer, ForeignKey("policy_profiles.profile_id"), nullable=True)
    integrations = relationship("Integration", back_populates="business")
    policy_profile = relationship("PolicyProfile")
    balances = relationship("Balance", back_populates="business")
    notifications = relationship("Notification", back_populates="business")
