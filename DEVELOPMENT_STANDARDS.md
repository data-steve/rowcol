# Development Standards & Anti-Patterns

## Quick Reference
- [Build Plan](Oodaloo_v4.5_Build_Plan.md)



### Service Abstraction Benefits

1. **Rapid Development**: No external API setup required for Phases 0-3
2. **Predictable Testing**: Mock data ensures consistent test results
3. **Cost Control**: No API usage charges during development
4. **Offline Development**: Work without internet connectivity
5. **Easy Productionalization**: Simple environment variable changes

### Clean Mocking Architecture Standards

**Core Principle**: Business logic functions must be completely agnostic to whether they're using mock or real data providers.

**Implementation Pattern**:
```python
# ✅ GOOD: Clean dependency injection
class TrayService:
    def __init__(self, db: Session, data_provider: TrayDataProvider = None):
        self.data_provider = data_provider or get_tray_data_provider()
    
    def calculate_runway_impact(self, item):
        return self.data_provider.get_runway_impact(item.type)

# ❌ BAD: Mock data embedded in business logic
class TrayService:
    def calculate_runway_impact(self, item):
        if item.type == "overdue_bill":
            return {"cash_impact": -1500}  # Hard-coded mock data
```

**Provider Pattern Requirements**:
1. **Abstract Base Class**: Define interface contract
2. **Mock Provider**: External class with realistic test data
3. **Production Provider**: Real integration implementation
4. **Factory Function**: Environment-based provider selection
5. **Environment Variables**: `USE_MOCK_*=true/false` controls

**Mock Data Strategy**:

**Mock Email Provider**:
- Logs emails to console and `logs/mock_emails_*.json`
- Tracks engagement metrics for testing
- Simulates delivery success/failure scenarios
- **Location**: `runway/services/email/mock_provider.py`

**Mock QBO Integration**:
- Returns realistic bill/invoice/balance data
- Simulates API rate limiting and errors
- Supports different business scenarios (healthy, cash-strapped, etc.)
- **Location**: `domains/integrations/qbo/mock_provider.py`

**Mock Tray Data**:
- Priority weights, runway impacts, action results
- Realistic business scenarios and edge cases
- **Location**: `runway/tray/providers/mock_data_provider.py`

**Mock Payment Processing**:
- Simulates payment success/failure rates
- Mock bank account verification
- Realistic processing delays and confirmations
- **Location**: `domains/ap/providers/mock_payment_provider.py`

**Benefits of Clean Mocking**:
- Services work identically with mock/real providers
- Easy to swap providers via environment variables
- Mock data can be shared across tests
- No risk of "fooling ourselves" with embedded test data
- Production code has zero mock contamination

## Coding Standards for Maintainability

### Core Principle: "Junior Developer Test"
Every piece of code should be understandable and debuggable by a junior/mid-level developer within 30 seconds.

### Database Transaction Patterns

**✅ GOOD: Transaction Context Managers**
```python
from contextlib import contextmanager

@contextmanager
def db_transaction(db: Session):
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise

# Usage
def create_business_and_user(business_data, user_data):
    with db_transaction(db):
        business = Business(**business_data)
        db.add(business)
        db.flush()  # Get ID without committing
        
        user_data["business_id"] = business.business_id
        user = User(**user_data)
        db.add(user)
        # Both saved together or both fail
```

**❌ BAD: Manual Commits**
```python
def create_business_and_user(business_data, user_data):
    business = Business(**business_data)
    db.add(business)
    db.commit()  # Danger: partial state if user creation fails
    
    user = User(**user_data)
    db.add(user)
    db.commit()
```

### Exception Handling Patterns

**✅ GOOD: Specific Exceptions with Context**
```python
def send_digest_email(business_id: str):
    try:
        business = get_business(business_id)
        digest_data = calculate_runway(business)
        email_result = send_email(digest_data)
        return email_result
    except BusinessNotFoundError as e:
        logger.error(f"Business {business_id} not found for digest: {e}")
        raise HTTPException(status_code=404, detail="Business not found")
    except EmailDeliveryError as e:
        logger.error(f"Email delivery failed for business {business_id}: {e}")
        raise HTTPException(status_code=500, detail="Email delivery failed")
    except Exception as e:
        logger.error(f"Unexpected error in digest generation for {business_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

**❌ BAD: Bare Exception Handling**
```python
def send_digest_email(business_id: str):
    try:
        # Complex logic here
        return result
    except Exception:
        pass  # Silent failure - impossible to debug
```

### Configuration and Constants

**✅ GOOD: Named Constants with Business Context**
```python
# config/business_rules.py
class RunwayThresholds:
    CRITICAL_DAYS = 7      # Less than 1 week = critical
    WARNING_DAYS = 30      # Less than 1 month = warning
    HEALTHY_DAYS = 90      # More than 3 months = healthy

class TrayPriorities:
    URGENT_SCORE = 80      # Requires immediate attention
    MEDIUM_SCORE = 60      # Should be handled today
    LOW_SCORE = 40         # Can wait until tomorrow

# Usage
if runway_days < RunwayThresholds.CRITICAL_DAYS:
    alert_level = "critical"
```

**❌ BAD: Magic Numbers**
```python
if runway_days < 7:  # Why 7? What does this mean?
    alert_level = "critical"

if priority_score > 80:  # Why 80? Who decided this?
    mark_urgent()
```

### Service Layer Patterns

**✅ GOOD: Clear Dependencies and Error Boundaries**
```python
class DigestService:
    def __init__(self, db: Session, email_provider: EmailProvider, 
                 runway_calculator: RunwayCalculator):
        self.db = db
        self.email_provider = email_provider
        self.runway_calculator = runway_calculator
    
    def generate_weekly_digest(self, business_id: str) -> DigestResult:
        """Generate weekly runway digest for a business.
        
        Args:
            business_id: UUID of the business
            
        Returns:
            DigestResult with email status and runway data
            
        Raises:
            BusinessNotFoundError: If business doesn't exist
            RunwayCalculationError: If runway calculation fails
            EmailDeliveryError: If email sending fails
        """
        business = self._get_business_or_raise(business_id)
        runway_data = self.runway_calculator.calculate(business)
        email_result = self.email_provider.send_digest(runway_data)
        return DigestResult(runway_data=runway_data, email_result=email_result)
```

**❌ BAD: Unclear Dependencies and No Documentation**
```python
class DigestService:
    def generate_digest(self, biz_id):  # What type? What does it return?
        # Complex logic with no explanation
        pass
```

### Why These Standards Matter

1. **Onboarding Speed**: New developers productive in days, not weeks
2. **Debugging Efficiency**: Find and fix bugs in minutes, not hours  
3. **Change Velocity**: Business requirement changes don't require rewrites
4. **Code Reviews**: Reviewers can focus on business logic, not deciphering code
5. **Technical Debt**: Prevents accumulation of "clever" code that becomes unmaintainable

## Risk Mitigation

### Technical Risks
- **QBO API Rate Limits**: Implement caching, batch operations, graceful degradation
- **Email Delivery Issues**: Multiple provider backup (SendGrid + Amazon SES)
- **Database Performance**: Query optimization, indexing strategy, connection pooling
- **Integration Complexity**: Comprehensive error handling, retry logic, audit trails

### Product Risks  
- **User Adoption**: Free digest preview, gradual feature introduction, customer success outreach
- **Feature Complexity**: Start simple, add complexity based on user feedback
- **Competitive Response**: Focus on unique runway ritual, build switching costs through data

### Business Risks
- **Market Validation**: Beta program with real agencies, measure engagement metrics
- **Pricing Sensitivity**: Modular pricing, clear ROI demonstration, free tier
- **Sales Channel**: QBO marketplace + direct CAS firm outreach

