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

## Review these files first:
- docs/build_plan_v5.md
- docs/architecture/

## **Progress Tracking**

- `[ ]` - Not started
- `[🔄]` - In progress  
- `[✅]` - Completed
- `[❌]` - Failed/Blocked

**IMPORTANT**: Always update the task status in the document as you work through tasks. This allows tracking progress and identifying which tasks are complete.

## **Execution Pattern**

### **For Each Task:**
1. **Read the task completely** - understand files to fix, patterns to implement
2. **CRITICAL: Use Recursive Discovery/Triage Pattern** - understand what actually needs to be done : 
- from a basic grep, search recursively outward in that file until you understand what that code was intended to help with
- then you will understand what the fix actually needs to be beyond simplistic search and replace
- with that understanding you could even compare it to your understanding off broader task and ADRs, biulding plan etc
3. **Follow the implementation pattern** - use the provided code examples
4. **Run verification commands** - ensure changes work correctly
5. **Test with pytest** - run the specified test commands
6. **Update status in document** - change `[ ]` to `[✅]` in the task list
7. **Surgical git commit** - commit only the files modified for this task:
   ```bash
   git add [specific-files-modified]
   git commit -m "feat: [task-description] - [brief-summary]"
   ```

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