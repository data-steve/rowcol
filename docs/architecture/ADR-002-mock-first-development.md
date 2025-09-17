# ADR-002: Mock-First Development Strategy

**Date**: 2025-09-17  
**Status**: Accepted  
**Deciders**: Steve Simpson, Claude (AI Assistant)  
**Technical Story**: Phase 0.2 QBO Integration Validation  

## Context

Oodaloo integrates with multiple external services (QBO, email providers, payment processors) that have complex setup requirements, API costs, rate limits, and varying reliability. We need a development strategy that:

1. **Enables rapid development** without external dependencies
2. **Provides predictable testing** with consistent, realistic data
3. **Controls costs** during development and testing phases
4. **Supports offline development** when internet connectivity is limited
5. **Simplifies productionalization** with minimal code changes
6. **Validates business logic** independently from integration complexity

## Decision

We will implement a **Mock-First Development Strategy** using the provider pattern with environment-driven service selection.

### **Development Philosophy**

**Build → Validate → Integrate → Deploy**

1. **Build**: Develop business logic with mocked external services
2. **Validate**: Test with realistic mock data that mirrors production scenarios  
3. **Integrate**: Switch to sandbox/staging APIs for integration testing
4. **Deploy**: Enable production APIs with safety gates and monitoring

### **Provider Pattern Implementation**

All external integrations use the provider pattern:

```python
# Abstract provider interface
class EmailProvider(ABC):
    @abstractmethod
    def send_email(self, message: EmailMessage) -> EmailResult:
        pass

# Mock implementation for development
class MockEmailProvider(EmailProvider):
    def send_email(self, message: EmailMessage) -> EmailResult:
        # Realistic mock behavior with delays, success rates
        return EmailResult(status="sent", message_id=f"mock_{uuid4()}")

# Production implementation
class SendGridProvider(EmailProvider):
    def send_email(self, message: EmailMessage) -> EmailResult:
        # Real SendGrid API calls
        pass

# Environment-driven factory
def get_email_provider() -> EmailProvider:
    use_mock = os.getenv("USE_MOCK_EMAIL", "true").lower() == "true"
    if use_mock or os.getenv("ENVIRONMENT") == "development":
        return MockEmailProvider()
    else:
        return SendGridProvider()
```

### **Configuration-Driven Service Selection**

Services are selected based on environment variables:

**Development Configuration**:
```bash
# .env for development
ENVIRONMENT=development
USE_MOCK_EMAIL=true
USE_MOCK_QBO=true
USE_MOCK_PAYMENTS=true
USE_MOCK_HASH=true
DATABASE_URL=sqlite:///oodaloo.db
```

**Production Configuration**:
```bash
# .env for production
ENVIRONMENT=production
USE_MOCK_EMAIL=false
USE_MOCK_QBO=false
USE_MOCK_PAYMENTS=false
USE_MOCK_HASH=false
DATABASE_URL=postgresql://user:pass@host:5432/oodaloo

# Real API credentials
SENDGRID_API_KEY=real_key
QBO_CLIENT_ID=real_client_id
QBO_CLIENT_SECRET=real_secret
```

## Implementation Standards

### **Clean Mock Architecture**

❌ **Bad**: Mock data embedded in business logic
```python
class TrayService:
    def calculate_runway_impact(self, item):
        if item.type == "overdue_bill":
            return {"cash_impact": -1500}  # Hardcoded mock data
```

✅ **Good**: Mock data external via dependency injection
```python
class TrayService:
    def __init__(self, data_provider: TrayDataProvider = None):
        self.data_provider = data_provider or get_tray_data_provider()
    
    def calculate_runway_impact(self, item):
        return self.data_provider.get_runway_impact(item.type)
```

### **Realistic Mock Data**

Mock providers must generate realistic data that mirrors production:

```python
class MockQBOProvider(QBOProvider):
    def fetch_transactions(self, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        # Generate realistic variety
        transaction_types = [
            {"type": "expense", "base_amount": -500, "description": "Office supplies"},
            {"type": "deposit", "base_amount": 2500, "description": "Client payment"},
            {"type": "expense", "base_amount": -1200, "description": "Software subscription"},
        ]
        
        # Create realistic patterns
        transactions = []
        for i in range(20):  # Reasonable number for development
            tx_type = transaction_types[i % len(transaction_types)]
            transactions.append({
                "txn_id": f"MOCK_TXN_{i:04d}",
                "amount": tx_type["base_amount"] + (i * 10),  # Add variation
                "date": f"2025-01-{(i % 28) + 1:02d}",  # Spread across month
                "description": f"{tx_type['description']} #{i+1}",
                "vendor": f"Vendor_{i % 5 + 1}",  # Multiple vendors
            })
        
        return transactions
```

### **Service Abstraction Benefits**

1. **Rapid Development**: No external API setup required for Phases 0-3
2. **Predictable Testing**: Mock data ensures consistent test results
3. **Cost Control**: No API usage charges during development
4. **Offline Development**: Work without internet connectivity
5. **Easy Productionalization**: Simple environment variable changes

## Testing Strategy

### **Mock-Driven Testing**

```python
def test_runway_calculation_with_mock_data():
    """Test runway calculation with predictable mock data."""
    mock_provider = MockQBOProvider()
    digest_service = DigestService(db, qbo_provider=mock_provider)
    
    # Mock data is predictable and testable
    result = digest_service.calculate_runway(business_id="test")
    assert result["runway_months"] == 6.5  # Known expected value
```

### **Integration Testing Progression**

1. **Unit Tests**: Use mock providers exclusively
2. **Integration Tests**: Mix of mock and sandbox providers
3. **E2E Tests**: Sandbox providers with realistic test data
4. **Production Validation**: Real providers with monitoring

### **Test Data Management**

```python
# tests/fixtures/qbo_scenarios.py
MARKETING_AGENCY_SCENARIO = {
    "monthly_revenue": 50000,
    "monthly_expenses": 35000,
    "cash_accounts": [
        {"name": "Operating", "balance": 75000},
        {"name": "Payroll", "balance": 25000},
    ],
    "recurring_bills": [
        {"vendor": "HubSpot", "amount": 1200, "frequency": "monthly"},
        {"vendor": "Google Workspace", "amount": 144, "frequency": "monthly"},
    ]
}
```

## Production Transition

### **Staged Rollout**

**Phase 0-1**: Pure mock development
- All external services mocked
- Focus on business logic validation
- Rapid iteration and testing

**Phase 2**: Sandbox integration
- Switch to sandbox APIs for critical integrations (QBO)
- Keep non-critical services mocked (email, payments)
- Validate API contracts and error handling

**Phase 3**: Staging environment
- All real services in staging environment
- Production-like configuration
- End-to-end testing with real data

**Phase 4**: Production deployment
- Real services with monitoring
- Gradual feature rollout
- Comprehensive logging and alerting

### **Safety Gates**

All production services include safety gates:

```python
class ProductionEmailProvider(EmailProvider):
    def __init__(self):
        # Fail fast if not properly configured
        if os.getenv("ENVIRONMENT") == "production" and not os.getenv("SENDGRID_API_KEY"):
            raise ValueError("SENDGRID_API_KEY required in production")
        
        # Rate limiting
        self.rate_limiter = RateLimiter(max_requests=100, per_seconds=60)
    
    def send_email(self, message: EmailMessage) -> EmailResult:
        # Production safety checks
        if not self.rate_limiter.allow_request():
            raise RateLimitError("Email rate limit exceeded")
        
        # Real API call with comprehensive error handling
        try:
            return self._send_via_sendgrid(message)
        except Exception as e:
            logger.error(f"Email send failed: {e}", exc_info=True)
            raise EmailDeliveryError("Failed to send email")
```

## Benefits

### **Positive Outcomes**

✅ **Development Speed**: 3-5x faster development without external API setup  
✅ **Test Reliability**: Consistent, predictable test results  
✅ **Cost Efficiency**: No API charges during development  
✅ **Team Productivity**: Developers can work offline and independently  
✅ **Quality Assurance**: Business logic validated before integration complexity  
✅ **Risk Reduction**: Integration issues isolated from business logic bugs  

### **Business Value**

- **Faster Time to Market**: Rapid prototyping and validation
- **Lower Development Costs**: Reduced external service usage
- **Higher Code Quality**: Focus on business logic correctness
- **Predictable Releases**: Fewer integration-related surprises

## Risks and Mitigations

### **Risk**: Mock data doesn't match production reality
**Mitigation**: 
- Use realistic mock data based on actual API responses
- Regular validation against sandbox/staging APIs
- Comprehensive integration testing before production

### **Risk**: Hidden integration issues discovered late
**Mitigation**:
- Staged rollout with sandbox testing
- Comprehensive error handling in all providers
- Monitoring and alerting in production

### **Risk**: Mock providers become outdated
**Mitigation**:
- Regular updates to mock providers based on API changes
- Automated tests that validate mock vs real provider contracts
- Documentation of mock data sources and assumptions

## Implementation Guidelines

### **When to Create Mock Providers**

Create mock providers for services that:
- Have setup complexity (OAuth, API keys, webhooks)
- Charge per API call
- Have rate limits that affect development
- Require internet connectivity
- Have unreliable sandbox environments

### **When to Use Real Services**

Use real services for:
- Local services (database, file system)
- Simple, free APIs with good uptime
- Services where mocking adds more complexity than value

### **Mock Provider Quality Standards**

1. **Realistic Data**: Mirror production data patterns
2. **Error Simulation**: Include realistic error scenarios
3. **Performance Simulation**: Include realistic delays
4. **State Management**: Maintain consistency across calls
5. **Configuration**: Support different scenarios via environment variables

## Monitoring and Success Metrics

### **Development Metrics**

- **Setup Time**: New developer productive within 2 hours
- **Test Reliability**: >99% test pass rate with mock providers
- **Development Velocity**: Features completed 3x faster with mocks

### **Production Transition Metrics**

- **Integration Success Rate**: >95% successful mock → real transitions
- **Bug Discovery**: <10% of bugs discovered in production vs staging
- **Performance**: Real providers perform within 20% of mock provider benchmarks

## Future Considerations

### **Advanced Mock Capabilities**

- **Record/Replay**: Capture real API responses for mock data
- **Chaos Testing**: Introduce realistic failure scenarios
- **Performance Testing**: Simulate production load characteristics

### **Multi-Environment Strategy**

```bash
# Development
USE_MOCK_*=true

# Staging  
USE_MOCK_EMAIL=false  # Test real email
USE_MOCK_QBO=true     # Keep QBO mocked for cost control

# Production
USE_MOCK_*=false      # All real services
```

## References

- **Clean Architecture**: Martin, Robert. "Clean Architecture: A Craftsman's Guide"
- **Test-Driven Development**: Beck, Kent. "Test Driven Development: By Example"
- **Oodaloo Implementation**: `runway/services/email/`, `runway/tray/providers/`
- **QBO Integration**: `docs/integrations/qbo/README.md`

---

**Last Updated**: 2025-09-17  
**Next Review**: Phase 1 completion (when we integrate real payment processing)
