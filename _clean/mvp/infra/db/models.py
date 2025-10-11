"""
SQLAlchemy Models for MVP Mirror Tables

Defines the mirror tables used by the Smart Sync pattern for the MVP.
These models provide database abstraction and will work with both SQLite (dev) and PostgreSQL (prod).
"""

from sqlalchemy import Column, String, DateTime, Numeric, Text, JSON, Index, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()


class SystemIntegrationToken(Base):
    """System-level integration tokens for QBO OAuth."""
    __tablename__ = 'system_integration_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rail = Column(String(50), nullable=False, index=True)  # 'qbo', 'ramp', 'plaid', 'stripe'
    environment = Column(String(50), nullable=False)  # 'sandbox', 'production'
    external_id = Column(String(255), nullable=True)  # realm_id for QBO
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    access_expires_at = Column(DateTime, nullable=True)
    refresh_expires_at = Column(DateTime, nullable=True)
    status = Column(String(50), default='active')  # 'active', 'expired', 'revoked'
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_system_tokens_rail_env', 'rail', 'environment', 'status'),
    )


class MirrorBill(Base):
    """Mirror table for bills from QBO."""
    __tablename__ = 'mirror_bills'
    
    bill_id = Column(String(255), primary_key=True)
    advisor_id = Column(String(255), nullable=False, index=True)
    business_id = Column(String(255), nullable=False, index=True)
    vendor_id = Column(String(255), nullable=True)
    vendor_name = Column(String(255), nullable=True)
    due_date = Column(String(50), nullable=True)  # QBO date format
    amount = Column(Numeric(10, 2), nullable=True)
    status = Column(String(50), nullable=True, default='OPEN')
    source_version = Column(String(50), nullable=True)
    last_synced_at = Column(DateTime, nullable=True, default=func.now())
    data_json = Column(Text, nullable=True)  # Full QBO JSON data
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_mirror_bills_advisor_business', 'advisor_id', 'business_id'),
    )

class MirrorInvoice(Base):
    """Mirror table for invoices from QBO."""
    __tablename__ = 'mirror_invoices'
    
    invoice_id = Column(String(255), primary_key=True)
    advisor_id = Column(String(255), nullable=False, index=True)
    business_id = Column(String(255), nullable=False, index=True)
    customer_id = Column(String(255), nullable=True)
    customer_name = Column(String(255), nullable=True)
    due_date = Column(String(50), nullable=True)  # QBO date format
    amount = Column(Numeric(10, 2), nullable=True)
    status = Column(String(50), nullable=True, default='OPEN')
    source_version = Column(String(50), nullable=True)
    last_synced_at = Column(DateTime, nullable=True, default=func.now())
    data_json = Column(Text, nullable=True)  # Full QBO JSON data
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_mirror_invoices_advisor_business', 'advisor_id', 'business_id'),
    )

class MirrorBalance(Base):
    """Mirror table for account balances from QBO."""
    __tablename__ = 'mirror_balances'
    
    balance_id = Column(String(255), primary_key=True)
    advisor_id = Column(String(255), nullable=False, index=True)
    business_id = Column(String(255), nullable=False, index=True)
    account_id = Column(String(255), nullable=True)
    account_name = Column(String(255), nullable=True)
    account_type = Column(String(50), nullable=True)
    balance = Column(Numeric(10, 2), nullable=True)
    as_of_date = Column(String(50), nullable=True)  # QBO date format
    source_version = Column(String(50), nullable=True)
    last_synced_at = Column(DateTime, nullable=True, default=func.now())
    data_json = Column(Text, nullable=True)  # Full QBO JSON data
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_mirror_balances_advisor_business', 'advisor_id', 'business_id'),
    )

class IntegrationLog(Base):
    """Transaction log for sync operations."""
    __tablename__ = 'integration_log'
    
    log_id = Column(String(255), primary_key=True)
    advisor_id = Column(String(255), nullable=False, index=True)
    business_id = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # 'bill', 'invoice', 'balance'
    entity_id = Column(String(255), nullable=True)
    operation = Column(String(50), nullable=False)  # 'read', 'write', 'sync'
    status = Column(String(50), nullable=False)  # 'success', 'error', 'throttled'
    error_message = Column(Text, nullable=True)
    source_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    metadata_json = Column(Text, nullable=True)  # Additional sync metadata
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_integration_log_advisor_business', 'advisor_id', 'business_id'),
        Index('idx_integration_log_entity', 'entity_type', 'entity_id'),
    )

class AdvisorBusiness(Base):
    """Advisor-Business relationships for multi-tenancy."""
    __tablename__ = 'advisor_businesses'
    
    id = Column(String(255), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    advisor_id = Column(String(255), nullable=False, index=True)
    business_id = Column(String(255), nullable=False, index=True)
    qbo_realm_id = Column(String(255), nullable=True)
    qbo_access_token = Column(Text, nullable=True)
    qbo_refresh_token = Column(Text, nullable=True)
    qbo_connected_at = Column(DateTime, nullable=True)
    qbo_status = Column(String(50), default='disconnected')
    qbo_environment = Column(String(50), default='sandbox')
    qbo_token_expires_at = Column(DateTime, nullable=True)
    qbo_error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_advisor_businesses_advisor', 'advisor_id'),
        Index('idx_advisor_businesses_business', 'business_id'),
    )

class EntityPolicy(Base):
    """Entity TTL policies for Smart Sync."""
    __tablename__ = 'entity_policy'
    
    policy_id = Column(String(255), primary_key=True)
    advisor_id = Column(String(255), nullable=False, index=True)
    business_id = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # 'bill', 'invoice', 'balance'
    soft_ttl_seconds = Column(Numeric(10, 0), nullable=False, default=300)  # 5 minutes
    hard_ttl_seconds = Column(Numeric(10, 0), nullable=False, default=3600)  # 1 hour
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_entity_policy_advisor_business', 'advisor_id', 'business_id'),
        Index('idx_entity_policy_entity_type', 'entity_type'),
    )

