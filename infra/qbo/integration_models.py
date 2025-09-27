from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from enum import Enum
from infra.database.models import Base
from domains.core.models.base import TimestampMixin, TenantMixin

class IntegrationStatuses(Enum):
    """Integration status enumeration."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    EXPIRED = "expired"

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
    token_expires_at = Column(DateTime, nullable=True)  # For QBO OAuth
    account_id = Column(String, nullable=True)
    realm_id = Column(String, nullable=True)  # QBO company ID
    status = Column(String, default="active")  # active, inactive, expired, error
    oauth_state = Column(String, nullable=True)  # OAuth state parameter
    connected_at = Column(DateTime, nullable=True)  # When connection was established
    error_message = Column(String, nullable=True)  # Error details if failed
    created_by = Column(String, nullable=True)  # User who initiated connection
    platform_metadata = Column(String, nullable=True)  # JSON string for platform-specific data
    test_drive_data = Column(JSON, nullable=True)  # Store test drive results
    
    # Relationships
    business = relationship("Business", back_populates="integrations")
    transactions = relationship("Transaction", back_populates="integration")
    # jobs = relationship("Job", back_populates="integration")  # Parked for Phase 0

