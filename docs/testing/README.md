# Testing Strategy Guide

Comprehensive testing approach for Oodaloo's multi-phase development with mock-first strategy.

## Quick Start

### Run All Tests
```bash
# Run full test suite
poetry run pytest

# Run with coverage
poetry run pytest --cov=domains --cov=runway --cov-report=html

# Run specific domain tests
poetry run pytest domains/core/tests/ -v
poetry run pytest runway/tests/ -v
```

### Run Phase-Specific Tests
```bash
# Phase 0 tests only (active features)
poetry run pytest -m "phase0" -v

# Skip parked feature tests
poetry run pytest -m "not parked" -v

# QBO integration tests
poetry run pytest tests/qbo_integration/ -v
```

## Testing Architecture

### **Phase-Focused Testing Strategy**

Tests are organized by development phase to avoid testing parked features:

```python
# pytest.ini markers
[tool:pytest]
markers = 
    phase0: Phase 0 core functionality tests
    phase1: Phase 1 AP/payment tests  
    phase2: Phase 2 AR/collections tests
    parked: Tests for parked features (skipped)
    integration: Integration tests requiring external services
    qbo: QBO-specific integration tests
```

### **Test Organization**

```
tests/
├── conftest.py                 # Global fixtures and configuration
├── qbo_integration/            # QBO sandbox validation tests
│   ├── test_scenarios.py       # Realistic business scenarios
│   └── conftest.py            # QBO-specific fixtures
└── fixtures/                  # Shared test data
    ├── business_scenarios.py   # Business test data
    └── qbo_responses.py       # Mock QBO API responses

domains/core/tests/             # Core domain tests
├── test_business_model.py      # Business model tests
├── test_user_model.py         # User model tests
└── conftest.py                # Core domain fixtures

runway/tests/                   # Runway product tests
├── test_digest_service.py      # Digest generation tests
├── test_tray_service.py       # Tray functionality tests
└── conftest.py                # Runway-specific fixtures
```

## Mock-First Testing

### **Mock Provider Testing**

All external services use mock providers in tests:

```python
# Test with mock providers
def test_digest_generation_with_mock_qbo(db_session):
    """Test digest generation with predictable mock data."""
    mock_qbo_provider = MockQBOProvider()
    digest_service = DigestService(db_session, qbo_provider=mock_qbo_provider)
    
    result = digest_service.generate_digest(business_id="test_business")
    
    # Mock data is predictable and testable
    assert result["status"] == "success"
    assert result["runway_months"] == 6.5  # Known mock value
    assert result["email_sent"] == True
```

### **Provider Switching Tests**

Test that services work identically with mock and real providers:

```python
@pytest.mark.parametrize("provider_type", ["mock", "real"])
def test_email_service_provider_compatibility(provider_type):
    """Test email service works with both mock and real providers."""
    if provider_type == "mock":
        provider = MockEmailProvider()
    else:
        provider = SendGridProvider()  # In test mode
    
    email_service = EmailService(provider)
    result = email_service.send_digest_email(business_id="test")
    
    # Both providers should return same interface
    assert "message_id" in result
    assert result["status"] in ["sent", "queued"]
```

## Test Data Management

### **Realistic Business Scenarios**

Use realistic business data that mirrors production complexity:

```python
# tests/fixtures/business_scenarios.py
MARKETING_AGENCY_SCENARIO = {
    "business_profile": {
        "name": "Pixel Perfect Marketing",
        "industry": "Digital Marketing",
        "monthly_revenue": 50000,
        "employee_count": 8
    },
    "bank_accounts": [
        {"name": "Operating", "balance": 75000.00},
        {"name": "Payroll", "balance": 25000.00}
    ],
    "recurring_bills": [
        {"vendor": "HubSpot", "amount": 1200, "frequency": "monthly"},
        {"vendor": "Google Workspace", "amount": 144, "frequency": "monthly"}
    ],
    "outstanding_invoices": [
        {"client": "TechStart Inc", "amount": 8000, "terms": "NET 30"},
        {"client": "Healthcare Practice", "amount": 15000, "overdue_days": 5}
    ]
}
```

### **QBO Mock Responses**

Maintain realistic QBO API responses for consistent testing:

```python
# tests/fixtures/qbo_responses.py
QBO_COMPANY_INFO_RESPONSE = {
    "QueryResponse": {
        "CompanyInfo": [{
            "Name": "Test Company",
            "CompanyAddr": {"Line1": "123 Main St"},
            "Country": "US",
            "Id": "1"
        }]
    }
}

QBO_TRANSACTIONS_RESPONSE = {
    "QueryResponse": {
        "Item": [
            {
                "Id": "1",
                "Name": "Services",
                "Type": "Service",
                "UnitPrice": 100.00
            }
        ]
    }
}
```

## Testing Patterns

### **Service Layer Testing**

Test business logic independently from external dependencies:

```python
class TestTrayService:
    """Test tray service business logic."""
    
    @pytest.fixture
    def tray_service(self, db_session):
        """Create tray service with mock provider."""
        mock_provider = MockTrayDataProvider()
        return TrayService(db_session, data_provider=mock_provider)
    
    def test_priority_scoring(self, tray_service):
        """Test tray item priority calculation."""
        # Create test tray item
        item = TrayItem(
            type="overdue_bill",
            due_date=datetime.now() - timedelta(days=2),  # 2 days overdue
            amount=1500
        )
        
        score = tray_service.calculate_priority_score(item)
        
        # Overdue bill should have high priority
        assert score >= 80  # Urgent threshold
    
    def test_runway_impact_calculation(self, tray_service):
        """Test runway impact calculation."""
        item = TrayItem(type="overdue_bill", amount=2500)
        
        impact = tray_service._calculate_runway_impact(item)
        
        assert "cash_impact" in impact
        assert "days_impact" in impact
        assert impact["cash_impact"] < 0  # Bill reduces cash
```

### **API Route Testing**

Test API endpoints with proper tenant isolation:

```python
class TestTrayRoutes:
    """Test tray API endpoints."""
    
    def test_get_tray_items_requires_auth(self, client):
        """Test that tray endpoints require authentication."""
        response = client.get("/runway/tray/items")
        assert response.status_code == 401
    
    def test_get_tray_items_tenant_isolation(self, client, auth_headers):
        """Test that users only see their business's tray items."""
        # Create items for different businesses
        business_a_item = create_tray_item(business_id="business_a")
        business_b_item = create_tray_item(business_id="business_b")
        
        # User from business A should only see their items
        response = client.get(
            "/runway/tray/items",
            headers=auth_headers(business_id="business_a")
        )
        
        assert response.status_code == 200
        items = response.json()
        item_ids = [item["id"] for item in items]
        
        assert business_a_item.id in item_ids
        assert business_b_item.id not in item_ids
```

### **Integration Testing**

Test service interactions and data flow:

```python
class TestDigestIntegration:
    """Test digest generation end-to-end."""
    
    @pytest.mark.integration
    def test_digest_generation_flow(self, db_session):
        """Test complete digest generation workflow."""
        # Setup: Create business with realistic data
        business = create_test_business("test_business")
        create_test_bank_accounts(business.business_id)
        create_test_transactions(business.business_id)
        
        # Execute: Generate digest
        digest_service = DigestService(db_session)
        result = digest_service.generate_digest(business.business_id)
        
        # Verify: All components work together
        assert result["status"] == "success"
        assert "runway_months" in result
        assert "email_sent" in result
        
        # Verify: Email was generated with correct data
        assert result["runway_months"] > 0
        assert result["email_sent"] == True
```

## QBO Integration Testing

### **Sandbox Testing**

Test against real QBO sandbox when needed:

```python
@pytest.mark.qbo
@pytest.mark.skipif(not os.getenv("QBO_SANDBOX_ENABLED"), reason="QBO sandbox not configured")
class TestQBOSandboxIntegration:
    """Test QBO integration with real sandbox."""
    
    def test_qbo_connection(self):
        """Test QBO API connectivity."""
        qbo_service = QBOIntegrationService()
        result = qbo_service.test_connection()
        
        assert result["status"] == "connected"
        assert "company_info" in result
    
    def test_transaction_sync(self):
        """Test transaction synchronization."""
        data_service = DataIngestionService(db)
        result = data_service.sync_qbo(business_id="sandbox_business")
        
        assert result["status"] == "success"
        assert result["transactions_stored"] > 0
```

### **Webhook Testing**

Test QBO webhook handling:

```python
class TestQBOWebhooks:
    """Test QBO webhook processing."""
    
    def test_webhook_signature_verification(self, client):
        """Test webhook signature verification."""
        payload = {"eventNotifications": []}
        signature = generate_qbo_webhook_signature(payload)
        
        response = client.post(
            "/webhooks/qbo",
            json=payload,
            headers={"intuit-signature": signature}
        )
        
        assert response.status_code == 200
    
    def test_webhook_data_processing(self, client, db_session):
        """Test webhook data processing."""
        webhook_payload = {
            "eventNotifications": [{
                "realmId": "test_realm",
                "dataChangeEvent": {
                    "entities": [{
                        "name": "Bill",
                        "id": "123",
                        "operation": "Create"
                    }]
                }
            }]
        }
        
        response = client.post("/webhooks/qbo", json=webhook_payload)
        
        assert response.status_code == 200
        # Verify data was processed correctly
```

## Performance Testing

### **Load Testing**

Test performance with realistic data volumes:

```python
@pytest.mark.performance
class TestPerformance:
    """Test system performance under load."""
    
    def test_tray_query_performance(self, db_session):
        """Test tray query performance with large datasets."""
        # Setup: Create large dataset
        business_id = "perf_test_business"
        for i in range(1000):
            create_tray_item(business_id=business_id, index=i)
        
        # Test: Query performance
        start_time = time.time()
        tray_service = TrayService(db_session)
        items = tray_service.get_tray_items(business_id)
        query_time = time.time() - start_time
        
        # Verify: Performance meets requirements
        assert query_time < 0.1  # Sub-100ms
        assert len(items) == 1000
    
    def test_digest_generation_performance(self, db_session):
        """Test digest generation performance."""
        business_id = create_large_business_dataset()
        
        start_time = time.time()
        digest_service = DigestService(db_session)
        result = digest_service.generate_digest(business_id)
        generation_time = time.time() - start_time
        
        assert generation_time < 5.0  # Under 5 seconds
        assert result["status"] == "success"
```

## Test Configuration

### **pytest.ini Configuration**

```ini
[tool:pytest]
testpaths = tests domains runway
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    phase0: Phase 0 core functionality
    phase1: Phase 1 AP/payment features  
    phase2: Phase 2 AR/collections features
    parked: Parked features (skipped by default)
    integration: Integration tests
    qbo: QBO-specific tests
    performance: Performance tests

addopts = 
    -v
    --strict-markers
    --tb=short
    -m "not parked"  # Skip parked features by default

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### **conftest.py Global Configuration**

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(test_engine):
    """Create test database session."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def mock_qbo_provider():
    """Provide mock QBO service."""
    return MockQBOProvider()

# Skip parked features by default
def pytest_configure(config):
    """Configure pytest with custom markers."""
    if not config.option.markexpr:
        config.option.markexpr = "not parked"
```

## CI/CD Testing

### **GitHub Actions Configuration**

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    
    - name: Run Phase 0 tests
      run: poetry run pytest -m "phase0" --cov=domains --cov=runway
    
    - name: Run integration tests
      run: poetry run pytest -m "integration and not qbo"
      
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Monitoring and Metrics

### **Test Coverage Requirements**

- **Phase 0 Core**: >90% coverage
- **Runway Services**: >85% coverage  
- **Domain Models**: >95% coverage
- **API Routes**: >80% coverage

### **Test Performance Benchmarks**

- **Unit Tests**: <10ms average
- **Integration Tests**: <1s average
- **QBO Tests**: <5s average (with mocks)
- **Full Suite**: <2 minutes

## Troubleshooting

### **Common Test Issues**

**Problem**: Tests failing with tenant isolation errors
```bash
# Solution: Ensure all test data includes business_id
def create_test_tray_item(business_id="test_business"):
    return TrayItem(business_id=business_id, ...)
```

**Problem**: QBO integration tests timing out
```bash
# Solution: Use mock providers in unit tests
USE_MOCK_QBO=true poetry run pytest
```

**Problem**: Database state leaking between tests
```bash
# Solution: Use proper test fixtures with cleanup
@pytest.fixture
def db_session():
    session = TestSession()
    yield session
    session.rollback()  # Clean up after test
    session.close()
```

## Best Practices

### **Test Naming**
- Use descriptive test names that explain the scenario
- Follow pattern: `test_[action]_[condition]_[expected_result]`
- Example: `test_digest_generation_with_insufficient_data_returns_error`

### **Test Structure**
- Use AAA pattern: Arrange, Act, Assert
- One assertion per test when possible
- Use fixtures for common test data

### **Mock Usage**
- Mock external services, not internal business logic
- Use realistic mock data that mirrors production
- Test both mock and real providers when feasible

---

**Next**: See `docs/architecture/ADR-002-mock-first-development.md` for mock strategy details.
