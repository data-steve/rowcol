# E01_FIRM_FIRST_FOUNDATION.md - Multi-Tenant Foundation

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
git add domains/core/models/firm.py domains/core/models/firm_staff.py
git commit -m "feat: add firm models - multi-tenant foundation"
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

#### **Task: Add Firm Models**
- **Status**: `[ ]` Not started
- **Priority**: P0 Critical
- **Justification**: Multi-tenant foundation requires Firm and FirmStaff models

- **Initial Files to Fix**: (Starting point - NOT comprehensive)
  - `domains/core/models/firm.py` - needs to be created
  - `domains/core/models/firm_staff.py` - needs to be created
  - `domains/core/models/business.py` - needs firm_id field added
  - `alembic/versions/` - needs new migration

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find all existing model patterns
  grep -r "class.*Base" domains/core/models/ --include="*.py"
  grep -r "business_id" domains/core/models/ --include="*.py"
  find domains/core/models/ -name "*.py" -type f
  grep -r "from.*base" domains/core/models/ --include="*.py"
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
     - Create Firm model following existing patterns
     - Create FirmStaff model following existing patterns
     - Add firm_id to Business model (nullable)
     - Create Alembic migration
     - Handle edge cases and multiple patterns in same file

- **Pattern to Implement:**
  ```python
  # Create: domains/core/models/firm.py
  from sqlalchemy import Column, Integer, String, Boolean, DateTime
  from sqlalchemy.orm import relationship
  from domains.core.models.base import Base
  
  class Firm(Base):
      __tablename__ = "firms"
      
      id = Column(Integer, primary_key=True, index=True)
      name = Column(String(255), nullable=False)
      contact_email = Column(String(255), nullable=False)
      active = Column(Boolean, default=True)
      created_at = Column(DateTime, default=datetime.utcnow)
      updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
      
      # Relationships
      staff = relationship("FirmStaff", back_populates="firm")
      businesses = relationship("Business", back_populates="firm")
  
  # Create: domains/core/models/firm_staff.py
  from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
  from sqlalchemy.orm import relationship
  from domains.core.models.base import Base
  
  class FirmStaff(Base):
      __tablename__ = "firm_staff"
      
      id = Column(Integer, primary_key=True, index=True)
      firm_id = Column(Integer, ForeignKey("firms.id"), nullable=False)
      user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
      role = Column(String(50), nullable=False)  # admin, staff, view_only
      created_at = Column(DateTime, default=datetime.utcnow)
      updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
      
      # Relationships
      firm = relationship("Firm", back_populates="staff")
      user = relationship("User", back_populates="firm_staff")
  
  # Update: domains/core/models/business.py
  # Add this field to existing Business model:
  firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
  firm = relationship("Firm", back_populates="businesses")
  ```

- **Required Imports/Changes:**
  - Create: `domains/core/models/firm.py`
  - Create: `domains/core/models/firm_staff.py`
  - Update: `domains/core/models/business.py` to add firm_id field
  - Create: Alembic migration for new tables
  - Add: Import statements for new models

- **Dependencies**: None - this is a foundational task

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification**: 
  - Run `grep -r "class Firm" domains/core/models/` - should show new model
  - Run `grep -r "class FirmStaff" domains/core/models/` - should show new model
  - Run `grep -r "firm_id" domains/core/models/business.py` - should show new field
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - Firm model created following established patterns
  - FirmStaff model created following established patterns
  - Business model updated with firm_id field
  - Alembic migration created and applied
  - All imports and references updated
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add domains/core/models/firm.py domains/core/models/firm_staff.py domains/core/models/business.py alembic/versions/[migration_file].py`
  - `git commit -m "feat: add firm models - multi-tenant foundation"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state

---

#### **Task: Implement Firm-Level Authentication & RBAC**
- **Status**: `[ ]` Not started
- **Priority**: P0 Critical
- **Justification**: Firm staff need role-based access control

- **Initial Files to Fix**: (Starting point - NOT comprehensive)
  - `infra/auth/auth.py` - needs firm context extraction
  - All route files - need firm context filtering
  - `infra/database/dependency_injection.py` - needs firm context

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find all authentication related code
  grep -r "get_current_user" . --include="*.py"
  grep -r "get_current_business_id" . --include="*.py"
  grep -r "Depends.*auth" . --include="*.py"
  grep -r "JWT" . --include="*.py"
  grep -r "token" . --include="*.py"
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
     - Extract firm_id from JWT/session
     - Filter queries by firm_id → client_ids
     - Implement RBAC (admin/staff/view-only)
     - Handle edge cases and multiple patterns in same file

- **Pattern to Implement:**
  ```python
  # Update: infra/auth/auth.py
  def get_current_firm_id(current_user: User = Depends(get_current_user)) -> str:
      """Get current firm ID from user context."""
      # Extract firm_id from user's firm_staff relationship
      return current_user.firm_staff[0].firm_id if current_user.firm_staff else None
  
  def get_current_client_ids(current_user: User = Depends(get_current_user)) -> List[str]:
      """Get current client IDs for firm context."""
      firm_id = get_current_firm_id(current_user)
      if not firm_id:
          return []
      
      # Get all business_ids for this firm
      db = next(get_db())
      businesses = db.query(Business).filter(Business.firm_id == firm_id).all()
      return [str(b.id) for b in businesses]
  
  # Update: All route files
  @router.get("/bills")
  async def get_bills(
      firm_id: str = Depends(get_current_firm_id),
      client_ids: List[str] = Depends(get_current_client_ids),
      db: Session = Depends(get_db)
  ):
      # Filter by client_ids instead of single business_id
      bills = db.query(Bill).filter(Bill.business_id.in_(client_ids)).all()
      return bills
  ```

- **Required Imports/Changes:**
  - Update: `infra/auth/auth.py` with firm context functions
  - Update: All route files to use firm context filtering
  - Add: Import statements for new auth functions

- **Dependencies**: Task 1 (Add Firm Models) must be complete

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification**: 
  - Run `grep -r "get_current_firm_id" . --include="*.py"` - should show usage
  - Run `grep -r "get_current_client_ids" . --include="*.py"` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - Firm context extraction implemented
  - RBAC system implemented
  - All routes updated for firm context filtering
  - All imports and references updated
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add infra/auth/auth.py [all-modified-route-files]`
  - `git commit -m "feat: implement firm-level authentication and RBAC"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state

---

#### **Task: Create Firm-Level Routes**
- **Status**: `[ ]` Not started
- **Priority**: P0 Critical
- **Justification**: CAS firms need batch views across all clients

- **Initial Files to Fix**: (Starting point - NOT comprehensive)
  - `runway/routes/firm_dashboard.py` - needs to be created
  - `runway/routes/firm_clients.py` - needs to be created
  - `runway/experiences/firm_dashboard.py` - needs to be created

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find all existing route patterns
  grep -r "@router.get" runway/routes/ --include="*.py"
  grep -r "def.*dashboard" runway/routes/ --include="*.py"
  grep -r "def.*clients" runway/routes/ --include="*.py"
  find runway/routes/ -name "*.py" -type f
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
     - Create firm dashboard routes
     - Create firm clients management routes
     - Handle edge cases and multiple patterns in same file

- **Pattern to Implement:**
  ```python
  # Create: runway/routes/firm_dashboard.py
  from fastapi import APIRouter, Depends, HTTPException
  from sqlalchemy.orm import Session
  from infra.database.session import get_db
  from infra.auth.auth import get_current_firm_id, get_current_client_ids
  from runway.experiences.firm_dashboard import FirmDashboardExperience
  
  router = APIRouter(prefix="/firms", tags=["firm-dashboard"])
  
  @router.get("/{firm_id}/dashboard")
  async def get_firm_dashboard(
      firm_id: str,
      current_firm_id: str = Depends(get_current_firm_id),
      client_ids: List[str] = Depends(get_current_client_ids),
      db: Session = Depends(get_db)
  ):
      """Get batch runway view for all clients."""
      if firm_id != current_firm_id:
          raise HTTPException(status_code=403, detail="Access denied")
      
      experience = FirmDashboardExperience(db, firm_id, client_ids)
      return experience.get_dashboard_data()
  
  @router.get("/{firm_id}/data-quality")
  async def get_firm_data_quality(
      firm_id: str,
      current_firm_id: str = Depends(get_current_firm_id),
      client_ids: List[str] = Depends(get_current_client_ids),
      db: Session = Depends(get_db)
  ):
      """Get data quality scores for all clients."""
      if firm_id != current_firm_id:
          raise HTTPException(status_code=403, detail="Access denied")
      
      experience = FirmDashboardExperience(db, firm_id, client_ids)
      return experience.get_data_quality_scores()
  
  # Create: runway/routes/firm_clients.py
  @router.get("/{firm_id}/clients")
  async def get_firm_clients(
      firm_id: str,
      current_firm_id: str = Depends(get_current_firm_id),
      db: Session = Depends(get_db)
  ):
      """List all clients for the firm."""
      if firm_id != current_firm_id:
          raise HTTPException(status_code=403, detail="Access denied")
      
      clients = db.query(Business).filter(Business.firm_id == firm_id).all()
      return clients
  
  @router.post("/{firm_id}/clients")
  async def add_firm_client(
      firm_id: str,
      client_data: dict,
      current_firm_id: str = Depends(get_current_firm_id),
      db: Session = Depends(get_db)
  ):
      """Add new client to the firm."""
      if firm_id != current_firm_id:
          raise HTTPException(status_code=403, detail="Access denied")
      
      client = Business(**client_data, firm_id=firm_id)
      db.add(client)
      db.commit()
      return client
  ```

- **Required Imports/Changes:**
  - Create: `runway/routes/firm_dashboard.py`
  - Create: `runway/routes/firm_clients.py`
  - Create: `runway/experiences/firm_dashboard.py`
  - Add: Import statements for new routes

- **Dependencies**: Task 2 (Firm-Level Authentication) must be complete

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Verification**: 
  - Run `grep -r "firm_dashboard" . --include="*.py"` - should show usage
  - Run `grep -r "firm_clients" . --include="*.py"` - should show usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - Firm dashboard routes created
  - Firm clients management routes created
  - All imports and references updated
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add runway/routes/firm_dashboard.py runway/routes/firm_clients.py runway/experiences/firm_dashboard.py`
  - `git commit -m "feat: create firm-level routes - batch views and client management"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
  - Remove obsolete todos when files are deleted
  - Ensure todo list reflects current system state

---

**Status**: Ready for immediate execution  
**Next Action**: Start with Task 1 (Add Firm Models)  
**Branch**: `feat/firm-first`  
**Updated**: 2025-09-30
