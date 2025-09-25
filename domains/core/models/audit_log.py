from sqlalchemy import Column, String, ForeignKey, Enum, Text, Index, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
from enum import Enum as PyEnum
import uuid

class AuditSource(PyEnum):
    USER = "user"
    SYSTEM = "system"
    API = "api"

class AuditAction(PyEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    SIGNUP = "signup"

class EntityType(PyEnum):
    USER = "user"
    FIRM = "firm"
    CLIENT = "client"
    INVOICE = "invoice"
    BILL = "bill"

class AuditLog(Base, TimestampMixin):
    __tablename__ = 'audit_logs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # SOC2: Who, What, When, Where
    performed_by_user_id = Column(Integer, ForeignKey('users.user_id'), 
                                  nullable=True)  # Null for SIGNUP
    context_business_id = Column(String(36), ForeignKey('businesses.business_id'), 
                             nullable=True)  # Null for firm creation
    source = Column(Enum(AuditSource), nullable=False, default=AuditSource.USER)
    action = Column(Enum(AuditAction), nullable=False)
    
    # Entity tracking
    entity_type = Column(Enum(EntityType), nullable=False)
    entity_id = Column(String(36), nullable=False)
    
    # Change tracking
    new_values = Column(Text)  # JSON of new state
    
    # Traceability
    cause_id = Column(String(36), nullable=True, index=True)  # Links actions to a workflow event
    
    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    session_id = Column(String(36))  # For tracking related actions
    context_metadata = Column(Text)  # Additional context as JSON
    
    # Relationships
    performed_by = relationship(
        "User",
        foreign_keys=[performed_by_user_id]
    )
    business = relationship(
        "Business",
        foreign_keys=[context_business_id]
    )
    
    __table_args__ = (
        Index("ix_audit_log_entity_type_entity_id", "entity_type", "entity_id"),
        {"comment": "Audit log for tracking entity changes"},
    )