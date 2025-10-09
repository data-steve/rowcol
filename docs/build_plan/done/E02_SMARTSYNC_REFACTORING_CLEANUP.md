# E02: SmartSync Refactoring Cleanup

## **Task: Complete SmartSync Refactoring and Cleanup**
- **Status:** `[✅]` Complete
- **Priority:** P0 Critical
- **Justification:** S07 and E01 marked complete but refactoring is incomplete. Old SmartSyncService still exists and is used everywhere. New QBOSyncService is not properly integrated. Transaction log vs mirror model integration is unclear.
- **Execution Status:** **COMPLETE** - All actual imports updated, only comments and mocks remain

## **CRITICAL: Read These Files First (MANDATORY)**

### **Architecture Context (3 most relevant):**
- `docs/architecture/DATA_ARCHITECTURE_SPECIFICATION.md` - Foundational data architecture patterns
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles  
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy

### **Product Context (1 most relevant):**
- `docs/build_plan/MVP_DATA_ARCHITECTURE_PLAN.md` - MVP implementation plan

### **Current Phase Context:**
- **Phase 0.5**: QBO-only MVP (current focus)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Payment Execution**: QBO sync-only (no execution), Ramp execution gated
- **Data Architecture**: Local mirroring + SmartSyncService for live data

### **Task-Specific Context (3 most relevant):**
- `docs/build_plan/done/S07_SYNC_AND_TRANSACTION_LOG_IMPLEMENTATION.md` - What was implemented
- `infra/qbo/smart_sync.py` - Old monolithic SmartSyncService to replace
- `domains/qbo/services/sync_service.py` - New QBOSyncService to integrate

## **CRITICAL: Architecture Understanding (MANDATORY)**

### **The Overall Plan (From Architecture Context):**
- **Multi-Rail Architecture**: System supports QBO, Ramp, Plaid, Stripe rails
- **Domain Separation (ADR-001)**: `domains/` = business logic, `runway/` = product orchestration, `infra/` = cross-cutting concerns
- **Data Architecture**: Local mirroring + transaction logs for audit trails
- **QBO Strategy**: QBO is the ledger rail - read-only sync, no execution

### **What Should Exist (From S07 Implementation):**
- **BaseSyncService** (`infra/jobs/base_sync_service.py`) - Generic orchestration for all rails
- **QBOSyncService** (`domains/qbo/services/sync_service.py`) - QBO-specific business logic
- **Transaction Log Models** (`domains/ap/models_trans/`) - Immutable audit trails
- **Mirror Models** (`domains/ap/models/`) - Current state for fast queries
- **Sync Integration** - Updates both mirror and transaction log models

### **What Actually Exists (Current Reality):**
- **Old SmartSyncService** (`infra/qbo/smart_sync.py`) - Monolithic, used in 44+ files
- **New QBOSyncService** (`domains/qbo/services/sync_service.py`) - Exists but not integrated
- **Transaction Log Models** - Created but not properly integrated
- **Sync Methods** - Placeholders, don't actually update mirror models

### **The Gap (What Needs Fixing):**
- **Import Migration**: 44+ files still use old SmartSyncService
- **Integration**: New QBOSyncService not actually used anywhere
- **Implementation**: Sync methods are placeholders, don't update mirror models
- **Cleanup**: Old SmartSyncService needs to be deleted

## **Problem Statement**

**Current State**: SmartSync refactoring is incomplete:
- Old `infra/qbo/smart_sync.py` still exists and is used in 44+ files
- New `domains/qbo/services/sync_service.py` is not properly integrated
- `sync_bill_with_log` methods are just placeholders
- Transaction log vs mirror model integration is unclear
- Import references are inconsistent

**The Problem**: We have a half-finished refactoring that's causing confusion:
- Two different SmartSync implementations exist
- Old imports are still being used everywhere
- New sync service doesn't actually update mirror models
- Transaction log integration is incomplete

## **User Story**
"As a developer working on the sync system, I need the SmartSync refactoring to be completed properly so that I can understand how transaction logs and mirror models work together, and so that all imports are consistent and working."

## **Solution Overview**
Complete the SmartSync refactoring:
1. **Keep QBOSyncService as-is** - naming is clear and consistent
2. **Update all imports** from old SmartSyncService to new QBOSyncService
3. **Implement actual mirror model updates** in sync methods
4. **Delete old SmartSyncService** once migration is complete
5. **Document transaction log vs mirror model integration**

## **CRITICAL: Assumption Validation Before Execution (MANDATORY)**

### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all SmartSyncService usage
2. **Read Actual Code** - Understand current implementation
3. **Compare Old vs New** - Document differences
4. **Identify Integration Gaps** - What's missing in new implementation
5. **Plan Migration Strategy** - How to safely migrate

### **Discovery Documentation Template:**
```
### What Actually Exists:
- Old SmartSyncService: infra/qbo/smart_sync.py (317 lines) - MONOLITHIC, violates ADR-001
- New QBOSyncService: domains/qbo/services/sync_service.py (355 lines) - NOT INTEGRATED
- 44+ files still importing old SmartSyncService - BLOCKING MIGRATION
- sync_bill_with_log methods are placeholders - NOT IMPLEMENTED
- Transaction log models exist but not integrated - INCOMPLETE

### What the Architecture Requires:
- BaseSyncService in infra/jobs/ - Generic orchestration for all rails
- QBOSyncService in domains/qbo/services/ - QBO-specific business logic
- Transaction logs in domains/ap/models_trans/ - Immutable audit trails
- Mirror models in domains/ap/models/ - Current state for queries
- Sync integration updates both mirror and transaction log models

### Architecture Violations Found:
- Old SmartSyncService violates ADR-001 (mixes infra and domain concerns)
- New QBOSyncService not integrated (44+ files still use old service)
- Transaction log integration incomplete (sync methods are placeholders)
- Multi-rail support missing (old service is QBO-specific)

### What Needs Fixing:
- Import migration: 44+ files need to use new QBOSyncService
- Integration: New service needs to be actually used
- Implementation: Sync methods need to update mirror models
- Cleanup: Old service needs to be deleted
- Documentation: Transaction log vs mirror model integration needs to be clear
```

## **MANDATORY: Comprehensive Discovery Commands**

```bash
# Find all SmartSyncService usage
grep -r "SmartSyncService" . --include="*.py"
grep -r "infra\.qbo\.smart_sync" . --include="*.py"
grep -r "domains\.qbo\.services\.sync_service" . --include="*.py"

# Check current implementation
find . -name "*smart_sync*" -type f
find . -name "*sync_service*" -type f

# Check transaction log integration
grep -r "sync_bill_with_log\|sync_vendor_with_log\|sync_payment_with_log" . --include="*.py"
grep -r "TransactionLogService" . --include="*.py"

# Check mirror model updates
grep -r "Bill\|Vendor\|Payment" domains/ap/models/ --include="*.py"
grep -r "transaction_logs" domains/ap/models/ --include="*.py"

# Test current state
poetry run python -c "from infra.qbo.smart_sync import SmartSyncService; print('Old SmartSyncService works')"
poetry run python -c "from domains.qbo.services.sync_service import QBOSyncService; print('New QBOSyncService works')"
```

## **MANDATORY: Recursive Triage Process**

1. **For each file using old SmartSyncService:**
   - Read the broader context around each occurrence
   - Understand what the method/service/route is doing
   - Determine if it needs simple replacement, contextual update, or complete overhaul
   - Identify all related imports, method calls, and dependencies

2. **Map the real system:**
   - How do transaction logs and mirror models actually work together?
   - What are the real data flows?
   - What would break if you changed the SmartSyncService?

3. **Plan comprehensive updates:**
   - Rename QBOSyncService to SmartSyncService
   - Update ALL imports from old to new
   - Implement actual mirror model updates in sync methods
   - Delete old SmartSyncService
   - Update ALL references and documentation

## **Pattern to Implement**

### **Step 1: Keep QBOSyncService as-is**
```python
# domains/qbo/services/sync_service.py (keep current name)
class QBOSyncService:
    """QBO-specific sync service with business logic and transaction log integration."""
    
    def __init__(self, business_id: str, realm_id: str, db_session=None):
        self.business_id = business_id
        self.realm_id = realm_id
        self.db_session = db_session
        self.base_sync = BaseSyncService(business_id, db_session)
        self.qbo_client = QBORawClient(business_id, realm_id, db_session)
        self.transaction_log_service = TransactionLogService(db_session)
```

### **Step 2: Implement Actual Mirror Model Updates**
```python
async def sync_bill_with_log(
    self, 
    bill, 
    qbo_bill_data: Dict[str, Any],
    created_by_user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Sync bill data and create transaction log entry."""
    
    # Map QBO data to our format
    mapped_data = QBOMapper.map_bill_data(qbo_bill_data)
    
    # Update mirror model
    bill.qbo_bill_id = mapped_data['qbo_id']
    bill.amount = mapped_data['amount']
    bill.balance = mapped_data['balance']
    bill.due_date = mapped_data['due_date']
    bill.status = mapped_data['status']
    bill.updated_at = datetime.utcnow()
    
    # Save mirror model
    self.db_session.commit()
    
    # Create transaction log entry
    transaction_log = await self.transaction_log_service.log_bill_sync(
        bill=bill,
        qbo_bill_data=qbo_bill_data,
        source="qbo",
        created_by_user_id=created_by_user_id,
        session_id=session_id
    )
    
    return {
        "bill": bill,
        "transaction_log": transaction_log,
        "status": "synced"
    }
```

### **Step 3: Update All Imports**
```python
# Change from:
from infra.qbo.smart_sync import SmartSyncService

# To:
from domains.qbo.services.sync_service import QBOSyncService
```

## **Required Imports/Changes**

- **Keep**: `domains/qbo/services/sync_service.py` (current name)
- **Keep**: `QBOSyncService` (current class name)
- **Update**: All 44+ import references from old to new
- **Implement**: Actual mirror model updates in sync methods
- **Delete**: `infra/qbo/smart_sync.py` once migration is complete

## **Dependencies**
- S07: Sync and Transaction Log Implementation (needs to be properly integrated)
- E01: MVP Sync Infrastructure Setup (needs to use new SmartSyncService)

## **MANDATORY: Comprehensive Cleanup Requirements**

- **File Operations**: Use `cp` then `rm` for moves, never just `mv`
- **Import Cleanup**: Update ALL 44+ import references
- **Method Implementation**: Implement actual mirror model updates
- **Reference Cleanup**: Update ALL references to renamed methods/classes
- **Dependency Cleanup**: Update ALL dependent code
- **Test Cleanup**: Update ALL test files that reference changed code
- **Documentation Cleanup**: Update ALL documentation references
- **Verification Cleanup**: Run cleanup verification commands

## **Verification**

- Run `grep -r "infra\.qbo\.smart_sync" . --include="*.py"` - should return no results
- Run `grep -r "domains\.qbo\.services\.sync_service" . --include="*.py"` - should show new usage
- Run `poetry run python -c "from domains.qbo.services.sync_service import QBOSyncService; print('New QBOSyncService works')"`
- **Check uvicorn in Cursor terminal** - should be running without errors
- Run `pytest` - should pass without import failures

## **Definition of Done**

- [ ] QBOSyncService kept as-is (naming is clear)
- [ ] All 44+ import references updated
- [ ] Actual mirror model updates implemented in sync methods
- [ ] Old SmartSyncService deleted
- [ ] Transaction log vs mirror model integration documented
- [ ] All tests passing
- [ ] No broken references or imports anywhere
- [ ] Comprehensive cleanup completed

## **Progress Tracking**

- Update status to `[🔄]` when starting work
- Update status to `[✅]` when task is complete
- Update status to `[❌]` if blocked or failed

## **Git Commit**

- After completing verification, commit the specific files modified:
- `git add [specific-files-modified]`
- `git commit -m "feat: complete SmartSync refactoring - update all imports to QBOSyncService, implement mirror model updates"`

## **Todo List Integration**

- Create Cursor todo for this task when starting
- Update todo status as work progresses
- Mark todo complete when task is done
- Add cleanup todos for discovered edge cases
- Remove obsolete todos when files are deleted
- Ensure todo list reflects current system state
