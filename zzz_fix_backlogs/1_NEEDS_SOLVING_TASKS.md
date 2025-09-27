# Needs Solving Tasks - SmartSync & QBO Architecture Cleanup

*Generated from infrastructure consolidation cleanup on 2025-01-27*  
*Status: ⚠️ NEEDS ANALYSIS AND SOLUTION WORK*

## **Task Complexity Curation**

**⚠️ NEEDS SOLUTION WORK (8 tasks)** - These tasks require:
- Analysis and discovery work
- "Figure out" or "determine" language present
- Dependencies on other solution tasks
- Architectural decisions that need human input
- Cannot be executed without solution phase

---

## **Context for All Tasks**

**IMPORTANT**: Before starting any solutioning work, read `LAUNCH_SOLUTIONING_TASKS.md` twice. It contains the complete solutioning framework and methodology you must follow.

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
cd ~/projects/oodaloo
poetry shell
uvicorn main:app --reload
```
This activates the virtual environment and starts the application once. Keep uvicorn running in the background throughout your analysis work.

---

## **Phase 0: Solution Task Alignment and Validation (P0 Critical)**

#### **Task 0: Validate Solution Task Alignment with Architecture**
- **Status:** `[🔄]` Discovery in progress
- **Priority:** P0 Critical
- **Justification:** Before starting any solution work, verify that all solution tasks align with ADR-005 architecture and current system state. This prevents analysis work on outdated or contradictory requirements.
- **Code Pointers:**
  - `docs/architecture/ADR-005-qbo-api-strategy.md` - Current architecture
  - `infra/jobs/smart_sync.py` - Current implementation
  - All solution tasks in this document
- **Current Issues to Resolve:**
  - Solution tasks may reference outdated architecture patterns
  - Tasks may contradict current SmartSyncService implementation
  - Analysis work may be wasted on wrong assumptions
- **Required Analysis:**
  - Read ADR-005 to understand current architecture
  - Review each solution task for alignment with current patterns
  - Identify any tasks that contradict the architecture
  - Determine which tasks need updates before analysis can begin
- **Discovery Commands to Run:**
  - `grep -r "SmartSyncService" . --include="*.py"` - Find current usage patterns
  - `grep -r "from infra.jobs import" . --include="*.py"` - Check current import patterns
  - `uvicorn main:app --reload` - Verify application starts
  - `pytest tests/ -k "smart_sync"` - Check existing tests
- **Files to Read First:**
  - `docs/architecture/ADR-005-qbo-api-strategy.md` - Complete API strategy
  - `infra/jobs/smart_sync.py` - Current implementation
  - `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Overall architecture
  - `zzz_fix_backlogs/LAUNCH_SOLUTIONING_TASKS.md` - Solutioning framework
  - `zzz_fix_backlogs/LAUNCH_EXECUTABLE_TASKS.md` - Execution framework
- **Dependencies:** None
- **Verification:** 
  - All solution tasks align with ADR-005 architecture
  - No tasks contradict current SmartSyncService implementation
  - All tasks reference current system state
- **Definition of Done:**
  - All solution tasks are verified to align with current architecture
  - No contradictory or outdated task requirements remain
  - Analysis work can proceed with confidence
- **Solution Required:** Review and validation of all solution tasks against current architecture
- **Progress Tracking:**
  - Update status to `[🔄]` when starting validation
  - Update status to `[✅]` when all tasks are validated
  - Update status to `[❌]` if tasks need major updates

---

## **Phase 1: Data Architecture Problems (P1 High)**

#### **Task 2: Fix Calculator → Experience Data Flow**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Each calculator in `runway/core/` should feed its specific `runway/experiences/` with the right data for their goals. Current data flow is broken or inconsistent, causing experiences to show wrong or missing data.
- **Code Pointers:**
  - `runway/core/` - Calculator services that should feed experiences
  - `runway/experiences/` - Experience services that need calculator data
  - `domains/qbo/data_service.py` - Current data service implementation
  - `infra/jobs/smart_sync.py` - SmartSync orchestration layer
- **Current Issues to Resolve:**
  - Calculator services not properly feeding experience services
  - Data flow between runway/core and runway/experiences is unclear
  - Each experience may be fetching data independently instead of using calculators
  - Data consistency between calculators and experiences is broken
- **Required Analysis:**
  - Map current data flow from calculators to experiences
  - Identify which calculators should feed which experiences
  - Determine proper data passing patterns
  - Design consistent data flow architecture
- **Discovery Commands to Run:**
  - `grep -r "runway_calculator" runway/experiences/` - Find calculator usage in experiences
  - `grep -r "get_.*_data" runway/core/` - Find data methods in calculators
  - `grep -r "from runway.core" runway/experiences/` - Find calculator imports
  - `grep -r "for_digest" . --include="*.py"` - Find remaining for_digest methods
- **Files to Read First:**
  - `runway/core/runway_calculator.py` - Main calculator service
  - `runway/experiences/digest.py` - Digest experience data needs
  - `runway/experiences/tray.py` - Tray experience data needs
  - `runway/experiences/test_drive.py` - Test drive experience data needs
  - `zzz_fix_backlogs/backlog/006_experiences_cleanup_and_consolidation.md` - Known experience issues
- **Dependencies:** `Create Solution Analysis Framework`
- **Verification:** 
  - Clear data flow from calculators to experiences
  - Each experience gets data from appropriate calculator
  - No duplicate data fetching across experiences
  - Data consistency maintained
- **Definition of Done:**
  - Calculator → Experience data flow clearly designed
  - Each experience uses appropriate calculator for data
  - No duplicate data fetching patterns
  - Data consistency patterns established
- **Solution Required:** Analysis of current data flow, design of calculator → experience patterns
- **Progress Tracking:**
  - Update status to `[🔄]` when starting analysis
  - Update status to `[💡]` when solution is identified
  - Update status to `[✅]` when solution is documented
  - Update status to `[❌]` if blocked or need help

---

#### **Task 3: Clean Up Experience Services Data Patterns**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Experience services in `runway/experiences/` have scattered mocks, providers, and broken data patterns. Need to inspect and fix each experience service to use proper data patterns.
- **Code Pointers:**
  - `runway/experiences/digest.py` - Digest service data patterns
  - `runway/experiences/tray.py` - Tray service data patterns
  - `runway/experiences/test_drive.py` - Test drive service data patterns
  - `zzz_fix_backlogs/backlog/006_experiences_cleanup_and_consolidation.md` - Known issues
- **Current Issues to Resolve:**
  - Experience services have scattered mocks and providers
  - Data patterns are inconsistent across experiences
  - Some services may be broken or non-functional
  - Mock violations in experience data
- **Required Analysis:**
  - Audit each experience service for data patterns
  - Identify mock violations and broken patterns
  - Determine proper data access patterns for each experience
  - Design consistent experience data architecture
- **Discovery Commands to Run:**
  - `grep -r "mock" runway/experiences/` - Find mock usage in experiences
  - `grep -r "provider" runway/experiences/` - Find provider usage in experiences
  - `grep -r "get_.*_for_digest" runway/experiences/` - Find for_digest usage
  - `grep -r "SmartSyncService" runway/experiences/` - Find SmartSync usage
- **Files to Read First:**
  - `runway/experiences/digest.py` - Digest service implementation
  - `runway/experiences/tray.py` - Tray service implementation
  - `runway/experiences/test_drive.py` - Test drive service implementation
  - `zzz_fix_backlogs/backlog/006_experiences_cleanup_and_consolidation.md` - Known issues
- **Dependencies:** `Create Solution Analysis Framework`
- **Verification:** 
  - All experience services use consistent data patterns
  - No mock violations in experience data
  - All services are functional and tested
  - Data patterns align with calculator → experience flow
- **Definition of Done:**
  - All experience services cleaned up and functional
  - Consistent data patterns across all experiences
  - No mock violations in experience data
  - All services properly integrated with calculators
- **Solution Required:** Audit and cleanup of experience services, design of consistent patterns
- **Progress Tracking:**
  - Update status to `[🔄]` when starting analysis
  - Update status to `[💡]` when solution is identified
  - Update status to `[✅]` when solution is documented
  - Update status to `[❌]` if blocked or need help

---

#### **Task 4: Fix Digest Data Architecture - Replace Wrong `get_qbo_data_for_digest` Pattern**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Digest is using the wrong data pattern (`get_qbo_data_for_digest`) instead of proper bulk operations. Digest needs to pull across lots of entities and run calculators for all customers on Friday morning jobs - this requires bulk operations on 2 dimensions, not generic data fetching. The `get_qbo_data_for_digest` pattern was decided against because it's a singular solution for every experience when each experience should get data from its specific calculator.
- **Code Pointers:**
  - `runway/experiences/digest.py` - Currently uses wrong `get_qbo_data_for_digest` pattern
  - `domains/qbo/data_service.py` - Contains `get_qbo_data_for_digest` methods that need removal
  - `domains/qbo/service.py` - QBOBulkScheduledService for proper bulk operations
  - `infra/jobs/smart_sync.py` - SmartSync orchestration for bulk operations
- **Current Issues to Resolve:**
  - Digest uses `get_qbo_data_for_digest` which is the wrong pattern
  - Need proper bulk operations that pull across lots of entities for all customers
  - Friday morning jobs need coordinated bulk data fetching, not individual data calls
  - `get_qbo_data_for_digest` pattern exists throughout domains and needs removal
- **Required Analysis:**
  - Analyze current `get_qbo_data_for_digest` usage across all files
  - Design proper bulk operations architecture for digest
  - Determine how digest should pull across lots of entities for all customers
  - Design Friday morning job coordination for bulk operations
- **Discovery Commands to Run:**
  - `grep -r "get_qbo_data_for_digest" . --include="*.py"` - Find all usage of wrong pattern
  - `grep -r "for_digest" . --include="*.py"` - Find all for_digest methods that need removal
  - `grep -r "get_.*_for_digest" domains/` - Find scattered for_digest methods in domains
  - `grep -r "bulk" runway/experiences/digest.py` - Check current bulk operations
- **Files to Read First:**
  - `runway/experiences/digest.py` - Current wrong implementation
  - `domains/qbo/data_service.py` - Contains wrong pattern methods
  - `domains/qbo/service.py` - QBOBulkScheduledService for proper bulk
  - `infra/jobs/smart_sync.py` - SmartSync for bulk orchestration
- **Dependencies:** `Create Solution Analysis Framework`
- **Verification:** 
  - All `get_qbo_data_for_digest` usage removed from digest
  - Proper bulk operations implemented for Friday morning jobs
  - Digest pulls across lots of entities for all customers efficiently
  - No more scattered `get_X_for_digest` methods in domains
- **Definition of Done:**
  - Digest uses proper bulk operations instead of `get_qbo_data_for_digest`
  - Friday morning jobs coordinate bulk data fetching for all customers
  - All `get_X_for_digest` methods removed from domains
  - Digest efficiently pulls across lots of entities in coordinated bulk operations
- **Solution Required:** Analysis of wrong pattern usage, design of proper bulk operations architecture
- **Progress Tracking:**
  - Update status to `[🔄]` when starting analysis
  - Update status to `[💡]` when solution is identified
  - Update status to `[✅]` when solution is documented
  - Update status to `[❌]` if blocked or need help

---

#### **Task 5: Replace Mock Violations with Real QBO Data**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Replace hardcoded mocks with real QBO API calls and need realistic sandbox data for testing. Current system has mock violations that break the "no more mocks" commitment.
- **Code Pointers:**
  - `dev_plans/Oodaloo_v4.5_Restructured_Build_Plan.md` - Mock violation requirements
  - `qbo_sandbox_data_examples.md` - Sandbox data examples
  - `domains/qbo/client.py` - QBO client implementation
  - `infra/jobs/smart_sync.py` - SmartSync orchestration
- **Current Issues to Resolve:**
  - Hardcoded mock values in KPI calculations
  - Mock violations throughout the system
  - Need realistic sandbox data for testing
  - Tests using mocks instead of real QBO data
- **Required Analysis:**
  - Identify all mock violations in the system
  - Design realistic sandbox data strategy
  - Determine proper QBO API integration patterns
  - Design testing strategy with real data
- **Discovery Commands to Run:**
  - `grep -r "mock" . --include="*.py" | grep -v test` - Find mock usage outside tests
  - `grep -r "hardcoded" . --include="*.py"` - Find hardcoded values
  - `grep -r "TODO.*mock" . --include="*.py"` - Find mock TODOs
  - `grep -r "NotImplementedError" . --include="*.py"` - Find unimplemented methods
- **Files to Read First:**
  - `dev_plans/Oodaloo_v4.5_Restructured_Build_Plan.md` - Mock violation requirements
  - `qbo_sandbox_data_examples.md` - Sandbox data examples
  - `domains/qbo/client.py` - QBO client implementation
  - `infra/jobs/smart_sync.py` - SmartSync orchestration
- **Dependencies:** `Create Solution Analysis Framework`
- **Verification:** 
  - All mock violations identified and replaced
  - Realistic sandbox data available for testing
  - All tests use real QBO data
  - No hardcoded mock values in production code
- **Definition of Done:**
  - All mock violations replaced with real QBO data
  - Realistic sandbox data strategy implemented
  - All tests use real data instead of mocks
  - System works with real QBO API calls
- **Solution Required:** Analysis of mock violations, design of real data strategy
- **Progress Tracking:**
  - Update status to `[🔄]` when starting analysis
  - Update status to `[💡]` when solution is identified
  - Update status to `[✅]` when solution is documented
  - Update status to `[❌]` if blocked or need help

---

## **Phase 2: Testing and Validation (P2 Medium)**

#### **Task 6: Design Comprehensive Testing Strategy**
- **Status:** `[ ]` Not started
- **Priority:** P2 Medium
- **Justification:** After all data architecture problems are solved, need to design comprehensive testing strategy that covers all the new patterns and ensures system reliability.
- **Code Pointers:**
  - `tests/` - Current test structure
  - `infra/jobs/smart_sync.py` - Needs comprehensive testing
  - `domains/qbo/` - QBO integration testing
  - `runway/experiences/` - Experience testing
- **Current Issues to Resolve:**
  - Testing strategy may not cover new data patterns
  - Integration tests may be missing
  - Error handling tests may be incomplete
  - Performance tests may be missing
- **Required Analysis:**
  - Analyze current test coverage
  - Design tests for new data patterns
  - Design integration test strategy
  - Design performance test strategy
- **Discovery Commands to Run:**
  - `find tests/ -name "*.py" | wc -l` - Count test files
  - `grep -r "def test_" tests/ | wc -l` - Count test functions
  - `pytest --collect-only` - See all tests
- **Files to Read First:**
  - `tests/` - Current test structure
  - `infra/jobs/smart_sync.py` - Needs testing
  - `domains/qbo/` - QBO testing
  - `runway/experiences/` - Experience testing
- **Dependencies:** All previous solution tasks
- **Verification:** 
  - Comprehensive testing strategy designed
  - All new patterns have tests
  - Integration tests cover all scenarios
  - Performance tests are included
- **Definition of Done:**
  - Comprehensive testing strategy designed
  - All new patterns have test coverage
  - Integration tests cover all scenarios
  - Performance tests are included
- **Solution Required:** Analysis of current testing, design of comprehensive strategy
- **Progress Tracking:**
  - Update status to `[🔄]` when starting analysis
  - Update status to `[💡]` when solution is identified
  - Update status to `[✅]` when solution is documented
  - Update status to `[❌]` if blocked or need help

---

## **Summary**

- **Total Tasks:** 6
- **P0 Critical:** 2 tasks (alignment and framework)
- **P1 High:** 3 tasks (data architecture problems)
- **P2 Medium:** 1 task (testing)

**Key Solutioning Patterns:**
- **Task 0**: Always validate alignment before starting analysis
- **Task 1**: Create consistent analysis framework
- **Tasks 2-5**: Data architecture problems (calculator flow, experience cleanup, bulk operations, mock violations)
- **Task 6**: Comprehensive testing strategy

**Critical Success Factors:**
- All tasks must align with ADR-005 architecture
- Consistent analysis framework prevents scattered work
- Focus on real data problems, not theoretical architecture
- Solutions must be documented as executable tasks

**Data Architecture Focus:**
- Calculator → Experience data flow
- Experience services cleanup and consistency
- Digest bulk operations efficiency
- Mock violations replacement with real QBO data

This backlog contains only tasks that require **analysis and solution work** before they can be executed.