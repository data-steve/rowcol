## **SmartSync & QBO Architecture Cleanup Backlog**

*Generated from infrastructure consolidation cleanup on 2025-01-27*  
*Status: ⚠️ **CURATED INTO PHASES** - See Phase A and Phase B backlogs*

**⚠️ IMPORTANT: This backlog has been curated by complexity. Do not execute directly.**

**✅ Use Phase A for Hands-Free Execution:**
- `000_phase_a_executable_tasks.md` - 8 fully-solved tasks ready for execution

**⚠️ Use Phase B for Solution Work:**
- `001_phase_b_solution_tasks.md` - 5 tasks needing analysis and solution work

**This file is kept for reference only.**

**Instructions:**
1. **Create Git Branch**: `git checkout -b cleanup/smartsync-cleanup`
2. **Execute Tasks Sequentially**: Work through Phase 1 tasks in order (they have dependencies)
3. **For Each Task**: Follow the specific implementation patterns and verification steps
4. **Test After Each Task**: Run the specified pytest commands to verify changes
5. **Commit After Each Task**: `git add . && git commit -m "Task: [task-name] - [brief summary]"`
6. **When All Tasks Complete**: `git checkout main && git merge cleanup/smartsync-cleanup && git branch -d cleanup/smartsync-cleanup`

**⚠️ IMPORTANT: Do NOT run multiple tasks simultaneously - they have dependencies and will collide!**

**Git Workflow:**
```bash
# Start this cleanup phase
git checkout -b cleanup/smartsync-cleanup

# Execute tasks in order, committing after each major change
git add .
git commit -m "Task: Remove QBOBulkScheduledService - Cleaned up user action flows"

# When all tasks complete, merge back
git checkout main
git merge cleanup/smartsync-cleanup
git branch -d cleanup/smartsync-cleanup
```

**Rollback Plan:**
```bash
# If this phase fails, abandon it
git checkout main
git branch -D cleanup/smartsync-cleanup

# Or rollback specific changes
git checkout main
git reset --hard HEAD~1  # Go back one commit
```

**Context for All Tasks:**
- **SmartSyncService** (`infra/jobs/smart_sync.py`): Central orchestration layer for ALL QBO interactions. Handles retries, deduplication, rate limiting, and caching while enabling immediate user actions through direct API calls. See [ADR-005: QBO API Strategy](../docs/architecture/ADR-005-qbo-api-strategy.md) for complete architecture.
- **QBOBulkScheduledService** (`domains/qbo/service.py`): ONLY for bulk background data operations (like digest generation). NOT for user actions.
- **Direct QBO API calls** (`domains/qbo/client.py`): For immediate user actions (pay bill, delay payment, send collection). Must be wrapped in SmartSyncService for fragility handling.
- **QBODataService** (`domains/qbo/data_service.py`): ONLY for `runway/experiences/` data formatting. NOT a generic data fetcher.
- **User Actions vs Data Syncs**: User actions = immediate QBO API calls wrapped in SmartSyncService. Data syncs = background operations coordinated by SmartSyncService.

**Key Architecture Principle**: The question isn't "SmartSyncService vs direct API calls" - it's "How do we use SmartSyncService to handle QBO's fragility while maintaining the UX of immediate user actions?" Answer: SmartSyncService as the orchestration layer that handles retries, deduplication, rate limiting, and caching, while still allowing direct API calls for user actions.

**CRITICAL WARNINGS FROM PAINFUL LESSONS:**
- **NEVER** replace SmartSyncService with QBODataService in route files - they serve different purposes
- **NEVER** use QBOBulkScheduledService for user actions - it's for background bulk operations only
- **ALWAYS** check existing imports before making changes - don't assume what's there
- **ALWAYS** run verification commands after each change - don't trust that it worked
- **NEVER** delete files without checking all references first - circular imports will break everything
- **ALWAYS** test uvicorn startup after import changes - silent failures are the worst
- **REMEMBER** that domains/ar/services/ should use SmartSyncService + direct QBO calls, NOT QBOBulkScheduledService

---

## **Phase 1: Fix SmartSync Architecture (P0 Critical)**

#### **Task: Remove QBOBulkScheduledService from User Action Flows**
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

#### **Task: Implement Direct QBO API Calls for User Actions**
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

#### **Task: Fix SmartSyncService Usage in Domain Services**
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

#### **Task: Update All Imports to Use infra/jobs/ Structure**
- **Status:** `Ready for Spec`
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
- **Next Action:** Ready for you to run `@spec "Update All Imports to Use infra/jobs/ Structure"`

---

#### **Task: Delete Old Scattered Infrastructure Directories**
- **Status:** `Ready for Spec`
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
- **Next Action:** Ready for you to run `@spec "Delete Old Scattered Infrastructure Directories"`

---

#### **Task: Test SmartSyncService Integration End-to-End**
- **Status:** `Ready for Spec`
- **Justification:** After all refactoring, we need to verify that `SmartSyncService` works correctly for both user actions and background syncs across the entire application.
- **Code Pointers:**
  - `infra/jobs/smart_sync.py` (main orchestrator)
  - `runway/core/runway_calculator.py` (uses SmartSync for data sync)
  - `runway/routes/bills.py` (uses SmartSync for user activity tracking)
  - `domains/ar/services/invoice.py` (uses SmartSync for sync timing)
- **Dependencies:** `Fix SmartSyncService Usage in Domain Services`
- **Verification:** Current SmartSyncService is not fully integrated across all use cases
- **Definition of Done:**
  - SmartSyncService handles both user actions and background syncs
  - Sync timing works correctly for different strategies
  - Caching works for data sync operations
  - User activity tracking works for immediate actions
  - Integration tests cover all use cases
- **Next Action:** Ready for you to run `@spec "Test SmartSyncService Integration End-to-End"`

---

## **Phase 3: Clean Up QBODataService Misuse (P1 High)**

#### **Task: Fix QBODataService Scope and Remove Bulk Methods**
- **Status:** `Ready for Spec`
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
- **Next Action:** Ready for you to run `@spec "Fix QBODataService Scope and Remove Bulk Methods"`

---

#### **Task: Revert Incorrect SmartSyncService → QBODataService Replacements**
- **Status:** `Ready for Spec`
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
- **Next Action:** Ready for you to run `@spec "Revert Incorrect SmartSyncService → QBODataService Replacements"`

---

## **Phase 4: Complete Infrastructure Consolidation (P2 Medium)**

#### **Task: Consolidate Digest Architecture**
- **Status:** `Ready for Spec`
- **Justification:** `digest.py` and `digest_jobs.py` have overlapping responsibilities. The digest experience should have a clear architecture for weekly email generation and sending.
- **Specific Files to Analyze:**
  - `runway/experiences/digest.py` - Contains digest experience logic and commented email service
  - `infra/scheduler/digest_jobs.py` - Contains job scheduling for digest generation
- **Current Issues to Resolve:**
  - Unclear boundaries between experience logic and job scheduling
  - Commented email service code in digest.py
  - Potential duplicate functionality between files
- **Required Analysis:**
  - Read both files to understand current responsibilities
  - Identify overlapping or duplicate functionality
  - Determine clear separation of concerns
- **Dependencies:** `Fix QBODataService Scope and Remove Bulk Methods`
- **Verification:** 
  - Run `grep -r "digest" runway/experiences/ infra/scheduler/` - understand current usage
  - Read both files completely to understand responsibilities
  - Identify specific areas of overlap or confusion
- **Definition of Done:**
  - Single clear architecture for digest experience
  - `digest_jobs.py` handles scheduling via `infra/jobs/`
  - `digest.py` handles data formatting and email generation
  - No duplicate or conflicting logic
  - Clear documentation of responsibilities
- **Next Action:** Ready for you to run `@spec "Consolidate Digest Architecture"`

---

#### **Task: Remove Old get_X_for_digest Methods from Domains**
- **Status:** `Ready for Spec`
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
- **Dependencies:** `Consolidate Digest Architecture`
- **Verification:** 
  - Run `grep -r "get_.*_for_digest" domains/` - should return no results
  - Run `grep -r "def get_.*_for_digest" domains/` - should return no results
  - Run `uvicorn main:app --reload` - should start without import errors
- **Definition of Done:**
  - All `get_X_for_digest` methods are removed from domain services
  - Digest experience uses `QBODataService` for data formatting
  - No broken references or imports
  - Domain services focus on their core responsibilities
- **Next Action:** Ready for you to run `@spec "Remove Old get_X_for_digest Methods from Domains"`

---

#### **Task: Update Runway Calculators to Use SmartSyncService**
- **Status:** `Ready for Spec`
- **Justification:** Runway calculators currently use individual sync utilities directly. They should use `SmartSyncService` as the orchestrator for consistent sync behavior across the application.
- **Specific Files to Fix:**
  - `runway/core/runway_calculator.py` - Replace SyncTimingManager with SmartSyncService
  - `runway/experiences/tray.py` - Replace SyncTimingManager with SmartSyncService
  - `runway/experiences/digest.py` - Replace SyncTimingManager with SmartSyncService
- **Search Commands to Run:**
  - `grep -r "SyncTimingManager" runway/`
  - `grep -r "from infra\.jobs\.sync_strategies import SyncTimingManager"`
- **Required Changes:**
  - Remove: `from infra.jobs.sync_strategies import SyncTimingManager`
  - Add: `from infra.jobs import SmartSyncService`
  - Replace: `SyncTimingManager(business_id)` with `SmartSyncService(business_id)`
- **Dependencies:** `Test SmartSyncService Integration End-to-End`
- **Verification:** 
  - Run `grep -r "SyncTimingManager" runway/` - should return no results
  - Run `grep -r "SmartSyncService" runway/` - should show new imports
  - Run `uvicorn main:app --reload` - should start without import errors
- **Definition of Done:**
  - All runway calculators use `SmartSyncService` from `infra.jobs`
  - Individual sync utility imports are removed
  - Sync behavior is consistent across all calculators
  - SmartSyncService handles timing, caching, and retry logic
- **Next Action:** Ready for you to run `@spec "Update Runway Calculators to Use SmartSyncService"`

---

## **Phase 5: Final Cleanup and Validation (P2 Medium)**

#### **Task: Audit and Fix All Remaining Import Errors**
- **Status:** `Ready for Spec`
- **Justification:** After all refactoring, there may be remaining import errors or circular dependencies that need to be resolved to ensure the application starts correctly.
- **Commands to Run:**
  - `uvicorn main:app --reload` - Check for startup import errors
  - `pytest` - Check for test import failures
  - `python -c "import main"` - Test basic import chain
- **Common Import Issues to Check:**
  - Circular imports between domains and infra
  - Missing imports after file moves
  - Incorrect import paths after consolidation
- **Dependencies:** `Update All Imports to Use infra/jobs/ Structure`
- **Verification:** 
  - Run `uvicorn main:app --reload` - should start without errors
  - Run `pytest` - should pass without import failures
  - Run `python -c "import main"` - should complete without errors
- **Definition of Done:**
  - No import errors in `uvicorn` startup
  - All tests pass without import failures
  - No circular import dependencies
  - Application starts successfully
- **Next Action:** Ready for you to run `@spec "Audit and Fix All Remaining Import Errors"`

---

#### **Task: Update Documentation to Reflect New Architecture**
- **Status:** `Ready for Spec`
- **Justification:** The infrastructure consolidation and SmartSync refactoring have changed the architecture significantly. Documentation needs to be updated to reflect the new structure and service responsibilities.
- **Specific Files to Update:**
  - `infrastructure_consolidation_plan.md` - Update status and mark completed phases
  - `README.md` - Update architecture section with new structure
  - `docs/` directory - Update any architecture documentation
- **Key Changes to Document:**
  - New `infra/jobs/` consolidated structure
  - SmartSyncService as main orchestrator
  - User Actions vs Data Syncs distinction
  - QBOBulkScheduledService deprecation
  - QBODataService scope limitation
- **Dependencies:** `Audit and Fix All Remaining Import Errors`
- **Verification:** 
  - Read existing documentation to understand current state
  - Identify specific sections that need updates
  - Check for outdated references to old architecture
- **Definition of Done:**
  - All documentation reflects new `infra/jobs/` structure
  - Service responsibilities are clearly documented
  - User Actions vs Data Syncs distinction is explained
  - Architecture diagrams are updated
  - No references to deprecated patterns
- **Next Action:** Ready for you to run `@spec "Update Documentation to Reflect New Architecture"`

---

**Summary:**
- **Total Tasks:** 12
- **P0 Critical:** 3 tasks
- **P1 High:** 6 tasks  
- **P2 Medium:** 3 tasks
- **Ready for Spec:** 12 tasks

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

This backlog captures all the remaining work with the clarity we've achieved about **User Actions vs Data Syncs** and provides clear direction for any developer to pick up and execute without needing this thread's context.