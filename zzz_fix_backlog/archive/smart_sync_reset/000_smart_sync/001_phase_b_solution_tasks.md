# Phase B: Solution Tasks - Analysis & Complex Refactoring Required

*Generated from infrastructure consolidation cleanup on 2025-01-27*  
*Status: ⚠️ NEEDS SOLUTION WORK - NOT READY FOR HANDS-FREE EXECUTION*

## **Task Complexity Curation**

**⚠️ NEEDS SOLUTION WORK (5 tasks)** - These tasks require:
- Analysis and discovery work
- "Figure out" or "determine" language present
- Dependencies on other solution tasks
- Architectural decisions that need human input
- Cannot be executed without solution phase

**✅ EXCLUDED FROM PHASE B** - These tasks are fully solved:
- All 8 tasks from Phase A (see `000_phase_a_executable_tasks.md`)

---

## **Instructions**

**⚠️ DO NOT EXECUTE THESE TASKS HANDS-FREE**

These tasks require analysis, discovery, and solution work. They should be tackled when you have time for:
- Reading and understanding existing code
- Making architectural decisions
- Analyzing dependencies and relationships
- Testing and validating complex changes

**Recommended Approach:**
1. **Complete Phase A first** - get the executable tasks done
2. **Review Phase B tasks** - understand what needs solution work
3. **Tackle one at a time** - work through them together when you have bandwidth
4. **Document solutions** - once solved, they can become executable tasks

---

## **Context for All Tasks**

These tasks build on the foundation established in Phase A:
- SmartSyncService architecture is implemented
- QBOBulkScheduledService is properly scoped
- Direct QBO API calls are working for user actions
- Infrastructure is consolidated in `infra/jobs/`

**Key Challenge**: These tasks require understanding complex relationships and making architectural decisions that affect multiple parts of the system.

---

## **Phase 1: SmartSyncService Integration (P1 High)**

#### **Task 1: Test SmartSyncService Integration End-to-End**
- **Status:** ⚠️ **NEEDS SOLUTION WORK**
- **Justification:** After all refactoring, we need to verify that `SmartSyncService` works correctly for both user actions and background syncs across the entire application.
- **Code Pointers:**
  - `infra/jobs/smart_sync.py` (main orchestrator)
  - `runway/core/runway_calculator.py` (uses SmartSync for data sync)
  - `runway/routes/bills.py` (uses SmartSync for user activity tracking)
  - `domains/ar/services/invoice.py` (uses SmartSync for sync timing)
- **Current Issues:**
  - SmartSyncService is not fully integrated across all use cases
  - Need to verify sync timing works correctly for different strategies
  - Need to verify caching works for data sync operations
  - Need to verify user activity tracking works for immediate actions
- **Required Analysis:**
  - Read `infra/jobs/smart_sync.py` to understand current implementation
  - Test each use case to identify what's missing
  - Determine what integration tests are needed
  - Identify gaps in functionality
- **Dependencies:** `Fix SmartSyncService Usage in Domain Services` (from Phase A)
- **Verification:** 
  - Current SmartSyncService is not fully integrated across all use cases
  - Need to create integration tests
  - Need to verify all use cases work correctly
- **Definition of Done:**
  - SmartSyncService handles both user actions and background syncs
  - Sync timing works correctly for different strategies
  - Caching works for data sync operations
  - User activity tracking works for immediate actions
  - Integration tests cover all use cases
- **Solution Required:** Analysis of current implementation, identification of gaps, creation of integration tests

---

## **Phase 2: Digest Architecture Consolidation (P2 Medium)**

#### **Task 2: Consolidate Digest Architecture**
- **Status:** ⚠️ **NEEDS SOLUTION WORK**
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
  - Decide on single architecture for digest experience
- **Dependencies:** `Fix QBODataService Scope and Remove Bulk Methods` (from Phase A)
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
- **Solution Required:** Analysis of current files, architectural decision on separation of concerns, implementation of consolidated architecture

---

#### **Task 3: Update Runway Calculators to Use SmartSyncService**
- **Status:** ⚠️ **NEEDS SOLUTION WORK**
- **Justification:** Runway calculators currently use individual sync utilities directly. They should use `SmartSyncService` as the orchestrator for consistent sync behavior across the application.
- **Specific Files to Fix:**
  - `runway/core/runway_calculator.py` - Replace SyncTimingManager with SmartSyncService
  - `runway/experiences/tray.py` - Replace SyncTimingManager with SmartSyncService
  - `runway/experiences/digest.py` - Replace SyncTimingManager with SmartSyncService
- **Current Issues:**
  - Calculators use individual sync utilities directly
  - Inconsistent sync behavior across calculators
  - Need to verify SmartSyncService works for all calculator use cases
- **Required Analysis:**
  - Read each calculator to understand current sync usage
  - Determine how to replace individual utilities with SmartSyncService
  - Test that SmartSyncService works for all calculator scenarios
  - Verify no functionality is lost in the transition
- **Dependencies:** `Test SmartSyncService Integration End-to-End` (this phase)
- **Verification:** 
  - Run `grep -r "SyncTimingManager" runway/`
  - Run `grep -r "from infra\.jobs\.sync_strategies import SyncTimingManager"`
  - Test each calculator to ensure it still works
- **Definition of Done:**
  - All runway calculators use `SmartSyncService` from `infra.jobs`
  - Individual sync utility imports are removed
  - Sync behavior is consistent across all calculators
  - SmartSyncService handles timing, caching, and retry logic
- **Solution Required:** Analysis of current calculator sync usage, determination of SmartSyncService integration approach, testing of all calculator scenarios

---

## **Phase 3: Final Cleanup and Validation (P2 Medium)**

#### **Task 4: Audit and Fix All Remaining Import Errors**
- **Status:** ⚠️ **NEEDS SOLUTION WORK**
- **Justification:** After all refactoring, there may be remaining import errors or circular dependencies that need to be resolved to ensure the application starts correctly.
- **Current Issues:**
  - Unknown import errors may exist
  - Circular dependencies may have been introduced
  - Need to discover what's broken
- **Required Analysis:**
  - Run `uvicorn main:app --reload` to discover import errors
  - Run `pytest` to discover test import failures
  - Analyze each error to determine root cause
  - Determine fix for each error
- **Commands to Run:**
  - `uvicorn main:app --reload` - Check for startup import errors
  - `pytest` - Check for test import failures
  - `python -c "import main"` - Test basic import chain
- **Common Import Issues to Check:**
  - Circular imports between domains and infra
  - Missing imports after file moves
  - Incorrect import paths after consolidation
- **Dependencies:** `Update All Imports to Use infra/jobs/ Structure` (from Phase A)
- **Verification:** 
  - Run `uvicorn main:app --reload` - should start without errors
  - Run `pytest` - should pass without import failures
  - Run `python -c "import main"` - should complete without errors
- **Definition of Done:**
  - No import errors in `uvicorn` startup
  - All tests pass without import failures
  - No circular import dependencies
  - Application starts successfully
- **Solution Required:** Discovery of import errors, analysis of root causes, implementation of fixes

---

#### **Task 5: Update Documentation to Reflect New Architecture**
- **Status:** ⚠️ **NEEDS SOLUTION WORK**
- **Justification:** The infrastructure consolidation and SmartSync refactoring have changed the architecture significantly. Documentation needs to be updated to reflect the new structure and service responsibilities.
- **Current Issues:**
  - Documentation is outdated
  - Need to identify what needs updating
  - Need to determine how to document new architecture
- **Required Analysis:**
  - Read existing documentation to understand current state
  - Identify specific sections that need updates
  - Check for outdated references to old architecture
  - Determine what new documentation is needed
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
- **Dependencies:** `Audit and Fix All Remaining Import Errors` (this phase)
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
- **Solution Required:** Analysis of current documentation, identification of what needs updating, implementation of documentation updates

---

## **Summary**

- **Total Tasks:** 5
- **P1 High:** 2 tasks
- **P2 Medium:** 3 tasks
- **Status:** ⚠️ **NEEDS SOLUTION WORK - NOT READY FOR HANDS-FREE EXECUTION**

**Key Characteristics of Solution Tasks:**
- Require analysis and discovery work
- Have "figure out" or "determine" language
- Dependencies on other solution tasks
- Architectural decisions that need human input
- Cannot be executed without solution phase

**Recommended Approach:**
1. **Complete Phase A first** - get the executable tasks done
2. **Review Phase B tasks** - understand what needs solution work
3. **Tackle one at a time** - work through them together when you have bandwidth
4. **Document solutions** - once solved, they can become executable tasks

**Next Steps:**
1. Execute Phase A tasks to get a clean, working codebase
2. Review Phase B tasks to understand the solution work needed
3. Work through Phase B tasks one at a time when you have time for analysis
4. Convert solved Phase B tasks into executable tasks for future work

This backlog contains tasks that require **analysis, discovery, and solution work** and should not be executed hands-free.
