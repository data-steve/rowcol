# _parked/ Directory - Phase-Based Feature Parking

## Overview
This directory contains code that has been temporarily or permanently removed from the active codebase during the Phase 0 refactor. Files are organized by their intended reactivation phase or permanent deprecation status.

## Organization Structure
```
_parked/
├── domains/           # Mirror of active domains/ - organized by business domain
├── features/          # Feature-specific parking - organized by major features  
├── tools/            # Development tools and bootstrappers
└── deprecated/       # Files that will NEVER be reactivated
```

## Phase Roadmap & Reactivation Plan

### **Phase 0** (Current - MVP Complete) ✅
**Focus**: Single business, basic QBO integration, cash runway management
- ✅ Business model (replaces Client/Firm)
- ✅ User management (single user per business)
- ✅ Basic QBO integration (mocked initially)
- ✅ Prep Tray for cash runway
- ✅ Core database functionality

### **Phase 1** (Payment Processing & Basic AP/AR) 🔄
**Reactivate from `domains/ap/` and `domains/ar/`:**
- `domains/ap/models/payment.py` - AP payment processing
- `domains/ap/services/statement_reconciliation.py` - Statement matching
- `domains/ar/models/payment.py` - AR payment processing  
- `domains/ar/services/payment_application.py` - Payment application
- `domains/bank/services/cash_reconciliation.py` - Basic reconciliation

**Status**: Ready to reactivate - just needs relationship fixes

### **Phase 2** (Advanced Features & Job Costing) 📋
**Reactivate from `domains/core/` and `features/job_costing/`:**
- `domains/core/models/job.py` - Job costing model
- `domains/core/models/staff.py` - Staff management
- `domains/core/models/task.py` - Task management
- `domains/integrations/` - Advanced integrations (Stripe, Jobber)
- `domains/policy/` - Advanced policy engine features

**Status**: Needs significant work - parked due to complexity

### **Phase 3** (Close Automation & Advanced Reporting) 📊
**Reactivate from `features/close/`:**
- `features/close/models/preclose.py` - Month-end close automation
- `features/close/services/` - Close process orchestration
- `features/close/routes/` - Close management APIs

**Status**: Future phase - complete feature set

## File Categories & Reactivation Status

### 🟢 **Ready to Reactivate** (Minor fixes needed)
Files that can be brought back with minimal relationship/import fixes:

**AP Domain:**
- `domains/ap/models/payment.py` - Just needs customer_id FK fix
- `domains/ap/services/statement_reconciliation.py` - Import path fixes
- `domains/ap/tests/test_payment.py` - Update for new relationships

**AR Domain:**  
- `domains/ar/models/payment.py` - Just needs customer_id FK fix
- `domains/ar/services/payment_application.py` - Minor relationship fixes
- `domains/ar/tests/test_payment_application.py` - Update test fixtures

**Bank Domain:**
- `domains/bank/services/cash_reconciliation.py` - Import path updates
- `domains/bank/services/transfer.py` - FK reference fixes

### 🟡 **Needs Moderate Work** (Architectural changes needed)
Files that require more significant refactoring:

**Core Domain:**
- `domains/core/models/job.py` - Job costing relationships need redesign
- `domains/core/models/staff.py` - Staff/User relationship conflicts  
- `domains/core/models/task.py` - Task assignment system needs rework

**Policy Domain:**
- `domains/policy/services/` - Policy engine advanced features
- `domains/policy/models/correction.py` - Already partially reactivated

**Integrations:**
- `domains/integrations/qbo/` - Advanced QBO features beyond basic sync
- `domains/webhooks/` - Webhook system for real-time updates

### 🔴 **Permanently Deprecated** (Will NEVER be reactivated)
Files that are obsolete due to architectural changes:

**Deprecated Models:**
- `deprecated/legacy_models/client.py` - Replaced by Business model
- `deprecated/legacy_models/firm.py` - Replaced by Business model  
- `deprecated/legacy_models/engagement_entities.py` - Obsolete engagement model

**Deprecated Services:**
- `deprecated/legacy_services/client.py` - Business service handles this
- `deprecated/legacy_services/business_entity.py` - Simplified in Phase 0

**Deprecated Tests:**
- `deprecated/legacy_tests/` - Tests for deprecated models/services

### 🔧 **Tools & Utilities** (Situational reactivation)
Development tools that may be useful for bootstrapping:

**Policy Tools:**
- `tools/policy_bootstrapper/` - Policy engine setup and data migration
- `tools/sample/` - Sample data generation for testing

## Reactivation Guidelines

### Before Reactivating Any File:
1. **Check Phase Alignment** - Ensure the feature belongs in the current phase
2. **Update Imports** - Fix any import paths that changed during refactor
3. **Fix Relationships** - Update SQLAlchemy relationships for Business model
4. **Update Tests** - Ensure test fixtures use new Business/User models
5. **Remove Client References** - Replace any remaining client/firm references

### Import Path Updates Needed:
```python
# OLD (will break)
from app.models.client import Client
from runway.services.policy_engine import PolicyEngineService

# NEW (current structure)  
from domains.core.models import Business
from domains.policy.services import PolicyEngineService
```

### Relationship Updates Needed:
```python
# OLD (will break)
client_id = Column(Integer, ForeignKey("clients.id"))
firm_id = Column(Integer, ForeignKey("firms.id"))

# NEW (current structure)
business_id = Column(String(36), ForeignKey("businesses.business_id"))
```

## Testing Strategy for Reactivated Files

### Phase 1 Testing:
```bash
# Test only Phase 1 features
poetry run pytest _parked/domains/ap/tests/ -v --disable-warnings
poetry run pytest _parked/domains/ar/tests/ -v --disable-warnings
```

### Avoid Full Test Suite Until Phase 3:
```bash
# DON'T DO THIS until all phases complete
poetry run pytest  # Will fail due to remaining parked features
```

## Maintenance Notes

- **Last Reorganized**: December 2024 during Phase 0 refactor
- **Reorganized By**: AI Assistant following user feedback on messy structure
- **Next Review**: After Phase 1 completion to validate reactivation success

## Questions for Future Phases

1. **Job Costing Scope**: How complex should the job costing model be in Phase 2?
2. **Staff Management**: Should Staff be separate from User or merged?
3. **Close Automation**: What level of automation is needed for month-end close?
4. **Integration Priority**: Which integrations (Stripe, Jobber, etc.) are highest priority?

---
*This README should be updated after each phase completion to reflect reactivation success and any architectural learnings.*
