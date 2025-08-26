from sqlalchemy import Column, String, ForeignKey, Enum, Text, Index
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from app.models.enums import AuditSource, AuditAction, EntityType
import uuid

class AuditLog(Base, TimestampMixin):
    __tablename__ = 'audit_logs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # SOC2: Who, What, When, Where
    performed_by_user_id = Column(String(36), ForeignKey('users.id'), 
                                  nullable=True)  # Null for SIGNUP
    context_firm_id = Column(String(36), ForeignKey('firms.id'), 
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
        back_populates="performed_audits",
        foreign_keys=[performed_by_user_id]
    )
    firm = relationship(
        "Firm",
        back_populates="audit_logs",
        foreign_keys=[context_firm_id]
    )
    
    __table_args__ = (
        Index("ix_audit_log_entity_type_entity_id", "entity_type", "entity_id"),
        {"comment": "Audit log for tracking entity changes"},
    )