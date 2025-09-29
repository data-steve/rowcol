# Executable Tasks - Critical Development Blockers

*Consolidated from backlog analysis on 2025-01-27*  
*Status: ✅ READY FOR HANDS-FREE EXECUTION*

## **Task Complexity Curation**

**✅ FULLY SOLVED (6 tasks)** - These tasks have:
- Clear implementation patterns with code examples
- Specific files to fix with exact changes needed
- Complete verification steps with pytest commands
- No "figure out" or "analyze" language
- Ready for execution by any developer

---

## **CRITICAL: Read These Files First**

Before starting any executable tasks, you MUST read these files to understand the system:

### **Architecture Context:**
- `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Complete system architecture
- `docs/build_plan_v5.md` - Current build plan and phase context
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `docs/architecture/ADR-003-multi-tenancy-strategy.md` - Multi-tenancy patterns

## **Context for All Tasks**

**IMPORTANT**: These are critical development blockers that prevent real data implementation and core functionality. They should be completed before moving to new product features.

### **Post-Nuclear Cleanup Context**
- Clean architecture: `Domain Service → SmartSyncService → Raw QBO HTTP Calls`
- No circular dependencies
- Integration model simplified (QBO fields in Business model)
- SmartSync test patterns established
- Database connection fixtures created

### **Critical Success Factors**
- All tasks must align with post-nuclear architecture
- Use new SmartSync patterns and database fixtures
- Address mock violations documented in 008_eliminate_remaining_mock_violations.md
- Solutions must be documented as executable tasks

---

## **Phase 1: Data Orchestrator Pattern Implementation (P0 Critical)**

#### **Task 1: Implement Data Orchestrator Pattern for Tray and Console**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** Establish the architectural foundation for experience services using data orchestrators. Implement Tray (simple) and Console (with state management) to establish the pattern for all other experiences.
- **Files to Fix:**
  - `runway/core/runway_calculator.py` - Refactor to pure calculation service
  - `runway/experiences/tray.py` - Use HygieneTrayDataOrchestrator
  - `runway/experiences/console.py` - Use DecisionConsoleDataOrchestrator
- **Required Changes:**
  - Create `runway/core/data_orchestrators/` directory
  - Implement `HygieneTrayDataOrchestrator` (simple data pulling)
  - Implement `DecisionConsoleDataOrchestrator` (data + state management)
  - Refactor RunwayCalculator to pure calculation service
  - Update Tray and Console services to use orchestrators
  - Remove direct SmartSyncService calls from Tray and Console
- **Pattern to Implement:**
  ```python
  # Tray Orchestrator (Simple)
  class HygieneTrayDataOrchestrator:
      async def get_tray_data(self, business_id: str) -> Dict[str, Any]:
          bills = await self.ap_service.get_bills_with_issues(business_id)
          invoices = await self.ar_service.get_invoices_with_issues(business_id)
          return {"bills": bills, "invoices": invoices}
  
  # Console Orchestrator (With State Management)
  class DecisionConsoleDataOrchestrator:
      async def get_console_data(self, business_id: str) -> Dict[str, Any]:
          bills = await self.ap_service.get_bills_ready_for_decision(business_id)
          invoices = await self.ar_service.get_invoices_ready_for_decision(business_id)
          balances = await self.bank_service.get_balances(business_id)
          decision_queue = await self._get_decision_queue(business_id)
          return {"bills": bills, "invoices": invoices, "balances": balances, "decision_queue": decision_queue}
      
      async def add_decision(self, business_id: str, decision: Dict) -> Dict:
          await self._store_decision(business_id, decision)
          return await self.get_console_data(business_id)
  
  # Update experience services
  class HygieneTrayService:
      def __init__(self, db: Session):
          self.db = db
          self.orchestrator = HygieneTrayDataOrchestrator()
      
      async def get_tray_items(self, business_id: str) -> List[Dict]:
          data = await self.orchestrator.get_tray_data(business_id)
          return data["bills"] + data["invoices"]
  
  class DecisionConsoleService:
      def __init__(self, db: Session):
          self.db = db
          self.orchestrator = DecisionConsoleDataOrchestrator()
      
      async def get_console_data(self, business_id: str) -> Dict[str, Any]:
          return await self.orchestrator.get_console_data(business_id)
      
      async def add_decision(self, business_id: str, decision: Dict) -> Dict[str, Any]:
          return await self.orchestrator.add_decision(business_id, decision)
  ```
- **Dependencies:** None
- **Verification:**
  - Run `grep -r "SmartSyncService" runway/experiences/` - should return no results
  - Run `grep -r "get_.*_for_digest" runway/core/` - should return no results
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest tests/runway/` - should pass without import failures
- **Definition of Done:**
  - All experiences use their specific data orchestrator
  - No direct SmartSyncService calls from experiences
  - RunwayCalculator is pure calculation service
  - No runtime errors from broken method calls
  - Domain separation maintained (ADR-001 compliance)
- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed
- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/core/data_orchestrators/ runway/experiences/`
  - `git commit -m "feat: implement data orchestrator pattern for experience services"`
- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state
- **Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Remove Obsolete Files:** Delete any files that are no longer needed
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references
  - **Verification Cleanup:** Run cleanup verification commands

---

## **Phase 2: Mock Violations & Real Data Implementation (P0 Critical)**

#### **Task 2: Eliminate Mock Violations in Experience Services**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** Experience services still have hardcoded mock data that violates our "no more mocks" commitment. This prevents real data implementation and testing.
- **Files to Fix:**
  - `runway/experiences/test_drive.py` - Mock QBO data violations
  - `sandbox/scenario_runner.py` - Mock QBO data violations
  - `tests/integration/qbo/test_qbo_integration.py` - Mock data violations
- **Required Changes:**
  - Replace mock QBO data with real SmartSyncService calls
  - Use database fixtures from `tests/conftest.py`
  - Implement proper error handling for missing QBO data
- **Pattern to Implement:**
  ```python
  # Instead of: mock_qbo_data = {"bills": [], "invoices": []}
  # Use: 
  from infra.qbo.smart_sync import SmartSyncService
  smart_sync = SmartSyncService(business_id)
  bills = await smart_sync.get_bills()
  invoices = await smart_sync.get_invoices()
  ```
- **Dependencies:** None
- **Verification:** 
  - Run `grep -r "mock.*qbo" runway/experiences/` - should return no results
  - Run `grep -r "mock.*qbo" sandbox/` - should return no results
  - Run `grep -r "mock.*qbo" tests/` - should return no results
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - All mock QBO data replaced with real SmartSyncService calls
  - Experience services use real QBO data
  - Proper error handling for missing QBO data
  - No mock violations remain in experience services
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

#### **Task 2: Implement Real Data in Tray Experience**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** `runway/experiences/tray.py` returns empty lists instead of real data. This is a core user-facing feature that needs real data.
- **Files to Fix:**
  - `runway/experiences/tray.py` - Connect to real domain services
  - `runway/experiences/digest.py` - Connect to real domain services
- **Required Changes:**
  - Connect tray experience to real domain services
  - Use SmartSyncService for QBO data
  - Implement proper data transformation from domain models to experience format
- **Pattern to Implement:**
  ```python
  # Instead of: return []
  # Use:
  from domains.ap.services.bill_service import BillService
  from domains.ar.services.invoice_service import InvoiceService
  
  bill_service = BillService(business_id)
  invoice_service = InvoiceService(business_id)
  
  bills = await bill_service.get_bills()
  invoices = await invoice_service.get_invoices()
  
  return transform_to_tray_format(bills, invoices)
  ```
- **Dependencies:** `Eliminate Mock Violations in Experience Services`
- **Verification:** 
  - Run `grep -r "return \[\]" runway/experiences/` - should return no results
  - Run `grep -r "SmartSyncService" runway/experiences/` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - Tray experience returns real data from domain services
  - Digest experience returns real data from domain services
  - All experience services use SmartSyncService for QBO data
  - No empty list returns in experience services
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

#### **Task 3: Create Comprehensive Test Data Service**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** Tests need real QBO sandbox data instead of hardcoded mocks. This is documented in 008_eliminate_remaining_mock_violations.md as a comprehensive solution.
- **Files to Create:**
  - `infra/qbo/test_data_service.py` - Centralized test data service
  - `tests/fixtures/qbo_data.py` - QBO data fixtures
- **Required Implementation:**
  ```python
  class QBOTestDataService:
      def __init__(self, business_id: str):
          self.smart_sync = SmartSyncService(business_id)
      
      async def get_test_bills(self) -> List[Dict]:
          """Get real QBO sandbox bills for testing."""
          return await self.smart_sync.get_bills()
      
      async def get_test_invoices(self) -> List[Dict]:
          """Get real QBO sandbox invoices for testing."""
          return await self.smart_sync.get_invoices()
      
      def create_mock_business(self) -> Business:
          """Create test business with QBO fields."""
          # Implementation here
  ```
- **Dependencies:** `Implement Real Data in Tray Experience`
- **Verification:** 
  - Run `pytest tests/` - all tests should pass with real QBO data
  - Run `grep -r "mock.*qbo" tests/` - should return no results
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - Centralized test data service created
  - All tests use real QBO sandbox data
  - No mock violations in test files
  - Test data service integrates with SmartSyncService
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

#### **Task 4: Fix Tray Experience Data Implementation**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical
- **Justification:** `runway/experiences/tray.py` returns empty lists instead of real data. This is a core user-facing feature that needs real data.
- **Files to Fix:**
  - `runway/experiences/tray.py` - Connect to real domain services
  - `runway/experiences/digest.py` - Connect to real domain services
- **Required Changes:**
  - Connect tray experience to real domain services
  - Use SmartSyncService for QBO data
  - Implement proper data transformation from domain models to experience format
- **Pattern to Implement:**
  ```python
  # Instead of: return []
  # Use:
  from domains.ap.services.bill_service import BillService
  from domains.ar.services.invoice_service import InvoiceService
  
  bill_service = BillService(business_id)
  invoice_service = InvoiceService(business_id)
  
  bills = await bill_service.get_bills()
  invoices = await invoice_service.get_invoices()
  
  return transform_to_tray_format(bills, invoices)
  ```
- **Dependencies:** `Eliminate Mock Violations in Experience Services`
- **Verification:** 
  - Run `grep -r "return \[\]" runway/experiences/` - should return no results
  - Run `grep -r "SmartSyncService" runway/experiences/` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - Tray experience returns real data from domain services
  - Digest experience returns real data from domain services
  - All experience services use SmartSyncService for QBO data
  - No empty list returns in experience services
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

## **Phase 2: Architecture Cleanup (P1 High)**

#### **Task 5: Refactor Business ID Dependency Injection Pattern**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Current `get_services()` pattern creates over-engineered dependency injection containers that are fragile and inconsistent.
- **Files to Fix:**
  - `runway/routes/` - All route files using `get_services()`
  - `infra/api/routes/` - All route files using `get_services()`
- **Required Changes:**
  - Replace `get_services()` pattern with direct service instantiation
  - Use `business_id` parameter directly in route functions
  - Remove over-engineered dependency injection containers
- **Pattern to Implement:**
  ```python
  # Instead of:
  def get_services(business_id: str = Depends(get_current_business_id)):
      return {"bill_service": BillService(business_id), ...}
  
  # Use:
  @router.get("/bills")
  async def get_bills(business_id: str = Depends(get_current_business_id)):
      bill_service = BillService(business_id)
      return await bill_service.get_bills()
  ```
- **Dependencies:** `Create Comprehensive Test Data Service`
- **Verification:** 
  - Run `grep -r "get_services" runway/routes/` - should return no results
  - Run `grep -r "get_services" infra/api/routes/` - should return no results
  - **Check uvicorn in Cursor terminal** - should be running without errors
- **Definition of Done:**
  - All route files use direct service instantiation
  - No over-engineered dependency injection containers
  - Clean, simple route patterns
  - All tests pass
  - All obsolete files removed
  - All imports cleaned up
  - All references updated

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases

- **Comprehensive Cleanup Requirements:**
  - Remove ALL obsolete files and folders
  - Clean up ALL unused imports and references
  - Update ALL dependent code and test files
  - Verify no broken references anywhere
  - Run cleanup verification commands

---

## **Summary**

- **Total Tasks:** 5
- **P0 Critical:** 4 tasks (mock violations, real data, test data service, tray experience)
- **P1 High:** 1 task (dependency injection refactoring)
- **Completed:** 0 tasks
- **Remaining:** 5 tasks

**Key Success Patterns:**
- Use SmartSyncService for all QBO operations
- Use database fixtures from tests/conftest.py
- Replace mock data with real QBO sandbox data
- Follow post-nuclear architecture patterns

**Critical Success Factors:**
- All tasks must align with post-nuclear architecture
- Use new SmartSync patterns and database fixtures
- Address mock violations comprehensively
- Solutions must be documented as executable tasks

This backlog contains only tasks that are **fully solved and ready for hands-free execution** by any developer familiar with the codebase.
