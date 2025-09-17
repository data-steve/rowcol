from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class Integration(Base, TimestampMixin, TenantMixin):
    __tablename__ = "integrations"
    
    def __init__(self, *args, **kwargs):
        # Enforce explicit multi-tenancy: do not accept tenant_id here
        if 'tenant_id' in kwargs:
            raise TypeError(
                "Integration does not accept 'tenant_id'. "
                "Pass explicit 'business_id' (and optional 'business_id') instead."
            )
        super().__init__(*args, **kwargs)

    integration_id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(36), ForeignKey("businesses.business_id"), nullable=False)
    platform = Column(String(50), nullable=False)  # QBO, Stripe, Jobber
    credentials = Column(JSON, nullable=True)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    account_id = Column(String, nullable=True)
    status = Column(String, default="active")  # active, inactive, expired, error
    platform_metadata = Column(String, nullable=True)  # JSON string for platform-specific data
    
    # Relationships
    business = relationship("Business", back_populates="integrations")
    transactions = relationship("Transaction", back_populates="integration")
    # jobs = relationship("Job", back_populates="integration")  # Parked for Phase 0

