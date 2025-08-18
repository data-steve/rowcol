You're absolutely right on both points! Let me address these:

## 1. **Audit Logging Integration with Review System**

Looking at the `auditlogs.md`, I can see that audit logging was designed as a **separate system** from the review queue, but you're correct that they should be **integrated**. The current design has:

- **Audit Logging**: Tracks mutations (who, what, when) - read-only
- **Review Queue**: Interactive validation of low-confidence data

But for your operational model, these should work together where:
- **BookClose** detects issues → **Audit Log** tracks the detection
- **Bookkeeper** resolves tier 1 → **Audit Log** tracks the resolution  
- **Controller** handles tier 2 → **Audit Log** tracks the escalation

## 2. **Missing Cloudfirms.io Features in dev_plan.md**

You're absolutely correct! Looking at the current `dev_plan.md`, several key models and services that would support your tier classification and evidence packaging are **missing**:

### **Missing Models That Support Your Requirements:**

```python
# These are mentioned in the backlog but not in the main stages:

class Service(Base):  # Missing from core models
    """Service offerings and pricing tiers"""
    
class FixedAsset(Base):  # Missing from core models  
    """Fixed asset tracking and depreciation"""
    
class TrialBalance(Base):  # Missing from core models
    """Trial balance validation and integrity checks"""
    
class ComplianceCheck(Base):  # Missing from core models
    """Compliance and regulatory checks"""
    
class Review(Base):  # Missing from core models
    """Review workflow and approval tracking"""
    
class IntakeRequest(Base):  # Missing from core models
    """Client intake and onboarding requests"""
    
class QBOConnection(Base):  # Missing from core models
    """QBO connection management and sync status"""
    
class ValidationEvent(Base):  # Missing from core models
    """Data validation events and integrity checks"""
    
class Workpaper(Base):  # Missing from core models
    """Workpaper management and evidence linking"""
    
class WorkpaperAnnotation(Base):  # Missing from core models
    """Annotations and notes on workpapers"""
```

## **What This Means for Your Requirements:**

### **Missing Tier Classification Support:**
- `ComplianceCheck` and `ValidationEvent` would handle the detection logic you need
- `Review` would manage the escalation workflow (Bookkeeper → Controller)
- `Workpaper` and `WorkpaperAnnotation` would handle evidence packaging

### **Missing Close Integrity Detection:**
- `TrialBalance` would handle the reconciliation integrity checks
- `FixedAsset` would handle depreciation and cutoff tests
- `Service` would handle pricing tier logic for different automation levels

## **Recommendation:**

The `dev_plan.md` should be updated to include these missing models in **Stage 0** (core foundation) since they're fundamental to the tier classification and evidence packaging system you need. They're currently buried in the backlog but should be part of the core architecture.

Would you like me to:
1. **Update the dev_plan.md** to include these missing models in the appropriate stages?
2. **Integrate audit logging with the review system** so they work together instead of separately?
3. **Show how these missing models** would support your tier classification requirements?

The current plan is about 85% complete, but these missing pieces are critical for the operational model you described.