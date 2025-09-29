# Launch Executable Tasks - Reusable Recipe

*This file contains the standard instructions for executing fully-solved tasks hands-free*

## **Quick Start**

1. **Navigate to Project**: `cd ~/projects/oodaloo` (if not already there)
2. **Activate Environment**: `poetry shell` (one-time setup)
3. **Create Branch**: `git checkout -b cleanup/[task-name]`
4. **Start Application**: `uvicorn main:app --reload` (one-time, keep running in background)
5. **Execute Sequentially**: Work through tasks in order by their number
6. **Update Status**: Change `[ ]` to `[✅]` when complete
7. **Archive When Done**: Move completed task file to `archive/` when all tasks complete

## **CRITICAL: Read These Files First**

Before starting any executable tasks, you MUST read these files to understand the system:

### **Architecture Context:**
- `docs/architecture/COMPREHENSIVE_ARCHITECTURE.md` - Complete system architecture
- `docs/build_plan_v5.md` - Current build plan and phase context
- `docs/architecture/ADR-001-domains-runway-separation.md` - Domain separation principles
- `docs/architecture/ADR-005-qbo-api-strategy.md` - QBO integration strategy
- `docs/architecture/ADR-003-multi-tenancy-strategy.md` - Multi-tenancy patterns

### **Task-Specific Context:**
- Review the specific task document for additional context files
- Understand the current phase and architectural constraints
- Familiarize yourself with the codebase structure and patterns

## **Progress Tracking**

- `[ ]` - Not started
- `[🔄]` - In progress  
- `[✅]` - Completed
- `[❌]` - Failed/Blocked

**IMPORTANT**: Always update the task status in the document as you work through tasks. This allows tracking progress and identifying which tasks are complete.

## **Todo List Management (MANDATORY)**

### **For Each Task:**
1. **Create Cursor Todo:** When starting a task, create a todo in Cursor
2. **Update Todo Status:** As work progresses, update todo status
3. **Add Cleanup Todos:** For discovered edge cases, add cleanup todos
4. **Complete Todos:** Mark todos complete when work is done
5. **Clean Up Todos:** Remove obsolete todos when files are deleted

### **Todo Status Mapping:**
- `[ ]` Not started → Todo: "Not Started"
- `[🔄]` In progress → Todo: "In Progress"
- `[✅]` Completed → Todo: "Complete"
- `[❌]` Failed/Blocked → Todo: "Blocked"

## **Execution Pattern**

### **For Each Task:**
1. **Read the task completely** - understand files to fix, patterns to implement
2. **CRITICAL: Validate Assumptions Against Reality** - don't assume task descriptions are accurate
3. **CRITICAL: Use Recursive Discovery/Triage Pattern** - understand what actually needs to be done
4. **Follow the implementation pattern** - use the provided code examples
5. **Run verification commands** - ensure changes work correctly
6. **Test with pytest** - run the specified test commands
7. **Update status in document** - change `[ ]` to `[✅]` in the task list
8. **Surgical git commit** - commit only the files modified for this task:
   ```bash
   git add [specific-files-modified]
   git commit -m "feat: [task-description] - [brief-summary]"
   ```

### **CRITICAL: Assumption Validation Before Execution**

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

#### **Validation Process:**
1. **From a basic grep, search recursively outward** in that file until you understand what that code was intended to help with
2. **Then you will understand what the fix actually needs to be** beyond simplistic search and replace
3. **With that understanding you can compare it** to your understanding of broader task and ADRs, building plan etc
4. **Document mismatches** between task assumptions and code reality
5. **Plan fixes based on reality** not assumptions

### **CRITICAL: Recursive Discovery/Triage Pattern**

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

**Example Pattern:**
```bash
# Step 1: Find all occurrences
grep -r "get_.*_for_digest" . --include="*.py"

# Step 2: For each file found, read the broader context
# - What is this method doing?
# - What are the dependencies?
# - What needs to be updated beyond just the method name?

# Step 3: Plan comprehensive updates
# - Update method name
# - Update all calls to the method
# - Update imports if needed
# - Update related logic if needed

# Step 4: Implement with full context understanding
```

## **Comprehensive Cleanup (MANDATORY)**

### **After Each Task:**
1. **Remove Obsolete Files:** Delete any files that are no longer needed
2. **Clean Up Imports:** Remove unused imports, add missing imports
3. **Update References:** Fix all broken references and method calls
4. **Clean Up Tests:** Update test files that reference changed code
5. **Verify Cleanup:** Run verification commands to ensure no broken references

### **Cleanup Verification Commands:**
```bash
# Check for broken references
grep -r "old_pattern" . --include="*.py"
find . -name "*.py" -exec grep -l "obsolete_pattern" {} \;

# Check for unused imports
grep -r "import.*unused" . --include="*.py"

# Verify no broken references
pytest
uvicorn main:app --reload
```

### **After All Tasks:**
1. **Archive task file** - move to `archive/` directory
2. **Merge branch** - `git checkout main && git merge cleanup/[task-name] && git branch -d cleanup/[task-name]`

## **Verification Strategy**

- **One-time startup**: `uvicorn main:app --reload` (keep running in background)
- **After EACH file change**: Check that uvicorn is still running (no restart needed)
- **After EACH task**: Run specified pytest commands
- **Before deleting ANY file**: `grep -r "filename" . --include="*.py"` to check references
- **Test user actions**: Verify they work immediately
- **Test background syncs**: Verify they use SmartSyncService correctly

## **Common Commands**

```bash
# Check for QBOBulkScheduledService usage
grep -r "QBOBulkScheduledService" domains/ar/services/ runway/routes/

# Check for QBODataService misuse
grep -r "QBODataService" runway/routes/ tests/

# Check for old infra imports
grep -r "from infra\.(cache|queue|scheduler)" . --include="*.py"

# Check for get_X_for_digest methods
grep -r "get_.*_for_digest" domains/

# Test application startup (one-time)
uvicorn main:app --reload

# Run tests
pytest
```

## **Git Workflow**

### **Surgical Commits (Per Task)**
```bash
# After completing each task, commit only the files you modified:
git add [file1.py] [file2.py] [file3.py]
git commit -m "feat: [task-name] - [brief-description-of-changes]"

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

## **Architecture Context**

- **SmartSyncService** (`infra/jobs/smart_sync.py`): Central orchestration for ALL QBO interactions
- **QBOBulkScheduledService** (`domains/qbo/service.py`): ONLY bulk background operations (digest generation)
- **QBODataService** (`domains/qbo/data_service.py`): ONLY `runway/experiences/` data formatting
- **Direct QBO API calls** (`domains/qbo/client.py`): Immediate user actions (pay bill, delay payment)

**Key Principle**: User actions = Direct QBO API calls wrapped in SmartSyncService. Data syncs = SmartSyncService orchestration.

---

## **TASK LIST GOES HERE**

*Attach your specific executable task list to this file*

**⚠️ IMPORTANT: Do NOT run multiple tasks simultaneously - they have dependencies and will collide!**

**⚠️ IMPORTANT: Use surgical git commits - only commit the files you actually modified for each task!**