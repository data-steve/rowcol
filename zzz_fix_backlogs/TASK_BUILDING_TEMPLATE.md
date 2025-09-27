# Task Building Template

*Template for curating tasks by complexity into Executable, Needs Solving, and Blocked categories*

## **Overview**

This template documents the process for taking raw task backlogs and curating them into three categories based on complexity and readiness for execution.

## **Task Categories**

### **0_EXECUTABLE_TASKS.md** - Ready for Hands-Free Execution
**Characteristics:**
- Clear implementation patterns with code examples
- Specific files to fix with exact changes needed
- Complete verification steps with pytest commands
- No "figure out" or "analyze" language
- Ready for execution by any developer familiar with the codebase

**Status Format:** `[ ]` Not started

**Required Sections:**
- Context for All Tasks
- Critical Warnings from Painful Lessons
- **CRITICAL: Recursive Discovery/Triage Pattern** - Built into every task
- Task details with:
  - Status, Priority, Justification
  - **Initial Files to Fix** (starting point, not comprehensive)
  - **MANDATORY: Comprehensive Discovery Commands** (find ALL occurrences)
  - **MANDATORY: Recursive Triage Process** (understand context before changing)
  - **MANDATORY: Comprehensive Cleanup Requirements** (handle all edge cases)
  - Required Imports/Changes
  - Pattern to Implement (with code examples)
  - Dependencies
  - Verification Commands
  - Definition of Done
- **Progress Tracking Instructions** - Clear steps for updating task status as work progresses
- **Git Workflow Instructions** - Surgical commit steps for each task
- **Todo List Integration** - Cursor todo list management requirements

### **1_NEEDS_SOLVING_TASKS.md** - Needs Analysis and Solution Work
**Characteristics:**
- Analysis and discovery work required
- "Figure out" or "determine" language present
- Dependencies on other solution tasks
- Architectural decisions that need human input
- Cannot be executed without solution phase

**Status Format:** `[ ]` Not started

**Required Sections:**
- Context for All Tasks
- Task details with:
  - Status, Priority, Justification
  - Code Pointers
  - Current Issues to Resolve
  - Required Analysis
  - Dependencies
  - Verification
  - Definition of Done
  - Solution Required (what needs to be figured out)
- **Progress Tracking Instructions** - Clear steps for updating task status as analysis progresses

### **2_BLOCKED_TASKS.md** - Blocked by Solution Tasks
**Characteristics:**
- Ready for hands-free execution (same complexity as executable tasks)
- Blocked by solution tasks that need to be completed first
- Will become executable once dependencies are resolved

**Status Format:** `[ ]` Not started

**Required Sections:**
- Context for Blocked Tasks
- Blocking Analysis
- Resolution Path
- Summary

## **Curation Process**

### **Step 1: Read and Understand**
1. Read the original backlog completely
2. Understand the context and goals
3. Identify all tasks and their current state

### **Step 2: Categorize by Complexity**
For each task, ask:

#### **Executable Task Gatekeeping Questions:**
- **Is this fully solved?** (Clear implementation pattern exists)
- **Are ALL files identified?** (Not just initial files, but comprehensive discovery commands provided)
- **Is the recursive triage process defined?** (Understand context before changing)
- **Are cleanup requirements comprehensive?** (Handle all edge cases, not just basic changes)
- **Is there NO "figure out" language?** (Everything is specific and actionable)
- **Can any developer execute this?** (No additional context needed)

**If ANY answer is NO → Needs Solving**

#### **Needs Solving Task Gatekeeping Questions:**
- **Does this need analysis work?** (Discovery, understanding, design required)
- **Is there "figure out" or "determine" language?** (Indicates unknowns)
- **Are there architectural decisions needed?** (Requires human input)
- **Are dependencies unclear?** (Need to map relationships)
- **Does the solution need to be designed?** (Not just implemented)

**If ANY answer is YES → Needs Solving**

#### **Blocked Task Gatekeeping Questions:**
- **Is this ready for execution?** (Same complexity as executable tasks)
- **Is it blocked by solution tasks?** (Dependencies need to be resolved first)
- **Will it become executable once unblocked?** (No additional analysis needed)

**If ALL answers are YES → Blocked**

### **CRITICAL: Recursive Discovery/Triage Pattern**

**NEVER do blind search-and-replace!** This pattern prevents costly mistakes during task curation:

1. **Search for all occurrences** of patterns mentioned in the task
2. **Read the broader context** around each occurrence to understand what the method, service, route, or file is doing
3. **Triage each occurrence** - determine what it actually does vs what the task assumes:
   - What is this method's real purpose?
   - What are its dependencies and relationships?
   - What would break if we changed it?
   - Is this a false positive or actually relevant?
4. **Map the real system** - understand how things actually work vs how the task assumes they work
5. **Document assumptions vs reality** - write down what you found vs what the task assumed
6. **Plan based on reality** - design solutions based on what actually exists

**Example Discovery Pattern:**
```bash
# Step 1: Find all occurrences
grep -r "get_.*_for_digest" . --include="*.py"

# Step 2: For each file found, read the broader context
# - What is this method actually doing?
# - What are its real dependencies?
# - How is it being used in practice?
# - What would break if we changed it?

# Step 3: Map the real system
# - How do these pieces actually connect?
# - What are the real data flows?
# - What are the real dependencies?

# Step 4: Document reality vs assumptions
# - What did the task assume vs what actually exists?
# - What patterns are we seeing?
# - What needs to be designed vs what can be fixed?
```

### **Step 3: Preserve All Detail**
- **Lift and shift** - don't edit or simplify
- Preserve all critical warnings, search commands, verification steps
- Keep all implementation patterns and code examples
- Maintain all context and justification

### **Step 4: Create Curated Files**
1. Create `0_EXECUTABLE_TASKS.md` with fully-solved tasks
2. Create `1_NEEDS_SOLVING_TASKS.md` with analysis tasks
3. Create `2_BLOCKED_TASKS.md` with blocked tasks
4. Archive original files

### **Step 5: Clean Up**
- Remove "spec" and "agent" references
- Remove "Ready for Spec" status
- Update "Next Action" to point to next task
- Ensure consistent formatting

## **Quality Checklist**

### **Executable Tasks**
- [ ] Clear implementation patterns with code examples
- [ ] Specific files to fix with exact changes
- [ ] Complete verification steps
- [ ] No "figure out" language
- [ ] Ready for hands-free execution
- [ ] **Progress tracking instructions included**
- [ ] **Git workflow instructions included**

### **Needs Solving Tasks**
- [ ] Clear analysis requirements
- [ ] "Figure out" or "determine" language present
- [ ] Dependencies clearly identified
- [ ] Solution Required section explains what needs to be figured out
- [ ] **Progress tracking instructions included**

### **Blocked Tasks**
- [ ] Ready for execution once unblocked
- [ ] Blocking dependencies clearly identified
- [ ] Resolution path outlined

## **Common Patterns**

### **Executable Task Pattern**
```markdown
#### **Task: [Task Name]**
- **Status:** `[ ]` Not started
- **Priority:** P0 Critical / P1 High / P2 Medium
- **Justification:** [Why this task is needed]

- **Initial Files to Fix:** (Starting point - NOT comprehensive)
  - `file1.py` - [specific change needed]
  - `file2.py` - [specific change needed]

- **MANDATORY: Comprehensive Discovery Commands:**
  ```bash
  # Find ALL occurrences of the pattern
  grep -r "pattern" . --include="*.py"
  grep -r "related_pattern" . --include="*.py"
  grep -r "import.*pattern" . --include="*.py"
  find . -name "*.py" -exec grep -l "pattern" {} \;
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
     - Update method names AND all calls to those methods
     - Update imports AND all references
     - Handle edge cases and multiple patterns in same file
     - Update related logic that depends on the changes

- **MANDATORY: Comprehensive Cleanup Requirements:**
  - **File Operations:** Use `cp` then `rm` for moves, never just `mv`
  - **Import Cleanup:** Remove ALL old imports, add ALL new imports
  - **Reference Cleanup:** Update ALL references to renamed methods/classes
  - **Dependency Cleanup:** Update ALL dependent code
  - **Test Cleanup:** Update ALL test files that reference changed code
  - **Documentation Cleanup:** Update ALL documentation references

- **Required Imports/Changes:**
  - Remove: `old_import`
  - Add: `new_import`

- **Pattern to Implement:**
  ```python
  # Code example here
  ```

- **Dependencies:** [List any dependencies]

- **Verification:** 
  - Run `grep -r "old_pattern" . --include="*.py"` - should return no results
  - Run `grep -r "new_pattern" . --include="*.py"` - should show new usage
  - **Check uvicorn in Cursor terminal** - should be running without errors
  - Run `pytest` - should pass without import failures

- **Definition of Done:**
  - [Specific outcome 1]
  - [Specific outcome 2]
  - ALL occurrences found and updated (not just initial files)
  - No broken references or imports anywhere
  - Comprehensive cleanup completed

- **Progress Tracking:**
  - Update status to `[🔄]` when starting work
  - Update status to `[✅]` when task is complete
  - Update status to `[❌]` if blocked or failed

- **Git Commit:**
  - After completing verification, commit the specific files modified:
  - `git add [specific-files-modified]`
  - `git commit -m "feat: [task-description] - [brief-summary]"`

- **Todo List Integration:**
  - Create Cursor todo for this task when starting
  - Update todo status as work progresses
  - Mark todo complete when task is done
  - Add cleanup todos for discovered edge cases
```

### **Needs Solving Task Pattern**
```markdown
#### **Task: [Task Name]**
- **Status:** `[ ]` Not started
- **Priority:** P1 High / P2 Medium
- **Justification:** [Why this task is needed]
- **Code Pointers:**
  - `file1.py` - [what to look at]
  - `file2.py` - [what to look at]
- **Current Issues to Resolve:**
  - [Issue 1]
  - [Issue 2]
- **Required Analysis:**
  - [What needs to be figured out]
- **Dependencies:** [List any dependencies]
- **Verification:** 
  - [How to verify the solution works]
- **Definition of Done:**
  - [What the solution should achieve]
- **Solution Required:** [What needs to be figured out]
- **Progress Tracking:**
  - Update status to `[🔄]` when starting analysis
  - Update status to `[💡]` when solution is identified
  - Update status to `[✅]` when solution is documented
  - Update status to `[❌]` if blocked or need help
```

## **File Naming Convention**

- `0_EXECUTABLE_TASKS.md` - Ready for execution
- `1_NEEDS_SOLVING_TASKS.md` - Need analysis work
- `2_BLOCKED_TASKS.md` - Blocked by dependencies
- `backlog/` - Original backlogs for future curation

## **Git Workflow**

1. **Create branch:** `git checkout -b curate/[backlog-name]`
2. **Curate tasks:** Create the 3 curated files
3. **Clean up:** Remove spec/agent references
4. **Archive:** Move original files to archive/
5. **Commit:** `git add . && git commit -m "Curate [backlog-name] tasks by complexity"`
6. **Merge:** `git checkout main && git merge curate/[backlog-name]`

## **Success Metrics**

- **Executable Tasks:** Can be executed by any developer without additional context
- **Needs Solving Tasks:** Clear what analysis work is needed
- **Blocked Tasks:** Clear what dependencies need to be resolved
- **No Information Loss:** All detail preserved from original backlogs
- **Clean Formatting:** No spec/agent references, consistent status format
- **Git Workflow:** Clear surgical commit instructions for each task

## **Common Mistakes to Avoid**

- **Don't simplify** - preserve all detail from original
- **Don't edit tasks** - just curate by complexity
- **Don't remove warnings** - they're there for a reason
- **Don't change verification steps** - they're tested and working
- **Don't add new requirements** - just organize existing ones
- **Don't forget git workflow** - surgical commits are essential

## **Critical Lessons Learned**

### **Why Tasks Fail:**
1. **Incomplete Discovery**: Tasks list specific files but miss others found during execution
2. **Blind Search-and-Replace**: Changes made without understanding context
3. **Insufficient Cleanup**: Edge cases and dependencies not handled
4. **Missing File Operations**: Using `mv` instead of `cp` then `rm`
5. **No Todo Integration**: Progress not tracked in Cursor todo list

### **Success Patterns:**
1. **Comprehensive Discovery**: Find ALL occurrences, not just initial files
2. **Recursive Triage**: Understand context before making changes
3. **Comprehensive Cleanup**: Handle all edge cases and dependencies
4. **Proper File Operations**: Use `cp` then `rm` for moves
5. **Todo Integration**: Track progress and discovered edge cases

### **Template Requirements:**
- **Every executable task MUST have comprehensive discovery commands**
- **Every executable task MUST have recursive triage process**
- **Every executable task MUST have comprehensive cleanup requirements**
- **Every executable task MUST have todo list integration**
- **Gatekeeping questions MUST be used to distinguish task types**

## **Updates to This Template**

As we discover issues or improvements in the curation process, update this template to capture the learnings for future use.