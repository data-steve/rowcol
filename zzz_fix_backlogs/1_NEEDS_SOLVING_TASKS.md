# Needs Solving Tasks - Data Architecture & Experience Cleanup

*Updated after nuclear cleanup completion on 2025-01-27*  
*Status: Ready

## **Task Complexity Curation**

**⚠️ NEEDS SOLUTION WORK (6 tasks)** - These tasks require:
- Analysis and discovery work
- "Figure out" or "determine" language present
- Dependencies on other solution tasks
- Architectural decisions that need human input
- Cannot be executed without solution phase

---

## **Context for All Tasks**

**IMPORTANT**: Before starting any solutioning work, read `LAUNCH_SOLUTIONING_TASKS.md` twice. It contains the complete solutioning framework and methodology you must follow.

### **Nuclear Cleanup Foundation - COMPLETED ✅**
The QBO architecture has been completely reset and rebuilt with clean separation of concerns:

**✅ COMPLETED NUCLEAR CLEANUP:**
- **Clean Architecture**: `Domain Service → SmartSyncService → Raw QBO HTTP Calls`
- **No Circular Dependencies**: Infrastructure independence maintained
- **Integration Model Simplified**: QBO fields moved to Business model
- **SmartSync Test Patterns**: All tests use new architecture
- **Database Fixtures**: Centralized database connection patterns
- **Mock Violations Documented**: Ready for comprehensive test data service

### **Current Architecture State (Post-Nuclear)**
- **SmartSyncService** (`infra/qbo/smart_sync.py`): Central orchestration layer for ALL QBO interactions. Handles retries, deduplication, rate limiting, and caching. Provides resilience infrastructure for domain services.
- **QBORawClient** (`infra/qbo/client.py`): Raw HTTP calls to QBO endpoints only. No business logic, no orchestration.
- **Domain Services** (`domains/*/services/`): Handle their own CRUD operations and business logic using SmartSyncService.
- **Business Model**: Contains QBO connection fields (`qbo_realm_id`, `qbo_access_token`, etc.) - Integration model removed.

### **Key Architecture Principle**
Domain services handle their own business logic and CRUD operations. SmartSyncService provides resilience infrastructure (retry, dedup, rate limiting, caching). Raw QBO client just makes HTTP calls. Clean dependency flow with no circular dependencies.

### **Critical Context for Future Developers**

**🚨 READ THIS FIRST - What Was Accomplished in Nuclear Cleanup:**

The QBO architecture was completely reset and rebuilt. Key changes that affect these solution tasks:

1. **Deleted Components** (tasks may reference these - they're gone):
   - `domains/qbo/` directory (entire directory deleted)
   - `domains/integrations/qbo/` directory (entire directory deleted)
   - `Integration` model (removed, QBO fields moved to Business model)
   - `infra/jobs/smart_sync.py` (moved to `infra/qbo/smart_sync.py`)

2. **New Components** (tasks should use these):
   - `infra/qbo/smart_sync.py` - SmartSyncService (moved from infra/jobs/)
   - `infra/qbo/client.py` - QBORawClient (new raw HTTP client)
   - `domains/core/models/business.py` - Now has QBO fields (qbo_realm_id, qbo_access_token, etc.)
   - `tests/conftest.py` - New database fixtures (prod_database_session, qbo_connected_business)

3. **New Patterns** (tasks should follow these):
   - Use `SmartSyncService` for all QBO operations
   - Use `Business` model QBO fields instead of Integration model
   - Use database fixtures instead of inline database connections
   - Use new test patterns documented in nuclear cleanup

4. **Mock Violations** (documented for cleanup):
   - See `zzz_fix_backlogs/backlog/008_eliminate_remaining_mock_violations.md`
   - Tests need comprehensive test data service solution
   - Experience services have mock data that needs real QBO data

**Before starting any solution task, verify it aligns with these changes!**

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

#### **Task 0: Validate Solution Task Alignment with Post-Nuclear Architecture**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** After nuclear cleanup completion, verify that all solution tasks align with the new clean architecture. The nuclear cleanup has fundamentally changed the system, so tasks may reference outdated patterns.
- **Code Pointers:**
  - `infra/qbo/smart_sync.py` - New SmartSyncService location
  - `infra/qbo/client.py` - New QBORawClient
  - `domains/core/models/business.py` - QBO fields added to Business model
  - All solution tasks in this document
- **Current Issues to Resolve:**
  - Tasks may reference old `domains/qbo/` patterns (now deleted)
  - Tasks may reference old `infra/jobs/smart_sync.py` (moved to `infra/qbo/`)
  - Tasks may reference Integration model (now removed)
  - Tasks may not account for new database fixture patterns
- **Required Analysis:**
  - Review each solution task for alignment with post-nuclear architecture
  - Identify tasks that reference deleted or moved components
  - Update task requirements to reflect new patterns
  - Ensure tasks account for new SmartSync test patterns
- **Discovery Commands to Run:**
  - `grep -r "domains/qbo" . --include="*.py"` - Should return no results (all deleted)
  - `grep -r "infra/jobs/smart_sync" . --include="*.py"` - Should return no results (moved)
  - `grep -r "Integration" . --include="*.py"` - Should return no results (removed)
  - `grep -r "SmartSyncService" . --include="*.py"` - Find current usage patterns
  - `grep -r "from infra.qbo" . --include="*.py"` - Check new import patterns
- **Files to Read First:**
  - `zzz_fix_backlogs/smart_sync_reset/0_EXECUTABLE_NUCLEAR_TASKS.md` - What was completed
  - `infra/qbo/smart_sync.py` - New SmartSyncService implementation
  - `infra/qbo/client.py` - New QBORawClient implementation
  - `domains/core/models/business.py` - QBO fields in Business model
  - `tests/conftest.py` - New database fixture patterns
- **Dependencies:** None
- **Verification:** 
  - All solution tasks align with post-nuclear architecture
  - No tasks reference deleted or moved components
  - All tasks account for new patterns and fixtures
- **Definition of Done:**
  - All solution tasks are verified to align with current architecture
  - No contradictory or outdated task requirements remain
  - Analysis work can proceed with confidence
- **Solution Required:** Review and validation of all solution tasks against post-nuclear architecture
- **Progress Tracking:**
  - Update status to `[🔄]` when starting validation
  - Update status to `[✅]` when all tasks are validated
  - Update status to `[❌]` if tasks need major updates

---

## **Phase 1: Data Architecture Problems (P1 High)**

#### **Task 1: Fix Calculator → Experience Data Flow**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Each calculator in `runway/core/` should feed its specific `runway/experiences/` with the right data for their goals. Current data flow is broken or inconsistent, causing experiences to show wrong or missing data. This is now possible with the clean SmartSync architecture.
- **Code Pointers:**
  - `runway/core/runway_calculator.py` - Main calculator service (now uses SmartSyncService)
  - `runway/experiences/` - Experience services that need calculator data
  - `infra/qbo/smart_sync.py` - SmartSync orchestration layer (new location)
  - `tests/conftest.py` - New database fixture patterns
- **Current Issues to Resolve:**
  - Calculator services not properly feeding experience services
  - Data flow between runway/core and runway/experiences is unclear
  - Each experience may be fetching data independently instead of using calculators
  - Data consistency between calculators and experiences is broken
  - Mock violations in experience data (documented in 008_eliminate_remaining_mock_violations.md)
- **Required Analysis:**
  - Map current data flow from calculators to experiences
  - Identify which calculators should feed which experiences
  - Determine proper data passing patterns using SmartSyncService
  - Design consistent data flow architecture
  - Address mock violations in experience data
- **Discovery Commands to Run:**
  - `grep -r "runway_calculator" runway/experiences/` - Find calculator usage in experiences
  - `grep -r "get_.*_data" runway/core/` - Find data methods in calculators
  - `grep -r "from runway.core" runway/experiences/` - Find calculator imports
  - `grep -r "SmartSyncService" runway/` - Find SmartSync usage in runway
  - `grep -r "mock" runway/experiences/` - Find mock violations in experiences
- **Files to Read First:**
  - `runway/core/runway_calculator.py` - Main calculator service (updated for SmartSync)
  - `runway/experiences/digest.py` - Digest experience data needs
  - `runway/experiences/tray.py` - Tray experience data needs
  - `runway/experiences/test_drive.py` - Test drive experience data needs
  - `zzz_fix_backlogs/backlog/008_eliminate_remaining_mock_violations.md` - Mock violations
- **Dependencies:** `Validate Solution Task Alignment with Post-Nuclear Architecture`
- **Verification:** 
  - Clear data flow from calculators to experiences
  - Each experience gets data from appropriate calculator
  - No duplicate data fetching across experiences
  - Data consistency maintained
  - No mock violations in experience data
- **Definition of Done:**
  - Calculator → Experience data flow clearly designed
  - Each experience uses appropriate calculator for data
  - No duplicate data fetching patterns
  - Data consistency patterns established
  - Mock violations addressed
- **Solution Required:** Analysis of current data flow, design of calculator → experience patterns using SmartSyncService
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
- **P0 Critical:** 1 task (alignment validation)
- **P1 High:** 4 tasks (data architecture problems)
- **P2 Medium:** 1 task (testing strategy)

**Key Solutioning Patterns:**
- **Task 0**: Validate alignment with post-nuclear architecture
- **Tasks 1-4**: Data architecture problems (calculator flow, experience cleanup, bulk operations, mock violations)
- **Task 5**: Comprehensive testing strategy

**Critical Success Factors:**
- All tasks must align with post-nuclear architecture
- Use new SmartSync patterns and database fixtures
- Address mock violations documented in 008_eliminate_remaining_mock_violations.md
- Solutions must be documented as executable tasks

**Data Architecture Focus:**
- Calculator → Experience data flow using SmartSyncService
- Experience services cleanup and consistency
- Digest bulk operations efficiency
- Mock violations replacement with real QBO data
- Comprehensive test data service solution

**Post-Nuclear Context:**
- Clean architecture: `Domain Service → SmartSyncService → Raw QBO HTTP Calls`
- No circular dependencies
- Integration model simplified (QBO fields in Business model)
- SmartSync test patterns established
- Database connection fixtures created

This backlog contains only tasks that require **analysis and solution work** before they can be executed.