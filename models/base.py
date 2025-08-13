from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import Query
from typing import TypeVar, Type
    
Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TenantMixin:
    """
    Multi-tenancy mixin that enforces firm_id filtering.
    
    IMPORTANT: Models using this mixin MUST explicitly define their own firm_id column.
    This mixin provides query filtering methods but does NOT define the column.
    """
    
    @classmethod
    def tenant_filter(cls, firm_id: str) -> Query:
        """Filter query to only return records for the specified firm."""
        return cls.query.filter(cls.firm_id == firm_id)
    
    @classmethod
    def by_firm(cls, firm_id: str) -> Query:
        """Alternative method name for tenant filtering."""
        return cls.tenant_filter(firm_id)
    
    @classmethod
    def ensure_tenant_context(cls, firm_id: str) -> None:
        """Validate that firm_id is provided for multi-tenant operations."""
        if not firm_id:
            raise ValueError(f"{cls.__name__} requires firm_id for multi-tenant operations")