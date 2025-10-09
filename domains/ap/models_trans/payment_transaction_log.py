"""
PaymentTransactionLog model for immutable audit trails.

Stores immutable transaction logs for all payment changes, providing complete
audit trails for compliance and reconciliation across integration rails.

Key Features:
- Immutable append-only records
- Complete data snapshots at time of change
- Change tracking and source attribution
- Multi-rail support (QBO, Ramp, Plaid, Stripe)
- SOC2 compliance audit trails
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text, Index
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TenantMixin
import uuid


class PaymentTransactionLog(Base, TenantMixin):
    """
    Immutable transaction log for payment changes.
    
    This model provides append-only audit trails for all payment operations,
    supporting compliance requirements and multi-rail reconciliation.
    
    Key Features:
    - Immutable: Never update or delete records
    - Complete snapshots: Full data state at time of change
    - Change tracking: What changed and why
    - Source attribution: Which rail or user initiated the change
    - Multi-rail support: QBO, Ramp, Plaid, Stripe integration
    """
    
    __tablename__ = "payment_transaction_logs"
    
    # Primary key
    transaction_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to payment
    payment_id = Column(Integer, ForeignKey("ap_payments.payment_id"), nullable=False, index=True)
    
    # Transaction metadata
    transaction_type = Column(String(50), nullable=False)  # created, updated, synced, deleted
    source = Column(String(50), nullable=False)  # qbo, ramp, plaid, stripe, user, system
    
    # Complete data snapshots
    payment_data = Column(JSON, nullable=False)  # Complete payment data at time of transaction
    changes = Column(JSON, nullable=True)  # What changed (field: {old_value, new_value})
    
    # Audit information
    created_at = Column(DateTime, nullable=False, index=True)
    created_by_user_id = Column(String(36), nullable=True)  # User who initiated the change
    session_id = Column(String(36), nullable=True)  # Session tracking
    
    # Multi-rail reconciliation
    external_id = Column(String(255), nullable=True)  # External system ID (QBO payment ID, etc.)
    external_sync_token = Column(String(50), nullable=True)  # External system sync token
    
    # Additional context
    reason = Column(Text, nullable=True)  # Why the change was made
    additional_metadata = Column(JSON, nullable=True)  # Additional context data
    
    # Relationships
    payment = relationship("Payment", back_populates="transaction_logs")
    
    __table_args__ = (
        Index("ix_payment_transaction_log_payment_id_created_at", "payment_id", "created_at"),
        Index("ix_payment_transaction_log_source_type", "source", "transaction_type"),
        Index("ix_payment_transaction_log_external_id", "external_id"),
        {"comment": "Immutable transaction log for payment changes"},
    )
    
    def __repr__(self):
        return f"<PaymentTransactionLog(transaction_id={self.transaction_id}, payment_id={self.payment_id}, type={self.transaction_type}, source={self.source})>"
