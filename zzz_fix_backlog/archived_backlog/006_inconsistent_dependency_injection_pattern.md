# Tech Debt Discovery: Inconsistent Dependency Injection Pattern

**Status:** Discovery  
**Priority:** Medium  
**Effort:** Low-Medium  
**Type:** Architectural Consistency  

## Problem Statement

During the SmartSync refactoring, we have inconsistent patterns for injecting `SmartSyncService` and `QBOClient` dependencies:

1. **Correct Pattern:** Services injected via `get_services()` dependency injection
2. **Code Smell Pattern:** Services created inline within route methods

## Root Cause Analysis

This appears to be a symptom of incomplete refactoring where we replaced `QBOBulkScheduledService` calls but didn't complete the architectural pattern. The inline creation pattern was likely used to avoid circular dependency issues between `domains/qbo/` and `runway/routes/`.

## Impact

- **Performance:** Creating new instances on every request instead of reusing
- **Inconsistency:** Mixed patterns across the codebase
- **Maintainability:** Harder to mock/test and track dependencies
- **Architecture:** Violates established dependency injection patterns

## Discovery Scope

Search for all instances of:
1. `SmartSyncService(business_id)` created inline in route methods
2. `QBOClient(business_id)` created inline in route methods
3. `from infra.jobs import SmartSyncService` inside route functions
4. `from domains.qbo.client import QBOClient` inside route functions

## Files to Investigate

- `runway/routes/collections.py` (confirmed - lines 47-51)
- `runway/routes/kpis.py` (likely affected)
- `runway/routes/invoices.py` (likely affected)
- `runway/routes/bills.py` (likely affected)
- `runway/routes/payments.py` (likely affected)
- Any other route files that use QBO data

## Expected Pattern

```python
# In get_services()
def get_services(db: Session, business_id: str):
    return {
        "smart_sync": SmartSyncService(business_id),
        "qbo_client": QBOClient(business_id),
        # ... other services
    }

# In route methods
def some_route(services: Dict = Depends(get_services)):
    smart_sync = services["smart_sync"]
    qbo_client = services["qbo_client"]
```

## Current Code Smell Examples

```python
# BAD: Creating instances inside methods
def get_collections_dashboard(services: Dict = Depends(get_services)):
    from infra.jobs import SmartSyncService
    from domains.qbo.client import QBOClient
    
    smart_sync = SmartSyncService(business_id)
    qbo_client = QBOClient(business_id)
```

## Search Commands

```bash
# Find inline SmartSyncService creation
grep -r "SmartSyncService(business_id)" runway/routes/ --include="*.py"

# Find inline QBOClient creation
grep -r "QBOClient(business_id)" runway/routes/ --include="*.py"

# Find inline imports
grep -r "from infra.jobs import SmartSyncService" runway/routes/ --include="*.py"
grep -r "from domains.qbo.client import QBOClient" runway/routes/ --include="*.py"
```

## Dependencies

None (can be done incrementally)

## Notes

This should be addressed as part of the broader SmartSync cleanup to ensure consistent architecture patterns across all route handlers. The pattern is likely a workaround for circular dependency issues that should be resolved at the architectural level.
