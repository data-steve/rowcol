from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin
from domains.core.models.balance import Balance

class Business(Base, TimestampMixin, TenantMixin):
    __tablename__ = "businesses"
    business_id = Column(String(36), primary_key=True, index=True, default=lambda: str(__import__('uuid').uuid4()))
    name = Column(String(255), nullable=False, index=True)
    qbo_id = Column(String(50), nullable=True, index=True)
    industry = Column(String(50), nullable=True)  # agency, consulting, retail
    policy_profile_id = Column(Integer, ForeignKey("policy_profiles.profile_id"), nullable=True)
    
    # QBO Integration Fields (replacing Integration model)
    qbo_realm_id = Column(String(255), nullable=True)
    qbo_access_token = Column(String(500), nullable=True) 
    qbo_refresh_token = Column(String(500), nullable=True)
    qbo_connected_at = Column(DateTime, nullable=True)
    qbo_status = Column(String(50), default="disconnected")
    qbo_environment = Column(String(50), default="sandbox")
    qbo_token_expires_at = Column(DateTime, nullable=True)
    qbo_error_message = Column(String(500), nullable=True)
    
    # Legacy relationship removed - QBO integration now handled via Business model fields
    policy_profile = relationship("PolicyProfile", foreign_keys=[policy_profile_id])
    balances = relationship("Balance", back_populates="business", foreign_keys=[Balance.business_id])
    tray_items = relationship("TrayItem", back_populates="business")
    users = relationship("User", back_populates="business")
    transactions = relationship("Transaction", back_populates="business")
    ap_payments = relationship("domains.ap.models.payment.Payment", back_populates="business")
    ar_payments = relationship("domains.ar.models.payment.ARPayment", back_populates="business")
    bank_transactions = relationship("domains.bank.models.bank_transaction.BankTransaction", back_populates="business")
    
    # Runway reserves relationship removed to enforce ADR-001
    # The relationship is now defined on the RunwayReserve model itself.
