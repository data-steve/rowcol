# ADR-002: Comprehensive Testing Strategy

**Date**: 2025-09-18  
**Status**: Accepted  
**Decision**: Unified testing approach covering mock-first development, multi-tenancy testing, and architectural alignment.

## Context

Oodaloo requires a comprehensive testing strategy that addresses:
1. **External dependencies** (QBO, email, payment processors) with complex setup and costs
2. **Multi-tenant architecture** requiring tenant isolation testing
3. **Architectural boundaries** between domains/ (QBO primitives) and runway/ (product features)
4. **Development velocity** with fast feedback loops
5. **Production confidence** through realistic testing scenarios

## Decision

We implement a **Mock-First, Multi-Tenant Aware, Architecturally-Aligned Testing Strategy** with three complementary approaches.

## I. Mock-First Development

### Core Principle
Develop against mocks first, integrate with real services second.

### Provider Pattern Implementation
```python
# Abstract provider interface
class QBOProvider(ABC):
    @abstractmethod
    def get_bills(self, business_id: str) -> List[Dict]:
        pass

# Mock implementation (default)
class MockQBOProvider(QBOProvider):
    def get_bills(self, business_id: str) -> List[Dict]:
        return load_realistic_mock_data("bills.json")

# Real implementation (production)
class QuickBooksProvider(QBOProvider):
    def get_bills(self, business_id: str) -> List[Dict]:
        return self.qbo_client.query_bills(business_id)

# Factory pattern for seamless switching
def get_qbo_provider(business_id: str) -> QBOProvider:
    if settings.USE_MOCK_QBO:
        return MockQBOProvider()
    return QuickBooksProvider(business_id)
```

### Benefits
- **Fast development** without external API dependencies
- **Predictable testing** with consistent, realistic data
- **Cost control** during development phases
- **Offline development** capability

## II. Multi-Tenancy Testing

### Tenant-Aware Service Testing
```python
# Enhanced TenantAwareService with optional validation
class TenantAwareService:
    def __init__(self, db: Session, business_id: str, validate_business: bool = True):
        if validate_business:
            self.business = self._validate_business_access(business_id)
        else:
            self.business = None  # For testing

# Three testing approaches:
# 1. Database-dependent (integration)
def test_tenant_isolation_integration():
    business_a = create_test_business("biz_a")
    business_b = create_test_business("biz_b")
    
    service_a = BillService(db, business_a.business_id)
    service_b = BillService(db, business_b.business_id)
    
    # Verify tenant isolation
    assert service_a.get_bills() != service_b.get_bills()

# 2. Decoupled unit (fast)
def test_business_logic_decoupled():
    service = TestServiceFactory.create_service(
        BillService, 
        business_id="test_biz",
        validate_business=False
    )
    # Test pure business logic without database overhead

# 3. In-memory pure (fastest)
def test_calculation_algorithm():
    due_date = datetime(2025, 10, 15)
    result = due_date + timedelta(days=5)  # Direct calculation
    assert result == expected
```

### Tenant Isolation Verification
```python
def test_tenant_data_isolation():
    """Ensure businesses cannot access each other's data."""
    business_a = create_test_business("business_a")
    business_b = create_test_business("business_b")
    
    tray_item_a = create_tray_item(business_id=business_a.business_id)
    
    tray_service_b = TrayService(db, business_b.business_id)
    items_b = tray_service_b.get_tray_items()
    
    assert tray_item_a not in items_b
    assert len(items_b) == 0
```

## III. Architectural Alignment

### Test Structure
```
tests/
├── domains/unit/{ap,ar,bank,core,integrations}/     # QBO Primitives
├── domains/integration/                             # Cross-domain integration
├── runway/unit/{ap,ar,analytics,auth,digest}/      # Product Features  
├── runway/integration/                              # End-to-end workflows
└── shared/{fixtures,services,utils}/               # Reusable test utilities
```

### Testing Boundaries
- **`domains/` tests** = QBO primitive stability, data models, sync logic
- **`runway/` tests** = Product features, business logic, user workflows

### Test Categories by Speed
1. **Unit Tests** (< 1s) - Pure business logic, algorithms, calculations
2. **Integration Tests** (< 5s) - Database operations, service interactions  
3. **End-to-End Tests** (< 30s) - Full workflows with mocked external services

## Implementation Guidelines

### All Services Support Testing Modes
```python
class DomainService(TenantAwareService):
    def __init__(self, db: Session, business_id: str, 
                 validate_business: bool = True, **providers):
        super().__init__(db, business_id, validate_business)
        self.qbo_provider = providers.get('qbo_provider') or get_qbo_provider(business_id)
        self.email_provider = providers.get('email_provider') or get_email_provider()
```

### Test Service Factory
```python
class TestServiceFactory:
    @staticmethod
    def create_service(service_class, business_id="test_business", 
                      use_mocks=True, **kwargs):
        providers = {}
        if use_mocks:
            providers.update({
                'qbo_provider': MockQBOProvider(),
                'email_provider': MockEmailProvider(),
            })
        
        return service_class(
            db=kwargs.get('db', Mock()),
            business_id=business_id,
            validate_business=False,
            **providers
        )
```

### Mock Data Strategy
- **Realistic scenarios** based on actual customer data patterns
- **Edge cases** for error handling and boundary conditions
- **Performance data** for load testing scenarios
- **Versioned fixtures** maintained alongside API changes

## Testing Workflows

### Development Workflow
1. **Write tests with mocks** - Fast feedback, no external dependencies
2. **Implement business logic** - Focus on algorithms and workflows
3. **Validate with integration tests** - Real database, mocked externals
4. **Production validation** - Real services in staging environment

### CI/CD Pipeline
1. **Unit tests** (mocked) - Every commit, < 30 seconds
2. **Integration tests** (database) - Every PR, < 5 minutes  
3. **E2E tests** (mocked externals) - Every merge, < 15 minutes
4. **Production smoke tests** - Post-deployment, real services

## Benefits

✅ **Development Velocity** - Fast feedback loops without external dependencies  
✅ **Cost Control** - Minimal API usage during development  
✅ **Tenant Safety** - Guaranteed isolation through comprehensive testing  
✅ **Architectural Integrity** - Tests respect domain boundaries  
✅ **Production Confidence** - Realistic scenarios with predictable data  
✅ **Maintenance Efficiency** - Clear test organization and responsibilities  

## Migration Path

1. ✅ **Enhanced TenantAwareService** with optional validation
2. ✅ **Test structure reorganization** aligned with ADR-001
3. ✅ **Mock providers** for external services
4. ✅ **Decoupled testing utilities** in tests/shared/
5. 🔄 **Gradual service updates** to support testing modes
6. 📝 **Mock data expansion** for comprehensive scenarios

---

**Status**: Successfully implemented with Smart AP features demonstrating all three testing approaches.
