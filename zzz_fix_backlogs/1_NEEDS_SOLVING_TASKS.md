# Needs Solving Tasks - SmartSync & QBO Architecture Cleanup

*Generated from infrastructure consolidation cleanup on 2025-01-27*  
*Status: ⚠️ NEEDS ANALYSIS AND SOLUTION WORK*

## **Task Complexity Curation**

**⚠️ NEEDS SOLUTION WORK (5 tasks)** - These tasks require:
- Analysis and discovery work
- "Figure out" or "determine" language present
- Dependencies on other solution tasks
- Architectural decisions that need human input
- Cannot be executed without solution phase

---

## **Context for All Tasks**

### **What is zzz_fix_backlogs?**
This directory contains cleanup tasks from a major infrastructure consolidation effort. The codebase was refactored to move scattered utilities into a consolidated `infra/jobs/` directory, but several architectural decisions need analysis and solution work before they can be executed.

### **Current Architecture State**
- **SmartSyncService** (`infra/jobs/smart_sync.py`): Central orchestration layer for ALL QBO interactions. Handles retries, deduplication, rate limiting, and caching while enabling immediate user actions through direct API calls. See [ADR-005: QBO API Strategy](../docs/architecture/ADR-005-qbo-api-strategy.md) for complete architecture.
- **QBOBulkScheduledService** (`domains/qbo/service.py`): ONLY for bulk background data operations (like digest generation). NOT for user actions.
- **Direct QBO API calls** (`domains/qbo/client.py`): For immediate user actions (pay bill, delay payment, send collection). Must be wrapped in SmartSyncService for fragility handling.
- **QBODataService** (`domains/qbo/data_service.py`): ONLY for `runway/experiences/` data formatting. NOT a generic data fetcher.
- **User Actions vs Data Syncs**: User actions = immediate QBO API calls wrapped in SmartSyncService. Data syncs = background operations coordinated by SmartSyncService.

### **Key Architecture Principle**
The question isn't "SmartSyncService vs direct API calls" - it's "How do we use SmartSyncService to handle QBO's fragility while maintaining the UX of immediate user actions?" Answer: SmartSyncService as the orchestration layer that handles retries, deduplication, rate limiting, and caching, while still allowing direct API calls for user actions.

### **QBO Fragility Context**
QuickBooks Online API has well-documented fragility that can disrupt the cash runway ritual:
- **Rate Limiting**: 500 requests/min per app, 100 requests/sec per realm
- **Intermittent Failures**: 503 Service Unavailable, network latency, maintenance windows
- **Duplicate Actions**: Retrying failed requests can create duplicate transactions
- **Lost Actions**: QBO's async processing can make actions appear to fail when they succeeded
- **Data Inconsistencies**: QBO data may not reflect real-time changes
- **Webhook Reliability**: Missed events, out-of-order delivery, duplicates

### **Product Context**
Oodaloo is a cash runway management tool for service agencies ($1M–$5M, 10-30 staff) that automates 70-80% of weekly cash runway decisions through QBO integration. The core value proposition is the "weekly cash runway ritual" - a seamless, trustworthy experience where users can make immediate decisions (pay bills, send reminders) with real-time feedback.

**Key Challenge**: These tasks require understanding complex relationships and making architectural decisions that affect multiple parts of the system.

## **Development Environment Setup**

**IMPORTANT**: Start your development session with:
```bash
poetry shell
```
This activates the virtual environment and saves you from typing `poetry run` before every command. You can then run commands directly like `uvicorn main:app --reload` instead of `poetry run uvicorn main:app --reload`.

---

## **Phase 1: SmartSyncService Integration (P1 High)**

#### **Task 1: Test SmartSyncService Integration End-to-End**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
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
- **Discovery Commands to Run:**
  - `grep -r "SmartSyncService" . --include="*.py"` - Find all current usage
  - `grep -r "from infra.jobs import SmartSyncService" . --include="*.py"` - Check imports
  - `grep -r "smart_sync\." . --include="*.py"` - Find method calls
  - `uvicorn main:app --reload` - Test application startup
  - `pytest tests/ -k "smart_sync"` - Run existing SmartSync tests
- **Files to Read First:**
  - `docs/architecture/ADR-005-qbo-api-strategy.md` - Complete API strategy
  - `infra/jobs/smart_sync.py` - Current implementation
  - `dev_plans/Oodaloo_v4.5_Restructured_Build_Plan.md` - Product context
  - `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Overall architecture
- **Dependencies:** `Fix SmartSyncService Usage in Domain Services` (from executable tasks)
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
- **Status:** `[ ]` Not started
- **Priority:** P2 Medium
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
- **Discovery Commands to Run:**
  - `grep -r "digest" runway/experiences/ infra/scheduler/` - Find all digest usage
  - `grep -r "DigestService" . --include="*.py"` - Find service usage
  - `grep -r "digest_jobs" . --include="*.py"` - Find job usage
  - `ls -la runway/experiences/digest.py infra/scheduler/digest_jobs.py` - Check file existence
  - `uvicorn main:app --reload` - Test application startup
- **Files to Read First:**
  - `runway/experiences/digest.py` - Experience logic
  - `infra/scheduler/digest_jobs.py` - Job scheduling
  - `dev_plans/Oodaloo_v4.5_Restructured_Build_Plan.md` - Digest requirements
  - `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Background jobs architecture
- **Dependencies:** `Fix QBODataService Scope and Remove Bulk Methods` (from executable tasks)
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
- **Status:** `[ ]` Not started
- **Priority:** P2 Medium
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
- **Discovery Commands to Run:**
  - `grep -r "SyncTimingManager" runway/` - Find current usage
  - `grep -r "from infra\.jobs\.sync_strategies import SyncTimingManager"` - Check imports
  - `grep -r "sync_timing\." runway/` - Find method calls
  - `grep -r "SyncCache" runway/` - Find cache usage
  - `uvicorn main:app --reload` - Test application startup
- **Files to Read First:**
  - `runway/core/runway_calculator.py` - Main calculator
  - `runway/experiences/tray.py` - Tray experience
  - `runway/experiences/digest.py` - Digest experience
  - `infra/jobs/smart_sync.py` - SmartSync implementation
  - `docs/architecture/ADR-005-qbo-api-strategy.md` - API strategy
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
- **Status:** `[ ]` Not started
- **Priority:** P2 Medium
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
- **Discovery Commands to Run:**
  - `uvicorn main:app --reload` - Check for startup import errors
  - `pytest` - Check for test import failures
  - `python -c "import main"` - Test basic import chain
  - `grep -r "from infra\.(cache|queue|scheduler)" . --include="*.py"` - Find old imports
  - `grep -r "import infra\.(cache|queue|scheduler)" . --include="*.py"` - Find old imports
  - `grep -r "circular import" . --include="*.py"` - Find circular import issues
- **Files to Read First:**
  - `main.py` - Application entry point
  - `infra/jobs/__init__.py` - Consolidated exports
  - `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Import structure
  - `infrastructure_consolidation_plan.md` - Consolidation history
- **Commands to Run:**
  - `uvicorn main:app --reload` - Check for startup import errors
  - `pytest` - Check for test import failures
  - `python -c "import main"` - Test basic import chain
- **Common Import Issues to Check:**
  - Circular imports between domains and infra
  - Missing imports after file moves
  - Incorrect import paths after consolidation
- **Dependencies:** `Update All Imports to Use infra/jobs/ Structure` (from executable tasks)
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
- **Status:** `[ ]` Not started
- **Priority:** P2 Medium
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
- **Discovery Commands to Run:**
  - `grep -r "infra\.(cache|queue|scheduler)" docs/` - Find old references
  - `grep -r "SmartSyncService" docs/` - Find SmartSync references
  - `grep -r "QBOBulkScheduledService" docs/` - Find bulk service references
  - `grep -r "domains/qbo" docs/` - Find QBO references
  - `find docs/ -name "*.md" -exec grep -l "infra/" {} \;` - Find infra references
- **Files to Read First:**
  - `infrastructure_consolidation_plan.md` - Consolidation plan
  - `README.md` - Main documentation
  - `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Architecture docs
  - `docs/architecture/ADR-005-qbo-api-strategy.md` - API strategy
  - `dev_plans/Oodaloo_v4.5_Restructured_Build_Plan.md` - Build plan
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
1. **Complete executable tasks first** - get the foundation working
2. **Review solution tasks** - understand what needs analysis work
3. **Tackle one at a time** - work through them together when you have bandwidth
4. **Document solutions** - once solved, they can become executable tasks

**Next Steps:**
1. Execute executable tasks to get a clean, working codebase
2. Review solution tasks to understand the analysis work needed
3. Work through solution tasks one at a time when you have time for analysis
4. Convert solved solution tasks into executable tasks for future work

This backlog contains tasks that require **analysis, discovery, and solution work** and should not be executed hands-free.

---

## **How to Use This Backlog**

### **For New Threads Starting This Work**

1. **Read the Context Section First** - Understand what zzz_fix_backlogs is and the current architecture state
2. **Read the Key Architecture Principle** - Understand the SmartSyncService vs direct API calls distinction
3. **Read the QBO Fragility Context** - Understand why SmartSyncService is necessary
4. **Read the Product Context** - Understand what Oodaloo is and why it matters

### **For Each Task**

1. **Read the Files to Read First** - Get the necessary context before starting
2. **Run the Discovery Commands** - Understand the current state
3. **Analyze the Current Issues** - Understand what needs to be solved
4. **Follow the Required Analysis** - Work through the analysis systematically
5. **Document Your Solution** - Once solved, document the approach for future reference

### **Common Patterns to Look For**

- **Import Issues**: Look for old `infra.cache`, `infra.queue`, `infra.scheduler` imports
- **Service Misuse**: Look for QBOBulkScheduledService used for user actions
- **Missing Integration**: Look for direct QBO calls not wrapped in SmartSyncService
- **Circular Dependencies**: Look for domains importing from runway or vice versa

### **Decision Making Guidelines**

- **When in doubt, use SmartSyncService** - It's the central orchestration layer
- **User actions = direct QBO calls wrapped in SmartSyncService** - Not bulk operations
- **Background syncs = SmartSyncService + QBOBulkScheduledService** - Not direct calls
- **Experience data = QBODataService** - Only for runway/experiences/ formatting

### **Testing Strategy**

- **Always test uvicorn startup** - `uvicorn main:app --reload`
- **Always run pytest** - `pytest` to check for test failures
- **Test the specific functionality** - Don't just check imports
- **Verify the solution works** - Don't just fix the immediate error

### **When You're Stuck**

1. **Read the ADR-005** - It has the complete API strategy
2. **Read the Comprehensive Architecture** - It has the overall system design
3. **Read the Build Plan** - It has the product context and requirements
4. **Check the executable tasks** - They might have solved similar problems
5. **Ask for help** - These are complex architectural decisions

### **Success Criteria**

- **Application starts without errors** - `uvicorn main:app --reload` works
- **All tests pass** - `pytest` passes
- **Architecture is consistent** - All services follow the same patterns
- **Documentation is updated** - Reflects the new architecture
- **Solution is documented** - Future developers can understand the decisions
