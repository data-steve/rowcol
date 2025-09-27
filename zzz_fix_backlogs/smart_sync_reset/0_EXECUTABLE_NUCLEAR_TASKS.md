# Executable Nuclear Tasks - QBO Architecture Reset

*Generated from nuclear cleanup analysis on 2025-01-27*  
*Status: ✅ READY FOR HANDS-FREE EXECUTION*

## **Task Complexity Curation**

**✅ FULLY SOLVED (7 tasks)** - These tasks have:
- Clear implementation patterns with code examples
- Specific files to fix with exact changes needed
- Complete verification steps with pytest commands
- No "figure out" or "analyze" language
- Ready for execution by any developer

---

## **Context for All Tasks**

**CRITICAL DISCOVERY**: The current QBO architecture is a complete mess with 3 duplicate implementations, circular dependencies, and 4000+ lines of mixed code. The application won't start due to import errors.

**NUCLEAR SOLUTION**: Delete everything QBO-related and rebuild cleanly with proper separation of concerns.

**TARGET ARCHITECTURE**: `Domain Service → SmartSyncService → Raw QBO HTTP Calls`

**Key Principles**:
- **Domain services** handle their own CRUD operations
- **SmartSyncService** provides resilience (retry, dedup, rate limiting, caching)
- **Raw QBO HTTP calls** are just HTTP requests to QBO endpoints
- **No circular dependencies** - clean dependency flow

## **Development Environment Setup**

**IMPORTANT**: Start your development session with:
```bash
poetry shell
```
This activates the virtual environment and saves you from typing `poetry run` before every command.

**CRITICAL WARNINGS FROM PAINFUL LESSONS:**
- **NEVER** delete files without checking all references first - circular imports will break everything
- **ALWAYS** test uvicorn startup after import changes - silent failures are the worst
- **ALWAYS** run verification commands after each change - don't trust that it worked
- **ALWAYS** check existing imports before making changes - don't assume what's there

---

## **Phase 1: Nuclear Cleanup (P0 Critical)**

#### **Task 1: Delete Circular Dependency Mess**
- **Status:** `[x]` ✅ COMPLETED
- **Priority:** P0 Critical
- **Justification:** Delete all the circular dependency files that are preventing the application from starting. These files contain mixed responsibilities and circular imports.
- **Files to Delete:**
  - `domains/qbo/client.py` (2105 lines of mixed mess)
  - `domains/qbo/data_service.py` (92 lines, redundant with SmartSyncService)
  - `domains/qbo/service.py` (423 lines, redundant with SmartSyncService)
  - `domains/integrations/qbo/` (1800+ lines, complete duplicate directory)
  - `domains/qbo/interfaces.py` (irrelevant)
  - `domains/qbo/scenario_runner.py` (moving to sandbox service)
  - `domains/qbo/create_sandbox_data.py` (moving to sandbox service)
  - `domains/qbo/get_qbo_tokens.py` (redundant)
  - `domains/qbo/dev_tokens.json` (development only)
- **Pre-deletion Verification:**
  - Run `grep -r "domains/qbo/client" . --include="*.py"` - check for references
  - Run `grep -r "domains/qbo/data_service" . --include="*.py"` - check for references
  - Run `grep -r "domains/qbo/service" . --include="*.py"` - check for references
  - Run `grep -r "domains/integrations/qbo" . --include="*.py"` - check for references
- **Dependencies:** None
- **Verification:** 
  - Run `ls domains/qbo/` - should show only: `auth.py`, `setup.py`, `config.py`, `health.py`, `models.py`
  - Run `ls domains/integrations/` - should show no `qbo/` directory
  - Run `uvicorn main:app --reload` - should start without import errors
- **Git Commit:**
  - Run `git add . && git commit -m "feat: nuclear cleanup - delete circular dependency files"`
- **Definition of Done:**
  - All circular dependency files are deleted
  - No broken references or imports
  - Application starts without import errors
  - Clean foundation for rebuilding

---

## **Phase 2: Build Clean Foundation (P0 Critical)**

#### **Task 2: Create Raw QBO HTTP Client**
- **Status:** `[x]` ✅ COMPLETED
- **Priority:** P0 Critical
- **Justification:** Create a clean raw QBO HTTP client that only makes HTTP calls to QBO endpoints. No business logic, no orchestration, just HTTP calls.
- **File to Create:**
  - `infra/qbo/client.py` - Raw QBO HTTP client
- **Required Implementation:**
  ```python
  class QBORawClient:
      def __init__(self, business_id: str, realm_id: str):
          self.business_id = business_id
          self.realm_id = realm_id
          self.base_url = qbo_config.api_url
      
      async def get_bills_from_qbo(self, due_days: int = 30) -> Dict:
          """Raw HTTP call to QBO bills endpoint."""
          # Just HTTP call, no business logic
          
      async def create_payment_in_qbo(self, payment_data: Dict) -> Dict:
          """Raw HTTP call to QBO payment endpoint."""
          # Just HTTP call, no business logic
          
      async def get_invoices_from_qbo(self, aging_days: int = 30) -> Dict:
          """Raw HTTP call to QBO invoices endpoint."""
          # Just HTTP call, no business logic
          
      async def get_customers_from_qbo(self) -> Dict:
          """Raw HTTP call to QBO customers endpoint."""
          # Just HTTP call, no business logic
          
      async def get_vendors_from_qbo(self) -> Dict:
          """Raw HTTP call to QBO vendors endpoint."""
          # Just HTTP call, no business logic
          
      async def get_accounts_from_qbo(self) -> Dict:
          """Raw HTTP call to QBO accounts endpoint."""
          # Just HTTP call, no business logic
          
      async def get_company_info_from_qbo(self) -> Dict:
          """Raw HTTP call to QBO company info endpoint."""
          # Just HTTP call, no business logic
  ```
- **Dependencies:** `Delete Circular Dependency Mess`
- **Verification:** 
  - Run `poetry run python -c "from infra.qbo.client import QBORawClient; print('QBORawClient import works')"`
  - Run `uvicorn main:app --reload` - should start without import errors
- **Git Commit:**
  - Run `git add . && git commit -m "feat: create QBORawClient for raw QBO HTTP calls"`
- **Definition of Done:**
  - Raw QBO HTTP client created with all necessary methods
  - No business logic, just HTTP calls
  - Clean, simple interface
  - Ready for SmartSyncService integration

---

#### **Task 3: Move SmartSyncService to infra/qbo/ and Enhance with QBO Operations**
- **Status:** `[x]` ✅ COMPLETED
- **Priority:** P0 Critical
- **Justification:** Move SmartSyncService to infra/qbo/ since it's QBO-specific orchestration, not general job infrastructure. Then enhance it to handle QBO operations with resilience (retry, dedup, rate limiting, caching).
- **Files to Move/Update:**
  - Move `infra/jobs/smart_sync.py` → `infra/qbo/smart_sync.py`
  - Update SmartSyncService to depend on `infra/jobs/` for general utilities
  - Add QBO operation handling methods
- **Required Implementation:**
  ```python
  class SmartSyncService:
      async def execute_qbo_call(self, operation: str, *args, **kwargs) -> Any:
          """Execute any QBO operation with resilience."""
          # 1. Check rate limits
          # 2. Check for duplicates
          # 3. Execute with retry
          # 4. Cache if needed
          # 5. Return result
          
          qbo_client = QBORawClient(self.business_id, realm_id)
          return await self._execute_with_retry(
              getattr(qbo_client, operation), *args, **kwargs
          )
  ```
- **Dependencies:** `Create Raw QBO HTTP Client`
- **Verification:** 
  - Run `poetry run python -c "from infra.qbo.smart_sync import SmartSyncService; print('SmartSyncService import works')"`
  - Run `uvicorn main:app --reload` - should start without import errors
- **Git Commit:**
  - Run `git add . && git commit -m "feat: move SmartSyncService to infra/qbo/ with QBO orchestration"`
- **Definition of Done:**
  - SmartSyncService enhanced with QBO operation handling
  - Resilience features working (retry, dedup, rate limiting, caching)
  - Clean interface for domain services
  - Ready for domain service integration

---

## **Phase 3: Fix Import Errors (P0 Critical)**

#### **Task 4: Fix Import Errors After Foundation is Built**
- **Status:** `[x]` ✅ COMPLETED
- **Priority:** P0 Critical
- **Justification:** After building the foundation (raw QBO client + SmartSyncService), fix all import errors by updating imports to use the new services.
- **CRITICAL PROCESS - NO BLIND SEARCH-REPLACE:**
  1. **PRIORITIZE CORE APPLICATION CODE** over tests and sandbox files
  2. **Search for all cases** using grep commands
  3. **For each file found:**
     - **Read the broader context** to understand what the file/method/route is doing
     - **Identify ALL cases** in the file that need updating (not just the first one)
     - **Understand the business logic** to know if it needs significant overhaul
     - **Make comprehensive updates** that align with new architecture
     - **Handle edge cases** and multiple patterns in the same file
  4. **Test after each file** to ensure changes work correctly
  5. **COMMIT AFTER EACH MAJOR CHANGE** to prevent data loss
  6. **SKIP TEST FILES** for now - focus on getting core application imports working first
- **Search Commands to Run:**
  - `grep -r "from domains.qbo.smart_sync" . --include="*.py"`
  - `grep -r "from domains.qbo.client" . --include="*.py"`
  - `grep -r "from domains.qbo.data_service" . --include="*.py"`
  - `grep -r "from domains.qbo.service" . --include="*.py"`
  - `grep -r "from domains.integrations.qbo" . --include="*.py"`
  - `grep -r "from infra.jobs import SmartSyncService" . --include="*.py"`
- **Required Changes:**
  - Replace: `from domains.qbo.smart_sync import SmartSyncService`
  - With: `from infra.qbo.smart_sync import SmartSyncService`
  - Replace: `from domains.qbo.client import QBOClient`
  - With: `from infra.qbo.client import QBORawClient`
  - Replace: `from infra.jobs import SmartSyncService`
  - With: `from infra.qbo.smart_sync import SmartSyncService`
- **Dependencies:** `Move SmartSyncService to infra/qbo/ and Enhance with QBO Operations`
- **Verification:** 
  - Run `grep -r "from domains.qbo" . --include="*.py"` - should return no results
  - Run `grep -r "from domains.integrations.qbo" . --include="*.py"` - should return no results
  - Run `grep -r "from infra.jobs import SmartSyncService" . --include="*.py"` - should return no results
  - Run `grep -r "from infra.qbo.smart_sync import SmartSyncService" . --include="*.py"` - should show new imports
  - Run `uvicorn main:app --reload` - should start without import errors
- **Definition of Done:**
  - All import errors are fixed
  - All imports use correct paths
  - Application starts without import errors
  - Clean foundation for rebuilding

---

## **Phase 4: Update Documentation (P0 Critical)**

#### **Task 5: Update ADR-005 to Reflect Nuclear Architecture**
- **Status:** `[x]` ✅ COMPLETED
- **Priority:** P0 Critical
- **Justification:** ADR-005 currently describes the old architecture with QBOClient. It needs to be updated to reflect the new nuclear architecture: Domain Service → SmartSyncService → Raw QBO HTTP Calls.
- **File to Fix:**
  - `docs/architecture/ADR-005-qbo-api-strategy.md` - Update to reflect nuclear architecture
- **Required Changes:**
  - Update dependency direction to: `Domain Service → SmartSyncService → Raw QBO HTTP Calls`
  - Remove QBOClient references
  - Update service responsibilities to reflect new architecture
  - Update API call patterns to show domain services handling their own CRUD
  - Update code examples to show correct patterns
- **New Architecture Pattern:**
  ```python
  # Domain Service Pattern
  class BillService:
      def __init__(self, business_id: str):
          self.smart_sync = SmartSyncService(business_id)
      
      async def get_bills(self, due_days: int = 30) -> List[Bill]:
          """Get bills - domain handles its own CRUD."""
          qbo_data = await self.smart_sync.execute_qbo_call(
              "get_bills_from_qbo", due_days=due_days
          )
          # Transform QBO data to domain models
          return [Bill.from_qbo_data(item) for item in qbo_data]
  ```
- **Dependencies:** `Fix Import Errors After Foundation is Built`
- **Verification:** 
  - Run `grep -r "QBOClient" docs/architecture/ADR-005-qbo-api-strategy.md` - should return no results
  - Run `grep -r "Domain Service → SmartSyncService → Raw QBO HTTP Calls" docs/architecture/ADR-005-qbo-api-strategy.md` - should show the new pattern
  - Run `uvicorn main:app --reload` - should start without import errors
- **Definition of Done:**
  - ADR-005 reflects the new nuclear architecture
  - No references to QBOClient or old patterns
  - Clear documentation of new service responsibilities
  - Code examples show correct patterns
  - Architecture is consistent with implementation

---

## **Phase 5: Update Domain Services (P1 High)**

#### **Task 6: Update Domain Services to Use SmartSyncService**
- **Status:** `[x]` ✅ COMPLETED
- **Priority:** P1 High
- **Justification:** Update domain services to call SmartSyncService directly for QBO operations, handling their own CRUD operations.
- **Files to Fix:**
  - `domains/ap/services/bill_service.py` - Update to use SmartSyncService
  - `domains/ar/services/invoice_service.py` - Update to use SmartSyncService
  - `domains/ar/services/customer_service.py` - Update to use SmartSyncService
  - `domains/ar/services/vendor_service.py` - Update to use SmartSyncService
- **Required Pattern:**
  ```python
  class BillService:
      def __init__(self, business_id: str):
          self.smart_sync = SmartSyncService(business_id)
      
      async def get_bills(self, due_days: int = 30) -> List[Bill]:
          """Get bills - domain handles its own CRUD."""
          qbo_data = await self.smart_sync.execute_qbo_call(
              "get_bills_from_qbo", due_days=due_days
          )
          # Transform QBO data to domain models
          return [Bill.from_qbo_data(item) for item in qbo_data]
      
      async def create_payment(self, bill_id: str, payment_data: Dict) -> Payment:
          """Create payment - domain handles its own CRUD."""
          qbo_result = await self.smart_sync.execute_qbo_call(
              "create_payment_in_qbo", payment_data=payment_data
          )
          # Transform and save to local DB
          return Payment.from_qbo_data(qbo_result)
  ```
- **Dependencies:** `Fix Import Errors After Foundation is Built`
- **Verification:** 
  - Run `grep -r "SmartSyncService" domains/` - should show new imports
  - Run `uvicorn main:app --reload` - should start without import errors
  - Run `pytest tests/domains/` - domain tests should pass
- **Definition of Done:**
  - All domain services use SmartSyncService for QBO operations
  - Domain services handle their own CRUD operations
  - Clean separation of concerns
  - All tests pass

---

#### **Task 7: Update Route Files to Use Domain Services**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Update route files to use domain services instead of direct QBO calls, following ADR-001 separation.
- **Files to Fix:**
  - `runway/routes/bills.py` - Update to use BillService
  - `runway/routes/invoices.py` - Update to use InvoiceService
  - `runway/routes/customers.py` - Update to use CustomerService
  - `runway/routes/vendors.py` - Update to use VendorService
- **Required Pattern:**
  ```python
  @router.get("/bills")
  async def get_bills(business_id: str = Depends(get_business_id)):
      bill_service = BillService(business_id)
      bills = await bill_service.get_bills(due_days=30)
      return bills
  ```
- **Dependencies:** `Update Domain Services to Use SmartSyncService`
- **Verification:** 
  - Run `grep -r "QBORawClient" runway/routes/` - should return no results
  - Run `grep -r "SmartSyncService" runway/routes/` - should return no results
  - Run `uvicorn main:app --reload` - should start without import errors
  - Run `pytest tests/runway/` - runway tests should pass
- **Definition of Done:**
  - All route files use domain services
  - Clean separation between routes and QBO operations
  - All tests pass
  - Architecture follows ADR-001

---

## **Phase 6: Integration Model Simplification (P1 High)**

#### **Task 8: Remove Integration Model and Add QBO Fields to Business**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Since QBO is mandatory and the only integration, we don't need a complex Integration table. Add QBO connection details directly to the Business model for simplicity and performance.
- **Files to Modify:**
  - `domains/core/models/business.py` - Add QBO connection fields
  - `domains/core/models/__init__.py` - Remove Integration import
  - `infra/qbo/integration_models.py` - Delete this file
  - All files importing from `infra.qbo.integration_models` - Update to use Business model
- **Required Changes to Business Model:**
  ```python
  class Business:
      # ... existing fields ...
      qbo_realm_id = Column(String(255), nullable=True)
      qbo_access_token = Column(String(500), nullable=True) 
      qbo_refresh_token = Column(String(500), nullable=True)
      qbo_connected_at = Column(DateTime, nullable=True)
      qbo_status = Column(String(50), default="disconnected")
      qbo_environment = Column(String(50), default="sandbox")
  ```
- **Dependencies:** `Update Route Files to Use Domain Services`
- **Verification:** 
  - Run `grep -r "from infra.qbo.integration_models" . --include="*.py"` - should return no results
  - Run `grep -r "Integration" domains/core/models/__init__.py` - should return no results
  - Run `uvicorn main:app --reload` - should start without import errors
  - Run `pytest tests/domains/` - domain tests should pass
- **Git Commit:**
  - Run `git add . && git commit -m "feat: simplify integration model - add QBO fields to Business"`
- **Definition of Done:**
  - Integration model removed entirely
  - QBO connection fields added to Business model
  - All references updated to use Business model
  - Application starts without import errors
  - Cleaner, simpler data model

---

#### **Task 9: Comprehensive Integration Model Cleanup**
- **Status:** `[ ]` Not started
- **Priority:** P1 High
- **Justification:** Integration model references are scattered throughout the entire codebase - tests, routes, services, models, configs, and documentation. All must be cleaned up to prevent broken references.
- **CRITICAL PROCESS - COMPREHENSIVE CLEANUP:**
  1. **Search for ALL Integration references** using multiple grep patterns
  2. **Categorize by file type** (tests, routes, services, models, configs, docs)
  3. **Update each category systematically** to use Business model
  4. **Verify no references remain** anywhere in the codebase
  5. **Test thoroughly** after each category cleanup
- **Search Commands to Run:**
  - `grep -r "from infra.qbo.integration_models" . --include="*.py"`
  - `grep -r "from domains.core.models.integration" . --include="*.py"`
  - `grep -r "Integration\." . --include="*.py"`
  - `grep -r "integration\." . --include="*.py"`
  - `grep -r "Integration" . --include="*.py" | grep -v "integration_models"`
  - `grep -r "integration" . --include="*.py" | grep -v "integration_models"`
- **Files to Update by Category:**
  - **Test Files:** All files in `tests/` directory
  - **Route Files:** All files in `runway/routes/` and `infra/api/routes/`
  - **Service Files:** All files in `domains/*/services/` and `runway/*/services/`
  - **Model Files:** All files in `domains/core/models/`
  - **Config Files:** All files in `infra/qbo/` and `domains/qbo/`
  - **Documentation:** All files in `docs/` directory
- **Required Pattern Updates:**
  ```python
  # Instead of: from infra.qbo.integration_models import Integration
  # Use: from domains.core.models.business import Business
  
  # Instead of: integration.realm_id
  # Use: business.qbo_realm_id
  
  # Instead of: integration.access_token
  # Use: business.qbo_access_token
  
  # Instead of: integration.status
  # Use: business.qbo_status
  ```
- **Dependencies:** `Remove Integration Model and Add QBO Fields to Business`
- **Verification:** 
  - Run `grep -r "from infra.qbo.integration_models" . --include="*.py"` - should return no results
  - Run `grep -r "from domains.core.models.integration" . --include="*.py"` - should return no results
  - Run `grep -r "Integration\." . --include="*.py"` - should return no results
  - Run `grep -r "integration\." . --include="*.py"` - should return no results
  - Run `uvicorn main:app --reload` - should start without import errors
  - Run `pytest tests/` - all tests should pass
- **Git Commit:**
  - Run `git add . && git commit -m "feat: comprehensive cleanup - remove all Integration model references"`
- **Definition of Done:**
  - No Integration model references anywhere in codebase
  - All QBO references use Business model fields
  - All tests pass
  - Application starts without import errors
  - Clean, consistent data access patterns

---

## **Success Criteria**

### **System Health**
- ✅ Application starts without import errors
- ✅ All tests can run without import errors
- ✅ No broken functionality

### **Architecture Compliance**
- ✅ All QBO operations go through SmartSyncService
- ✅ Domain services handle their own CRUD operations
- ✅ Clean separation between orchestration and integration
- ✅ No circular dependencies

### **Code Quality**
- ✅ No architectural violations
- ✅ Consistent patterns across all files
- ✅ Clear separation of concerns
- ✅ Maintainable codebase

---

## **Summary**

- **Total Tasks:** 9
- **P0 Critical:** 5 tasks (nuclear cleanup + foundation + import fixes + documentation)
- **P1 High:** 4 tasks (domain service updates + integration simplification)
- **Completed:** 6 tasks (Tasks 1-6)
- **Remaining:** 3 tasks (Tasks 7-9)
- **Status:** ✅ **READY FOR HANDS-FREE EXECUTION**

**Quick Reference Commands:**
```bash
# Check for old QBO imports
grep -r "from domains.qbo" . --include="*.py"

# Check for old integrations imports
grep -r "from domains.integrations.qbo" . --include="*.py"

# Check for Integration model references
grep -r "from infra.qbo.integration_models" . --include="*.py"
grep -r "from domains.core.models.integration" . --include="*.py"
grep -r "Integration\." . --include="*.py"
grep -r "integration\." . --include="*.py"

# Test application startup
uvicorn main:app --reload

# Run tests
pytest
```

**THOROUGH VERIFICATION CHECKLIST:**
- [ ] After EACH file change, run `uvicorn main:app --reload` to test startup
- [ ] After EACH import change, run `pytest` to test functionality
- [ ] Before deleting ANY file, run `grep -r "filename" . --include="*.py"` to check references
- [ ] After EACH service replacement, verify the new service actually works
- [ ] Test user actions to ensure they work immediately
- [ ] Test background syncs to ensure they use SmartSyncService correctly

**Key Service Responsibilities:**
- **SmartSyncService** (`infra/qbo/smart_sync.py`): Central orchestration for ALL QBO interactions. Encapsulates sync timing, caching, user activity tracking, rate limiting, retry logic, and deduplication.
- **QBORawClient** (`infra/qbo/client.py`): Raw HTTP calls to QBO endpoints only. No business logic, no orchestration.
- **Domain Services** (`domains/*/services/`): Handle their own CRUD operations and business logic.

**CRITICAL ARCHITECTURE PRINCIPLE:**
- **Domain services** handle their own business logic and CRUD
- **SmartSyncService** provides resilience infrastructure
- **Raw QBO client** just makes HTTP calls
- **No circular dependencies** - clean dependency flow

This backlog contains only tasks that are **fully solved and ready for hands-free execution** by any developer familiar with the codebase.
