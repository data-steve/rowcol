# QBO Integration Testing Suite
## Comprehensive Testing for Production-Grade QBO Infrastructure

This testing suite validates the QBO integration infrastructure with real-world business scenarios and production-grade reliability testing.

---

## **Test Architecture**

### **Core Test Components**

#### **1. Unit Tests** (`test_qbo_integration.py`)
- **QBOConnectionManager** functionality
- **QBOHealthMonitor** operations  
- **SmartSyncService** integration
- Token refresh and authentication flows
- Circuit breaker patterns
- Error handling and recovery

#### **2. Scenario Tests** (`test_scenarios.py`)
- **Business Scenario Validation**: 5 real-world business types
- **End-to-End Testing**: Complete data flow validation
- **Production Simulation**: Load testing and resilience
- **Data Quality Analysis**: QBO data structure validation

#### **3. Integration Tests** (Built-in)
- **Real QBO Sandbox**: Live API testing
- **Mock Data Testing**: Isolated unit testing
- **Performance Testing**: Response time and throughput
- **Failure Simulation**: Recovery and resilience testing

---

## **Business Scenarios**

### **1. Marketing Agency**
```bash
python domains/integrations/qbo/tests/test_scenarios.py --scenario marketing_agency
```
**Profile**: High AR, seasonal cash flow, 15 employees, $85k monthly revenue  
**Tests**: High-volume invoices, AR aging, payment timing optimization  
**Success Criteria**: 92% accuracy, 85% data quality, 120 days expected runway

### **2. Construction Company**
```bash
python domains/integrations/qbo/tests/test_scenarios.py --scenario construction_company
```
**Profile**: Large projects, equipment purchases, 45 employees, $250k monthly revenue  
**Tests**: Large transactions, progress billing, project-based cash flow  
**Success Criteria**: 88% accuracy, 80% data quality, 90 days expected runway

### **3. Professional Services**
```bash
python domains/integrations/qbo/tests/test_scenarios.py --scenario professional_services
```
**Profile**: Law firm, recurring revenue, 25 employees, $150k monthly revenue  
**Tests**: Recurring patterns, retainer handling, time-based billing  
**Success Criteria**: 95% accuracy, 90% data quality, 180 days expected runway

### **4. E-commerce Business**
```bash
python domains/integrations/qbo/tests/test_scenarios.py --scenario ecommerce_business
```
**Profile**: High transaction volume, inventory, 12 employees, $180k monthly revenue  
**Tests**: High-volume processing, inventory expenses, seasonal patterns  
**Success Criteria**: 85% accuracy, 75% data quality, 100 days expected runway

### **5. Consulting Firm**
```bash
python domains/integrations/qbo/tests/test_scenarios.py --scenario consulting_firm
```
**Profile**: Project-based billing, 8 employees, $120k monthly revenue  
**Tests**: Project revenue, contractor payments, milestone billing  
**Success Criteria**: 93% accuracy, 88% data quality, 200 days expected runway

---

## **Running Tests**

### **Prerequisites**
```bash
# Install dependencies
pip install pytest pytest-asyncio

# Set up environment (for real QBO testing)
export QBO_CLIENT_ID="your_client_id"
export QBO_CLIENT_SECRET="your_client_secret"
export QBO_REALM_ID="your_sandbox_realm_id"
export QBO_ACCESS_TOKEN="your_access_token"
export QBO_REFRESH_TOKEN="your_refresh_token"
```

### **Unit Tests**
```bash
# Run all unit tests
python -m pytest domains/integrations/qbo/tests/test_qbo_integration.py -v

# Run specific test class
python -m pytest domains/integrations/qbo/tests/test_qbo_integration.py::TestQBOConnectionManager -v

# Run with coverage
python -m pytest domains/integrations/qbo/tests/test_qbo_integration.py --cov=domains.integrations.qbo
```

### **Scenario Tests**
```bash
# Run all scenarios (mock data)
python domains/integrations/qbo/tests/test_scenarios.py --all

# Run specific scenario (mock data)
python domains/integrations/qbo/tests/test_scenarios.py --scenario marketing_agency

# Run with real QBO sandbox
QBO_TEST_MODE=sandbox python domains/integrations/qbo/tests/test_scenarios.py --scenario marketing_agency --real-qbo

# Save results to file
python domains/integrations/qbo/tests/test_scenarios.py --all --output qbo_test_results.json
```

### **Integration Tests**
```bash
# Run integration tests with real QBO
QBO_TEST_MODE=sandbox python -m pytest domains/integrations/qbo/tests/test_qbo_integration.py::TestProductionScenarios -v

# Run load testing simulation
python -m pytest domains/integrations/qbo/tests/test_qbo_integration.py::TestProductionScenarios::test_load_testing_simulation -v
```

---

## **Test Results Interpretation**

### **Success Criteria**

#### **QBO Health Score** (0-100%)
- **90-100%**: Excellent - Production ready
- **80-89%**: Good - Minor issues to address
- **70-79%**: Fair - Significant issues present
- **<70%**: Poor - Major problems require attention

#### **Data Quality Score** (0-100%)
- **90-100%**: Excellent - Clean, complete data
- **80-89%**: Good - Minor data issues
- **70-79%**: Fair - Some data quality problems
- **<70%**: Poor - Significant data issues

#### **Runway Accuracy** (0-100%)
- **95-100%**: Excellent - Highly accurate calculations
- **90-94%**: Good - Acceptable accuracy
- **85-89%**: Fair - Some calculation drift
- **<85%**: Poor - Inaccurate runway calculations

### **Common Issues and Solutions**

#### **Connection Health Issues**
```
Issue: QBO connection unhealthy
Solution: Check credentials, network connectivity, token expiration
Command: Check /integrations/qbo/health/business/{business_id}
```

#### **Data Quality Issues**
```
Issue: Missing or incomplete QBO data
Solution: Verify QBO setup, permissions, data completeness
Command: Review QBO sandbox data via QBO web interface
```

#### **Runway Accuracy Issues**
```
Issue: Runway calculations inaccurate
Solution: Review calculation logic, QBO data mapping
Command: Debug with SmartSyncService.get_qbo_data_for_digest()
```

#### **Token Refresh Issues**
```
Issue: Token refresh failing
Solution: Verify client credentials, refresh token validity
Command: Test with QBOConnectionManager._refresh_token()
```

---

## **Continuous Integration**

### **CI/CD Integration**
```yaml
# .github/workflows/qbo-tests.yml
name: QBO Integration Tests
on: [push, pull_request]

jobs:
  qbo-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run QBO unit tests
        run: |
          python -m pytest domains/integrations/qbo/tests/test_qbo_integration.py -v --cov=domains.integrations.qbo
      
      - name: Run QBO scenario tests (mock)
        run: |
          python domains/integrations/qbo/tests/test_scenarios.py --all
      
      - name: Run QBO integration tests (if sandbox credentials available)
        env:
          QBO_TEST_MODE: sandbox
          QBO_CLIENT_ID: ${{ secrets.QBO_CLIENT_ID }}
          QBO_CLIENT_SECRET: ${{ secrets.QBO_CLIENT_SECRET }}
          QBO_REALM_ID: ${{ secrets.QBO_REALM_ID }}
          QBO_ACCESS_TOKEN: ${{ secrets.QBO_ACCESS_TOKEN }}
          QBO_REFRESH_TOKEN: ${{ secrets.QBO_REFRESH_TOKEN }}
        run: |
          if [ ! -z "$QBO_CLIENT_ID" ]; then
            python domains/integrations/qbo/tests/test_scenarios.py --scenario marketing_agency --real-qbo
          fi
```

### **Pre-commit Hooks**
```bash
# Install pre-commit
pip install pre-commit

# Add to .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: qbo-tests
        name: QBO Integration Tests
        entry: python -m pytest domains/integrations/qbo/tests/test_qbo_integration.py -x
        language: system
        pass_filenames: false
```

---

## **Development Workflow**

### **Adding New Tests**
1. **Unit Tests**: Add to `test_qbo_integration.py`
   - Follow existing test patterns
   - Use proper mocking for external dependencies
   - Test both success and failure scenarios

2. **Scenario Tests**: Add to `test_scenarios.py`
   - Create realistic business scenario
   - Define clear success criteria
   - Include data quality validation

### **Test Data Management**
```python
# Create test fixtures in test_qbo_integration.py
@pytest.fixture
def sample_qbo_data():
    return {
        "bills": [...],
        "invoices": [...],
        "accounts": [...]
    }
```

### **Debugging Failed Tests**
```bash
# Run with verbose output
python -m pytest domains/integrations/qbo/tests/ -v -s

# Run specific failing test
python -m pytest domains/integrations/qbo/tests/test_qbo_integration.py::TestQBOConnectionManager::test_token_refresh_success -v -s

# Use pdb for debugging
python -m pytest domains/integrations/qbo/tests/ --pdb
```

---

## **Production Monitoring Integration**

### **Health Check Endpoints**
```bash
# Test health monitoring endpoints
curl http://localhost:8000/integrations/qbo/health/summary
curl http://localhost:8000/integrations/qbo/health/business/{business_id}
curl http://localhost:8000/integrations/qbo/health/dashboard
```

### **Prometheus Metrics**
```bash
# Get metrics for monitoring
curl http://localhost:8000/integrations/qbo/health/metrics/prometheus
```

### **Status Page**
```bash
# Client-facing status
curl http://localhost:8000/integrations/qbo/health/status-page
```

---

## **Best Practices**

### **Test Organization**
- ✅ **Separate concerns**: Unit tests, integration tests, scenario tests
- ✅ **Use fixtures**: Reusable test data and setup
- ✅ **Mock external dependencies**: Isolate QBO API calls for unit tests
- ✅ **Test failure scenarios**: Error handling and recovery paths

### **Test Data**
- ✅ **Realistic scenarios**: Based on actual business patterns
- ✅ **Edge cases**: Empty data, large datasets, malformed responses
- ✅ **Consistent data**: Reproducible test results
- ✅ **Clean up**: Remove test data after tests complete

### **Performance Testing**
- ✅ **Response times**: API calls should complete within reasonable time
- ✅ **Concurrent access**: Multiple businesses accessing QBO simultaneously
- ✅ **Rate limiting**: Respect QBO API rate limits
- ✅ **Memory usage**: Monitor memory consumption during tests

### **Security Testing**
- ✅ **Token security**: Ensure tokens are not logged or exposed
- ✅ **Input validation**: Test with malformed QBO responses
- ✅ **Error information**: Don't leak sensitive information in errors
- ✅ **Access controls**: Verify business isolation

---

## **Troubleshooting**

### **Common Test Failures**

#### **Import Errors**
```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/oodaloo"
```

#### **Database Connection Issues**
```bash
# Verify database configuration
python -c "from db.session import SessionLocal; db = SessionLocal(); print('DB connected')"
```

#### **QBO Sandbox Issues**
```bash
# Verify QBO credentials
python -c "
import os
from domains.integrations.qbo.qbo_connection_manager import QBOConnectionManager
from db.session import SessionLocal
import asyncio

async def test():
    db = SessionLocal()
    manager = QBOConnectionManager(db)
    healthy = await manager.ensure_healthy_connection('test-business-123')
    print(f'QBO Health: {healthy}')

asyncio.run(test())
"
```

### **Getting Help**
- **Documentation**: Review QBO API documentation
- **Logs**: Check application logs for detailed error information
- **Health Endpoints**: Use health monitoring endpoints for diagnostics
- **Support**: Contact QBO developer support for API issues

---

## **Future Enhancements**

### **Planned Improvements**
- **Visual Test Reports**: HTML test result dashboards
- **Performance Benchmarking**: Historical performance tracking
- **Automated Data Generation**: QBO sandbox data seeding
- **Multi-Region Testing**: Geographic redundancy validation

### **Integration Opportunities**
- **Monitoring Systems**: Grafana/Prometheus integration
- **Alerting**: PagerDuty/Slack notifications for test failures
- **Documentation**: Auto-generated API documentation
- **Load Testing**: JMeter/Artillery integration for stress testing

This comprehensive testing suite ensures our QBO integration meets production-grade reliability and performance standards.
