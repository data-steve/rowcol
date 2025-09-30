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

#### **Task 1.3: Implement QBOMapper for Consistent Field Mapping**
- **Status**: `[ ]` Ready to execute
- **Priority**: P1 High  
- **Effort**: 12h
- **Files**:
  - Create: `runway/core/data_mappers/qbo_mapper.py`
  - Update: All files with direct QBO field access
- **Pattern**: Centralized field mapping service
- **Verification**: `grep -r "TotalAmt\|DueDate\|VendorRef" runway/` should return no results

#### **Task 1.4: Eliminate Mock Violations in Experience Services**
- **Status**: `[ ]` Ready to execute
- **Priority**: P0 Critical
- **Effort**: 12h
- **Files**:
  - Update: `runway/routes/kpis.py` (data quality scoring, sync health, runway trends)
  - Update: `runway/experiences/test_drive.py`
  - Update: `sandbox/scenario_runner.py` 
  - Update: `tests/integration/qbo/test_qbo_integration.py`
- **Pattern**: Replace all hardcoded mock values with real calculations
- **Specific Mocks to Fix**:
  - `_calculate_data_quality_score()` - return 85.0 → real calculation
  - `_calculate_sync_health_score()` - return 92.0 → real calculation  
  - `_calculate_runway_trend()` - return "stable" → real analysis
- **Verification**: `grep -r "return 85.0\|return 92.0\|return \"stable\"" runway/` should return no results

#### **Task 1.5: Implement Real Data in Tray Experience**
- **Status**: `[ ]` Ready to execute
- **Priority**: P0 Critical
- **Effort**: 4h
- **Files**:
  - Update: `runway/experiences/tray.py`
  - Update: `runway/experiences/digest.py`
- **Pattern**: Connect to real domain services via SmartSyncService
- **Verification**: `grep -r "return \[\]" runway/experiences/` should return no results

#### **Task 1.6: Refactor Business ID Dependency Injection Pattern**
- **Status**: `[ ]` Ready to execute
- **Priority**: P1 High
- **Effort**: 6h
- **Files**:
  - Update: All route files using `get_services()` pattern
  - Create: `infra/database/dependency_injection.py`
- **Pattern**: Replace over-engineered `get_services()` with direct `business_id` injection
- **Anti-Pattern to Fix**:
  ```python
  # ❌ WRONG: Over-engineered dependency container
  def get_services(db: Session, business_id: str):
      return {"bill_service": BillService(db, business_id), ...}
  ```
- **Correct Pattern**:
  ```python
  # ✅ CORRECT: Direct business_id injection
  @router.get("/bills")
  async def get_bills(business_id: str = Depends(get_current_business_id)):
      service = BillService(db, business_id)
  ```
- **Verification**: `grep -r "get_services" runway/routes/` should return no results

---

### **PHASE 2: Multi-Tenant Foundation (P0 Critical) - 40h**

#### **Task 2.1: Add Firm Models**
- **Status**: `[ ]` Ready to execute
- **Priority**: P0 Critical
- **Effort**: 16h
- **Files**:
  - Create: `domains/core/models/firm.py`
  - Create: `domains/core/models/firm_staff.py`
  - Update: `domains/core/models/business.py` (add firm_id)
  - Create: Alembic migration
- **Pattern**: Firm → Client hierarchy with nullable firm_id
- **Verification**: Database migration runs successfully

#### **Task 2.2: Firm-Level Authentication & RBAC**
- **Status**: `[ ]` Ready to execute
- **Priority**: P0 Critical
- **Effort**: 12h
- **Files**:
  - Update: `infra/auth/auth.py`
  - Update: All route files for firm context
- **Pattern**: Extract firm_id from JWT, filter by firm_id → client_ids
- **Verification**: Firm staff can only access assigned clients

#### **Task 2.3: Firm-Level Routes**
- **Status**: `[ ]` Ready to execute
- **Priority**: P0 Critical
- **Effort**: 12h
- **Files**:
  - Create: `runway/routes/firm_dashboard.py`
  - Create: `runway/routes/firm_clients.py`
- **Endpoints**:
  - `GET /firms/{firm_id}/clients` - List all clients
  - `GET /firms/{firm_id}/dashboard` - Batch runway view
  - `GET /firms/{firm_id}/data-quality` - Completeness scores
  - `POST /firms/{firm_id}/clients` - Add new client
- **Verification**: All endpoints return firm-scoped data

---

### **PHASE 3: Data Completeness (P0 Critical) - 60h**

#### **Task 3.1: Bank Feed Integration (Plaid)**
- **Status**: `[ ]` Ready to execute
- **Priority**: P0 Critical
- **Effort**: 40h
- **Files**:
  - Create: `infra/plaid/plaid_client.py`
  - Create: `domains/bank/services/bank_feed_service.py`
  - Update: `domains/bank/models/bank_transaction.py`
- **Features**:
  - Plaid Link for bank connection
  - Real-time bank transaction sync
  - Match bank transactions to QBO bills
  - Missing bill detection workflow
- **Verification**: Bank transactions sync and match to QBO bills

#### **Task 3.2: Point of Sale Integration**
- **Status**: `[ ]` Ready to execute
- **Priority**: P1 High
- **Effort**: 20h
- **Files**:
  - Create: `infra/pos/square_client.py`
  - Create: `domains/analytics/services/payroll_estimator.py`
- **Features**:
  - Square API integration
  - Payroll estimation from sales patterns
  - Data quality scoring per client
- **Verification**: POS data feeds into payroll estimates

---

### **PHASE 4: Multi-Client Dashboard (P1 High) - 50h**

#### **Task 4.1: Batch Runway View**
- **Status**: `[ ]` Ready to execute
- **Priority**: P1 High
- **Effort**: 30h
- **Files**:
  - Create: `runway/experiences/firm_dashboard.py`
  - Create: `runway/core/data_orchestrators/firm_dashboard_orchestrator.py`
- **Features**:
  - List all clients with runway status
  - Prioritize by runway risk (red/yellow/green)
  - Show data quality score per client
  - Filter by risk level, data quality
  - Client detail view with navigation
- **Verification**: Dashboard loads <2s for 50 clients

#### **Task 4.2: Firm-Level Analytics**
- **Status**: `[ ]` Ready to execute
- **Priority**: P1 High
- **Effort**: 20h
- **Files**:
  - Create: `runway/services/firm_analytics.py`
  - Create: `runway/routes/firm_analytics.py`
- **Features**:
  - Total clients at risk (runway < 30 days)
  - Average data completeness across clients
  - Export client list with runway status
  - Weekly firm digest (all clients summary)
- **Verification**: Analytics provide actionable insights

---

### **PHASE 5: CAS Firm Pilot Features (P1 High) - 30h**

#### **Task 5.1: Firm Onboarding Flow**
- **Status**: `[ ]` Ready to execute
- **Priority**: P1 High
- **Effort**: 15h
- **Files**:
  - Create: `runway/experiences/firm_onboarding.py`
  - Create: `runway/routes/firm_onboarding.py`
- **Features**:
  - Firm signup and setup
  - Add staff members with roles
  - Connect first client QBO account
  - Guided tour of firm dashboard
- **Verification**: New firm can onboard and add clients

#### **Task 5.2: White-Label Basics**
- **Status**: `[ ]` Ready to execute
- **Priority**: P1 High
- **Effort**: 15h
- **Files**:
  - Create: `infra/branding/firm_branding.py`
  - Update: All client-facing reports
- **Features**:
  - Upload firm logo
  - Customize primary color
  - Custom domain (optional)
  - Client-facing reports with firm branding
- **Verification**: Reports show firm branding

---

## **🔧 SOLUTIONING TASKS**

**See `SOLUTIONING_TASKS.md` for tasks that need analysis before execution.**

---

## **📊 SUCCESS METRICS**

### **Phase 1-2 (Weeks 1-4)**
- [ ] All experience services use real data
- [ ] Multi-tenant architecture working
- [ ] Firm dashboard loads <2s for 50 clients
- [ ] No mock violations remain
- [ ] Business ID dependency injection refactored

### **Phase 3-4 (Weeks 5-8)**
- [ ] Bank feed integration live (Plaid)
- [ ] Missing bill detection accurate (>90%)
- [ ] Data quality scoring implemented
- [ ] Multi-client analytics working

### **Phase 5 (Weeks 9-10)**
- [ ] 3-5 CAS firms ready to pilot
- [ ] Firm onboarding flow complete
- [ ] White-label branding working

### **Pilots (3 months)**
- [ ] 5-10 CAS firms signed
- [ ] 100-500 clients under management
- [ ] $5k-$25k MRR ($60k-$300k ARR)
- [ ] 85%+ data completeness across clients
- [ ] <10% churn rate for CAS firms

---

## **🚀 EXECUTION READINESS**

### **Ready to Start Immediately**
- ✅ All executable tasks have clear patterns
- ✅ All files and changes specified
- ✅ Verification commands provided
- ✅ Dependencies mapped
- ✅ Success criteria defined

### **Architecture Foundation**
- ✅ Multi-tenant ready (`business_id` scoping)
- ✅ Data orchestrator pattern implemented
- ✅ Service boundaries clarified (ADR-001 compliance)
- ✅ SmartSync patterns established
- ✅ Database fixtures created

### **Strategic Alignment**
- ✅ Firm-first CAS strategy documented
- ✅ Data completeness prioritized over AI features
- ✅ Multi-client workflows designed
- ✅ Pricing model established ($50/mo per client)

---

## **📁 REFERENCE DOCUMENTS**

### **Architecture**
- `docs/architecture/ADR-003-multi-tenancy-strategy.md` - Multi-tenant patterns
- `docs/architecture/ADR-006-data-orchestrator-pattern.md` - Data orchestration
- `docs/architecture/ADR-007-service-boundaries.md` - Service boundaries

### **Product Strategy**
- `docs/product/Oodaloo_RowCol_cash_runway_ritual.md` - Product vision
- `docs/BUILD_PLAN_FIRM_FIRST_V6.0.md` - Build plan

### **Implementation**
- `zzz_fix_backlog/working/F01_FIRM_FIRST_FOUNDATION.md` - Detailed implementation
- `tests/conftest.py` - Database fixtures
- `infra/qbo/smart_sync.py` - QBO integration patterns

---

**Status**: Ready for immediate execution  
**Next Action**: Start with Phase 1, Task 1.1 (TestDrive Data Orchestrator)  
**Branch**: `feat/firm-first`  
**Updated**: 2025-09-30
