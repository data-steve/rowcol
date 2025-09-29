# Needs Solving Tasks - Architecture Analysis & Design

*Consolidated from backlog analysis on 2025-01-27*  
*Status: ⚠️ NEEDS ANALYSIS AND SOLUTION WORK*

## **Task Complexity Curation**

**⚠️ NEEDS SOLUTION WORK (2 tasks)** - These tasks require:
- Analysis and discovery work
- "Figure out" or "determine" language present
- Dependencies on other solution tasks
- Architectural decisions that need human input
- Cannot be executed without solution phase

---

## **CRITICAL: Read These Files First**

Before starting any solutioning tasks, you MUST read these files to understand the system:

### **Architecture Context:**
- `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Complete system architecture
- `docs/build_plan_v5.md` - Current build plan and phase context
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `docs/architecture/ADR-003-multi-tenancy-strategy.md` - Multi-tenancy patterns

### **Solutioning Context:**
- Review the specific solutioning task document for additional context
- Understand the current phase and architectural constraints
- Familiarize yourself with the codebase structure and patterns

## **Context for All Tasks**

**IMPORTANT**: Before starting any solutioning work, read `LAUNCH_SOLUTIONING_TASKS.md` twice. It contains the complete solutioning framework and methodology you must follow.

### **Post-Nuclear Cleanup Context**
- Clean architecture: `Domain Service → SmartSyncService → Raw QBO HTTP Calls`
- No circular dependencies
- Integration model simplified (QBO fields in Business model)
- SmartSync test patterns established
- Database connection fixtures created

### **Key Architecture Principle**
Domain services handle their own business logic and CRUD operations. SmartSyncService provides resilience infrastructure (retry, dedup, rate limiting, caching). Raw QBO client just makes HTTP calls. Clean dependency flow with no circular dependencies.

---

## **Phase 1: Data Architecture Analysis (P1 High)**

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
  - Mock violations in experience data
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
- **Dependencies:** None
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

- **Todo List Integration:**
  - Create Cursor todo for this task when starting analysis
  - Update todo status as analysis progresses
  - Mark todo complete when solution is documented
  - Add discovery todos for found issues
  - Remove obsolete todos when analysis is complete
  - Ensure todo list reflects current analysis state

---

#### **Task 2: Fix Digest Data Architecture - Replace Wrong `get_qbo_data_for_digest` Pattern**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Digest is using the wrong data pattern (`get_qbo_data_for_digest`) instead of proper bulk operations. Digest needs to pull across lots of entities and run calculators for all customers on Friday morning jobs - this requires bulk operations on 2 dimensions, not generic data fetching.
- **Code Pointers:**
  - `runway/experiences/digest.py` - Currently uses wrong `get_qbo_data_for_digest` pattern
  - `infra/qbo/smart_sync.py` - SmartSync orchestration for bulk operations
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
  - `infra/qbo/smart_sync.py` - SmartSync for bulk orchestration
- **Dependencies:** `Fix Calculator → Experience Data Flow`
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

- **Todo List Integration:**
  - Create Cursor todo for this task when starting analysis
  - Update todo status as analysis progresses
  - Mark todo complete when solution is documented
  - Add discovery todos for found issues
  - Remove obsolete todos when analysis is complete
  - Ensure todo list reflects current analysis state

---

#### **Task 3: Design Comprehensive Testing Strategy**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** After all data architecture problems are solved, need to design comprehensive testing strategy that covers all the new patterns and ensures system reliability.
- **Code Pointers:**
  - `tests/` - Current test structure
  - `infra/qbo/smart_sync.py` - Needs comprehensive testing
  - `domains/*/services/` - Domain service testing
  - `runway/experiences/` - Experience testing
- **Current Issues to Resolve:**
  - Testing strategy may not cover new data patterns
  - Integration tests may be missing
  - Error handling tests may be incomplete
  - Performance tests may be missing
  - Mock violations in tests need systematic solution
- **Required Analysis:**
  - Analyze current test coverage
  - Design tests for new data patterns
  - Design integration test strategy
  - Design performance test strategy
  - Design comprehensive test data service solution
- **Discovery Commands to Run:**
  - `find tests/ -name "*.py" | wc -l` - Count test files
  - `grep -r "def test_" tests/ | wc -l` - Count test functions
  - `pytest --collect-only` - See all tests
  - `grep -r "mock" tests/` - Find mock usage in tests
  - `grep -r "SmartSyncService" tests/` - Find SmartSync usage in tests
- **Files to Read First:**
  - `tests/` - Current test structure
  - `infra/qbo/smart_sync.py` - Needs testing
  - `domains/*/services/` - Domain service testing
  - `runway/experiences/` - Experience testing
  - `zzz_fix_backlogs/backlog/008_eliminate_remaining_mock_violations.md` - Mock violations
- **Dependencies:** `Fix Calculator → Experience Data Flow`
- **Verification:** 
  - Comprehensive testing strategy designed
  - All new patterns have tests
  - Integration tests cover all scenarios
  - Performance tests are included
  - Mock violations systematically addressed
- **Definition of Done:**
  - Comprehensive testing strategy designed
  - All new patterns have test coverage
  - Integration tests cover all scenarios
  - Performance tests are included
  - Mock violations systematically addressed
- **Solution Required:** Analysis of current testing, design of comprehensive strategy
- **Progress Tracking:**
  - Update status to `[🔄]` when starting analysis
  - Update status to `[💡]` when solution is identified
  - Update status to `[✅]` when solution is documented
  - Update status to `[❌]` if blocked or need help

- **Todo List Integration:**
  - Create Cursor todo for this task when starting analysis
  - Update todo status as analysis progresses
  - Mark todo complete when solution is documented
  - Add discovery todos for found issues
  - Remove obsolete todos when analysis is complete
  - Ensure todo list reflects current analysis state

---

## **Summary**

- **Total Tasks:** 3
- **P1 High:** 3 tasks (calculator data flow, digest bulk operations, testing strategy)
- **Completed:** 0 tasks
- **Remaining:** 3 tasks

**Key Solutioning Patterns:**
- **Task 1**: Data flow analysis and design
- **Task 2**: Comprehensive testing strategy design

**Critical Success Factors:**
- All tasks must align with post-nuclear architecture
- Use new SmartSync patterns and database fixtures
- Address mock violations comprehensively
- Solutions must be documented as executable tasks

**Data Architecture Focus:**
- Calculator → Experience data flow using SmartSyncService
- Experience services cleanup and consistency
- Mock violations replacement with real QBO data
- Comprehensive test data service solution

**Post-Nuclear Context:**
- Clean architecture: `Domain Service → SmartSyncService → Raw QBO HTTP Calls`
- No circular dependencies
- Integration model simplified (QBO fields in Business model)
- SmartSync test patterns established
- Database connection fixtures created

This backlog contains only tasks that require **analysis and solution work** before they can be executed.
