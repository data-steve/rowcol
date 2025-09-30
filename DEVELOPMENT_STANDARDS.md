# Development Standards & Anti-Patterns

## Core Principle: "Junior Developer Test"
Every piece of code should be understandable and debuggable by a junior/mid-level developer within 30 seconds.

## Coding Standards for Maintainability



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


