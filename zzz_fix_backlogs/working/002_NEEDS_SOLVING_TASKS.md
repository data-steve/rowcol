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
- **Status:** `[✅]` Solution complete - Ready for execution
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
- **Solution Required:** ✅ COMPLETE - See `SOLUTIONING_PROGRESS_TASK1.md` for full analysis and proposed architecture
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

#### **Task 1.2: Design RunwayCalculator Service Architecture - Foundation for Priority Scoring**
- **Status:** `[✅]` Solution complete - Ready for execution
- **Priority:** P1 High
- **Justification:** RunwayCalculator has scope creep with mixed responsibilities violating ADR-001. Need to design proper service architecture that serves as foundation for priority scoring and other runway calculations. Current design mixes pure runway calculations with entity-specific calculations, making it unclear what belongs where.
- **Code Pointers:**
  - `runway/core/runway_calculator.py` - Current monolithic service with mixed responsibilities
  - `runway/core/priority_calculation_service.py` - Existing priority service that needs integration
  - `runway/experiences/` - Experience services that need different calculation types
  - `domains/` - Domain services that might need calculation integration
- **Current Issues to Resolve:**
  - RunwayCalculator mixes pure runway calculations with entity-specific calculations
  - Unclear boundaries between "scenario impact" vs "historical runway" vs "current runway"
  - Priority scoring scattered across multiple services instead of integrated
  - Entity-specific calculations (bills, invoices, collections) not properly organized
  - No clear foundation for how different calculation types should work together
- **Required Analysis:**
  - Map all current calculation methods and their actual purposes
  - Design service boundaries that make architectural sense
  - Determine how priority scoring integrates with runway calculations
  - Design consistent patterns for different calculation types
  - Plan how collections, bills, invoices, and other entities fit together
- **Discovery Commands to Run:**
  - `grep -r "def calculate_" runway/core/runway_calculator.py` - Find all calculation methods
  - `grep -r "calculate_.*runway" runway/` - Find runway calculation usage patterns
  - `grep -r "calculate_.*impact" runway/` - Find impact calculation patterns
  - `grep -r "calculate_.*priority" runway/` - Find priority calculation patterns
  - `grep -r "scenario\|historical\|current" runway/core/runway_calculator.py` - Find method naming patterns
- **Files to Read First:**
  - `runway/core/runway_calculator.py` - Current implementation to understand scope
  - `runway/core/priority_calculation_service.py` - Existing priority service
  - `runway/experiences/tray.py` - How tray uses calculations
  - `runway/experiences/digest.py` - How digest uses calculations
  - `runway/experiences/test_drive.py` - How test drive uses calculations
- **Dependencies:** None
- **Verification:** 
  - Clear service architecture designed with proper boundaries
  - Priority scoring properly integrated with runway calculations
  - Entity-specific calculations properly organized
  - Consistent naming and patterns across all calculation types
  - Foundation established for all runway calculation needs
- **Definition of Done:**
  - Service architecture designed with clear boundaries
  - All calculation types properly categorized and organized
  - Priority scoring integration plan created
  - Entity-specific calculations properly planned
  - Consistent patterns established for all calculation types
- **Solution Required:** Design comprehensive service architecture that serves as foundation for all runway calculations, including priority scoring, entity-specific calculations, and different calculation types (scenario, historical, current)
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
- **Status:** Done
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

#### **Task 4: Design Console Payment Decision Workflow - Bill Approval, Staging, and Batch Finalization**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Current console payment workflow is incomplete and architecturally confused. Need to design proper workflow for bill approval → staging → payment decisions → batch finalization. Current implementation has missing staging mechanism, unclear reserve allocation timing, and competing payment services. This affects core runway functionality and user experience.

## **Current Payment Workflow Analysis**

### **What We Have (Execution Layer):**
- ✅ **`domains/ap/services/payment.py:execute_payment_workflow()`** - Payment execution service
  - Validates payment can be executed
  - Executes payment using QBO bill pay rails
  - Syncs with QBO
  - Updates bill status to "paid"
  - Commits transaction
- ✅ **`runway/core/scheduled_payment_service.py`** - Scheduled payment service
- ✅ **`runway/core/reserve_runway.py`** - Reserve allocation service

### **What We're Missing (Decision Layer):**
- ❌ **Bill Approval & Staging** - Currently in routes, not console experience
- ❌ **Decision Making** - Console experience for "Pay Now" vs "Schedule" vs "Delay" decisions
- ❌ **Batch Finalization** - Missing logic for processing multiple decisions together
- ❌ **Decision Queue Management** - Just stores metadata, no real payment processing
- ❌ **Reserve Allocation Timing** - Unclear when reserves should be allocated (approval vs decision vs execution)

### **Complete Workflow Design Needed:**
```
1. Bill Approval → 2. Staging → 3. Decision Making → 4. Batch Finalization → 5. Payment Execution
   [MISSING]      [MISSING]    [MISSING]         [MISSING]            [EXISTS]
```

**Key Insight**: `execute_payment_workflow` is the **execution engine** that the console payment decision workflow needs to **orchestrate**. The solutioning work needs to design the decision-making and orchestration layer that uses this existing execution service.

- **Code Pointers:**
  - `runway/routes/bills.py` - Bill approval endpoint (approves but doesn't stage)
  - `runway/experiences/console.py` - Console experience service (incomplete decision handling)
  - `runway/core/data_orchestrators/decision_console_data_orchestrator.py` - Decision queue management
  - `domains/ap/services/payment.py` - Payment execution service (EXISTS - `execute_payment_workflow`)
  - `runway/core/scheduled_payment_service.py` - Scheduled payment service
  - `runway/core/reserve_runway.py` - Reserve allocation service
- **Current Issues to Resolve:**
  - Bill approval happens in routes, not console experience
  - No staging mechanism for approved bills (no immediate reserve allocation)
  - Decision queue just stores metadata, no real payment processing
  - Unclear when reserves should be allocated (approval vs payment decision)
  - Competing payment services (PaymentService vs ScheduledPaymentService)
  - Missing batch finalization logic for "Pay Now" vs "Schedule" vs "Delay"
  - ADR-001 violations (PaymentService depending on ScheduledPaymentService)
  - **Missing orchestration layer** between decision-making and payment execution
- **Required Analysis:**
  - Map current bill approval workflow and identify staging gaps
  - Design proper decision queue with real payment processing
  - Determine reserve allocation timing (approval vs decision vs execution)
  - Design console experience for bill staging and decision-making
  - Clarify service boundaries between PaymentService, ScheduledPaymentService, and RunwayReserveService
  - Design batch finalization workflow for different decision types
  - Determine how "Delay" decisions affect queue management vs reserve allocation
  - **Design orchestration layer** that connects decision-making to existing payment execution services
  - **Determine when to call** `execute_payment_workflow()` vs `schedule_payment()` vs delay logic
  - **Design batch processing** for multiple payment decisions
  - **Design reserve allocation strategy** for different decision types

## **Architecture Design Requirements**

### **Service Orchestration Pattern:**
```python
# Console Payment Decision Workflow (NEEDS SOLUTIONING)
├── Bill Approval & Staging
├── Decision Making (Pay Now/Schedule/Delay)
├── Batch Finalization
└── Payment Orchestration
    ├── execute_payment_workflow() ← EXISTS in domains/ap/services/payment.py
    ├── schedule_payment() ← EXISTS in runway/core/scheduled_payment_service.py
    └── delay_payment() ← NEEDS TO BE DESIGNED
```

### **Key Design Questions:**
1. **Reserve Allocation Timing**: When should reserves be allocated?
   - At bill approval (immediate staging)?
   - At decision making (Pay Now/Schedule/Delay)?
   - At payment execution (just before payment)?

2. **Decision Queue Management**: How should decisions be processed?
   - Individual processing as decisions are made?
   - Batch processing for multiple decisions?
   - Queue management for delayed decisions?

3. **Service Boundaries**: How should services interact?
   - Console experience → Decision queue → Payment orchestration → Payment execution
   - Reserve allocation → Decision making → Payment execution
   - Batch finalization → Multiple payment executions

4. **Error Handling**: How should failures be handled?
   - Payment execution failures
   - Reserve allocation failures
   - QBO sync failures
   - Batch processing failures
- **Discovery Commands to Run:**
  - `grep -r "approve.*bill" runway/` - Find all bill approval logic
  - `grep -r "decision.*queue" runway/` - Find decision queue usage
  - `grep -r "allocate.*reserve" runway/` - Find reserve allocation patterns
  - `grep -r "schedule.*payment" runway/` - Find payment scheduling patterns
  - `grep -r "PaymentService" runway/` - Find PaymentService usage in runway
  - `grep -r "ScheduledPaymentService" domains/` - Find ADR-001 violations
  - `grep -r "finalize.*decision" runway/` - Find batch finalization logic
- **Files to Read First:**
  - `zzz_fix_backlog/working/ARCHITECTURAL_DECISIONS_BILL_PAYMENT_RESERVES.md` - context
  - `runway/routes/bills.py` - Current bill approval workflow
  - `runway/experiences/console.py` - Console experience service
  - `runway/core/data_orchestrators/decision_console_data_orchestrator.py` - Decision queue
  - `domains/ap/services/payment.py` - Payment execution service
  - `runway/core/scheduled_payment_service.py` - Scheduled payment service
  - `runway/core/reserve_runway.py` - Reserve allocation service
- **Dependencies:** None
- **Verification:** 
  - Clear bill approval → staging → decision → finalization workflow designed
  - Proper reserve allocation timing determined
  - Service boundaries clarified and ADR-001 compliant
  - Console experience properly designed for decision-making
  - Batch finalization workflow designed for all decision types
  - Decision queue management properly designed
- **Definition of Done:**
  - Complete workflow design from bill approval to payment execution
  - Clear service boundaries and responsibilities
  - Proper reserve allocation timing and management
  - Console experience design for decision-making
  - Batch finalization workflow for all decision types
  - ADR-001 compliant architecture
- **Solution Required:** Design comprehensive console payment decision workflow including bill approval, staging mechanism, decision queue management, reserve allocation timing, service boundaries, and batch finalization for "Pay Now", "Schedule", and "Delay" decisions
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

- **Total Tasks:** 4
- **P1 High:** 4 tasks (calculator data flow, digest bulk operations, testing strategy, console payment workflow)
- **Completed:** 0 tasks
- **Remaining:** 4 tasks

**Key Solutioning Patterns:**
- **Task 1**: Data flow analysis and design
- **Task 2**: Comprehensive testing strategy design
- **Task 4**: Console payment workflow design

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
