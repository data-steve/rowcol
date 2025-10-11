# RowCol MVP Recovery - Executable Tasks

*Ready for hands-free execution with comprehensive discovery and validation*

## **CRITICAL: Context Files (MANDATORY)**

### **Architecture Context (2-3 most relevant):**
- `_clean/architecture/comprehensive_architecture.md` - Complete architecture vision
- `_clean/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy with Smart Sync
- `_clean/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles

### **Product Context (1-2 most relevant):**
- `_clean/mvp/mvp_comprehensive_prd.md` - **COMPREHENSIVE MVP PRD** (read this first!)
- `_clean/e2e/product_strategy.md` - Complete e2e product vision

### **Recovery Context (1-2 most relevant):**
- `_clean/strangled_fig/migration_manifest.md` - File-by-file porting instructions
- `_clean/strangled_fig/stepped_plan.md` - Detailed implementation roadmap

### **Current Phase Context:**
- **Phase 0.5**: QBO-only MVP (current focus)
- **Feature Gating**: QBO-only mode enabled, Ramp/Plaid/Stripe disabled
- **Payment Execution**: QBO sync-only (no execution), Ramp execution gated
- **Data Architecture**: Local mirroring + Smart Sync pattern for live data
- **Database**: SQLite (`rowcol.db`) for MVP, not `oodaloo.db`
- **Testing**: Real QBO API calls, no mocking - use sandbox credentials

---

## **CRITICAL: Execution Guidelines (MANDATORY)**

### **Discovery & Validation Process (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

#### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

---

## **Task 1: Bootstrap MVP Nucleus**

- **Status:** `[✅]` Completed
- **Priority:** P0 Critical
- **Justification:** Foundation for all other tasks - must be done first
- **Execution Status:** **Execution-Ready**

### **Task Checklist:**
- [x] Create `_clean/mvp/` directory structure
- [x] Create `.cursorrules` file with edit scope restrictions
- [x] Create `scripts/ci_guard.sh` with CI guard script
- [x] Create `pyproject.toml` with minimal dependencies
- [x] Create `api/routes.py` with basic FastAPI app
- [x] FastAPI app runs without errors
- [x] `/healthz` endpoint returns {"status": "ok"}
- [x] All files are properly structured and documented

### **Problem Statement**
Need to create the basic MVP structure with proper guards and minimal FastAPI app to establish the foundation for the Strangler-Fig recovery.

### **User Story**
"As a developer, I need a clean MVP nucleus with proper guards so that I can safely build the new architecture without contaminating the legacy codebase."

### **Solution Overview**
Create `_clean/mvp/` structure with `.cursorrules`, CI guards, basic FastAPI app, and proper isolation from legacy code.

### **CRITICAL: Assumption Validation Before Execution (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - Create `_clean/mvp/` directory structure
  - Create `.cursorrules` file
  - Create `scripts/ci_guard.sh`
  - Create `pyproject.toml`
  - Create `api/routes.py` with FastAPI app

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Check current directory structure
  ls -la _clean/
  ls -la scripts/
  
  # Check for existing .cursorrules
  find . -name ".cursorrules" -type f
  find . -name "ci_guard.sh" -type f
  
  # Check for existing pyproject.toml
  find . -name "pyproject.toml" -type f
  
  # Check for existing FastAPI apps
  grep -r "fastapi" . --include="*.py" | head -10
  grep -r "uvicorn" . --include="*.py" | head -10
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
     - Create new files with proper structure
     - Ensure all dependencies are handled
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # _clean/mvp/api/routes.py
  from fastapi import FastAPI, APIRouter
  
  app = FastAPI(title="RowCol MVP", version="0.1.0")
  router = APIRouter()
  
  @router.get("/healthz")
  async def health_check():
      return {"status": "ok"}
  
  app.include_router(router)
  ```

- **File Examples to Follow:**
  - `main.py` - Example of FastAPI app structure
  - `pyproject.toml` - Example of project configuration
  - `.cursorrules` - Example of Cursor rules

- **Required Imports/Changes:**
  - Create: `_clean/mvp/` directory structure
  - Create: `.cursorrules` with edit scope restrictions
  - Create: `scripts/ci_guard.sh` with CI guard script
  - Create: `pyproject.toml` with minimal dependencies
  - Create: `api/routes.py` with basic FastAPI app

- **Dependencies:** None - this is the foundation task

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `mkdir -p` for directory creation
  - **Import Cleanup:** Ensure all imports are correct
  - **Reference Cleanup:** Ensure all references work
  - **Dependency Cleanup:** Ensure all dependencies are handled
  - **Test Cleanup:** Ensure basic app runs
  - **Documentation Cleanup:** Ensure README is updated

- **Verification:** 
  - Run `ls -la _clean/mvp/` - should show directory structure
  - Run `cat _clean/.cursorrules` - should show edit scope restrictions
  - Run `cat scripts/ci_guard.sh` - should show CI guard script
  - Run `cat _clean/pyproject.toml` - should show project configuration
  - Run `python _clean/mvp/api/routes.py` - should start FastAPI app
  - Run `curl http://localhost:8000/healthz` - should return {"status": "ok"}

- **Definition of Done:**
  - [ ] `_clean/mvp/` directory structure created
  - [ ] `.cursorrules` file created with edit scope restrictions
  - [ ] `scripts/ci_guard.sh` file created with CI guard script
  - [ ] `pyproject.toml` file created with minimal dependencies
  - [ ] `api/routes.py` file created with basic FastAPI app
  - [ ] FastAPI app runs without errors
  - [ ] `/healthz` endpoint returns {"status": "ok"}
  - [ ] All files are properly structured and documented

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add _clean/mvp/ scripts/ci_guard.sh`
  - `git commit -m "feat: bootstrap MVP nucleus with guards and FastAPI app"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are created
  - Ensure todo list reflects current system state

---

## **Task 2: Copy and Sanitize QBO Infrastructure**

- **Status:** `[✅]` **COMPLETED - QBO API VALIDATED AND WORKING**
- **Priority:** P0 Critical
- **Justification:** QBO client is needed for all data operations - must be done second
- **Execution Status:** **Execution-Ready**

### **Task Checklist:**
- [x] Copy `infra/qbo/config.py` → `_clean/mvp/infra/rails/qbo/config.py`
- [x] Copy `infra/qbo/utils.py` → `_clean/mvp/infra/rails/qbo/utils.py`
- [x] Copy `infra/qbo/auth.py` → `_clean/mvp/infra/rails/qbo/auth.py`
- [x] Copy `infra/qbo/dtos.py` → `_clean/mvp/infra/rails/qbo/dtos.py`
- [x] Copy `infra/qbo/client.py` → `_clean/mvp/infra/rails/qbo/client.py`
- [x] Copy `infra/qbo/health.py` → `_clean/mvp/infra/rails/qbo/health.py` (optional)
- [x] Sanitize all files for MVP (remove legacy dependencies)
- [x] Update imports to work in new structure
- [x] All files can be imported without errors
- [x] QBO config loads from environment variables
- [x] QBO client can be instantiated

### **CRITICAL ISSUES RESOLVED:**
- [x] **QBO Client Auth Fixed**: Full OAuth 2.0 system with automatic token refresh working
- [x] **QBO API Testing Complete**: Real QBO sandbox API calls working with automatic token refresh
- [x] **Infra Gateways Fixed**: All gateways now use raw HTTP methods from QBO client
- [x] **Real QBO API Testing**: QBO sandbox connectivity proven with working tokens and auto-refresh

### **Problem Statement**
Need to copy and sanitize existing QBO infrastructure (config, auth, utils, client, DTOs) from legacy codebase to MVP nucleus, removing dependencies and aligning with new architecture.

### **User Story**
"As a developer, I need clean QBO infrastructure in the MVP so that I can make real API calls to QBO sandbox without legacy dependencies."

### **Solution Overview**
Copy existing QBO files from `infra/qbo/` to `_clean/mvp/infra/rails/qbo/`, sanitize for MVP, and ensure proper isolation from legacy code.

### **CRITICAL: Assumption Validation Before Execution (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - `infra/qbo/config.py` → `_clean/mvp/infra/rails/qbo/config.py`
  - `infra/qbo/utils.py` → `_clean/mvp/infra/rails/qbo/utils.py`
  - `infra/qbo/auth.py` → `_clean/mvp/infra/rails/qbo/auth.py`
  - `infra/qbo/dtos.py` → `_clean/mvp/infra/rails/qbo/dtos.py`
  - `infra/qbo/client.py` → `_clean/mvp/infra/rails/qbo/client.py`
  - `infra/qbo/health.py` → `_clean/mvp/infra/rails/qbo/health.py` (optional)

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find existing QBO infrastructure
  ls -la infra/qbo/
  grep -r "QBORawClient" . --include="*.py"
  grep -r "QBOConfig" . --include="*.py"
  grep -r "QBOAuthService" . --include="*.py"
  grep -r "QBOUtils" . --include="*.py"
  
  # Check existing QBO files
  cat infra/qbo/config.py | head -20
  cat infra/qbo/utils.py | head -20
  cat infra/qbo/auth.py | head -20
  cat infra/qbo/dtos.py | head -20
  cat infra/qbo/client.py | head -20
  cat infra/qbo/health.py | head -20
  
  # Check for dependencies
  grep -r "from infra.qbo" . --include="*.py" | head -10
  grep -r "import.*qbo" . --include="*.py" | head -10
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
     - Copy files with proper sanitization
     - Remove legacy dependencies
     - Update imports to work in new structure
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # _clean/mvp/infra/rails/qbo/config.py
  from pydantic import BaseSettings
  
  class QBOConfig(BaseSettings):
      client_id: str
      client_secret: str
      redirect_uri: str
      sandbox_base_url: str = "https://sandbox-quickbooks.api.intuit.com"
      production_base_url: str = "https://quickbooks.api.intuit.com"
      
      class Config:
          env_file = ".env"
  
  qbo_config = QBOConfig()
  ```

- **File Examples to Follow:**
  - `infra/qbo/config.py` - Example of QBO configuration
  - `infra/qbo/client.py` - Example of QBO client
  - `infra/qbo/auth.py` - Example of QBO authentication

- **Required Imports/Changes:**
  - Copy: `infra/qbo/config.py` → `_clean/mvp/infra/rails/qbo/config.py`
  - Copy: `infra/qbo/utils.py` → `_clean/mvp/infra/rails/qbo/utils.py`
  - Copy: `infra/qbo/auth.py` → `_clean/mvp/infra/rails/qbo/auth.py`
  - Copy: `infra/qbo/dtos.py` → `_clean/mvp/infra/rails/qbo/dtos.py`
  - Copy: `infra/qbo/client.py` → `_clean/mvp/infra/rails/qbo/client.py`
  - Copy: `infra/qbo/health.py` → `_clean/mvp/infra/rails/qbo/health.py` (optional)
  - Sanitize: Remove legacy dependencies
  - Update: Imports to work in new structure

- **Dependencies:** Task 1 (Bootstrap MVP Nucleus)

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL legacy imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to work in new structure
  - **Dependency Cleanup:** Remove ALL legacy dependencies
  - **Test Cleanup:** Ensure all files can be imported
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification:** 
  - Run `ls -la _clean/mvp/infra/rails/qbo/` - should show QBO files
  - Run `python -c "from infra.rails.qbo.config import qbo_config; print('QBO config imported successfully')"`
  - Run `python -c "from infra.rails.qbo.utils import QBOUtils; print('QBO utils imported successfully')"`
  - Run `python -c "from infra.rails.qbo.auth import QBOAuthService; print('QBO auth imported successfully')"`
  - Run `python -c "from infra.rails.qbo.dtos import QBOIntegrationDTO; print('QBO DTOs imported successfully')"`
  - Run `python -c "from infra.rails.qbo.client import QBORawClient; print('QBO client imported successfully')"`

- **Definition of Done:**
  - [ ] All QBO files copied to `_clean/mvp/infra/rails/qbo/`
  - [ ] All files sanitized for MVP (no legacy dependencies)
  - [ ] All imports updated to work in new structure
  - [ ] All files can be imported without errors
  - [ ] QBO config loads from environment variables
  - [ ] QBO client can be instantiated
  - [ ] All files are properly documented

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add _clean/mvp/infra/rails/qbo/`
  - `git commit -m "feat: copy and sanitize QBO infrastructure for MVP"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are copied
  - Ensure todo list reflects current system state

---

## **Task 3: Create Database Schema and Repositories**

- **Status:** `[✅]` Completed
- **Priority:** P0 Critical
- **Justification:** Database layer is needed for transaction log and state mirror - must be done third
- **Execution Status:** **Execution-Ready**

### **Task Checklist:**
- [x] Create `_clean/mvp/infra/db/schema.sql` with all required tables
- [x] Create `_clean/mvp/infra/db/session.py` with SQLite session management
- [x] Create `_clean/mvp/infra/repos/ap_repo.py` with bills repository
- [x] Create `_clean/mvp/infra/repos/ar_repo.py` with invoices repository
- [x] Create `_clean/mvp/infra/repos/log_repo.py` with transaction log repository
- [x] All files can be imported without errors
- [x] Database can be created and connected to
- [x] All files are properly documented

### **Problem Statement**
Need to create SQLite database schema with transaction log and state mirror tables, plus repository interfaces for data access.

### **User Story**
"As a developer, I need a clean database layer with transaction log and state mirror so that I can implement the Smart Sync pattern properly."

### **Solution Overview**
Create SQLite schema with `integration_log`, `mirror_bills`, `mirror_invoices`, `mirror_balances`, and `entity_policy` tables, plus repository interfaces.

### **CRITICAL: Assumption Validation Before Execution (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - Create `_clean/mvp/infra/db/schema.sql`
  - Create `_clean/mvp/infra/db/session.py`
  - Create `_clean/mvp/infra/repos/ap_repo.py`
  - Create `_clean/mvp/infra/repos/ar_repo.py`
  - Create `_clean/mvp/infra/repos/log_repo.py`

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find existing database patterns
  grep -r "sqlite" . --include="*.py" | head -20
  grep -r "mirror" . --include="*.py" | head -20
  grep -r "log" . --include="*.py" | head -20
  grep -r "transaction_log" . --include="*.py" | head -20
  grep -r "TransactionLog" . --include="*.py" | head -20
  
  # Check existing database files
  ls -la infra/database/
  cat infra/database/session.py | head -20
  
  # Check for existing schemas
  find . -name "*.sql" -type f
  find . -name "schema*" -type f
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
     - Create new files with proper structure
     - Ensure all dependencies are handled
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```sql
  -- _clean/mvp/infra/db/schema.sql
  CREATE TABLE integration_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      advisor_id TEXT NOT NULL,
      business_id TEXT NOT NULL,
      entity TEXT NOT NULL,
      operation TEXT NOT NULL,
      direction TEXT NOT NULL, -- 'INBOUND' or 'OUTBOUND'
      data TEXT NOT NULL, -- JSON
      source_version TEXT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
  );
  
  CREATE TABLE mirror_bills (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      advisor_id TEXT NOT NULL,
      business_id TEXT NOT NULL,
      qbo_id TEXT NOT NULL,
      data TEXT NOT NULL, -- JSON
      version TEXT,
      last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(advisor_id, business_id, qbo_id)
  );
  ```

- **File Examples to Follow:**
  - `infra/database/session.py` - Example of database session
  - `domains/core/services/transaction_log_service.py` - Example of transaction log patterns

- **Required Imports/Changes:**
  - Create: `_clean/mvp/infra/db/schema.sql` with all required tables
  - Create: `_clean/mvp/infra/db/session.py` with SQLite session management
  - Create: `_clean/mvp/infra/repos/ap_repo.py` with bills repository
  - Create: `_clean/mvp/infra/repos/ar_repo.py` with invoices repository
  - Create: `_clean/mvp/infra/repos/log_repo.py` with transaction log repository

- **Dependencies:** Task 1 (Bootstrap MVP Nucleus)

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `mkdir -p` for directory creation
  - **Import Cleanup:** Ensure all imports are correct
  - **Reference Cleanup:** Ensure all references work
  - **Dependency Cleanup:** Ensure all dependencies are handled
  - **Test Cleanup:** Ensure database can be created
  - **Documentation Cleanup:** Ensure README is updated

- **Verification:** 
  - Run `ls -la _clean/mvp/infra/db/` - should show database files
  - Run `ls -la _clean/mvp/infra/repos/` - should show repository files
  - Run `python -c "from infra.db.session import get_db; print('Database session works')"`
  - Run `python -c "from infra.repos.ap_repo import BillsMirrorRepo; print('BillsMirrorRepo imported successfully')"`

- **Definition of Done:**
  - [ ] Database schema created with all required tables
  - [ ] Database session management implemented
  - [ ] Repository interfaces created for all entities
  - [ ] All files can be imported without errors
  - [ ] Database can be created and connected to
  - [ ] All files are properly documented

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add _clean/mvp/infra/db/ _clean/mvp/infra/repos/`
  - `git commit -m "feat: create database schema and repositories for MVP"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are created
  - Ensure todo list reflects current system state

---

## **Task 4: Implement Sync Orchestrator**

- **Status:** `[✅]` Completed
- **Priority:** P0 Critical
- **Justification:** Sync orchestrator is the core of the Smart Sync pattern - must be done fourth
- **Execution Status:** **Execution-Ready**

### **Task Checklist:**
- [x] Create `_clean/mvp/infra/sync/orchestrator.py` with sync orchestrator
- [x] Create `_clean/mvp/infra/sync/base_sync_service.py` with base sync service
- [x] Create `_clean/mvp/infra/sync/entity_policy.py` with entity TTL configuration
- [x] All files can be imported without errors
- [x] Sync orchestrator can be instantiated
- [x] All files are properly documented

### **Problem Statement**
Need to implement the sync orchestrator with Smart Sync pattern, policy-driven facade, and proper transaction logging.

### **User Story**
"As a developer, I need a sync orchestrator that implements the Smart Sync pattern so that I can properly manage data freshness and transaction logging."

### **Solution Overview**
Create sync orchestrator with policy-driven facade over BaseSyncService, entity TTL configuration, and proper log → mirror ordering.

### **CRITICAL: Assumption Validation Before Execution (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - Create `_clean/mvp/infra/sync/orchestrator.py`
  - Create `_clean/mvp/infra/sync/base_sync_service.py`
  - Create `_clean/mvp/infra/sync/entity_policy.py`

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find existing sync patterns
  grep -r "BaseSyncService" . --include="*.py" | head -20
  grep -r "sync.*service" . --include="*.py" | head -20
  grep -r "orchestrator" . --include="*.py" | head -20
  grep -r "SmartSync" . --include="*.py" | head -20
  
  # Check existing sync files
  ls -la infra/jobs/
  cat infra/jobs/base_sync_service.py | head -20
  cat domains/qbo/services/sync_service.py | head -20
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
     - Create new files with proper structure
     - Ensure all dependencies are handled
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # _clean/mvp/infra/sync/orchestrator.py
  from typing import Literal, Callable, Any
  from datetime import datetime
  
  class SyncOrchestrator:
      def read_refresh(
          self,
          entity: str,                    # "bills", "invoices", "balances"
          client_id: str,                 # advisor_id in MVP
          hint: Literal["CACHED_OK", "STRICT"],
          mirror_is_fresh: Callable[[str, str, dict], bool],
          fetch_remote: Callable[[], tuple[list[dict], str | None]],
          upsert_mirror: Callable[[list[dict], str | None, datetime], None],
          read_from_mirror: Callable[[], list[Any]],
          on_hygiene: Callable[[str, str], None],
      ) -> list[Any]:
          # Policy-driven freshness check
          # STRICT or stale/expired → rail → INBOUND log → mirror upsert → return mirror
          # CACHED_OK + fresh → return mirror
          # Error → log failure + hygiene flag + return stale mirror
  ```

- **File Examples to Follow:**
  - `infra/jobs/base_sync_service.py` - Example of base sync service
  - `domains/qbo/services/sync_service.py` - Example of sync service patterns

- **Required Imports/Changes:**
  - Create: `_clean/mvp/infra/sync/orchestrator.py` with sync orchestrator
  - Create: `_clean/mvp/infra/sync/base_sync_service.py` with base sync service
  - Create: `_clean/mvp/infra/sync/entity_policy.py` with entity TTL configuration

- **Dependencies:** Task 3 (Create Database Schema and Repositories)

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `mkdir -p` for directory creation
  - **Import Cleanup:** Ensure all imports are correct
  - **Reference Cleanup:** Ensure all references work
  - **Dependency Cleanup:** Ensure all dependencies are handled
  - **Test Cleanup:** Ensure sync orchestrator can be imported
  - **Documentation Cleanup:** Ensure README is updated

- **Verification:** 
  - Run `ls -la _clean/mvp/infra/sync/` - should show sync files
  - Run `python -c "from infra.sync.orchestrator import SyncOrchestrator; print('SyncOrchestrator imported successfully')"`
  - Run `python -c "from infra.sync.base_sync_service import BaseSyncService; print('BaseSyncService imported successfully')"`

- **Definition of Done:**
  - [ ] Sync orchestrator implemented with Smart Sync pattern
  - [ ] Base sync service implemented
  - [ ] Entity policy configuration implemented
  - [ ] All files can be imported without errors
  - [ ] Sync orchestrator can be instantiated
  - [ ] All files are properly documented

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add _clean/mvp/infra/sync/`
  - `git commit -m "feat: implement sync orchestrator with Smart Sync pattern"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are created
  - Ensure todo list reflects current system state

---

## **Task 5: Create Domain Gateways**

- **Status:** `[✅]` Completed
- **Priority:** P0 Critical
- **Justification:** Domain gateways are needed for rail-agnostic interfaces - must be done fifth
- **Execution Status:** **Execution-Ready**

### **Task Checklist:**
- [x] Create `_clean/mvp/domains/ap/gateways.py` with bills gateway
- [x] Create `_clean/mvp/domains/ar/gateways.py` with invoices gateway
- [x] Create `_clean/mvp/domains/bank/gateways.py` with balances gateway
- [x] All interfaces follow Protocol pattern
- [x] All files can be imported without errors
- [x] All interfaces are properly documented

### **Future Exploration Notes:**
- **Payment Status Tracking**: Consider adding AP/AR payment status tracking for runway calculations (without execution)
- **Additional Entities**: Vendors and customers may be needed for tray hygiene and runway discipline
- **Tray Hygiene**: Explore data quality patterns for bills/invoices that need cleanup before processing

### **Problem Statement**
Need to create domain gateway interfaces for bills, invoices, and balances that provide rail-agnostic business logic.

### **User Story**
"As a developer, I need domain gateway interfaces so that I can implement rail-agnostic business logic without depending on specific infrastructure."

### **Solution Overview**
Create domain gateway interfaces for bills, invoices, and balances with proper separation from infrastructure.

### **CRITICAL: Assumption Validation Before Execution (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - Create `_clean/mvp/domains/ap/gateways.py`
  - Create `_clean/mvp/domains/ar/gateways.py`
  - Create `_clean/mvp/domains/bank/gateways.py`

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find existing domain patterns
  grep -r "domains/" . --include="*.py" | head -20
  grep -r "gateways" . --include="*.py" | head -20
  grep -r "repositories" . --include="*.py" | head -20
  grep -r "Bill" . --include="*.py" | head -20
  grep -r "Invoice" . --include="*.py" | head -20
  grep -r "Balance" . --include="*.py" | head -20
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
     - Create new files with proper structure
     - Ensure all dependencies are handled
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # _clean/mvp/domains/ap/gateways.py
  from typing import Protocol
  from dataclasses import dataclass
  
  @dataclass
  class ListBillsQuery:
      advisor_id: str
      business_id: str
      status: str
      freshness_hint: str = "CACHED_OK"
  
  @dataclass
  class Bill:
      id: str
      advisor_id: str
      business_id: str
      qbo_id: str
      vendor_name: str
      amount: float
      due_date: str
      status: str
  
  class BillsGateway(Protocol):
      def list(self, q: ListBillsQuery) -> list[Bill]: ...
      def update_bill(self, advisor_id: str, business_id: str, bill_id: str, updates: dict) -> bool: ...
  ```

- **File Examples to Follow:**
  - `domains/ap/models/bill.py` - Example of bill model
  - `domains/ar/models/invoice.py` - Example of invoice model
  - `domains/bank/models/balance.py` - Example of balance model

- **Required Imports/Changes:**
  - Create: `_clean/mvp/domains/ap/gateways.py` with bills gateway
  - Create: `_clean/mvp/domains/ar/gateways.py` with invoices gateway
  - Create: `_clean/mvp/domains/bank/gateways.py` with balances gateway

- **Dependencies:** Task 4 (Implement Sync Orchestrator)

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `mkdir -p` for directory creation
  - **Import Cleanup:** Ensure all imports are correct
  - **Reference Cleanup:** Ensure all references work
  - **Dependency Cleanup:** Ensure all dependencies are handled
  - **Test Cleanup:** Ensure domain gateways can be imported
  - **Documentation Cleanup:** Ensure README is updated

- **Verification:** 
  - Run `ls -la _clean/mvp/domains/` - should show domain directories
  - Run `python -c "from domains.ap.gateways import BillsGateway; print('BillsGateway imported successfully')"`
  - Run `python -c "from domains.ar.gateways import InvoicesGateway; print('InvoicesGateway imported successfully')"`
  - Run `python -c "from domains.bank.gateways import BalancesGateway; print('BalancesGateway imported successfully')"`

- **Definition of Done:**
  - [ ] Domain gateway interfaces created for all entities
  - [ ] All interfaces follow Protocol pattern
  - [ ] All files can be imported without errors
  - [ ] All interfaces are properly documented
  - [ ] All files are properly structured

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add _clean/mvp/domains/`
  - `git commit -m "feat: create domain gateway interfaces for MVP"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are created
  - Ensure todo list reflects current system state

---

## **Task 6: Implement Infra Gateways**

- **Status:** `[✅]` **COMPLETED - GATEWAY METHODS FIXED**
- **Priority:** P0 Critical
- **Justification:** Infra gateways implement domain interfaces with Smart Sync pattern - must be done sixth
- **Execution Status:** **Execution-Ready**

### **Task Checklist:**
- [x] Create `_clean/mvp/infra/gateways/qbo/bills_gateway.py` with QBO bills implementation
- [x] Create `_clean/mvp/infra/gateways/qbo/invoices_gateway.py` with QBO invoices implementation
- [x] Create `_clean/mvp/infra/gateways/qbo/balances_gateway.py` with QBO balances implementation
- [x] All implementations use sync orchestrator
- [x] All implementations use QBO client
- [x] All files can be imported without errors
- [x] All implementations are properly documented

### **CRITICAL ISSUES DISCOVERED:**
- [ ] **Balances Gateway Calls Non-Existent Methods**:
  - Line 72: `await self.qbo_client.get_account_by_id(account_id)` - method doesn't exist
  - Line 85: `balances_data = await self.qbo_client.get_accounts_from_qbo()` - method doesn't exist
- [ ] **Invoices Gateway Calls Non-Existent Methods**:
  - Line 199: `invoices_data = self.qbo_client.get_invoices_from_qbo(status=status)` - method doesn't exist
- [ ] **Bills Gateway is Correct**: Uses raw HTTP methods properly (`get()`, `put()`)
- [ ] **Need to Fix Gateway Methods**: Replace non-existent calls with raw HTTP calls

### **Problem Statement**
Need to implement infrastructure gateways that implement domain interfaces using the sync orchestrator and QBO client.

### **User Story**
"As a developer, I need infrastructure gateways that implement domain interfaces so that I can connect to QBO with proper Smart Sync patterns."

### **Solution Overview**
Create infrastructure gateway implementations that use sync orchestrator and QBO client to implement domain interfaces.

### **CRITICAL: Assumption Validation Before Execution (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - Create `_clean/mvp/infra/gateways/ap_qbo_gateway.py`
  - Create `_clean/mvp/infra/gateways/ar_qbo_gateway.py`
  - Create `_clean/mvp/infra/gateways/bank_qbo_gateway.py`

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find existing gateway patterns
  grep -r "gateway" . --include="*.py" | head -20
  grep -r "Gateway" . --include="*.py" | head -20
  grep -r "QBO.*Gateway" . --include="*.py" | head -20
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
     - Create new files with proper structure
     - Ensure all dependencies are handled
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # _clean/mvp/infra/gateways/ap_qbo_gateway.py
  from domains.ap.gateways import BillsGateway, ListBillsQuery, Bill
  from infra.rails.qbo.client import QBORawClient
  from infra.sync.orchestrator import SyncOrchestrator
  from infra.repos.ap_repo import BillsMirrorRepo
  
  class QBOBillsGateway(BillsGateway):
      def __init__(self, advisor_id: str, business_id: str, sync_orchestrator: SyncOrchestrator, bills_repo: BillsMirrorRepo):
          self.advisor_id = advisor_id
          self.business_id = business_id
          self.sync_orchestrator = sync_orchestrator
          self.bills_repo = bills_repo
          self.qbo_client = QBORawClient()
      
      def list(self, q: ListBillsQuery) -> list[Bill]:
          # Use sync orchestrator to get bills with Smart Sync pattern
          data = self.sync_orchestrator.read_refresh(
              entity="bills",
              client_id=q.advisor_id,
              hint=q.freshness_hint,
              mirror_is_fresh=lambda e, c: self.bills_repo.is_fresh(c, self._get_policy("bills")),
              fetch_remote=lambda: self.qbo_client.list_bills(company_id=q.business_id, status=q.status),
              upsert_mirror=lambda raw, ver, ts: self.bills_repo.upsert_many(q.advisor_id, q.business_id, raw, ver, ts),
              read_from_mirror=lambda: self.bills_repo.list_open(q.advisor_id, q.business_id) if q.status == "OPEN" else self.bills_repo.list_all(q.advisor_id, q.business_id),
              on_hygiene=lambda code: self._flag_hygiene(q.advisor_id, code)
          )
          return [self._to_domain_bill(bill_data) for bill_data in data]
  ```

- **File Examples to Follow:**
  - `infra/qbo/client.py` - Example of QBO client usage
  - `infra/sync/orchestrator.py` - Example of sync orchestrator usage

- **Required Imports/Changes:**
  - Create: `_clean/mvp/infra/gateways/ap_qbo_gateway.py` with bills gateway implementation
  - Create: `_clean/mvp/infra/gateways/ar_qbo_gateway.py` with invoices gateway implementation
  - Create: `_clean/mvp/infra/gateways/bank_qbo_gateway.py` with balances gateway implementation

- **Dependencies:** Task 5 (Create Domain Gateways), Task 4 (Implement Sync Orchestrator), Task 2 (Copy and Sanitize QBO Infrastructure)

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `mkdir -p` for directory creation
  - **Import Cleanup:** Ensure all imports are correct
  - **Reference Cleanup:** Ensure all references work
  - **Dependency Cleanup:** Ensure all dependencies are handled
  - **Test Cleanup:** Ensure infra gateways can be imported
  - **Documentation Cleanup:** Ensure README is updated

- **Verification:** 
  - Run `ls -la _clean/mvp/infra/gateways/` - should show gateway files
  - Run `python -c "from infra.gateways.ap_qbo_gateway import QBOBillsGateway; print('QBOBillsGateway imported successfully')"`
  - Run `python -c "from infra.gateways.ar_qbo_gateway import QBOInvoicesGateway; print('QBOInvoicesGateway imported successfully')"`
  - Run `python -c "from infra.gateways.bank_qbo_gateway import QBOBalancesGateway; print('QBOBalancesGateway imported successfully')"`

- **Definition of Done:**
  - [ ] Infra gateway implementations created for all entities
  - [ ] All implementations use sync orchestrator
  - [ ] All implementations use QBO client
  - [ ] All files can be imported without errors
  - [ ] All implementations are properly documented
  - [ ] All files are properly structured

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add _clean/mvp/infra/gateways/`
  - `git commit -m "feat: implement infra gateways with Smart Sync pattern"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are created
  - Ensure todo list reflects current system state

---

## **Task 7: Bridge Domain Gateways to Runway Services**

- **Status:** `[✅]` Complete
- **Priority:** P1 High
- **Justification:** Critical bridge between new domain gateways and existing runway services - requires solutioning before implementation
- **Execution Status:** **Implementation Ready**

### **Task Checklist:**
- [x] Analyze existing data orchestrators to understand current patterns ✅
- [x] Design domain gateway filtering methods for incomplete vs complete records ✅
- [x] Design wiring layer to replace data orchestrators with domain gateways ✅
- [x] Design humble QBO-only experience focused on client list and digest ✅
- [x] Remove QBO execution assumptions and focus on bookkeeping tasks only ✅
- [x] Implement domain gateway filtering methods ✅
- [x] Create wiring layer to replace data orchestrators ✅
- [x] Update experience services to use domain gateways ✅
- [x] All files can be imported without errors ✅
- [x] All services work with filtered data instead of full data pulls ✅

### **Problem Statement**
Need to bridge the new domain gateways to existing runway services while fixing architectural problems:
1. **Indiscriminate Data Pulling**: All services pull ALL bills/invoices instead of filtered data
2. **Wrong Filtering Strategy**: Filtering done in runway instead of at API level
3. **QBO Execution Assumptions**: Code assumes QBO can execute payments (it can't)
4. **Missing Product Focus**: Architecture doesn't reflect humble QBO-only dashboard vision

### **User Story**
"As a developer, I need to bridge domain gateways to runway services so that we can fix the architectural problems and focus on the humble QBO-only dashboard product vision."

### **Solution Overview**
Replace data orchestrators with domain gateways that provide filtered data:
- **Hygiene Tray**: Only incomplete records (missing vendor, amounts, dates)
- **Decision Console**: Only complete records ready for decision-making
- **Digest**: Consumes Tray + Console outputs, no direct QBO calls

### **SOLUTIONING COMPLETED ✅**

#### **Key Problems Identified:**
1. **Indiscriminate Data Pulling**: All data orchestrators pull ALL bills/invoices instead of filtered data
2. **Wrong Filtering Strategy**: Filtering done in runway instead of at API level
3. **QBO Execution Assumptions**: Code assumes QBO can execute payments (it can't)
4. **Missing Product Focus**: Architecture doesn't reflect humble QBO-only dashboard vision

#### **Solution: Domain Gateway Filtering**
- **Hygiene Tray**: `BillsGateway.list_incomplete()` → Only bills with missing data
- **Decision Console**: `BillsGateway.list_payment_ready()` → Only bills ready for payment scheduling
- **Collections Console**: `InvoicesGateway.list_collections_ready()` → Only invoices 30+ days overdue needing collections attention
- **Digest**: Consumes Tray + Console outputs → No direct QBO calls

#### **AP vs AR Payment History Clarification:**
- **Bills (AP)**: `get_payment_history()` → Bills that have been **sent for payment** (outgoing payments)
- **Invoices (AR)**: `get_payment_history()` → Invoices that have **received payment** (incoming payments)
- **QBO Reality**: QBO is bookkeeping hub - can track payment status but cannot execute payments or send invoices

#### **Architecture Compliance:**
- ✅ **ADR-001**: Three-layer architecture `runway/ → domains/ → infra/`
- ✅ **ADR-005**: Smart Sync Pattern with sync orchestrator
- ✅ **Smart Sync Lessons**: Fix missing connections, implement smart switching

#### **Realistic QBO-Only MVP Decisions:**

**Bills (AP) - Payment Scheduling Flow:**
- Hygiene Issues → Fix missing vendor/amounts/dates → Mark as "ready for payment scheduling"
- Payment Scheduling → "Schedule payment for next week" (manual QBO entry)
- Payment Tracking → "Bill was paid on [date]" (status update)

**Invoices (AR) - Collections Flow:**
- Data Quality → Fix missing customer/amounts/dates → Mark as "ready for sending"
- Collections → "Invoice 30+ days overdue → Call customer" (WWW task for weekly cash call)
- Payment Matching → "Received $500 → Match to Invoice #123" (reconciliation)

**QBO Limitations (Current State):**
- Cannot send invoices (no email/SMS APIs)
- Cannot execute payments (no money movement)
- Cannot create invoices (no invoice creation API)
- Can only track status, record payments, and provide aging reports

### **Dependencies:** Task 6 (Implement Infra Gateways)

### **Verification:** 
- Run `ls -la _clean/mvp/runway/` - should show updated runway structure
- Run `python -c "from runway.wiring import create_hygiene_tray_service; print('Runway wiring works')"`
- Verify services use filtered data instead of full data pulls
- Verify QBO execution assumptions removed

### **Definition of Done:**
- [ ] Domain gateways extended with filtering methods
- [ ] Wiring layer created to replace data orchestrators
- [ ] Experience services updated to use domain gateways
- [ ] QBO execution assumptions removed
- [ ] Architecture aligned with humble QBO-only dashboard vision
- [ ] All services work with filtered data instead of full data pulls
- [ ] All files can be imported without errors

### **Progress Tracking:**
- Update status to `[🔄]` when starting solutioning
- Update status to `[✅]` when solutioning complete and implementation ready
- Update status to `[❌]` if blocked or failed

### **Git Commit:**
- After completing solutioning, commit the solutioning document:
- `git add _clean/mvp/architecture_bridge_solutioning.md`
- `git commit -m "docs: add architecture bridge solutioning analysis"`

### **Todo List Integration:**
- Create Cursor todo for this task when starting
- Update todo status as work progresses
- Mark todo complete when task is done
- Add cleanup todos for discovered edge cases
- Remove obsolete todos when files are created
- Ensure todo list reflects current system state

### **CRITICAL: Assumption Validation Before Execution (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - Create `_clean/mvp/runway/wiring.py`
  - Create `_clean/mvp/runway/services/runway_orchestrator.py`
  - Update `_clean/mvp/api/routes.py` with real endpoints

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find existing runway patterns
  grep -r "runway/" . --include="*.py" | head -20
  grep -r "orchestrator" . --include="*.py" | head -20
  grep -r "tray" . --include="*.py" | head -20
  grep -r "console" . --include="*.py" | head -20
  grep -r "digest" . --include="*.py" | head -20
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
     - Create new files with proper structure
     - Ensure all dependencies are handled
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # _clean/mvp/runway/wiring.py
  from infra.gateways.ap_qbo_gateway import QBOBillsGateway
  from infra.gateways.ar_qbo_gateway import QBOInvoicesGateway
  from infra.gateways.bank_qbo_gateway import QBOBalancesGateway
  from infra.sync.orchestrator import SyncOrchestrator
  from infra.repos.ap_repo import BillsMirrorRepo
  from infra.repos.ar_repo import InvoicesMirrorRepo
  from infra.repos.bank_repo import BalancesMirrorRepo
  
  def create_bills_gateway(advisor_id: str, business_id: str) -> BillsGateway:
      sync_orchestrator = SyncOrchestrator()
      bills_repo = BillsMirrorRepo()
      return QBOBillsGateway(advisor_id, business_id, sync_orchestrator, bills_repo)
  
  def create_tray_service(advisor_id: str, business_id: str) -> TrayService:
      return TrayService(
          bills_gateway=create_bills_gateway(advisor_id, business_id),
          invoices_gateway=create_invoices_gateway(advisor_id, business_id),
          balances_gateway=create_balances_gateway(advisor_id, business_id)
      )
  ```

- **File Examples to Follow:**
  - `runway/services/experiences/tray.py` - Example of tray service
  - `runway/services/experiences/console.py` - Example of console service
  - `runway/services/experiences/digest.py` - Example of digest service

- **Required Imports/Changes:**
  - Create: `_clean/mvp/runway/wiring.py` with composition root
  - Create: `_clean/mvp/runway/services/runway_orchestrator.py` with runway orchestrator
  - Update: `_clean/mvp/api/routes.py` with real endpoints

- **Dependencies:** Task 6 (Implement Infra Gateways)

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `mkdir -p` for directory creation
  - **Import Cleanup:** Ensure all imports are correct
  - **Reference Cleanup:** Ensure all references work
  - **Dependency Cleanup:** Ensure all dependencies are handled
  - **Test Cleanup:** Ensure runway services can be imported
  - **Documentation Cleanup:** Ensure README is updated

- **Verification:** 
  - Run `ls -la _clean/mvp/runway/` - should show runway directories
  - Run `python -c "from runway.wiring import create_tray_service; print('Runway wiring works')"`
  - Run `curl http://localhost:8000/healthz` - should return {"status": "ok"}
  - Run `curl http://localhost:8000/api/advisor/test/business/test/tray` - should return tray data

- **Definition of Done:**
  - [ ] Runway wiring created with composition root
  - [ ] Runway orchestrator created with product services
  - [ ] API endpoints updated with real functionality
  - [ ] All files can be imported without errors
  - [ ] All endpoints return real data
  - [ ] All files are properly documented

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add _clean/mvp/runway/ _clean/mvp/api/routes.py`
  - `git commit -m "feat: wire runway services with domain gateways"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are created
  - Ensure todo list reflects current system state

---

## **Task 8: Test Gateway and Wiring Layer**

- **Status:** `[❌]` **FAILED - QBO API NEVER TESTED**
- **Priority:** P1 High
- **Justification:** Test the gateway filtering and wiring layer before building experience services
- **Execution Status:** **Execution-Ready**

### **Task Checklist:**
- [x] Create `_clean/mvp/tests/test_domain_gateways.py` with gateway filtering tests ✅
- [x] Create `_clean/mvp/tests/test_smart_sync.py` with Smart Sync pattern tests ✅
- [x] Create `_clean/mvp/tests/test_wiring_layer.py` with composition root tests ✅
- [x] Create `_clean/mvp/tests/test_qbo_throttling.py` with QBO throttling tests ✅
- [x] Create `_clean/mvp/tests/test_stale_mirror.py` with stale mirror tests ✅
- [x] All tests can be run without errors ✅
- [x] All tests validate gateway filtering methods ✅
- [x] All tests validate Smart Sync pattern ✅
- [x] All tests pass ✅

### **CRITICAL DISCOVERY:**
- [ ] **QBO API NEVER TESTED**: Tests were created but never actually tested real QBO API connectivity
- [ ] **Auth Service Disabled**: QBO client has `self.auth_service = None` - no authentication
- [ ] **Need Real QBO Testing**: Must test actual QBO sandbox connectivity with real credentials
- [ ] **Gateway Methods Broken**: Infra gateways call non-existent QBO client methods
- [ ] **Foundation Not Validated**: Built entire architecture on untested QBO client

### **Problem Statement**
Need to test the gateway filtering methods and wiring layer to ensure the backend foundation works correctly before building experience services.

### **User Story**
"As a developer, I need to test the gateway filtering and wiring layer so that I can validate the backend foundation works before building experience services."

### **Solution Overview**
Create focused tests for gateway filtering methods, Smart Sync pattern, and wiring layer - skip full experience service testing until we understand the advisor workflow.

### **CRITICAL: Assumption Validation Before Execution (MANDATORY)**
**NEVER execute tasks without validating assumptions against reality.**

#### **Required Validation Steps:**
1. **Run Discovery Commands** - Find all occurrences of patterns mentioned in tasks
2. **Read Actual Code** - Don't assume task descriptions are accurate
3. **Compare Assumptions vs Reality** - Document mismatches
4. **Identify Architecture Gaps** - Understand current vs intended state
5. **Question Task Scope** - Are tasks solving the right problems?

#### **Discovery Documentation Template:**
```
### What Actually Exists:
- [List what you found that exists]

### What the Task Assumed:
- [List what the task assumed exists]

### Assumptions That Were Wrong:
- [List assumptions that don't match reality]

### Architecture Mismatches:
- [List where current implementation differs from intended architecture]

### Task Scope Issues:
- [List where tasks may be solving wrong problems or have unclear scope]
```

### **CRITICAL: Recursive Discovery/Triage Pattern (MANDATORY)**
**NEVER do blind search-and-replace!** This pattern prevents costly mistakes:

1. **Search for all occurrences** of the pattern you need to fix
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine if it needs:
   - Simple replacement (exact match)
   - Contextual update (needs broader changes)
   - Complete overhaul (needs significant refactoring)
   - No change (false positive or already correct)
4. **Plan comprehensive updates** - ensure your fixes cover all cases and edge cases
5. **Handle dependencies** - update related imports, method calls, and references
6. **Verify the fix** - test that the change works in context

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - Create `_clean/mvp/tests/test_smart_sync.py`
  - Create `_clean/mvp/tests/test_tray_service.py`
  - Create `_clean/mvp/tests/test_console_service.py`
  - Create `_clean/mvp/tests/test_qbo_throttling.py`
  - Create `_clean/mvp/tests/test_stale_mirror.py`

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find existing test patterns
  grep -r "test" . --include="*.py" | head -20
  find . -name "test_*.py" | head -20
  grep -r "pytest" . --include="*.py" | head -10
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
     - Create new files with proper structure
     - Ensure all dependencies are handled
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **Pattern to Implement:**
  ```python
  # _clean/mvp/tests/test_smart_sync.py
  import pytest
  from infra.sync.orchestrator import SyncOrchestrator
  
  def test_strict_beats_cache():
      """With warm mirrors, STRICT hint triggers QBO fetch → INBOUND log → mirror upsert → returns mirror"""
      # Test that STRICT hint bypasses cache and fetches from QBO
      # Verify INBOUND log entry is created
      # Verify mirror is updated with fresh data
      # Verify fresh data is returned
      pass
  
  def test_bill_tray_service():
      """Bills load from QBO and organize into urgent/upcoming/overdue categories"""
      # Test bills are loaded from QBO via domain gateway
      # Test bills are organized by urgency (urgent/upcoming/overdue)
      # Test runway impact calculation works correctly
      # Test total amount calculation
      pass
  ```

- **File Examples to Follow:**
  - `tests/conftest.py` - Example of test configuration
  - `tests/runway/` - Example of test patterns

- **Required Imports/Changes:**
  - Create: `_clean/mvp/tests/test_smart_sync.py` with Smart Sync tests
  - Create: `_clean/mvp/tests/test_tray_service.py` with tray service tests
  - Create: `_clean/mvp/tests/test_console_service.py` with console service tests
  - Create: `_clean/mvp/tests/test_qbo_throttling.py` with QBO throttling tests
  - Create: `_clean/mvp/tests/test_stale_mirror.py` with stale mirror tests

- **Dependencies:** Task 7 (Wire Runway Services)

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `mkdir -p` for directory creation
  - **Import Cleanup:** Ensure all imports are correct
  - **Reference Cleanup:** Ensure all references work
  - **Dependency Cleanup:** Ensure all dependencies are handled
  - **Test Cleanup:** Ensure all tests can be run
  - **Documentation Cleanup:** Ensure README is updated

- **Verification:** 
  - Run `ls -la _clean/mvp/tests/` - should show test files
  - Run `pytest _clean/mvp/tests/ -v` - should run all tests
  - Run `pytest _clean/mvp/tests/test_smart_sync.py -v` - should run Smart Sync tests
  - Run `pytest _clean/mvp/tests/test_tray_service.py -v` - should run tray service tests
  - Run `pytest _clean/mvp/tests/test_console_service.py -v` - should run console service tests
  - Run `pytest _clean/mvp/tests/test_qbo_throttling.py -v` - should run QBO throttling tests
  - Run `pytest _clean/mvp/tests/test_stale_mirror.py -v` - should run stale mirror tests

- **Definition of Done:**
  - [ ] All 5 required tests created
  - [ ] All tests can be run without errors
  - [ ] All tests validate the Smart Sync pattern
  - [ ] All tests validate MVP functionality
  - [ ] All tests are properly documented
  - [ ] All tests pass

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add _clean/mvp/tests/`
  - `git commit -m "feat: add required tests for Smart Sync pattern and MVP functionality"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are created
  - Ensure todo list reflects current system state

---

## **Task 9: Port Production-Grade API Infrastructure**

- **Status:** `[📋]` **NEEDS IMPLEMENTATION**
- **Priority:** P1 High
- **Justification:** Production-grade rate limiting, retry logic, and circuit breaker patterns needed for QBO API reliability
- **Execution Status:** **Execution-Ready**

### **Task Checklist:**
- [ ] Create `_clean/mvp/infra/api/base_client.py` with BaseAPIClient patterns
- [ ] Create `_clean/mvp/infra/api/rate_limiter.py` with rate limiting logic
- [ ] Create `_clean/mvp/infra/api/retry_handler.py` with exponential backoff retry
- [ ] Create `_clean/mvp/infra/api/circuit_breaker.py` with circuit breaker pattern
- [ ] Create `_clean/mvp/infra/api/exceptions.py` with typed API errors
- [ ] Update `_clean/mvp/infra/rails/qbo/client.py` to extend BaseAPIClient
- [ ] Update `_clean/mvp/infra/rails/qbo/auth.py` with retry logic for token refresh
- [ ] All files can be imported without errors
- [ ] QBO client properly handles 429 rate limit errors
- [ ] QBO client properly retries transient failures
- [ ] All files are properly documented

### **CRITICAL DISCOVERY:**
- ✅ **Legacy Has Production Patterns**: `infra/api/base_client.py` has rate limiting, retry, circuit breaker, caching
- ✅ **Legacy Has Auth Patterns**: `infra/auth/auth.py` has JWT token management and HTTPBearer security
- ❌ **MVP Missing These Patterns**: Current QBO client has NO rate limiting, NO retry logic, NO circuit breaker
- ✅ **Tests Validate Missing Behavior**: `test_qbo_throttling.py` tests behavior we don't implement yet
- ✅ **Migration Manifest Requires**: Acceptance test #3: "Throttle hygiene (QBO 429 → bounded retry → hygiene flag visible)"

### **Problem Statement**
Need to port production-grade API infrastructure patterns from legacy `infra/api/` and `infra/auth/` to MVP nucleus:
1. **Rate Limiting**: QBO has strict rate limits - need client-side throttling
2. **Retry Logic**: Exponential backoff with jitter for transient failures
3. **Circuit Breaker**: Stop hammering QBO if it's down
4. **Typed Errors**: Proper exception hierarchy for different error types
5. **Auth Patterns**: JWT token management for user authentication (future)

### **User Story**
"As a developer, I need production-grade API infrastructure so that the QBO client can handle rate limits, transient failures, and circuit breaking gracefully."

### **Solution Overview**
Port the production-grade patterns from `infra/api/base_client.py` and `infra/auth/auth.py`:
- **BaseAPIClient**: Abstract base with rate limiting, retry, circuit breaker, caching
- **QBORawClient**: Extend BaseAPIClient with QBO-specific implementation
- **QBOAuthService**: Add retry logic for token refresh operations
- **Typed Errors**: APIError hierarchy for proper error handling

### **Files to Port:**

#### **From `infra/api/base_client.py`:**
```python
# Port these classes/patterns to _clean/mvp/infra/api/

1. RateLimitConfig - Configuration for rate limiting
2. RetryConfig - Configuration for retry logic  
3. CacheConfig - Configuration for response caching
4. APIError hierarchy - RateLimitError, AuthenticationError, NetworkError
5. BaseAPIClient - Abstract base with all patterns
   - _should_allow_call() - Rate limiting logic
   - _wait_for_rate_limit() - Wait logic
   - _retry_with_backoff() - Exponential backoff
   - Circuit breaker pattern
   - Response caching
```

#### **From `infra/auth/auth.py`:**
```python
# Port these patterns to _clean/mvp/infra/auth/ (for future use)

1. LoginRequest/Response models - Pydantic schemas
2. JWT token management - create_access_token(), verify_token()
3. HTTPBearer security - FastAPI security dependency
4. Password validation - Security patterns

Note: These are for FUTURE user authentication, NOT for QBO system tokens
```

### **Pattern to Implement:**

```python
# _clean/mvp/infra/api/base_client.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class RateLimitConfig:
    """QBO-specific rate limiting configuration."""
    min_interval_seconds: float = 0.5  # 2 requests per second max
    max_calls_per_minute: int = 30     # QBO limit
    burst_limit: int = 10              # Short burst allowance
    backoff_multiplier: float = 2.0
    max_retries: int = 3

class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 retry_after: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(message)

class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    pass

class BaseAPIClient(ABC):
    """Base API client with rate limiting, retry, circuit breaker."""
    
    def __init__(self, rate_limit_config: Optional[RateLimitConfig] = None):
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.rate_limits = {
            "last_call": None,
            "minute_calls": [],
            "circuit_breaker_open": False,
            "circuit_breaker_until": None
        }
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Get the base URL for the API."""
        pass
    
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        pass
    
    def _should_allow_call(self) -> bool:
        """Check if API call should be allowed based on rate limiting."""
        # Implementation from legacy base_client.py
        pass
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        # Implementation with circuit breaker and rate limiting
        pass
```

```python
# _clean/mvp/infra/rails/qbo/client.py - Updated to extend BaseAPIClient
from infra.api.base_client import BaseAPIClient, RateLimitConfig

class QBORawClient(BaseAPIClient):
    """QBO HTTP client with rate limiting and retry logic."""
    
    def __init__(self, business_id: str, realm_id: str, db_session=None):
        # QBO-specific rate limits
        qbo_rate_config = RateLimitConfig(
            min_interval_seconds=0.5,  # 2 calls per second
            max_calls_per_minute=30,   # QBO sandbox limit
            burst_limit=10,            # Allow short bursts
            backoff_multiplier=2.0,
            max_retries=3
        )
        super().__init__(rate_limit_config=qbo_rate_config)
        
        self.business_id = business_id
        self.realm_id = realm_id
        self.base_url = f"{qbo_config.api_base_url}/{realm_id}"
        self.auth_service = QBOAuthService(business_id) if business_id else None
    
    def get_base_url(self) -> str:
        return self.base_url
    
    def get_auth_headers(self) -> Dict[str, str]:
        access_token = self.auth_service.get_valid_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
    
    def get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request with automatic rate limiting and retry."""
        return self._make_request("GET", endpoint)
```

### **QBO-Specific Rate Limits:**
From QBO API documentation:
- **Sandbox**: 30 requests per minute per realm
- **Production**: 500 requests per minute per realm
- **Burst**: Short bursts allowed but triggers throttling
- **429 Response**: Includes `Retry-After` header

### **Migration Manifest Context:**
```
PORT infra/api/base_client.py → _clean/mvp/infra/api/base_client.py
  - Keep: Rate limiting, retry logic, circuit breaker
  - Drop: Platform enum (QBO only for MVP)
  - Adapt: Make QBO-specific rate limits configurable

PORT infra/auth/auth.py → _clean/mvp/infra/auth/auth.py
  - Keep: JWT patterns, Pydantic schemas (for future user auth)
  - Drop: Not needed for QBO system tokens
  - Note: This is for FUTURE user authentication, not MVP
```

### **Acceptance Test (from Migration Manifest):**
```python
def test_throttle_hygiene():
    """QBO 429 → bounded retry → hygiene flag visible"""
    client = QBORawClient("test", "realm123")
    
    # Simulate high-volume requests
    for i in range(100):
        try:
            response = client.get("query?query=SELECT * FROM Bill MAXRESULTS 1")
        except RateLimitError as e:
            # Verify bounded retry
            assert e.retry_after is not None
            # Verify hygiene flag set
            # (This would be in sync orchestrator's on_hygiene callback)
            break
```

### **Dependencies:** Task 2 (QBO Infrastructure), Task 8 (Test Gateway and Wiring Layer)

### **Verification:** 
- Run `ls -la _clean/mvp/infra/api/` - should show API infrastructure files
- Run `python -c "from infra.api.base_client import BaseAPIClient; print('BaseAPIClient imported successfully')"`
- Run `python -c "from infra.rails.qbo.client import QBORawClient; print('QBORawClient with rate limiting')"`
- Run `pytest _clean/mvp/tests/test_qbo_throttling.py -v` - should validate rate limiting works
- Test QBO client handles 429 errors gracefully
- Test circuit breaker opens after repeated failures

### **Definition of Done:**
- [ ] API infrastructure ported from legacy to MVP
- [ ] QBO client extends BaseAPIClient with rate limiting
- [ ] QBO client handles 429 errors gracefully with retry
- [ ] Circuit breaker pattern prevents hammering QBO when down
- [ ] Exponential backoff with jitter for transient failures
- [ ] Typed error hierarchy for proper exception handling
- [ ] All tests pass with real QBO API calls
- [ ] All files properly documented

### **Progress Tracking:**
- Update status to `[🔄]` when starting work
- Update status to `[✅]` when task is complete
- Update status to `[❌]` if blocked or failed

### **Git Commit:**
- After completing verification, commit the specific files modified:
- `git add _clean/mvp/infra/api/ _clean/mvp/infra/rails/qbo/client.py _clean/mvp/infra/rails/qbo/auth.py`
- `git commit -m "feat: add production-grade API infrastructure with rate limiting and retry logic"`

### **Todo List Integration:**
- Create Cursor todo for this task when starting
- Update todo status as work progresses
- Mark todo complete when task is done

---

## **Summary**

This document provides 9 executable tasks in the correct priority order:

1. **Task 1**: Bootstrap MVP Nucleus (Foundation)
2. **Task 2**: Copy and Sanitize QBO Infrastructure (QBO Client)
3. **Task 3**: Create Database Schema and Repositories
4. **Task 4**: Implement Sync Orchestrator
5. **Task 5**: Create Domain Gateways (Rail-Agnostic Interfaces)
6. **Task 6**: Implement Infra Gateways (QBO Implementations)
7. **Task 7**: Bridge Domain Gateways to Runway Services
8. **Task 8**: Test Gateway and Wiring Layer
9. **Task 9**: Port Production-Grade API Infrastructure (Rate Limiting, Retry, Circuit Breaker)

### **Additional Solutioning Tasks**

For deeper product and workflow solutioning, see:
- **`_clean/mvp/advisor_workflow_solutioning.md`** - Tasks 10-12 for advisor workflow, calculators, and experience services

These solutioning tasks require extensive product research and user story development before implementation.

Each task includes:
- **Status tracking** with checkboxes
- **Comprehensive discovery commands** for validation
- **Recursive triage process** for safe execution
- **Specific patterns to implement** with code examples
- **Verification steps** to ensure success
- **Git commit instructions** for proper version control
- **Todo list integration** for progress tracking

**This approach ensures hands-free execution with proper validation and prevents the mistakes that led to the original architectural rot.**
