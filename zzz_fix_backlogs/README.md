# ZZZ Fix Backlogs - Infrastructure Cleanup

## How to Use These Backlogs

Each file in this directory represents a complete cleanup phase that should be executed as a git branch workflow:

1. **Create Branch**: `git checkout -b cleanup/[backlog-name]`
2. **Execute Tasks**: Work through each task in order
3. **Commit Work**: `git commit -m "Complete [backlog-name]: [summary]"`
4. **Merge Back**: `git checkout main && git merge cleanup/[backlog-name]`
5. **Delete Branch**: `git branch -d cleanup/[backlog-name]`

## Self-Service Guidelines

**You have everything you need to execute these tasks independently:**

### **Code Navigation**
- Use `grep -r "pattern" . --include="*.py"` to find files
- Use `find . -name "*.py" -exec grep -l "pattern" {} \;` for file discovery
- Use `ls -la` to explore directory structure

### **Testing Strategy**
- **After each file change**: `python -c "import main"` (fast import test)
- **After major changes**: `uvicorn main:app --reload` (full startup test)
- **At task completion**: `pytest` (comprehensive test)

### **Git Workflow**
- **Always create branch first**: `git checkout -b cleanup/[phase-name]`
- **Commit frequently**: `git add . && git commit -m "Task: [description]"`
- **Test before committing**: Run verification commands first

### **Decision Making**
- **If you see an import**: Check if it's actually used before removing
- **If you see a service**: Check what methods it calls before replacing
- **If you're unsure**: Look at the file structure and existing patterns
- **If something breaks**: Use git to rollback and try a different approach

### **No Questions Needed**
- All necessary information is in the task descriptions
- All verification commands are provided
- All rollback plans are included
- All file paths and patterns are specified

## Testing Strategy (Don't Ask, Just Do)

**Fast Test (after each file change):**
```bash
python -c "import main"
```

**Medium Test (after major changes):**
```bash
uvicorn main:app --reload
```

**Full Test (at task completion):**
```bash
pytest
```

**If any test fails:**
```bash
git checkout main
git branch -D cleanup/[phase-name]
# Start over with a fresh branch
```

## Common Patterns to Look For

**Import Removal:**
```bash
# Check if imported
grep -r "from domains.qbo.service import QBOBulkScheduledService" .

# Check if used
grep -r "QBOBulkScheduledService" domains/ar/services/ runway/routes/
```

**Service Replacement:**
```bash
# Find service usage
grep -r "self\.qbo_service\." domains/ar/services/

# Find method calls
grep -r "\.some_method(" domains/ar/services/
```

**File Structure:**
```bash
# Explore directories
ls -la domains/ar/services/
ls -la runway/routes/
ls -la infra/jobs/
```

## **Task Complexity Curation Workflow**

### **Critical Step: Curation Before Execution**

Before executing any backlog, we must **curate tasks by complexity**:

#### **✅ FULLY SOLVED - Ready for Hands-Free Execution**
These tasks have:
- Clear implementation patterns with code examples
- Specific files to fix with exact changes needed
- Complete verification steps with pytest commands
- No "figure out" or "analyze" language
- Ready for execution by any developer

#### **⚠️ NEEDS SOLUTION WORK - Not Ready for Hands-Free**
These tasks require:
- Analysis and discovery work
- "Figure out" or "determine" language present
- Dependencies on other solution tasks
- Architectural decisions that need human input
- Cannot be executed without solution phase

### **Curation Process**
1. **Read each task completely** - look for solution language
2. **Check for clear patterns** - are implementation steps specific?
3. **Verify verification steps** - are pytest commands specific?
4. **Identify dependencies** - do tasks depend on analysis work?
5. **Split into phases** - executable vs solution tasks

### **Phase A: Executable Tasks**
- Contains only fully-solved tasks
- Ready for hands-free execution
- Can be run by any developer
- Clear success criteria

### **Phase B: Solution Tasks**
- Contains tasks needing analysis work
- Require human input and decision-making
- Should be tackled when you have bandwidth
- Can be converted to executable tasks once solved

### **Progress Tracking**
- **Work in sequence**: Execute tasks in order by their `00?` number
- **Update status**: Change `[ ]` to `[✅]` when complete
- **Archive completed**: Move completed files to `archive/` directory
- **Simple tracking**: Use the status field in each task

---

## Current Cleanup Phases:
- `000_phase_a_executable_tasks.md` - ✅ **READY FOR HANDS-FREE EXECUTION** (8 tasks)
- `001_phase_b_solution_tasks.md` - ⚠️ **NEEDS SOLUTION WORK** (5 tasks)
- `001_infra_phase3_consolidate_file_processing.md` - Consolidate file processing
- `002_infra_phase3_create_notifications.md` - Create notifications infrastructure
- `003_infra_phase3_create_monitoring.md` - Create monitoring infrastructure
- `004_infra_phase3_create_utils.md` - Create utilities infrastructure

## Git Workflow:
```bash
# Start a cleanup phase
git checkout -b cleanup/smartsync-cleanup
# ... do work ...
git add .
git commit -m "Complete SmartSync cleanup: Remove QBOBulkScheduledService, fix imports, consolidate infra/jobs/"
git checkout main
git merge cleanup/smartsync-cleanup
git branch -d cleanup/smartsync-cleanup
```

## Why This Approach:
- **Prevents Lost Work**: Each phase is isolated in its own branch
- **Clear Progress**: Easy to see what's been cleaned up and what's left
- **Recoverable**: If something goes wrong, just delete the branch and start over
- **Systematic**: Can't start next phase until current one is complete and merged
- **Clean History**: Each cleanup phase has a clear commit message

## Execution Order:
1. **SmartSync Cleanup** (P0 Critical) - Fix the architecture issues
2. **File Processing** (P1 High) - Consolidate file handling
3. **Notifications** (P1 High) - Create notification infrastructure
4. **Monitoring** (P1 High) - Create monitoring infrastructure
5. **Utilities** (P1 High) - Consolidate utility functions

## Rollback Strategy:
If any phase fails or causes issues:
```bash
# Abandon the current phase
git checkout main
git branch -D cleanup/[phase-name]

# Or rollback specific changes
git checkout main
git reset --hard HEAD~1  # Go back one commit
```

This approach ensures we never lose work and can always get back to a clean state.
