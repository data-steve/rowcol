# 0_EXECUTABLE_TASKS.md - Firm-First Development

**Status**: 🚀 READY FOR IMMEDIATE EXECUTION  
**Context**: Firm-first CAS strategy, multi-tenant architecture ready  
**Branch**: `feat/firm-first`  
**Updated**: 2025-09-30

---

## **CRITICAL: Read These Files First**

### **Architecture Context (Required for All Tasks):**
- `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Complete system architecture
- `docs/BUILD_PLAN_FIRM_FIRST_V6.0.md` - Current build plan and phase context
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `docs/architecture/ADR-003-multi-tenancy-strategy.md` - Multi-tenancy patterns
- `DEVELOPMENT_STANDARDS.md` - Development standards and anti-patterns

### **Task-Specific Context:**
- Review the specific task document for additional context files
- Understand the current phase and architectural constraints
- Familiarize yourself with the codebase structure and patterns

---

## **Context for All Tasks**

### **Strategic Pivot (2025-09-30)**
- **PRIMARY ICP**: CAS accounting firms (20-100 clients) 
- **SECONDARY ICP**: Individual business owners (Phase 7+)
- **PRIORITY**: Data completeness > Agentic features
- **PRICING**: $50/mo per client (CAS firms), $99/mo (future owners)
- **DISTRIBUTION**: Direct sales to CAS firms (primary), QBO App Store (Phase 7+)

### **Why We Pivoted**
Levi Morehouse (Aiwyn.ai President) validated the problem but identified the blocker:
- ✅ Problem is "10,000% right - real need"  
- ❌ BUT: "Owners won't do the work" (won't maintain data completeness)
- ✅ Solution: CAS firms can ensure data quality and enforce the ritual
- ✅ Pricing: $50/mo per client scales better than $99/mo per owner

### **Architecture Foundation**
- ✅ Multi-tenant ready (`business_id` scoping)
- ✅ Data orchestrator pattern implemented
- ✅ Service boundaries clarified (ADR-001 compliance)
- ✅ SmartSync patterns established
- ✅ Database fixtures created

### **Current State**
- **Phase 0-2**: Complete (foundation ready)
- **Phase 3**: Multi-tenant foundation (ready to start)
- **Phase 4**: Data completeness (bank feeds, missing bills)
- **Phase 5**: Multi-client dashboard
- **Phase 6**: CAS firm pilot features

---

## **CRITICAL WARNINGS FROM PAINFUL LESSONS**

### **NEVER Execute Without Assumption Validation**
- **Task descriptions may be wrong** - always validate against actual codebase
- **Discovery commands are mandatory** - find ALL occurrences, not just initial files
- **Recursive triage is required** - understand context before making changes
- **Comprehensive cleanup is mandatory** - handle all edge cases and dependencies

### **NEVER Do Blind Search-and-Replace**
- **Read broader context** around each occurrence
- **Understand what the method/service/route is doing**
- **Triage each occurrence** - simple replacement vs contextual update vs complete overhaul
- **Plan comprehensive updates** - update method names AND all calls to those methods

### **NEVER Skip Cleanup**
- **Remove obsolete files** - delete files that are no longer needed
- **Clean up imports** - remove unused imports, add missing imports
- **Update references** - fix all broken references and method calls
- **Clean up tests** - update test files that reference changed code

---

## **CRITICAL: Recursive Discovery/Triage Pattern**

**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of patterns mentioned in tasks
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine what it actually does vs what the task assumes:
   - What is this method's real purpose?
   - What are its dependencies and relationships?
   - What would break if we changed it?
   - Is this a false positive or actually relevant?
4. **Map the real system** - understand how things actually work vs how the task assumes they work
5. **Document assumptions vs reality** - write down what you found vs what the task assumed
6. **Plan based on reality** - design solutions based on what actually exists

---

## **Progress Tracking Instructions**

### **Task Status Tracking:**
- `[ ]` - Not started
- `[🔄]` - In progress  
- `[✅]` - Completed
- `[❌]` - Failed/Blocked

**IMPORTANT**: Always update the task status in the document as you work through tasks.

### **Cursor Todo Integration:**
1. **Create Cursor Todo** when starting a task
2. **Update Todo Status** as work progresses
3. **Add Cleanup Todos** for discovered edge cases
4. **Complete Todos** when work is done
5. **Clean Up Todos** when files are deleted

---

## **Git Workflow Instructions**

### **Surgical Commits (Per Task)**
```bash
# After completing each task, commit only the files you modified:
git add [file1.py] [file2.py] [file3.py]
git commit -m "feat: [task-description] - [brief-summary]"

# Example:
git add runway/experiences/tray.py qbo_sandbox_data_examples.md
git commit -m "feat: clean up tray.py - remove data providers, use SmartSyncService"
```

### **Final Merge (After All Tasks)**
```bash
# Switch to main branch
git checkout main

# Merge your cleanup branch
git merge cleanup/[task-name]

# Delete the cleanup branch
git branch -d cleanup/[task-name]
```

---

## **TASK LIST**

**⚠️ IMPORTANT: Do NOT run multiple tasks simultaneously - they have dependencies and will collide!**

**⚠️ IMPORTANT: Use surgical git commits - only commit the files you actually modified for each task!**

---

#### **Task: Implement TestDrive Data Orchestrator**
- **Status**: `[ ]` Not started
- **Priority**: P1 High
- **Justification**: TestDrive experience needs proper data orchestration following established patterns

- **Initial Files to Fix**: (Starting point - NOT comprehensive)
  - `runway/experiences/test_drive.py` - needs data orchestrator integration
  - `runway/core/data_orchestrators/` - needs new TestDriveDataOrchestrator

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find all TestDrive related code
  grep -r "test_drive" . --include="*.py"
  grep -r "TestDrive" . --include="*.py"
  find . -name "*test_drive*" -type f
  grep -r "from.*test_drive" . --include="*.py"
  ```

- **MANDATORY: Recursive Triage Process:**
  1. **For each file found in discovery:**
     - Read the broader context around each occurrence
     - Understand what the method/service/route is doing
     - Determine if it needs simple replacement, contextual update, or complete overhaul
     - Identify all related imports, method calls, and dependencies
  2. **Map the real system:**
     - How do these pieces actually connect?
     - What are the real data flows?
     - What would break if you changed it?
  3. **Plan comprehensive updates:**
     - Create TestDriveDataOrchestrator following existing patterns
     - Update test_drive.py to use the orchestrator
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # Create: runway/core/data_orchestrators/test_drive_data_orchestrator.py
  from runway.core.data_orchestrators.base_data_orchestrator import BaseDataOrchestrator
  from runway.services.calculators.runway_calculator import RunwayCalculator
  from runway.services.calculators.priority_calculator import PriorityCalculator
  
  class TestDriveDataOrchestrator(BaseDataOrchestrator):
      def __init__(self, db: Session, business_id: str):
          super().__init__(db, business_id)
          self.runway_calc = RunwayCalculator(db, business_id)
          self.priority_calc = PriorityCalculator(db, business_id)
      
      def get_test_drive_data(self) -> Dict:
          """Get all data needed for test drive experience."""
          return {
              "runway_data": self.runway_calc.calculate_runway(),
              "priority_data": self.priority_calc.calculate_priorities(),
              "business_context": self._get_business_context()
          }
  ```

- **Required Imports/Changes:**
  - Create: `runway/core/data_orchestrators/test_drive_data_orchestrator.py`
  - Update: `runway/experiences/test_drive.py` to use TestDriveDataOrchestrator
  - Add: Import statements for new orchestrator

- **Dependencies**: None - this is a foundational task

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification**: 
  - Run `grep -r "TestDriveDataOrchestrator" runway/experiences/test_drive.py` - should show usage
  - Run `grep -r "test_drive_data_orchestrator" . --include="*.py"` - should show imports
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - TestDriveDataOrchestrator created following established patterns
  - test_drive.py updated to use orchestrator
  - All imports and references updated
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/core/data_orchestrators/test_drive_data_orchestrator.py runway/experiences/test_drive.py`
  - `git commit -m "feat: implement TestDriveDataOrchestrator - following established patterns"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state

---

#### **Task: Implement Digest Data Orchestrator**
- **Status**: `[ ]` Not started
- **Priority**: P1 High
- **Justification**: Digest experience needs proper data orchestration for bulk processing

- **Initial Files to Fix**: (Starting point - NOT comprehensive)
  - `runway/experiences/digest.py` - needs data orchestrator integration
  - `infra/scheduler/digest_jobs.py` - needs orchestrator integration
  - `runway/core/data_orchestrators/` - needs new DigestDataOrchestrator

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find all digest related code
  grep -r "digest" . --include="*.py"
  grep -r "Digest" . --include="*.py"
  find . -name "*digest*" -type f
  grep -r "from.*digest" . --include="*.py"
  grep -r "digest_jobs" . --include="*.py"
  ```

- **MANDATORY: Recursive Triage Process:**
  1. **For each file found in discovery:**
     - Read the broader context around each occurrence
     - Understand what the method/service/route is doing
     - Determine if it needs simple replacement, contextual update, or complete overhaul
     - Identify all related imports, method calls, and dependencies
  2. **Map the real system:**
     - How do these pieces actually connect?
     - What are the real data flows?
     - What would break if you changed it?
  3. **Plan comprehensive updates:**
     - Create DigestDataOrchestrator following existing patterns
     - Update digest.py to use the orchestrator
     - Update digest_jobs.py to use the orchestrator
     - Handle edge cases and multiple patterns in same file

- **Pattern to Implement:**
  ```python
  # Create: runway/core/data_orchestrators/digest_data_orchestrator.py
  from runway.core.data_orchestrators.base_data_orchestrator import BaseDataOrchestrator
  from runway.services.calculators.runway_calculator import RunwayCalculator
  from runway.services.calculators.priority_calculator import PriorityCalculator
  
  class DigestDataOrchestrator(BaseDataOrchestrator):
      def __init__(self, db: Session, business_id: str):
          super().__init__(db, business_id)
          self.runway_calc = RunwayCalculator(db, business_id)
          self.priority_calc = PriorityCalculator(db, business_id)
      
      def get_digest_data(self) -> Dict:
          """Get all data needed for digest experience."""
          return {
              "runway_data": self.runway_calc.calculate_runway(),
              "priority_data": self.priority_calc.calculate_priorities(),
              "business_context": self._get_business_context()
          }
  ```

- **Required Imports/Changes:**
  - Create: `runway/core/data_orchestrators/digest_data_orchestrator.py`
  - Update: `runway/experiences/digest.py` to use DigestDataOrchestrator
  - Update: `infra/scheduler/digest_jobs.py` to use DigestDataOrchestrator
  - Add: Import statements for new orchestrator

- **Dependencies**: None - this is a foundational task

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification**: 
  - Run `grep -r "DigestDataOrchestrator" runway/experiences/digest.py` - should show usage
  - Run `grep -r "digest_data_orchestrator" . --include="*.py"` - should show imports
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - DigestDataOrchestrator created following established patterns
  - digest.py updated to use orchestrator
  - digest_jobs.py updated to use orchestrator
  - All imports and references updated
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/core/data_orchestrators/digest_data_orchestrator.py runway/experiences/digest.py infra/scheduler/digest_jobs.py`
  - `git commit -m "feat: implement DigestDataOrchestrator - following established patterns"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state

---

#### **Task: Implement QBOMapper for Consistent Field Mapping**
- **Status**: `[ ]` Not started
- **Priority**: P1 High
- **Justification**: Need centralized field mapping to avoid direct QBO field access

- **Initial Files to Fix**: (Starting point - NOT comprehensive)
  - All files with direct QBO field access (TotalAmt, DueDate, VendorRef)
  - `runway/core/data_mappers/` - needs new QBOMapper

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find all direct QBO field access
  grep -r "TotalAmt" . --include="*.py"
  grep -r "DueDate" . --include="*.py"
  grep -r "VendorRef" . --include="*.py"
  grep -r "\.TotalAmt" . --include="*.py"
  grep -r "\.DueDate" . --include="*.py"
  grep -r "\.VendorRef" . --include="*.py"
  ```

- **MANDATORY: Recursive Triage Process:**
  1. **For each file found in discovery:**
     - Read the broader context around each occurrence
     - Understand what the method/service/route is doing
     - Determine if it needs simple replacement, contextual update, or complete overhaul
     - Identify all related imports, method calls, and dependencies
  2. **Map the real system:**
     - How do these pieces actually connect?
     - What are the real data flows?
     - What would break if you changed it?
  3. **Plan comprehensive updates:**
     - Create QBOMapper with centralized field mapping
     - Replace all direct field access with mapper calls
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # Create: runway/core/data_mappers/qbo_mapper.py
  class QBOMapper:
      @staticmethod
      def get_bill_amount(bill_data: Dict) -> float:
          """Get bill amount from QBO data."""
          return bill_data.get('TotalAmt', 0.0)
      
      @staticmethod
      def get_bill_due_date(bill_data: Dict) -> str:
          """Get bill due date from QBO data."""
          return bill_data.get('DueDate', '')
      
      @staticmethod
      def get_vendor_ref(bill_data: Dict) -> str:
          """Get vendor reference from QBO data."""
          return bill_data.get('VendorRef', {}).get('value', '')
  ```

- **Required Imports/Changes:**
  - Create: `runway/core/data_mappers/qbo_mapper.py`
  - Update: All files with direct QBO field access to use QBOMapper
  - Add: Import statements for QBOMapper

- **Dependencies**: None - this is a foundational task

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification**: 
  - Run `grep -r "TotalAmt\|DueDate\|VendorRef" runway/` - should return no results
  - Run `grep -r "QBOMapper" . --include="*.py"` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - QBOMapper created with centralized field mapping
  - All direct QBO field access replaced with mapper calls
  - All imports and references updated
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/core/data_mappers/qbo_mapper.py [all-modified-files]`
  - `git commit -m "feat: implement QBOMapper - centralized field mapping"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state

---

#### **Task: Eliminate Mock Violations in Experience Services**
- **Status**: `[ ]` Not started
- **Priority**: P0 Critical
- **Justification**: Mock violations break trust and prevent real data usage

- **Initial Files to Fix**: (Starting point - NOT comprehensive)
  - `runway/routes/kpis.py` - data quality scoring, sync health, runway trends
  - `runway/experiences/test_drive.py` - mock data
  - `sandbox/scenario_runner.py` - mock data
  - `tests/integration/qbo/test_qbo_integration.py` - mock data

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find all mock violations
  grep -r "return 85.0" . --include="*.py"
  grep -r "return 92.0" . --include="*.py"
  grep -r "return \"stable\"" . --include="*.py"
  grep -r "mock.*qbo" . --include="*.py"
  grep -r "return \[\]" . --include="*.py"
  ```

- **MANDATORY: Recursive Triage Process:**
  1. **For each file found in discovery:**
     - Read the broader context around each occurrence
     - Understand what the method/service/route is doing
     - Determine if it needs simple replacement, contextual update, or complete overhaul
     - Identify all related imports, method calls, and dependencies
  2. **Map the real system:**
     - How do these pieces actually connect?
     - What are the real data flows?
     - What would break if you changed it?
  3. **Plan comprehensive updates:**
     - Replace mock values with real calculations
     - Connect to real domain services via SmartSyncService
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # Replace mock values with real calculations
  def _calculate_data_quality_score(qbo_data: Dict) -> float:
      """Calculate real data quality score based on QBO data."""
      # Real calculation logic here
      return calculated_score
  
  def _calculate_sync_health_score(smart_sync) -> float:
      """Calculate real sync health score."""
      # Real calculation logic here
      return calculated_score
  
  def _calculate_runway_trend(runway_calc: Dict) -> str:
      """Calculate real runway trend analysis."""
      # Real calculation logic here
      return trend_analysis
  ```

- **Required Imports/Changes:**
  - Update: All files with mock violations to use real calculations
  - Add: Import statements for real calculation services
  - Remove: All hardcoded mock values

- **Dependencies**: None - this is a foundational task

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification**: 
  - Run `grep -r "return 85.0\|return 92.0\|return \"stable\"" runway/` - should return no results
  - Run `grep -r "mock.*qbo" runway/experiences/` - should return no results
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - All mock violations eliminated
  - Real calculations implemented
  - All imports and references updated
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add [all-modified-files]`
  - `git commit -m "feat: eliminate mock violations - implement real calculations"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state

---

#### **Task: Refactor Business ID Dependency Injection Pattern**
- **Status**: `[ ]` Not started
- **Priority**: P1 High
- **Justification**: Over-engineered dependency injection containers are fragile and don't scale

- **Initial Files to Fix**: (Starting point - NOT comprehensive)
  - All route files using `get_services()` pattern
  - `infra/database/dependency_injection.py` - needs new pattern

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find all get_services usage
  grep -r "get_services" . --include="*.py"
  grep -r "def get_services" . --include="*.py"
  grep -r "from.*get_services" . --include="*.py"
  ```

- **MANDATORY: Recursive Triage Process:**
  1. **For each file found in discovery:**
     - Read the broader context around each occurrence
     - Understand what the method/service/route is doing
     - Determine if it needs simple replacement, contextual update, or complete overhaul
     - Identify all related imports, method calls, and dependencies
  2. **Map the real system:**
     - How do these pieces actually connect?
     - What are the real data flows?
     - What would break if you changed it?
  3. **Plan comprehensive updates:**
     - Replace get_services() with direct business_id injection
     - Update all route files to use new pattern
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # Replace over-engineered dependency container
  # ❌ WRONG: Over-engineered dependency container
  def get_services(db: Session, business_id: str):
      return {"bill_service": BillService(db, business_id), ...}
  
  # ✅ CORRECT: Direct business_id injection
  @router.get("/bills")
  async def get_bills(business_id: str = Depends(get_current_business_id)):
      service = BillService(db, business_id)
  ```

- **Required Imports/Changes:**
  - Update: All route files using get_services() pattern
  - Create: `infra/database/dependency_injection.py` with new pattern
  - Add: Import statements for new pattern

- **Dependencies**: None - this is a foundational task

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification**: 
  - Run `grep -r "get_services" runway/routes/` - should return no results
  - Run `grep -r "get_current_business_id" . --include="*.py"` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - All get_services() usage eliminated
  - Direct business_id injection implemented
  - All imports and references updated
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add [all-modified-files]`
  - `git commit -m "feat: refactor dependency injection - direct business_id injection"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state

---

**Status**: Ready for immediate execution  
**Next Action**: Start with Task 1 (TestDrive Data Orchestrator)  
**Branch**: `feat/firm-first`  
**Updated**: 2025-09-30
