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
    Multi-tenancy mixin that enforces business_id filtering.
    
    IMPORTANT: Models using this mixin MUST explicitly define their own business_id column.
    This mixin provides query filtering methods but does NOT define the column.
    """
    
    @classmethod
    def tenant_filter(cls, business_id: str) -> Query:
        """Filter query to only return records for the specified firm."""
        return cls.query.filter(cls.business_id == business_id)
    
    @classmethod
    def by_firm(cls, business_id: str) -> Query:
        """Alternative method name for tenant filtering."""
        return cls.tenant_filter(business_id)
    
    @classmethod
    def ensure_tenant_context(cls, business_id: str) -> None:
        """Validate that business_id is provided for multi-tenant operations."""
        if not business_id:
            raise ValueError(f"{cls.__name__} requires business_id for multi-tenant operations")