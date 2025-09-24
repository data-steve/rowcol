"""
Test-specific service base classes that remove tight coupling for unit testing.

These classes allow testing business logic without requiring database setup
or real business entities.
"""

from typing import TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from unittest.mock import Mock

from domains.core.services.base_service import TenantAwareService

T = TypeVar('T')


class MockTenantAwareService(TenantAwareService):
    """
    Mock version of TenantAwareService for unit testing.
    
    Removes the requirement for a real business entity to exist in the database,
    allowing pure unit testing of business logic.
    """
    
    def __init__(self, business_id: str = "test_business", db: Optional[Session] = None):
        """
        Initialize mock tenant-aware service.
        
        Args:
            business_id: Business identifier for tenant isolation (default: "test_business")
            db: Database session (can be None or Mock for unit tests)
        """
        self.db = db or Mock()
        self.business_id = business_id
        self.business = None  # No real business validation in tests
    
    def _validate_business_access(self, business_id: str):
        """Mock business validation - always succeeds."""
        return Mock(business_id=business_id, name="Mock Business")


class TestServiceFactory:
    """
    Factory for creating test-friendly service instances.
    
    Provides a clean way to create services for testing without database coupling.
    """
    
    @staticmethod
    def create_service(service_class: Type[TenantAwareService], 
                      business_id: str = "test_business",
                      db: Optional[Session] = None,
                      **kwargs) -> TenantAwareService:
        """
        Create a service instance for testing.
        
        Args:
            service_class: The service class to instantiate
            business_id: Business ID for tenant isolation
            db: Database session (can be Mock)
            **kwargs: Additional arguments for service initialization
            
        Returns:
            Service instance with business validation disabled
        """
        # For testing, disable business validation
        return service_class(
            db=db or Mock(),
            business_id=business_id,
            validate_business=False,
            **kwargs
        )


class InMemoryTestService:
    """
    In-memory service base for pure unit testing.
    
    Provides tenant-aware patterns without any database dependency.
    Useful for testing business logic in complete isolation.
    """
    
    def __init__(self, business_id: str = "test_business"):
        self.business_id = business_id
        self.business = Mock(business_id=business_id, name="Test Business")
        self._data_store: Dict[str, List[Any]] = {}
    
    def _get_store(self, model_name: str) -> List[Any]:
        """Get in-memory store for a model type."""
        if model_name not in self._data_store:
            self._data_store[model_name] = []
        return self._data_store[model_name]
    
    def _add_test_data(self, model_name: str, data: Any) -> Any:
        """Add test data to in-memory store."""
        store = self._get_store(model_name)
        # Auto-assign business_id for tenant isolation
        if hasattr(data, 'business_id'):
            data.business_id = self.business_id
        store.append(data)
        return data
    
    def _find_test_data(self, model_name: str, **filters) -> List[Any]:
        """Find test data with tenant filtering."""
        store = self._get_store(model_name)
        results = []
        
        for item in store:
            # Always filter by business_id for tenant isolation
            if hasattr(item, 'business_id') and item.business_id != self.business_id:
                continue
            
            # Apply additional filters
            match = True
            for field, value in filters.items():
                if not hasattr(item, field) or getattr(item, field) != value:
                    match = False
                    break
            
            if match:
                results.append(item)
        
        return results
    
    def get_tenant_context(self) -> dict:
        """Get tenant context for testing."""
        return {
            'business_id': self.business_id,
            'business_name': self.business.name,
            'tenant_type': 'test_business',
        }
