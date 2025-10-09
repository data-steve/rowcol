"""
Base Service Class for Tenant-Aware Operations

Provides common patterns for tenant isolation and service operations.
Follows ADR-003 Multi-Tenancy Strategy.
"""

from typing import TypeVar, Type, Optional, List
from sqlalchemy.orm import Session, Query

from domains.core.models.business import Business
from infra.config.exceptions import ValidationError, TenantAccessError

T = TypeVar('T')


class TenantAwareService:
    """
    Base class for all domain services that require tenant isolation.
    
    Provides automatic tenant filtering and validation for all database operations.
    Follows ADR-003 Multi-Tenancy Strategy patterns.
    """
    
    def __init__(self, db: Session, business_id: str, validate_business: bool = True):
        """
        Initialize tenant-aware service.
        
        Args:
            db: Database session
            business_id: Business identifier for tenant isolation
            validate_business: Whether to validate business exists (default: True)
            
        Raises:
            ValidationError: If business_id is invalid and validate_business is True
        """
        self.db = db
        self.business_id = business_id
        
        # Optionally validate business exists
        if validate_business:
            self.business = self._validate_business_access(business_id)
        else:
            self.business = None
    
    def _validate_business_access(self, business_id: str) -> Business:
        """
        Validate that the business exists and is accessible.
        
        Args:
            business_id: Business identifier to validate
            
        Returns:
            Business object if valid
            
        Raises:
            ValidationError: If business doesn't exist
            TenantAccessError: If access is denied
        """
        business = self.db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise ValidationError(f"Business {business_id} not found")
        
        # Future: Add role-based access control here
        # For now, assume access is granted if business exists
        
        return business
    
    def _base_query(self, model_class: Type[T]) -> Query:
        """
        Create base query with automatic tenant filtering.
        
        Args:
            model_class: SQLAlchemy model class
            
        Returns:
            Query object with tenant filtering applied
        """
        return self.db.query(model_class).filter(
            model_class.business_id == self.business_id
        )
    
    def _get_by_id(self, model_class: Type[T], record_id: str) -> Optional[T]:
        """
        Get a record by ID with tenant filtering.
        
        Args:
            model_class: SQLAlchemy model class
            record_id: Record identifier
            
        Returns:
            Record if found and accessible, None otherwise
        """
        return self._base_query(model_class).filter(
            model_class.id == record_id
        ).first()
    
    def _get_by_id_or_raise(self, model_class: Type[T], record_id: str, 
                           error_message: Optional[str] = None) -> T:
        """
        Get a record by ID with tenant filtering, raise if not found.
        
        Args:
            model_class: SQLAlchemy model class
            record_id: Record identifier
            error_message: Custom error message
            
        Returns:
            Record if found and accessible
            
        Raises:
            ValidationError: If record not found
        """
        record = self._get_by_id(model_class, record_id)
        if not record:
            message = error_message or f"{model_class.__name__} {record_id} not found"
            raise ValidationError(message)
        return record
    
    def _create_record(self, model_class: Type[T], **kwargs) -> T:
        """
        Create a new record with automatic tenant assignment.
        
        Args:
            model_class: SQLAlchemy model class
            **kwargs: Record attributes
            
        Returns:
            Created record
        """
        # Ensure business_id is set
        kwargs['business_id'] = self.business_id
        
        record = model_class(**kwargs)
        self.db.add(record)
        return record
    
    def _count_records(self, model_class: Type[T], **filters) -> int:
        """
        Count records with tenant filtering.
        
        Args:
            model_class: SQLAlchemy model class
            **filters: Additional filter criteria
            
        Returns:
            Number of matching records
        """
        query = self._base_query(model_class)
        
        # Apply additional filters
        for field, value in filters.items():
            if hasattr(model_class, field):
                query = query.filter(getattr(model_class, field) == value)
        
        return query.count()
    
    def _list_records(self, model_class: Type[T], limit: Optional[int] = None, 
                     offset: Optional[int] = None, **filters) -> List[T]:
        """
        List records with tenant filtering and pagination.
        
        Args:
            model_class: SQLAlchemy model class
            limit: Maximum number of records to return
            offset: Number of records to skip
            **filters: Additional filter criteria
            
        Returns:
            List of matching records
        """
        query = self._base_query(model_class)
        
        # Apply additional filters
        for field, value in filters.items():
            if hasattr(model_class, field):
                query = query.filter(getattr(model_class, field) == value)
        
        # Apply pagination
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def _update_record(self, record: T, **updates) -> T:
        """
        Update a record with validation.
        
        Args:
            record: Record to update
            **updates: Fields to update
            
        Returns:
            Updated record
            
        Raises:
            TenantAccessError: If record doesn't belong to current tenant
        """
        # Verify record belongs to current tenant
        if hasattr(record, 'business_id') and record.business_id != self.business_id:
            raise TenantAccessError(f"Access denied to record {record.id}")
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(record, field):
                setattr(record, field, value)
        
        return record
    
    def _delete_record(self, record: T) -> None:
        """
        Delete a record with tenant validation.
        
        Args:
            record: Record to delete
            
        Raises:
            TenantAccessError: If record doesn't belong to current tenant
        """
        # Verify record belongs to current tenant
        if hasattr(record, 'business_id') and record.business_id != self.business_id:
            raise TenantAccessError(f"Access denied to record {record.id}")
        
        self.db.delete(record)
    
    def get_tenant_context(self) -> dict:
        """
        Get tenant context information.
        
        Returns:
            Dictionary with tenant context details
        """
        return {
            'business_id': self.business_id,
            'business_name': self.business.name if self.business else None,
            'tenant_type': 'business',  # Future: support firm-level tenancy
        }
