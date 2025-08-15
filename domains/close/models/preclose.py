"""
Preamble: Defines SQLAlchemy models for the Close domain in Stage 2 of the Escher project.
Supports pre-close checks, exceptions, PBC requests, and close checklists with tenant isolation.
References: Stage 2 requirements, domains/core/models/base.py, domains/core/models/firm.py, domains/core/models/client.py, domains/core/models/task.py.
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from domains.core.models.base import Base, TimestampMixin, TenantMixin

class PreCloseCheck(Base, TimestampMixin, TenantMixin):
    __tablename__ = "preclose_checks"
    
    check_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    period = Column(DateTime, nullable=False)
    type = Column(String(50), nullable=False)  # e.g., bank_rec, pbc_complete
    status = Column(String(50), default="pending")  # pending, pass, fail
    evidence_refs = Column(JSON, default=[])  # Array of document IDs
    
    client = relationship("Client", back_populates="preclose_checks")

class Exception(Base, TimestampMixin, TenantMixin):
    __tablename__ = "exceptions"
    
    exception_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    period = Column(DateTime, nullable=False)
    type = Column(String(50), nullable=False)  # e.g., unmatched_txn, missing_pbc
    description = Column(String(500), nullable=False)
    resolution = Column(String(500), nullable=True)
    
    client = relationship("Client", back_populates="exceptions")

class PBCRequest(Base, TimestampMixin, TenantMixin):
    __tablename__ = "pbc_requests"
    
    request_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    period = Column(DateTime, nullable=False)
    item_type = Column(String(50), nullable=False)  # bank_stmt, payroll, invoice
    owner = Column(String(50), nullable=False)  # client, staff
    due_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")  # pending, received, overdue
    reminders = Column(JSON, default=[])  # Array of sent reminder timestamps
    task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=True)
    
    client = relationship("Client", back_populates="pbc_requests")
    task = relationship("Task", back_populates="pbc_requests")

class CloseChecklist(Base, TimestampMixin, TenantMixin):
    __tablename__ = "close_checklists"
    
    checklist_id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(String(36), ForeignKey("firms.firm_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    period = Column(DateTime, nullable=False)
    items = Column(JSON, default=[])  # Array of check IDs
    status = Column(String(50), default="open")  # open, ready, blocked
    
    client = relationship("Client", back_populates="close_checklists")
