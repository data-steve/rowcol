# Phase A: Executable Tasks - SmartSync & QBO Architecture Cleanup

*Generated from infrastructure consolidation cleanup on 2025-01-27*  
*Status: ✅ READY FOR HANDS-FREE EXECUTION*

## **Task Complexity Curation**

**✅ FULLY SOLVED (8 tasks)** - These tasks have:
- Clear implementation patterns with code examples
- Specific files to fix with exact changes needed
- Complete verification steps with pytest commands
- No "figure out" or "analyze" language
- Ready for execution by any developer

**⚠️ EXCLUDED FROM PHASE A** - These tasks need solution work:
- Test SmartSyncService Integration End-to-End (needs analysis)
- Consolidate Digest Architecture (needs analysis) 
- Update Runway Calculators to Use SmartSyncService (depends on above)
- Audit and Fix All Remaining Import Errors (needs discovery)
- Update Documentation to Reflect New Architecture (needs analysis)

---

## **Instructions**

1. **Create Git Branch**: `git checkout -b cleanup/phase-a-executable`
2. **Execute Tasks Sequentially**: Work through tasks in order by their number (1, 2, 3, etc.)
3. **For Each Task**: Follow the specific implementation patterns and verification steps
4. **Test After Each Task**: Run the specified pytest commands to verify changes
5. **Update Status**: Change `[ ]` to `[✅]` when task is complete
6. **Commit After Each Task**: `git add . && git commit -m "Task: [task-name] - [brief summary]"`
7. **Archive When Complete**: Move this file to `archive/` when all tasks are done
8. **When All Tasks Complete**: `git checkout main && git merge cleanup/phase-a-executable && git branch -d cleanup/phase-a-executable`

**⚠️ IMPORTANT: Do NOT run multiple tasks simultaneously - they have dependencies and will collide!**

---

## **Context for All Tasks**

- **SmartSyncService** (`infra/jobs/smart_sync.py`): Central orchestration layer for ALL QBO interactions. Handles retries, deduplication, rate limiting, and caching while enabling immediate user actions through direct API calls. See [ADR-005: QBO API Strategy](../docs/architecture/ADR-005-qbo-api-strategy.md) for complete architecture.
- **QBOBulkScheduledService** (`domains/qbo/service.py`): ONLY for bulk background data operations (like digest generation). NOT for user actions.
- **Direct QBO API calls** (`domains/qbo/client.py`): For immediate user actions (pay bill, delay payment, send collection). Must be wrapped in SmartSyncService for fragility handling.
- **QBODataService** (`domains/qbo/data_service.py`): ONLY for `runway/experiences/` data formatting. NOT a generic data fetcher.
- **User Actions vs Data Syncs**: User actions = immediate QBO API calls wrapped in SmartSyncService. Data syncs = background operations coordinated by SmartSyncService.

**Key Architecture Principle**: The question isn't "SmartSyncService vs direct API calls" - it's "How do we use SmartSyncService to handle QBO's fragility while maintaining the UX of immediate user actions?" Answer: SmartSyncService as the orchestration layer that handles retries, deduplication, rate limiting, and caching, while still allowing direct API calls for user actions.

---

## **Phase 1: Fix SmartSync Architecture (P0 Critical)**

#### **Task 1: Remove QBOBulkScheduledService from User Action Flows**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Estimated Time:** 30 minutes
- **Justification:** User actions (pay bill, delay payment, send collection) should trigger direct QBO API calls wrapped in SmartSyncService, not bulk scheduled operations. QBOBulkScheduledService is for background data syncs only. See [ADR-005: QBO API Strategy](../docs/architecture/ADR-005-qbo-api-strategy.md) for complete architecture.
- **Specific Files to Fix:**
  - `domains/ar/services/invoice.py` - Remove QBOBulkScheduledService import and usage
  - `domains/ar/services/collections.py` - Remove QBOBulkScheduledService import and usage  
  - `runway/routes/kpis.py` - Remove QBOBulkScheduledService import and usage
  - `runway/routes/invoices.py` - Remove QBOBulkScheduledService import and usage
  - `runway/routes/collections.py` - Remove QBOBulkScheduledService import and usage
- **Search Commands to Run:**
  - `grep -r "QBOBulkScheduledService" domains/ar/services/ runway/routes/`
  - `grep -r "from domains.qbo.service import QBOBulkScheduledService"`
- **PARANOID CHECKLIST:**
  - [ ] Read each file completely before making changes
  - [ ] Check if QBOBulkScheduledService is actually used in the file (not just imported)
  - [ ] Look for any method calls like `self.qbo_service.some_method()`
  - [ ] Check if there are any `__init__` methods that instantiate QBOBulkScheduledService
  - [ ] Verify that removing it won't break existing functionality
  - [ ] Test uvicorn startup after EACH file change, not just at the end
- **Dependencies:** None
- **Verification:** 
  - Run `grep -r "QBOBulkScheduledService" domains/ar/services/ runway/routes/` - should return no results
  - Run `uvicorn main:app --reload` - should start without import errors
  - Run `pytest tests/domains/unit/integrations/qbo/` - QBO integration tests should pass
  - Run `pytest tests/integration/qbo/` - QBO API tests should pass
- **Definition of Done:**
  - All user action endpoints use direct QBO API calls via `domains/qbo/client.py`
  - `SmartSyncService` is used only for sync timing/activity tracking
  - `QBOBulkScheduledService` is removed from all user-facing flows
  - Application starts without import errors
  - All tests pass

---

#### **Task 2: Implement Direct QBO API Calls for User Actions**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Estimated Time:** 45 minutes
- **Justification:** User actions need immediate QBO API responses wrapped in SmartSyncService for fragility handling, not background processing. This enables real-time dashboard updates and immediate user feedback while handling QBO's rate limits, retries, and deduplication. See [ADR-005: QBO API Strategy](../docs/architecture/ADR-005-qbo-api-strategy.md) for complete architecture.
- **Specific Files to Fix:**
  - `runway/routes/bills.py` - Replace bulk service calls with direct QBO API calls
  - `runway/routes/vendors.py` - Replace bulk service calls with direct QBO API calls
  - `runway/routes/invoices.py` - Replace bulk service calls with direct QBO API calls
  - `runway/routes/collections.py` - Replace bulk service calls with direct QBO API calls
- **Required Imports to Add:**
  - `from domains.qbo.client import QBOClient`
  - `from infra.jobs import SmartSyncService`
- **Pattern to Implement:**
  ```python
  # In each user action endpoint:
  @router.post("/bills/{bill_id}/pay")
  async def pay_bill(bill_id: str, payment_data: PaymentRequest):
      smart_sync = SmartSyncService(business_id)
      
      # Check rate limits and deduplication
      if not smart_sync.should_sync("qbo", SyncStrategy.USER_ACTION):
          raise HTTPException(status_code=429, detail="Rate limit exceeded")
      
      if smart_sync.deduplicate_action("payment", bill_id, payment_data.dict()):
          return {"status": "already_processed"}
      
      # Execute direct QBO API call with retry logic
      qbo_client = QBOClient(business_id)
      payment = await smart_sync.execute_with_retry(
          qbo_client.create_payment, payment_data, max_attempts=3
      )
      
      # Update local DB and record activity
      await smart_sync.update_local_db("payment", bill_id, {"status": "paid"})
      smart_sync.record_user_activity("bill_payment")
      
      # Trigger background reconciliation
      await smart_sync.schedule_reconciliation("payment", bill_id)
      
      return {"status": "paid", "payment_id": payment.id, "runway_impact": "+2 days"}
  ```
- **Dependencies:** `Remove QBOBulkScheduledService from User Action Flows`
- **Verification:** 
  - Run `grep -r "QBOBulkScheduledService" runway/routes/` - should return no results
  - Run `grep -r "QBOClient" runway/routes/` - should show new imports
  - Run `pytest tests/runway/unit/foundation/test_phase0_qbo.py` - QBO foundation tests should pass
  - Run `pytest tests/integration/test_qbo_api_direct.py` - Direct QBO API tests should pass
  - Test each endpoint manually to verify immediate responses
- **Definition of Done:**
  - Each user action endpoint uses direct QBO API calls wrapped in SmartSyncService
  - SmartSyncService handles rate limiting, deduplication, and retry logic
  - Background reconciliation is scheduled after user actions
  - Dashboard updates reflect changes immediately with proper error handling
  - All patterns follow [ADR-005: QBO API Strategy](../docs/architecture/ADR-005-qbo-api-strategy.md)

---

#### **Task 3: Fix SmartSyncService Usage in Domain Services**
- **Justification:** Domain services are incorrectly using `QBOBulkScheduledService` for sync operations. They should use `SmartSyncService` as the orchestration layer for all QBO interactions, handling fragility while enabling immediate responses. See [ADR-005: QBO API Strategy](../docs/architecture/ADR-005-qbo-api-strategy.md) for complete architecture.
- **Specific Files to Fix:**
  - `domains/ar/services/invoice.py` - Replace QBOBulkScheduledService with SmartSyncService
  - `domains/ar/services/collections.py` - Replace QBOBulkScheduledService with SmartSyncService
  - `domains/ap/services/bill_ingestion.py` - Replace QBOBulkScheduledService with SmartSyncService
- **Required Changes:**
  - Remove: `from domains.qbo.service import QBOBulkScheduledService`
  - Add: `from infra.jobs import SmartSyncService`
  - Add: `from domains.qbo.client import QBOClient`
- **Pattern to Implement:**
  ```python
  # In __init__ method:
  self.smart_sync = SmartSyncService(business_id)
  self.qbo_client = QBOClient(business_id)
  
  # In sync methods:
  async def sync_invoices(self, business_id: str):
      # Check if sync is needed
      if not self.smart_sync.should_sync("qbo", SyncStrategy.SCHEDULED):
          cached_data = self.smart_sync.get_cache("qbo")
          if cached_data:
              return cached_data
      
      # Execute sync with retry logic
      data = await self.smart_sync.execute_with_retry(
          self.qbo_client.get_invoices, max_attempts=3
      )
      
      # Cache results and record activity
      self.smart_sync.set_cache("qbo", data, ttl_minutes=240)
      self.smart_sync.record_user_activity("invoice_sync")
      
      return data
  ```
- **Dependencies:** None
- **Verification:** 
  - Run `grep -r "QBOBulkScheduledService" domains/` - should return no results
  - Run `grep -r "SmartSyncService" domains/` - should show new imports
  - Run `pytest tests/domains/unit/ap/` - AP domain tests should pass
  - Run `pytest tests/domains/unit/ar/` - AR domain tests should pass
  - Run `uvicorn main:app --reload` - should start without import errors
- **Definition of Done:**
  - All domain services use `SmartSyncService` as orchestration layer for QBO interactions
  - SmartSyncService handles rate limiting, caching, retry logic, and deduplication
  - Direct QBO API calls are wrapped in SmartSyncService.execute_with_retry()
  - Background reconciliation is scheduled after sync operations
  - All patterns follow [ADR-005: QBO API Strategy](../docs/architecture/ADR-005-qbo-api-strategy.md)
  - `QBOBulkScheduledService` is removed from domain services

---

## **Phase 2: Consolidate Job Infrastructure (P1 High)**

#### **Task 4: Update All Imports to Use infra/jobs/ Structure**
- **Justification:** Current codebase has scattered imports from old `cache/`, `queue/`, `scheduler/` directories. All job-related functionality is now consolidated in `infra/jobs/`.
- **Specific Files to Fix:**
  - `runway/experiences/tray.py` - Update imports from old infra directories
  - `infra/queue/job_storage.py` - Update imports from old infra directories
  - `infra/scheduler/job_providers.py` - Update imports from old infra directories
  - `infra/scheduler/digest_jobs.py` - Update imports from old infra directories
- **Search Commands to Run:**
  - `grep -r "from infra\.(cache|queue|scheduler)" . --include="*.py"`
  - `grep -r "import infra\.(cache|queue|scheduler)" . --include="*.py"`
- **Required Import Changes:**
  - `from infra.cache.sync_cache import SyncCache` → `from infra.jobs.job_storage import SyncCache`
  - `from infra.queue.job_storage import JobStorageProvider` → `from infra.jobs.job_storage import JobStorageProvider`
  - `from infra.scheduler.sync_strategies import SyncTimingManager` → `from infra.jobs.sync_strategies import SyncTimingManager`
  - `from infra.utils.sync_strategies import SyncStrategy` → `from infra.jobs.enums import SyncStrategy`
- **Dependencies:** None
- **Verification:** 
  - Run `grep -r "from infra\.(cache|queue|scheduler)" . --include="*.py"` - should return no results
  - Run `uvicorn main:app --reload` - should start without import errors
  - Run `pytest` - should pass without import failures
- **Definition of Done:**
  - All imports updated to use `infra.jobs` instead of scattered directories
  - No circular import errors
  - All tests pass with new import structure
  - Old import paths are completely removed

---

#### **Task 5: Delete Old Scattered Infrastructure Directories**
- **Justification:** After consolidating to `infra/jobs/`, the old `cache/`, `queue/`, `scheduler/` directories are redundant and should be removed to prevent confusion.
- **Directories to Delete:**
  - `infra/cache/` (entire directory)
  - `infra/queue/` (entire directory) 
  - `infra/scheduler/` (entire directory)
  - `infra/utils/sync_strategies.py` (moved to `infra/jobs/sync_strategies.py`)
- **Pre-deletion Verification:**
  - Run `grep -r "from infra\.(cache|queue|scheduler)" . --include="*.py"` - should return no results
  - Run `grep -r "import infra\.(cache|queue|scheduler)" . --include="*.py"` - should return no results
  - Run `uvicorn main:app --reload` - should start without import errors
- **Dependencies:** `Update All Imports to Use infra/jobs/ Structure`
- **Verification Commands:**
  - `ls infra/` - should show only: `api/`, `auth/`, `config/`, `files/`, `jobs/`, `monitoring/`, `utils/`
  - `grep -r "infra\.(cache|queue|scheduler)" . --include="*.py"` - should return no results
  - `uvicorn main:app --reload` - should start successfully
- **Definition of Done:**
  - All old infrastructure directories are deleted
  - No broken imports or references
  - `infra/jobs/` contains all consolidated functionality
  - Application starts without errors

---

## **Phase 3: Clean Up QBODataService Misuse (P1 High)**

#### **Task 6: Fix QBODataService Scope and Remove Bulk Methods**
- **Justification:** `QBODataService` was incorrectly used everywhere instead of `SmartSyncService`. It should only serve `runway/experiences/` with formatted data, not be a generic data fetcher.
- **Specific Files to Fix:**
  - `domains/qbo/data_service.py` - Remove `get_bulk_raw_data` method and generic data fetching
  - `runway/experiences/digest.py` - Update to use QBODataService only for digest formatting
  - `runway/experiences/tray.py` - Update to use QBODataService only for tray formatting
  - `runway/experiences/test_drive.py` - Update to use QBODataService only for test_drive formatting
- **Methods to Remove from QBODataService:**
  - `get_bulk_raw_data()` - duplicates `domains/qbo/service.py` functionality
  - Any generic data fetching methods
- **Methods to Keep in QBODataService:**
  - `get_digest_data()` - formats data specifically for digest experience
  - `get_tray_data()` - formats data specifically for tray experience
  - `get_test_drive_data()` - formats data specifically for test_drive experience
- **Dependencies:** None
- **Verification:** 
  - Run `grep -r "get_bulk_raw_data" domains/qbo/data_service.py` - should return no results
  - Run `grep -r "QBODataService" runway/routes/` - should return no results
  - Run `grep -r "QBODataService" domains/` - should return no results
- **Definition of Done:**
  - QBODataService only contains experience-specific data formatting methods
  - `get_bulk_raw_data` method is removed (duplicates existing service)
  - QBODataService is only used by `runway/experiences/` files
  - Each experience gets only the data it needs, not bulk data

---

#### **Task 7: Revert Incorrect SmartSyncService → QBODataService Replacements**
- **Justification:** Previous refactoring incorrectly replaced `SmartSyncService` with `QBODataService` in many files. These need to be reverted to use the correct service for each use case.
- **Specific Files to Fix:**
  - `runway/routes/payments.py` - Replace QBODataService with SmartSyncService
  - `runway/routes/kpis.py` - Replace QBODataService with SmartSyncService
  - `runway/routes/invoices.py` - Replace QBODataService with SmartSyncService
  - `runway/routes/collections.py` - Replace QBODataService with SmartSyncService
  - All test files with QBODataService imports
- **Search Commands to Run:**
  - `grep -r "QBODataService" runway/routes/`
  - `grep -r "QBODataService" tests/`
  - `grep -r "from domains.qbo.data_service import QBODataService"`
- **Required Changes:**
  - Remove: `from domains.qbo.data_service import QBODataService`
  - Add: `from infra.jobs import SmartSyncService`
  - Add: `from domains.qbo.client import QBOClient`
- **Dependencies:** None
- **Verification:** 
  - Run `grep -r "QBODataService" runway/routes/` - should return no results
  - Run `grep -r "QBODataService" tests/` - should return no results
  - Run `grep -r "SmartSyncService" runway/routes/` - should show new imports
  - Run `uvicorn main:app --reload` - should start without import errors
- **Definition of Done:**
  - All route files use `SmartSyncService` for sync operations
  - All route files use direct QBO API calls for user actions
  - QBODataService is only used in `runway/experiences/`
  - All incorrect replacements are reverted

---

## **Phase 4: Complete Infrastructure Consolidation (P2 Medium)**

#### **Task 8: Remove Old get_X_for_digest Methods from Domains**
- **Justification:** Domain services have `get_X_for_digest` methods that are no longer needed after consolidating digest architecture. These should be removed to clean up the codebase.
- **Specific Files to Fix:**
  - `domains/ap/services/bill_ingestion.py` - Remove `get_bills_for_digest` method
  - `domains/ar/services/invoice.py` - Remove `get_invoices_for_digest` method
  - `domains/ar/services/customer.py` - Remove `get_customers_for_digest` method
  - `domains/ar/services/vendor.py` - Remove `get_vendors_for_digest` method
  - `domains/core/services/balance_service.py` - Remove `get_balance_for_digest` method
- **Search Commands to Run:**
  - `grep -r "get_.*_for_digest" domains/`
  - `grep -r "def get_.*_for_digest" domains/`
- **Dependencies:** None
- **Verification:** 
  - Run `grep -r "get_.*_for_digest" domains/` - should return no results
  - Run `grep -r "def get_.*_for_digest" domains/` - should return no results
  - Run `uvicorn main:app --reload` - should start without import errors
- **Definition of Done:**
  - All `get_X_for_digest` methods are removed from domain services
  - Digest experience uses `QBODataService` for data formatting
  - No broken references or imports
  - Domain services focus on their core responsibilities

---

## **Summary**

- **Total Tasks:** 8
- **P0 Critical:** 3 tasks
- **P1 High:** 4 tasks  
- **P2 Medium:** 1 task
- **Status:** ✅ **READY FOR HANDS-FREE EXECUTION**

**Quick Reference Commands:**
```bash
# Check for QBOBulkScheduledService usage
grep -r "QBOBulkScheduledService" domains/ar/services/ runway/routes/

# Check for QBODataService misuse
grep -r "QBODataService" runway/routes/ tests/

# Check for old infra imports
grep -r "from infra\.(cache|queue|scheduler)" . --include="*.py"

# Check for get_X_for_digest methods
grep -r "get_.*_for_digest" domains/

# Test application startup
uvicorn main:app --reload

# Run tests
pytest
```

**PARANOID VERIFICATION CHECKLIST:**
- [ ] After EACH file change, run `uvicorn main:app --reload` to test startup
- [ ] After EACH import change, run `pytest` to test functionality
- [ ] Before deleting ANY file, run `grep -r "filename" . --include="*.py"` to check references
- [ ] After EACH service replacement, verify the new service actually works
- [ ] Test user actions (pay bill, delay payment) to ensure they work immediately
- [ ] Test background syncs to ensure they use SmartSyncService correctly
- [ ] Check that QBODataService is ONLY used in runway/experiences/
- [ ] Verify that QBOBulkScheduledService is ONLY used for digest generation

**Key Service Responsibilities:**
- **SmartSyncService** (`infra/jobs/smart_sync.py`): Sync timing, caching, user activity tracking
- **QBOBulkScheduledService** (`domains/qbo/service.py`): ONLY bulk background operations (digest generation)
- **Direct QBO API calls** (`domains/qbo/client.py`): Immediate user actions (pay bill, delay payment)
- **QBODataService** (`domains/qbo/data_service.py`): ONLY `runway/experiences/` data formatting

This backlog contains only tasks that are **fully solved and ready for hands-free execution** by any developer familiar with the codebase.
